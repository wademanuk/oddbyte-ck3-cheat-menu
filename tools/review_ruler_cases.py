"""Native effect/guard coverage for the five ruler-tool groups in a disposable game."""
from pdx_script import dump,get


def append_ruler_cases(add,action,expect,subjects,number,make,guard,guis,meta,grant):
 def no(name,case):expect('ruler_'+case,'NOT = { '+guard('twcm_editor_'+name)+' }')
 def begin(name):add(dump(get(guis['twcm_editor_'+name],'effect')))
 def cancel():add(dump(get(guis['twcm_ui_cancel'],'effect')))
 for person in ['lord','other_lord','person','teacher','teacher2','third_person']:
  make('twcm_ruler_'+person)
 for child,age in [('ward',10),('ward2',10),('ward3',10),('infant',3)]:
  make('twcm_ruler_'+child,age=age)
 grant('c_ossory','scope:twcm_ruler_lord');grant('c_thomond','scope:twcm_ruler_other_lord')
 # Receiving a county already creates a lowborn ruler's house/dynasty.
 subjects('scope:twcm_ruler_person')
 for name in ['legitimacy_add_100','legitimacy_remove_100','clear_tyranny']:
  no(name,'courtier_disabled_'+name)
 for name in ['dread_add','dread_remove','exact_dread']:
  no(name,'courtier_disabled_'+name)
 subjects('scope:twcm_ruler_lord')
 for value in [0,37,100]:
  number(value);action('exact_dread')
  expect('ruler_dread_'+str(value),'scope:twcm_ruler_lord = { dread = '+str(value)+' }')
 action('dread_add');expect('ruler_dread_upper_clamp','scope:twcm_ruler_lord = { dread = 100 }')
 number(0);action('exact_dread');action('dread_remove')
 expect('ruler_dread_lower_clamp','scope:twcm_ruler_lord = { dread = 0 }')
 number(101);no('exact_dread','dread_invalid_number')
 number(47);begin('exact_dread');subjects('scope:twcm_ruler_third_person');number(88)
 expect('ruler_dread_review_snapshot_valid',guard('twcm_ui_confirm'))
 add('twcm_smoke_apply_effect = yes')
 expect('ruler_dread_snapshot_applied','scope:twcm_ruler_lord = { dread = 47 } scope:twcm_ruler_third_person = { dread = 0 }')
 subjects('scope:twcm_ruler_lord')
 add('scope:twcm_ruler_lord = { add_legitimacy = { value = legitimacy multiply = -1 } add_tyranny = 37 }')
 action('legitimacy_add_100');expect('ruler_legitimacy_add','scope:twcm_ruler_lord = { legitimacy = 100 }')
 action('legitimacy_add_500');expect('ruler_legitimacy_add_large','scope:twcm_ruler_lord = { legitimacy = 600 }')
 action('legitimacy_remove_500');action('legitimacy_remove_100')
 expect('ruler_legitimacy_remove','scope:twcm_ruler_lord = { legitimacy = 0 }')
 action('legitimacy_remove_100');expect('ruler_legitimacy_floor','scope:twcm_ruler_lord = { legitimacy = 0 }')
 begin('clear_tyranny');cancel();expect('ruler_cancel_tyranny','scope:twcm_ruler_lord = { tyranny = 37 }')
 action('clear_tyranny');expect('ruler_tyranny_cleared','scope:twcm_ruler_lord = { tyranny = 0 }')
 no('clear_tyranny','already_clear_tyranny')

 # Shared culture edits are bidirectional, capped, and bound to the original cultures.
 add('scope:twcm_ruler_person = { set_culture = culture:irish } scope:twcm_ruler_teacher = { set_culture = culture:english } culture:irish = { set_cultural_acceptance = { target = culture:english value = 20 } }')
 subjects('scope:twcm_ruler_person','scope:twcm_ruler_teacher')
 action('learn_other_language');expect('ruler_language_learned','scope:twcm_ruler_person = { knows_language_of_culture = culture:english }')
 no('learn_other_language','known_language_disabled')
 for amount,total in [(10,30),(25,55)]:
  action('acceptance_'+str(amount))
  expect('ruler_acceptance_'+str(total),'culture:irish = { cultural_acceptance = { target = culture:english value = '+str(total)+' } } culture:english = { cultural_acceptance = { target = culture:irish value = '+str(total)+' } }')
 add('culture:irish = { set_cultural_acceptance = { target = culture:english value = 99 } }')
 action('acceptance_25');expect('ruler_acceptance_cap','culture:irish = { cultural_acceptance = { target = culture:english value = 100 } }')
 no('acceptance_10','max_acceptance_disabled');no('acceptance_max','already_max_acceptance_disabled')
 add('culture:irish = { set_cultural_acceptance = { target = culture:english value = 10 } }')
 begin('acceptance_max');cancel();expect('ruler_acceptance_cancel','culture:irish = { cultural_acceptance = { target = culture:english value = 10 } }')
 action('acceptance_max');expect('ruler_acceptance_max','culture:irish = { cultural_acceptance = { target = culture:english value = 100 } }')
 add('culture:irish = { set_cultural_acceptance = { target = culture:english value = 20 } }')
 for changed in ['person','teacher']:
  subjects('scope:twcm_ruler_person','scope:twcm_ruler_teacher');begin('acceptance_10')
  add('scope:twcm_ruler_'+changed+' = { set_culture = culture:norse }')
  expect('ruler_review_culture_changed_'+changed,'NOT = { '+guard('twcm_ui_confirm')+' }')
  add('twcm_smoke_apply_effect = yes')
  expect('ruler_changed_culture_no_effect_'+changed,'culture:irish = { cultural_acceptance = { target = culture:english value = 20 } }')
  add('scope:twcm_ruler_'+changed+' = { set_culture = culture:'+('irish' if changed=='person' else 'english')+' }')
 subjects('scope:twcm_ruler_person','scope:twcm_ruler_person')
 for name in ['learn_other_language','acceptance_10','acceptance_max','alliance_create','alliance_break','guardian_assign','guardian_remove']:
  no(name,'self_disabled_'+name)
 subjects('scope:twcm_ruler_ward','scope:twcm_ruler_ward2');no('acceptance_10','same_culture')
 subjects('scope:twcm_ruler_infant','scope:twcm_ruler_teacher');no('learn_other_language','infant_language')
 add('scope:twcm_ruler_teacher = { set_culture = culture:irish create_hybrid_culture = culture:norse }')
 subjects('scope:twcm_ruler_person','scope:twcm_ruler_teacher');action('acceptance_max')
 expect('ruler_dynamic_culture_acceptance','scope:twcm_ruler_person.culture = { cultural_acceptance = { target = scope:twcm_ruler_teacher.culture value = 100 } }')

 # Every legacy action gets an independent native result or eligibility check.
 subjects('scope:twcm_ruler_person');no('legacy_warfare_legacy_1','no_dynasty')
 subjects('scope:twcm_ruler_lord');number(4321);action('exact_renown')
 add('save_scope_value_as = { name = twcm_ruler_renown_level_before value = scope:twcm_ruler_lord.dynasty.dynasty_prestige_level }')
 for track,entries in meta['editor']['ruler_tools']['legacies'].items():
  first=entries[0]['entry']['id'].removeprefix('twcm_editor_')
  previous=None
  for data in entries:
   perk=data['perk'];name=data['entry']['id'].removeprefix('twcm_editor_')
   if perk!=previous and previous is None and len(entries)>1:
    later=next((d for d in entries if d['perk']!=perk),None)
    if later:no(later['entry']['id'].removeprefix('twcm_editor_'),'legacy_skip_'+track)
   # Multiple choices are tested from a clean copy of this single tier.
   add('scope:twcm_ruler_lord.dynasty = { if = { limit = { has_dynasty_perk = '+perk+' } remove_dynasty_perk = '+perk+' } }')
   valid=guard('twcm_editor_'+name)
   add('if = { limit = { '+valid+' } '+dump(get(guis['twcm_editor_'+name],'effect'))+' twcm_smoke_apply_effect = yes }')
   expect('ruler_legacy_result_'+name,'OR = { scope:twcm_ruler_lord.dynasty = { has_dynasty_perk = '+perk+' } NOT = { '+valid+' } }')
   # Unlocked entries cannot be re-granted. Locked entries remain unavailable.
   no(name,'legacy_repeated_or_locked_'+name)
   if data['trait']:
    choices=[d['trait'] for d in entries if d['perk']==perk]
    expected='has_variable = '+perk+'_'+data['trait']+' '+''.join('NOT = { has_variable = '+perk+'_'+t+' } ' for t in choices if t!=data['trait'])
    expect('ruler_legacy_choice_'+name,'OR = { scope:twcm_ruler_lord.dynasty = { NOT = { has_dynasty_perk = '+perk+' } } scope:twcm_ruler_lord.dynasty = { '+expected+' } }')
   previous=perk
 expect('ruler_base_legacy_tracks','scope:twcm_ruler_lord.dynasty = { has_dynasty_perk = blood_legacy_5 has_dynasty_perk = warfare_legacy_5 has_dynasty_perk = kin_legacy_5 has_dynasty_perk = law_legacy_5 has_dynasty_perk = guile_legacy_5 has_dynasty_perk = erudition_legacy_5 has_dynasty_perk = glory_legacy_5 }')
 expect('ruler_legacy_keeps_renown','scope:twcm_ruler_lord.dynasty = { dynasty_prestige = 4321 }')
 expect('ruler_legacy_keeps_renown_level','scope:twcm_ruler_lord.dynasty = { dynasty_prestige_level = scope:twcm_ruler_renown_level_before }')
 add('scope:twcm_ruler_lord.dynasty = { remove_dynasty_perk = warfare_legacy_5 }')
 begin('legacy_warfare_legacy_5');add('scope:twcm_ruler_lord = { set_house = scope:twcm_ruler_other_lord.house }')
 expect('ruler_legacy_changed_dynasty','NOT = { '+guard('twcm_ui_confirm')+' }');cancel()

 # Education: exact pair, reciprocal relation, replacement, capacity and age gates.
 subjects('scope:twcm_ruler_ward','scope:twcm_ruler_teacher')
 action('guardian_assign')
 expect('ruler_guardian_reciprocal','scope:twcm_ruler_ward = { has_relation_guardian = scope:twcm_ruler_teacher } scope:twcm_ruler_teacher = { has_relation_ward = scope:twcm_ruler_ward }')
 no('guardian_assign','guardian_already_assigned')
 subjects('scope:twcm_ruler_ward','scope:twcm_ruler_teacher2');no('guardian_remove','wrong_guardian')
 subjects('scope:twcm_ruler_ward','scope:twcm_ruler_teacher');action('guardian_remove')
 expect('ruler_guardian_removed_both_sides','scope:twcm_ruler_ward = { num_of_relation_guardian = 0 } scope:twcm_ruler_teacher = { num_of_relation_ward = 0 }')
 subjects('scope:twcm_ruler_ward','scope:twcm_ruler_teacher2');action('guardian_assign')
 for skill in ['diplomacy','martial','stewardship','intrigue','learning']:
  # Clear only this focus in the test setup to exercise all five real callbacks.
  add('scope:twcm_ruler_ward = { set_focus = education_'+('martial' if skill=='diplomacy' else 'diplomacy')+' }')
  action('education_'+skill);expect('ruler_education_'+skill,'scope:twcm_ruler_ward = { has_focus = education_'+skill+' }')
  no('education_'+skill,'same_focus_'+skill)
 subjects('scope:twcm_ruler_infant');no('education_diplomacy','education_too_young')
 subjects('scope:twcm_ruler_teacher');no('education_diplomacy','education_adult')
 subjects('scope:twcm_ruler_ward2','scope:twcm_ruler_teacher2');action('guardian_assign')
 subjects('scope:twcm_ruler_ward3','scope:twcm_ruler_teacher2');no('guardian_assign','guardian_capacity')
 subjects('scope:twcm_ruler_ward','scope:twcm_ruler_teacher2');begin('guardian_remove')
 add('scope:twcm_ruler_ward = { remove_relation_guardian = scope:twcm_ruler_teacher2 set_relation_guardian = scope:twcm_ruler_teacher }')
 expect('ruler_guardian_changed_during_review','NOT = { '+guard('twcm_ui_confirm')+' }')
 add('twcm_smoke_apply_effect = yes')
 expect('ruler_new_guardian_preserved','scope:twcm_ruler_ward = { has_relation_guardian = scope:twcm_ruler_teacher }')
 subjects('scope:twcm_ruler_ward3','scope:twcm_ruler_teacher')
 add('scope:twcm_ruler_teacher = { add_character_flag = under_offer_as_guardian_flag }')
 no('guardian_assign','guardian_pending_offer')
 add('scope:twcm_ruler_teacher = { remove_character_flag = under_offer_as_guardian_flag }')
 begin('guardian_assign');add('scope:twcm_ruler_ward3 = { set_age = 16 }')
 expect('ruler_ward_ages_out_during_review','NOT = { '+guard('twcm_ui_confirm')+' }');cancel()
 # A different court must use the normal game education/travel flow.
 subjects('scope:twcm_ruler_ward2','scope:twcm_ruler_other_lord');no('guardian_assign','guardian_other_court')

 subjects('scope:twcm_ruler_lord','scope:twcm_ruler_other_lord')
 action('alliance_create');expect('ruler_alliance_both_sides','scope:twcm_ruler_lord = { is_allied_to = scope:twcm_ruler_other_lord } scope:twcm_ruler_other_lord = { is_allied_to = scope:twcm_ruler_lord }')
 no('alliance_create','alliance_duplicate')
 begin('alliance_break');cancel();expect('ruler_alliance_cancel','scope:twcm_ruler_lord = { is_allied_to = scope:twcm_ruler_other_lord }')
 action('alliance_break');expect('ruler_alliance_broken_both','scope:twcm_ruler_lord = { NOT = { is_allied_to = scope:twcm_ruler_other_lord } } scope:twcm_ruler_other_lord = { NOT = { is_allied_to = scope:twcm_ruler_lord } }')
 no('alliance_break','alliance_absent')
 # Re-creating a deliberately broken alliance must clear the native blocking flag.
 action('alliance_create');action('alliance_break')
 add('create_title_and_vassal_change = { type = granted save_scope_as = twcm_ruler_liege_change } scope:twcm_ruler_lord = { change_liege = { liege = scope:twcm_smoke_root change = scope:twcm_ruler_liege_change } } resolve_title_and_vassal_change = scope:twcm_ruler_liege_change')
 subjects('scope:twcm_smoke_root','scope:twcm_ruler_lord');no('alliance_create','alliance_liege_chain')
 subjects('scope:twcm_ruler_lord','scope:twcm_ruler_person');no('alliance_create','alliance_unlanded')
 subjects('scope:twcm_ruler_lord','scope:twcm_ruler_other_lord');begin('alliance_create')
 add('scope:twcm_ruler_other_lord = { death = { death_reason = death_natural_causes } }')
 expect('ruler_alliance_dead_other_review','NOT = { '+guard('twcm_ui_confirm')+' }');cancel()

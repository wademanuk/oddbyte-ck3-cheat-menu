"""Additional disposable-engine cases, including catalog choices and invalid contexts."""
from pathlib import Path
from project_config import GAME
from editor_catalog import load_catalog
from pdx_script import get,dump

def append_review_cases(add,action,expect,subjects,number,make,guard,guis,meta,destination):
 catalog=load_catalog(GAME)
 def unavailable(name,case):expect(case,'NOT = { '+guard('twcm_editor_'+name)+' }')
 def grant(title,holder):
  add('create_title_and_vassal_change = { type = granted save_scope_as = twcm_review_change add_claim_on_loss = no } title:'+title+' = { change_title_holder = { holder = '+holder+' government_base = scope:twcm_smoke_root change = scope:twcm_review_change } } resolve_title_and_vassal_change = scope:twcm_review_change')
 # Match an actual sub-rite even when both people already share the parent faith.
 add('scope:twcm_smoke_subject = { set_character_faith = faith:christian_faith set_character_rite = rite:roman_rite } scope:twcm_smoke_spouse = { set_character_faith = faith:christian_faith set_character_rite = rite:insular_celtic }')
 subjects('scope:twcm_smoke_subject','scope:twcm_smoke_spouse')
 expect('rite_match_fixture','scope:twcm_smoke_subject.faith = scope:twcm_smoke_spouse.faith NOT = { scope:twcm_smoke_subject.rite = scope:twcm_smoke_spouse.rite }')
 action('match_other_faith')
 expect('match_same_faith_other_rite','scope:twcm_smoke_subject.rite = scope:twcm_smoke_spouse.rite')
 # Every role should retain the employer's rite, not silently pick the default one.
 add('set_character_faith = faith:christian_faith set_character_rite = rite:insular_celtic')
 subjects('scope:twcm_smoke_root')
 for role in ['courtier','commander','physician','councillor','knight']:
  action('spawn_'+role)
  expect('spawn_rite_'+role,'var:twcm_editor_last_created = { rite = scope:twcm_smoke_root.rite faith = scope:twcm_smoke_root.faith culture = scope:twcm_smoke_root.culture }')
 # Real age and numeric bounds, and disabled two-character actions.
 subjects('scope:twcm_smoke_subject')
 add('scope:twcm_smoke_subject = { '+' '.join('remove_trait = '+t for t in catalog['traits'])+' force_character_skill_recalculation = yes }')
 for age,valid in [(15,False),(16,True),(120,True),(121,False)]:
  number(age)
  if valid:action('exact_age');expect('age_boundary_'+str(age),'scope:twcm_smoke_subject = { age = '+str(age)+' }')
  else:unavailable('exact_age','age_disabled_'+str(age))
 # A landed ruler can have holding bonuses even after all traits are removed.
 # Use a fresh unlanded fixture when comparing effective skills to zero.
 make('twcm_review_skills');subjects('scope:twcm_review_skills')
 add('create_character = { age = 30 gender = male employer = scope:twcm_smoke_root culture = scope:twcm_smoke_root.culture faith = scope:twcm_smoke_root.faith dynasty = none random_traits = no diplomacy = 0 martial = 0 stewardship = 0 intrigue = 0 learning = 0 prowess = 0 after_creation = { save_scope_as = twcm_review_zero_skills } }')
 add('create_character = { age = 30 gender = male employer = scope:twcm_smoke_root culture = scope:twcm_smoke_root.culture faith = scope:twcm_smoke_root.faith dynasty = none random_traits = no diplomacy = 37 martial = 37 stewardship = 37 intrigue = 37 learning = 37 prowess = 37 after_creation = { save_scope_as = twcm_review_middle_skills } }')
 for skill in ['diplomacy','martial','stewardship','intrigue','learning','prowess']:
  number(101);unavailable('exact_'+skill,'skill_above_limit_'+skill)
  for value in [0,37,100]:
   number(value);action('exact_'+skill)
   expected=('scope:twcm_review_zero_skills.'+skill if value==0 else 'scope:twcm_review_middle_skills.'+skill if value==37 else str(value))
   expect('skill_boundary_'+skill+'_'+str(value),'scope:twcm_review_skills = { '+skill+' = '+expected+' }')
   if skill=='prowess':
    add('save_scope_value_as = { name = twcm_review_prowess_'+str(value)+' value = scope:twcm_review_skills.prowess } save_scope_value_as = { name = twcm_review_creation_zero value = scope:twcm_review_zero_skills.prowess } save_scope_value_as = { name = twcm_review_creation_middle value = scope:twcm_review_middle_skills.prowess } debug_log_scopes = yes')
 # Replacing incompatible traits must remove the prior one, in both directions.
 subjects('scope:twcm_smoke_subject')
 for old,new in [('intellect_good_2','intellect_good_3'),('intellect_good_3','intellect_bad_1'),('brave','craven')]:
  add('scope:twcm_smoke_subject = { remove_trait = '+old+' remove_trait = '+new+' }')
  action('trait_add_'+old);action('trait_add_'+new)
  expect('opposites_'+old+'_'+new,'scope:twcm_smoke_subject = { has_trait = '+new+' NOT = { has_trait = '+old+' } }')
 subjects('scope:twcm_smoke_root','scope:twcm_smoke_root')
 for name in ['recruit','imprison','release','marry','adopt','vassalize','artifact_transfer']:
  unavailable(name,'self_disabled_'+name)
 subjects('scope:twcm_smoke_subject','scope:twcm_smoke_child')
 for name in ['marry','marry_matrilineal']:unavailable(name,'child_disabled_'+name)
 # All eight pin slots preserve independent references, including Other and Clear.
 subjects('scope:twcm_smoke_subject')
 for slot in range(1,9):action('pin_save_'+str(slot))
 subjects('scope:twcm_smoke_root')
 for slot in range(1,9):
  action('pin_other_'+str(slot));expect('pin_other_'+str(slot),'var:twcm_ui_other = scope:twcm_smoke_subject')
  action('pin_select_'+str(slot));expect('pin_select_'+str(slot),'var:twcm_ui_target = scope:twcm_smoke_subject')
  action('pin_clear_'+str(slot));unavailable('pin_select_'+str(slot),'empty_pin_'+str(slot))
 # Trait inventory: literal native add/remove and both XP tracks where present.
 make('twcm_review_catalog')
 subjects('scope:twcm_review_catalog')
 for trait in catalog['traits']:
  minimum=get(catalog['traits'][trait],'minimum_age');maximum=get(catalog['traits'][trait],'maximum_age')
  if maximum:
   add('scope:twcm_review_catalog = { set_age = 30 }')
   unavailable('trait_add_'+trait,'trait_too_old_'+trait)
  if minimum:
   add('scope:twcm_review_catalog = { set_age = '+str(int(minimum)-1)+' }')
   unavailable('trait_add_'+trait,'trait_too_young_'+trait)
  age=int(minimum) if minimum else min(int(maximum or 30),30)
  add('scope:twcm_review_catalog = { set_age = '+str(age)+' }')
  action('trait_add_'+trait)
  expect('catalog_trait_'+trait,'scope:twcm_review_catalog = { has_trait = '+trait+' }')
  for track_index,track in enumerate(catalog['trait_tracks'][trait]):
   action('trait_xp_'+trait+'_'+str(track_index))
   expect('catalog_xp_'+trait+'_'+str(track_index),'scope:twcm_review_catalog = { has_trait_xp = { trait = '+trait+(' track = '+track if track else '')+' value >= 100 } }')
  action('trait_remove_'+trait)
  expect('catalog_remove_trait_'+trait,'scope:twcm_review_catalog = { NOT = { has_trait = '+trait+' } }')
 # Every static personal culture/faith choice, not only the one happy-path fixture.
 for field,catalog_key in [('culture','cultures'),('faith','faiths')]:
  for key in catalog[catalog_key]:
   subjects('scope:twcm_review_catalog')
   action(field+'_'+key)
   expect('catalog_'+field+'_'+key,'scope:twcm_review_catalog = { '+field+' = '+field+':'+key+' }')
 # Make an actual dynamic culture and copy the runtime object.
 add('scope:twcm_smoke_spouse = { set_culture = culture:irish create_hybrid_culture = culture:norse }')
 subjects('scope:twcm_review_catalog','scope:twcm_smoke_spouse');action('match_other_culture')
 expect('copy_dynamic_culture','scope:twcm_review_catalog.culture = scope:twcm_smoke_spouse.culture NOT = { scope:twcm_smoke_spouse = { culture = culture:irish } }')
 # Isolate a dynamically-created rite from all native followers before shared edits.
 add('scope:twcm_review_catalog = { set_character_faith = faith:christian_faith set_character_rite = rite:roman_rite create_dynamic_rite = { save_scope_as = twcm_review_rite convert = yes target_divergence = 10 include_unknown = yes override_tenets_first = no } }')
 subjects('scope:twcm_review_catalog')
 expect('dynamic_rite_fixture','exists = scope:twcm_review_rite scope:twcm_review_catalog.rite = scope:twcm_review_rite NOT = { scope:twcm_review_rite = rite:roman_rite }')
 subjects('scope:twcm_smoke_spouse','scope:twcm_review_catalog');action('match_other_faith')
 expect('copy_dynamic_rite','scope:twcm_smoke_spouse.rite = scope:twcm_review_catalog.rite')
 subjects('scope:twcm_review_catalog')
 for group,data in catalog['doctrine_groups'].items():
  for doctrine in data['choices']:
   for other in data['choices']:
    add('if = { limit = { rite:roman_rite = { rite_has_doctrine = '+other+' } } set_variable = { name = twcm_review_doctrine_'+other+' value = 1 } } else = { set_variable = { name = twcm_review_doctrine_'+other+' value = 0 } }')
   add('scope:twcm_review_rite = { if = { limit = { rite_has_doctrine = '+doctrine+' } remove_rite_doctrine = '+doctrine+' } }')
   action('doctrine_'+doctrine)
   expect('catalog_doctrine_'+doctrine,'scope:twcm_review_rite = { rite_has_doctrine = '+doctrine+' }')
   for other in data['choices']:
    expect('other_rite_'+doctrine+'_'+other,'OR = { AND = { var:twcm_review_doctrine_'+other+' = 1 rite:roman_rite = { rite_has_doctrine = '+other+' } } AND = { var:twcm_review_doctrine_'+other+' = 0 rite:roman_rite = { NOT = { rite_has_doctrine = '+other+' } } } }')
 for tenet in catalog['tenets']:
  add('scope:twcm_review_rite = { every_rite_tenet = { save_scope_as = twcm_review_old_tenet prev = { remove_rite_tenet = scope:twcm_review_old_tenet } } }')
  dlc=get(catalog['tenets'][tenet],'requires_dlc_flag')
  if dlc:
   feature='has_dlc_feature = '+dlc;valid=guard('twcm_editor_tenet_add_'+tenet)
   expect('catalog_tenet_dlc_'+tenet,'OR = { AND = { '+feature+' '+valid+' } AND = { NOT = { '+feature+' } NOT = { '+valid+' } } }')
   add('if = { limit = { '+feature+' } '+dump(get(guis['twcm_editor_tenet_add_'+tenet],'effect'))+' twcm_smoke_apply_effect = yes }')
   expect('catalog_tenet_'+tenet,'OR = { NOT = { '+feature+' } scope:twcm_review_rite = { rite_has_tenet = '+tenet+' } }')
   add('if = { limit = { '+feature+' } '+dump(get(guis['twcm_editor_tenet_remove_'+tenet],'effect'))+' twcm_smoke_apply_effect = yes }')
  else:
   action('tenet_add_'+tenet);expect('catalog_tenet_'+tenet,'scope:twcm_review_rite = { rite_has_tenet = '+tenet+' }')
   action('tenet_remove_'+tenet)
  expect('catalog_remove_tenet_'+tenet,'scope:twcm_review_rite = { NOT = { rite_has_tenet = '+tenet+' } }')
 for tradition in catalog['traditions']:
  add('scope:twcm_review_catalog.culture = { every_tradition = { save_scope_as = twcm_review_old_tradition prev = { remove_culture_tradition = scope:twcm_review_old_tradition } } }')
  action('tradition_add_'+tradition);expect('catalog_tradition_'+tradition,'scope:twcm_review_catalog.culture = { has_cultural_tradition = '+tradition+' }')
  action('tradition_remove_'+tradition);expect('catalog_remove_tradition_'+tradition,'scope:twcm_review_catalog.culture = { NOT = { has_cultural_tradition = '+tradition+' } }')
 action('innovations_all')
 for innovation in catalog['innovations']:
  expect('catalog_innovation_'+innovation,'scope:twcm_review_catalog.culture = { has_innovation = '+innovation+' }')
 for kind in ['sword','armor','crown','regalia','ring']:
  for rarity in ['common','masterwork','famed','illustrious']:
   action('artifact_create_'+kind+'_'+rarity)
 expect('artifact_catalog_count','scope:twcm_review_catalog = { any_character_artifact = { count = 20 } }')
 # Each removable boost leaves permanent base edits and unrelated boosts alone.
 # Isolate removable-boost checks from earlier destructive catalog fixtures.
 make('twcm_review_boost_subject');subjects('scope:twcm_review_boost_subject');number(37);action('exact_diplomacy')
 expect('active_boost_baseline','scope:twcm_review_boost_subject = { diplomacy = 37 }')
 for modifier in ['twcm_near_instant_construction','twcm_health_boost','twcm_high_fertility','twcm_low_fertility']:
  add('scope:twcm_review_boost_subject = { add_character_modifier = { modifier = '+modifier+' } }')
  action('remove_'+modifier)
  expect('active_remove_'+modifier,'scope:twcm_review_boost_subject = { diplomacy = 37 NOT = { has_character_modifier = '+modifier+' } }')
 for trait in ['twcm_super_character','twcm_super_governor','twcm_super_commander','twcm_super_all']:
  add('scope:twcm_review_boost_subject = { add_trait = '+trait+' force_character_skill_recalculation = yes }')
  action('remove_'+trait)
  expect('active_remove_'+trait,'scope:twcm_review_boost_subject = { diplomacy = 37 NOT = { has_trait = '+trait+' } }')
 # Cancel, original-person death, and other-person death must not apply a pending edit.
 subjects('scope:twcm_smoke_subject');number(123);action('exact_gold');number(999)
 add(dump(get(guis['twcm_editor_exact_gold'],'effect')))
 expect('review_cancel_valid',guard('twcm_ui_confirm'))
 add(dump(get(guis['twcm_ui_cancel'],'effect')))
 # The same actor can change dynasty or capital while their review remains open.
 subjects('scope:twcm_smoke_subject');number(444)
 add(dump(get(guis['twcm_editor_exact_renown'],'effect')))
 add('scope:twcm_smoke_subject = { set_house = title:k_france.holder.house }')
 expect('dynasty_changed_disables_apply','NOT = { '+guard('twcm_ui_confirm')+' }')
 add(dump(get(guis['twcm_ui_cancel'],'effect')))
 grant('c_connacht','scope:twcm_smoke_root');subjects('scope:twcm_smoke_root');number(44)
 add(dump(get(guis['twcm_editor_exact_development'],'effect')))
 add('set_realm_capital = title:c_connacht')
 expect('capital_changed_disables_apply','NOT = { '+guard('twcm_ui_confirm')+' }')
 add(dump(get(guis['twcm_ui_cancel'],'effect')))
 expect('cancel_keeps_balance','NOT = { has_variable = twcm_ui_pending } scope:twcm_smoke_subject = { gold = 123 }')
 make('twcm_review_doomed');subjects('scope:twcm_review_doomed');number(456)
 add(dump(get(guis['twcm_editor_exact_gold'],'effect')))
 add('scope:twcm_review_doomed = { death = { death_reason = death_natural_causes } }')
 expect('dead_original_disables_apply','NOT = { '+guard('twcm_ui_confirm')+' }')
 add('twcm_smoke_apply_effect = yes')
 make('twcm_review_doomed_other','female');subjects('scope:twcm_smoke_root','scope:twcm_review_doomed_other')
 add(dump(get(guis['twcm_editor_imprison'],'effect')))
 add('scope:twcm_review_doomed_other = { death = { death_reason = death_natural_causes } }')
 expect('dead_other_disables_apply','NOT = { '+guard('twcm_ui_confirm')+' }')
 add(dump(get(guis['twcm_ui_cancel'],'effect')))
 # Every contract level, including both ends of the native range.
 subjects('scope:twcm_smoke_subject')
 for kind,contract in [('tax','feudal_government_taxes'),('levies','feudal_government_levies')]:
  for level,index in [('exempt',0),('low',1),('normal',2),('high',3),('extortionate',4)]:
   action('contract_'+kind+'_'+level)
   expect('contract_'+kind+'_'+str(index),'scope:twcm_smoke_subject = { vassal_contract_obligation_level:'+contract+' = '+str(index)+' }')
 # A title with a real count vassal: direct-only preserves that liege; inclusive moves it.
 make('twcm_review_duke');make('twcm_review_count');make('twcm_review_recipient')
 grant('k_ireland','scope:twcm_smoke_root');grant('c_ailech','scope:twcm_review_duke');grant('d_ulster','scope:twcm_review_duke');grant('d_connacht','scope:twcm_review_duke');grant('c_ulster','scope:twcm_review_count')
 add('create_title_and_vassal_change = { type = granted save_scope_as = twcm_review_change } scope:twcm_review_count = { change_liege = { liege = scope:twcm_review_duke change = scope:twcm_review_change } } resolve_title_and_vassal_change = scope:twcm_review_change')
 expect('title_vassal_fixture','scope:twcm_review_count = { is_vassal_of = scope:twcm_review_duke }')
 subjects('scope:twcm_review_recipient')
 add('set_variable = { name = twcm_editor_title value = title:d_connacht } set_variable = { name = twcm_editor_title_owner value = scope:twcm_review_duke }')
 unavailable('transfer_title','duchy_to_unlanded_disabled')
 unavailable('transfer_title_vassals','duchy_and_vassals_to_unlanded_disabled')
 grant('c_breifne','scope:twcm_review_recipient')
 for title,action_name in [('d_connacht','transfer_title'),('d_ulster','transfer_title_vassals')]:
  add('set_variable = { name = twcm_editor_title value = title:'+title+' } set_variable = { name = twcm_editor_title_owner value = scope:twcm_review_duke }')
  action(action_name)
  expect('ownership_'+title,'title:'+title+'.holder = scope:twcm_review_recipient')
  expect('vassal_'+title,'scope:twcm_review_count = { is_vassal_of = scope:twcm_review_'+('duke' if title=='d_connacht' else 'recipient')+' }')
 # Ownership changing after review invalidates Apply, even if the current pick is replaced.
 grant('d_ulster','scope:twcm_review_duke');subjects('scope:twcm_review_recipient')
 add('set_variable = { name = twcm_editor_title value = title:d_ulster } set_variable = { name = twcm_editor_title_owner value = scope:twcm_review_duke }')
 add(dump(get(guis['twcm_editor_transfer_title'],'effect')))
 grant('d_ulster','scope:twcm_smoke_root')
 expect('title_owner_changed_disables_apply','NOT = { '+guard('twcm_ui_confirm')+' }')
 add(dump(get(guis['twcm_ui_cancel'],'effect')))
 # Test-only wars have no settlement effects. Native war on-actions record the real outcome.
 (destination/'common/casus_belli_types/twcm_review_war.txt').write_text('twcm_review_cb = { icon = claim_cb group = claim war_name = twcm_review_cb_name allowed_for_character = { always = yes } allowed_against_character = { always = yes } on_victory = { } on_defeat = { } on_white_peace = { } on_victory_desc = twcm_review_cb_name on_defeat_desc = twcm_review_cb_name on_white_peace_desc = twcm_review_cb_name on_invalidated_desc = twcm_review_cb_name }',encoding='utf-8-sig')
 (destination/'localization/english/twcm_review_l_english.yml').write_text('l_english:\n twcm_review_cb_name:0 "Editor review test war"\n',encoding='utf-8-sig')
 on_actions=[]
 for native,value in [('on_war_won_attacker',1),('on_war_won_defender',2),('on_war_white_peace',3)]:
  callback='twcm_review_result_'+str(value)
  on_actions.append(native+' = { on_actions = { '+callback+' } } '+callback+' = { effect = { scope:attacker = { set_variable = { name = twcm_review_war_result value = '+str(value)+' } } } }')
 (destination/'common/on_action/twcm_review_wars.txt').write_text('\n'.join(on_actions),encoding='utf-8-sig')
 # One simultaneous unrelated war must survive every chosen-war resolution.
 add('start_war = { casus_belli = twcm_review_cb target = title:k_aragon.holder } random_character_war = { limit = { primary_defender = title:k_aragon.holder } save_scope_as = twcm_review_spare_war }')
 expect('spare_war_fixture','exists = scope:twcm_review_spare_war')
 for side in ['primary_attacker','primary_defender','ally_attacker','ally_defender']:
  for outcome in ['victory','defeat','white_peace']:
   add('set_variable = { name = twcm_review_war_result value = 0 } start_war = { casus_belli = twcm_review_cb target = title:k_france.holder } random_character_war = { limit = { primary_defender = title:k_france.holder } save_scope_as = twcm_review_war }')
   if side.startswith('ally'):
    add('scope:twcm_review_war = { '+('add_attacker' if side=='ally_attacker' else 'add_defender')+' = title:k_castille.holder }')
    selected='title:k_castille.holder'
   else:selected='scope:twcm_smoke_root' if side=='primary_attacker' else 'title:k_france.holder'
   subjects(selected)
   add('set_variable = { name = twcm_editor_war value = scope:twcm_review_war }')
   expected=3 if outcome=='white_peace' else (1 if (side.endswith('attacker') == (outcome=='victory')) else 2)
   expect('war_side_fixture_'+side+'_'+outcome,'scope:twcm_review_war = { '+('is_attacker' if side.endswith('attacker') else 'is_defender')+' = '+selected+' }')
   action('war_'+outcome)
   expect('war_result_'+side+'_'+outcome,'var:twcm_review_war_result = '+str(expected))
   expect('other_war_survives_'+side+'_'+outcome,'any_character_war = { this = scope:twcm_review_spare_war }')
 add('scope:twcm_review_spare_war = { end_war = white_peace }')
 from review_ruler_cases import append_ruler_cases
 append_ruler_cases(add,action,expect,subjects,number,make,guard,guis,meta,grant)

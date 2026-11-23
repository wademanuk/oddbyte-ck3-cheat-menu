"""Extended editor invariants and real emitted state transitions; no user save is opened."""
from pathlib import Path
from project_config import ROOT,MOD,GAME
import json,re,unittest
from editor_catalog import load_catalog,definitions,search_terms,search_expression
from pdx_script import parse,dump,get,walk
from test_ui_state import SelectionScript,Character





class EditorTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.meta=json.loads((ROOT/'tools/cheat_mod_metadata.json').read_text())['window']
  cls.editor=cls.meta['editor'];cls.catalog=load_catalog(GAME)
  cls.guis={e.key:e.value for e in parse((MOD/'common/scripted_guis/twcm_window_guis.txt').read_text(encoding='utf-8-sig'))}
  cls.gui=(MOD/'gui/twcm_window.gui').read_text()
  cls.labels={line.split(':0 ',1)[0].strip():json.loads(line.split(':0 ',1)[1]) for line in (MOD/'localization/english/twcm_l_english.yml').read_text(encoding='utf-8-sig').splitlines()[1:]}
  dispatch=get(get(cls.guis['twcm_ui_confirm'],'effect'),'if')
  cls.confirmed={name:next(e.value for e in dispatch if e.key=='if' and get(get(e.value,'limit'),'var:twcm_ui_pending')==ident) for ident,name in cls.meta['confirmation_ids'].items()}
 def body(self,name):
  if name in self.confirmed:return get(self.confirmed[name],'if')
  return get(get(self.guis[name],'effect'),'if')
 def test_native_catalogs_are_populated_and_all_choices_have_actions(self):
  for catalog,stem in [('traits','trait_add'),('cultures','culture'),('faiths','faith'),('innovations','innovation'),('traditions','tradition_add'),('tenets','tenet_add')]:
   self.assertGreater(len(self.catalog[catalog]),20,catalog)
   for key in self.catalog[catalog]:self.assertIn('twcm_editor_'+stem+'_'+key,self.guis)
 def test_anonymous_native_lists_round_trip(self):
  tree=parse('names = { { name = "first" color = { 1 2 3 } } { name = "second" } }')
  self.assertEqual(parse(dump(tree)),tree)
 def test_every_editor_page_is_reachable_from_hub_or_sidebar(self):
  for page in self.editor['pages']:
   self.assertIn('twcm_editor_nav_'+str(page),self.guis)
   self.assertIn('name = "twcm_page_'+str(page)+'"',self.gui)
   self.assertIn("GetScriptedGui( 'twcm_editor_nav_"+str(page)+"' )",self.gui)
 def test_unavailable_action_help_uses_literal_tooltips(self):
  for name in self.editor['actions']:
   if not name.startswith('twcm_editor_'):continue
   trigger=get(self.guis[name],'is_valid')
   self.assertTrue(any(e.key=='custom_tooltip' and get(e.value,'text')==name+'_requirements' for e in trigger),name)
   self.assertFalse(any(e.key=='custom_description' for e in trigger),name)
 def test_window_visibility_has_no_character_root_during_loading(self):
  for name in ['twcm_ui_visible','twcm_ui_modal_visible']:
   self.assertIsNone(get(self.guis[name],'scope'))
   self.assertEqual(get(get(self.guis[name],'is_shown'),'exists'),'scope:twcm_view_player')
  self.assertIn("GuiScope.AddScope('twcm_view_player',GetPlayer.MakeScope).End",self.gui)
 def test_new_gui_references_resolve_including_dynamic_scope_lists(self):
  refs=set(re.findall(r"GetScriptedGui\(\s*'([^']+)'\s*\)",self.gui))
  self.assertFalse(refs-self.guis.keys())
  self.assertIn('twcm_editor_choose_war',refs)
  self.assertIn('twcm_editor_choose_artifact',refs)
  self.assertNotIn('ontextedited',self.gui) # Generic VariableSystem.Set is not an edit callback.
 def test_search_is_bounded_native_data_and_handles_english_accented_names(self):
  self.assertIn('gen',search_terms('Add Genius'))
  self.assertIn('court',search_terms('Bring other character to court'))
  self.assertIn('ore',search_terms('Örebro'))
  self.assertNotIn('enius',search_terms('Genius'))
  expression=search_expression("Genius'); ExecuteConsoleCommand('bad")
  self.assertNotIn("ExecuteConsoleCommand('",expression)
  self.assertIn('GetVariableSystem.HasValue',expression)
 def test_debug_toggle_is_the_only_console_command_in_the_gui(self):
  self.assertEqual(re.findall(r'ExecuteConsoleCommand\s*\(([^)]*)\)', self.gui), ["'debug_mode'"])
  self.assertIn("SelectLocalization(InDebugMode, 'twcm_debug_disable', 'twcm_debug_enable')", self.gui)
 def test_all_catalogued_actions_can_be_starred_and_keep_real_action_binding(self):
  for action in self.editor['actions']:
   self.assertIn('twcm_star_'+action,self.guis)
   self.assertIn("GetScriptedGui( '"+action+"' )",self.gui)
   self.assertIn("twcm_fav_"+action,self.gui)
 def test_all_confirmed_editor_actions_snapshot_objects_and_numbers(self):
  for name in self.editor['actions']:
   if name not in self.confirmed:continue
   assignments={get(e.value,'name'):get(e.value,'value') for e in walk(get(self.guis[name],'effect')) if e.key=='set_variable'}
   for field in self.editor['snapshot_scopes']+self.editor['snapshot_values']:
    self.assertEqual(assignments.get('twcm_ui_pending_editor_'+field),'var:twcm_editor_'+field,name)
 def test_confirmation_validity_rechecks_original_objects_and_values(self):
  trigger=dump(get(self.guis['twcm_ui_confirm'],'is_valid'))
  for field in ['title','title_owner','war','artifact','culture','rite','other_faith','number','spawn_age']:
   self.assertTrue('root.var:twcm_ui_pending_editor_'+field in trigger,field)
  self.assertNotIn('root.var:twcm_editor_',trigger)
  self.assertNotIn('root.var:twcm_ui_target',trigger)
 def test_shared_edit_reviews_name_the_snapshotted_culture_or_faith(self):
  for action,data in self.editor['actions'].items():
   group=data['group']
   if group not in ['innovations','innovation_bulk','traditions','doctrines','tenets']:continue
   field='culture' if group in ['innovations','innovation_bulk','traditions'] else 'rite'
   text=self.labels[action+'_review']
   self.assertIn("Var('twcm_ui_pending_editor_"+field+"')",text)
   self.assertNotIn("Var('twcm_editor_"+field+"')",text)
 def test_education_changes_preserve_separate_prowess_education(self):
  body=self.body('twcm_editor_trait_add_education_diplomacy_4')
  removed={e.value for e in walk(body) if e.key=='remove_trait'}
  self.assertIn('education_intrigue_3',removed)
  self.assertFalse(any(t.startswith('education_prowess_') for t in removed))
 def test_each_track_xp_action_uses_an_actual_native_track_and_owned_trait(self):
  for trait,tracks in self.catalog['trait_tracks'].items():
   for i,track in enumerate(tracks):
    name='twcm_editor_trait_xp_'+trait+'_'+str(i)
    body=self.body(name)
    effect=next(e.value for e in walk(body) if e.key=='add_trait_xp')
    self.assertEqual(get(effect,'trait'),trait)
    self.assertEqual(get(effect,'track'),track)
    self.assertIn('has_trait = '+trait,dump(get(self.guis[name],'is_valid')))
 def test_title_transfers_use_native_batch_and_government_source(self):
  for suffix,effect in [('', 'change_title_holder'),('_vassals','change_title_holder_include_vassals')]:
   body=self.body('twcm_editor_transfer_title'+suffix)
   transfer=next(e.value for e in walk(body) if e.key==effect)
   self.assertEqual(get(transfer,'holder'),'scope:twcm_target')
   self.assertEqual(get(transfer,'government_base'),'scope:twcm_editor_title_owner')
   self.assertIn('resolve_title_and_vassal_change',dump(body))
  independence=self.body('twcm_editor_independence')
  self.assertIn('becomes_independent',dump(independence))
  self.assertNotIn('liege = 0',dump(independence))
 def test_contract_values_are_native_bounded_indices(self):
  contracts=definitions(GAME/'common/subject_contracts/contracts')
  for name,data in self.editor['actions'].items():
   if data['group']!='contracts':continue
   setting=next(e.value for e in walk(self.body(name)) if e.key=='vassal_contract_set_obligation_level')
   levels=get(contracts[get(setting,'type')],'obligation_levels')
   self.assertGreaterEqual(int(get(setting,'level')),0)
   self.assertLess(int(get(setting,'level')),len(levels))
 def test_war_winner_tracks_side_and_does_not_end_all_wars(self):
  for outcome,expected in [('victory',['attacker','defender']),('defeat',['defender','attacker']),('white_peace',['white_peace'])]:
   name='twcm_editor_war_'+outcome;body=self.body(name)
   self.assertEqual([e.value for e in walk(body) if e.key=='end_war'],expected)
   self.assertNotIn('every_character_war',dump(body))
   self.assertIn('any_character_war',dump(get(self.guis[name],'is_valid')))
  self.assertIn('is_white_peace_possible',dump(get(self.guis['twcm_editor_war_white_peace'],'is_valid')))
 def test_doctrine_replacements_only_remove_the_matching_group(self):
  for group,data in self.catalog['doctrine_groups'].items():
   for choice in data['choices']:
    body=self.body('twcm_editor_doctrine_'+choice)
    removed={e.value for e in walk(body) if e.key=='remove_rite_doctrine'}
    self.assertEqual(removed,set(data['choices'])-{choice})
 def test_artifact_choices_reference_native_types_visuals_and_nonstacking_boost(self):
  native_types=definitions(GAME/'common/artifacts/types');visuals=definitions(GAME/'common/artifacts/visuals')
  visuals.update(definitions(MOD/'common/artifacts/visuals'))
  for name,data in self.editor['actions'].items():
   if data['group']!='artifact_create':continue
   effect=next(e.value for e in walk(self.body(name)) if e.key=='create_artifact')
   self.assertIn(get(effect,'type'),native_types);self.assertIn(get(effect,'visuals'),visuals)
  body=self.body('twcm_editor_artifact_improve')
  remove=[e.value for e in walk(body) if e.key=='remove_artifact_modifier']
  add=[e.value for e in walk(body) if e.key=='add_artifact_modifier']
  self.assertEqual(add,['twcm_editor_artifact_best']);self.assertIn(add[0],remove)
  self.assertNotIn('clear_artifact_modifiers',dump(body))
 def test_spawner_sets_all_six_base_skills_and_saved_person_reference(self):
  for name,data in self.editor['actions'].items():
   if data['group']!='spawn':continue
   body=self.body(name);create=next(e.value for e in walk(body) if e.key=='create_character')
   self.assertEqual(get(create,'employer'),'scope:twcm_target')
   for skill in ['diplomacy','martial','stewardship','intrigue','learning','prowess']:
    self.assertEqual(get(create,skill),'scope:twcm_editor_spawn_'+skill)
   self.assertIn('twcm_editor_last_created',dump(body))
 def test_family_tools_exclude_unsafe_heirs_and_require_children_and_unrelated_people(self):
  all_effects='\n'.join(dump(self.body(name)) for name in self.editor['actions'] if self.editor['actions'][name]['group']=='family')
  self.assertNotIn('set_designated_heir_unsafe',all_effects)
  self.assertIn('is_child_of',dump(get(self.guis['twcm_editor_designate_heir'],'is_valid')))
  self.assertIn('age < 16',dump(get(self.guis['twcm_editor_adopt'],'is_valid')))
  self.assertIn('is_close_or_extended_family_of',dump(get(self.guis['twcm_editor_adopt'],'is_valid')))
  self.assertIn('age >= 18',dump(get(self.guis['twcm_editor_marry'],'is_valid')))

 def test_knight_status_values_match_values_actually_used_by_native_events(self):
  native=set()
  for path in (GAME/'events').rglob('*.txt'):
   native.update(re.findall(r'\bset_knight_status\s*=\s*(\w+)',path.read_text(encoding='utf-8-sig')))
  for name in ['force','disallow','default']:
   actual=next(e.value for e in walk(self.body('twcm_editor_knight_'+name)) if e.key=='set_knight_status')
   self.assertIn(actual,native)
 def test_exact_skills_force_refresh_after_the_base_edit(self):
  for skill in ['diplomacy','martial','stewardship','intrigue','learning','prowess']:
   self.assertIn('force_character_skill_recalculation = yes',dump(self.body('twcm_editor_exact_'+skill)))
   for sign in ['plus','minus']:
    self.assertIn('force_character_skill_recalculation = yes',dump(get(self.guis['twcm_ui_skill_'+skill+'_'+sign],'effect')))
 def test_artifact_ownership_uses_the_artifact_link_not_the_domicile_link(self):
  for name in ['repair','improve','transfer']:
   entries=list(walk(get(self.guis['twcm_editor_artifact_'+name],'is_valid')))
   self.assertTrue(any(e.key=='artifact_owner' for e in entries))
   self.assertFalse(any(e.key=='owner' for e in entries))
 def test_core_tenet_additions_require_a_free_slot_and_edit_the_rite(self):
  for name,data in self.editor['actions'].items():
   if data['group']!='tenets' or '_add_' not in name:continue
   valid=dump(get(self.guis[name],'is_valid'))
   self.assertIn('any_rite_tenet',valid)
   self.assertIn('count >= pam_faith_core_tenets_cap_value',valid)
   body=dump(self.body(name));self.assertIn('add_rite_tenet',body)
   self.assertNotIn('add_tenet =',body)
 def test_favourite_currency_actions_name_the_currency_and_current_amount(self):
  self.assertTrue(self.labels['twcm_editor_find_twcm_ui_11_1'].startswith('Gold'))
  for name in ['twcm_ui_gold_plus','twcm_ui_prestige_minus','twcm_ui_clear_stress']:
   self.assertIn(name,self.editor['actions'])
 def test_hover_conditions_use_human_descriptions(self):
  valid=dump(get(self.guis['twcm_editor_recruit'],'is_valid'))
  for label in ['twcm_ui_finish_review','twcm_ui_select_living','twcm_editor_recruit_requirements']:
   self.assertIn(label,valid)
   self.assertTrue(self.labels[label])

class EditorStateTests(unittest.TestCase):
 def setUp(self):
  self.script=SelectionScript();self.root=self.script.root
  self.edited=Character('courtier');self.root.variables.update(twcm_ui_target=self.edited,twcm_ui_other=self.root)
 def test_number_pad_appends_digits_and_backspace_truncates(self):
  self.script.click('twcm_editor_number_clear')
  for digit in [2,5,9]:self.script.click('twcm_editor_digit_'+str(digit))
  self.assertEqual(self.root.variables['twcm_editor_number'],259)
  self.script.click('twcm_editor_number_back');self.assertEqual(self.root.variables['twcm_editor_number'],25)
  self.script.click('twcm_editor_number_back');self.assertEqual(self.root.variables['twcm_editor_number'],2)
 def test_number_pad_stops_at_the_documented_limit(self):
  self.script.click('twcm_editor_number_clear')
  for _ in range(8):self.script.click('twcm_editor_digit_9')
  self.assertEqual(self.root.variables['twcm_editor_number'],999999)
 def test_pin_selection_and_other_preserve_the_distinct_pair(self):
  self.script.click('twcm_editor_pin_save_1')
  self.root.variables['twcm_ui_target']=self.root
  self.script.click('twcm_editor_pin_other_1')
  self.assertIs(self.root.variables['twcm_ui_target'],self.root)
  self.assertIs(self.root.variables['twcm_ui_other'],self.edited)
  self.script.click('twcm_editor_pin_select_1')
  self.assertIs(self.root.variables['twcm_ui_target'],self.edited)
 def test_dead_pin_is_disabled_and_pin_can_be_cleared(self):
  self.script.click('twcm_editor_pin_save_1');self.edited.alive=False
  self.assertFalse(self.script.condition(get(self.script.guis['twcm_editor_pin_select_1'],'is_valid')))
  self.root.variables['twcm_ui_target']=self.root
  self.script.click('twcm_editor_pin_clear_1');self.assertNotIn('twcm_editor_pin_1',self.root.variables)
 def test_expired_weak_selection_is_cleared_before_entering_its_scope(self):
  self.root.variables['twcm_editor_war']=None
  self.script.run(self.script.helpers['twcm_ui_prepare_effect'])
  self.assertNotIn('twcm_editor_war',self.root.variables)
  self.assertNotIn('twcm_editor_war',self.script.scopes)
 def test_favourite_toggle_does_not_execute_its_action(self):
  name='twcm_star_twcm_editor_exact_gold'
  self.script.click(name);self.assertIn('twcm_fav_twcm_editor_exact_gold',self.root.variables)
  self.script.click(name);self.assertNotIn('twcm_fav_twcm_editor_exact_gold',self.root.variables)
  self.assertNotIn('twcm_ui_pending',self.root.variables)
 def test_exact_value_review_snapshots_input_before_later_changes(self):
  self.root.variables['twcm_editor_number']=37
  self.script.click('twcm_editor_exact_gold')
  self.assertEqual(self.root.variables['twcm_ui_pending_editor_number'],37)
  self.assertIs(self.root.variables['twcm_ui_pending_target'],self.edited)
  self.root.variables.update(twcm_editor_number=500,twcm_ui_target=self.root)
  self.assertEqual(self.root.variables['twcm_ui_pending_editor_number'],37)
  self.assertIs(self.root.variables['twcm_ui_pending_target'],self.edited)

if __name__=='__main__':unittest.main()

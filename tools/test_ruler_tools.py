"""Review invariants for shared state, native choices, eligibility and log evidence."""
import json,unittest
from project_config import ROOT,MOD
from pdx_script import parse,get,dump,walk
from smoke_editor_mod import classify_errors


class RulerToolReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.meta=json.loads((ROOT/'tools/cheat_mod_metadata.json').read_text())['window']
  cls.editor=cls.meta['editor']
  cls.guis={e.key:e.value for e in parse((MOD/'common/scripted_guis/twcm_window_guis.txt').read_text(encoding='utf-8-sig'))}
  cls.text=(MOD/'localization/english/twcm_l_english.yml').read_text(encoding='utf-8-sig')
  cls.confirmed=set(cls.meta['confirmation_ids'].values())
  dispatch=get(get(cls.guis['twcm_ui_confirm'],'effect'),'if')
  cls.bodies={name:get(next(e.value for e in dispatch if e.key=='if' and get(get(e.value,'limit'),'var:twcm_ui_pending')==ident),'if') for ident,name in cls.meta['confirmation_ids'].items()}
 def valid(self,name):return dump(get(self.guis['twcm_editor_'+name],'is_valid'))
 def test_all_five_groups_are_reviewed_and_searchable_favourites(self):
  groups=['standing','languages','legacies','education','alliances']
  self.assertEqual(self.editor['ruler_tools']['groups'],groups)
  for group in groups:
   entries=[name for name,data in self.editor['actions'].items() if data['group']==group]
   self.assertTrue(entries,group)
   for name in entries:
    self.assertIn(name,self.confirmed)
    self.assertIn('twcm_star_'+name,self.guis)
 def test_culture_changes_invalidate_shared_reviews(self):
  for name in ['learn_other_language','acceptance_10','acceptance_25','acceptance_max']:
   valid=self.valid(name)
   self.assertIn('root.var:twcm_ui_target.culture = root.var:twcm_editor_culture',valid)
   self.assertIn('root.var:twcm_ui_other.culture = root.var:twcm_editor_other_culture',valid)
  for name in ['acceptance_10','acceptance_25','acceptance_max']:
   self.assertIn('value < 100',self.valid(name))
 def test_native_activity_perks_use_tier_order_even_when_file_order_differs(self):
  entries=self.editor['ruler_tools']['legacies']['ep2_activities_legacy_track']
  self.assertEqual([e['perk'] for e in entries],['ep2_activities_legacy_'+str(i) for i in range(1,6)])
 def test_legacy_changes_keep_the_original_dynasty_and_preceding_perk(self):
  for track,entries in self.editor['ruler_tools']['legacies'].items():
   perks=list(dict.fromkeys(e['perk'] for e in entries))
   for entry in entries:
    valid=dump(get(self.guis[entry['entry']['id']],'is_valid'))
    self.assertIn('root.var:twcm_ui_target.dynasty = root.var:twcm_editor_dynasty',valid)
    index=perks.index(entry['perk'])
    if index:self.assertIn('has_dynasty_perk = '+perks[index-1],valid)
 def test_legacy_trait_choices_set_only_the_requested_native_variable(self):
  for entries in self.editor['ruler_tools']['legacies'].values():
   for entry in entries:
    if not entry['trait']:continue
    body=self.bodies[entry['entry']['id']]
    variables=[e.value for e in walk(body) if e.key=='set_variable']
    self.assertEqual([(get(v,'name'),get(v,'value')) for v in variables],[(entry['perk']+'_'+entry['trait'],'1')])
    removed={e.value for e in walk(body) if e.key=='remove_variable'}
    self.assertEqual(removed,{entry['perk']+'_'+e['trait'] for e in entries if e['perk']==entry['perk']})
 def test_guardian_changes_do_not_replace_an_unreviewed_guardian(self):
  self.assertIn('num_of_relation_guardian = 0',self.valid('guardian_assign'))
  self.assertIn('has_relation_guardian = root.var:twcm_ui_other',self.valid('guardian_remove'))
  for name in ['guardian_assign','guardian_remove']:
   valid=self.valid(name)
   self.assertIn('root.var:twcm_ui_target.court_owner = root.var:twcm_ui_other.court_owner',valid)
   self.assertIn('is_travelling = no',valid)
   self.assertNotIn('start_travel_plan',dump(self.bodies['twcm_editor_'+name]))
 def test_education_uses_native_focus_callbacks_and_child_age_bounds(self):
  for skill in ['diplomacy','martial','stewardship','intrigue','learning']:
   body=dump(self.bodies['twcm_editor_education_'+skill])
   self.assertIn('set_focus = education_'+skill,body)
   self.assertNotIn('add_trait = education_',body)
   valid=self.valid('education_'+skill)
   self.assertIn('age >= 6',valid);self.assertIn('age < 16',valid)
 def test_alliance_creation_prevents_self_enemy_and_both_liege_directions(self):
  valid=self.valid('alliance_create')
  self.assertIn('is_at_war_with = root.var:twcm_ui_other',valid)
  self.assertIn('is_vassal_or_below_of = root.var:twcm_ui_other',valid)
  self.assertIn('is_vassal_or_below_of = root.var:twcm_ui_target',valid)
  self.assertIn('allow_alliance',dump(self.bodies['twcm_editor_alliance_create']))
 def test_clear_tyranny_uses_current_value_not_an_arbitrary_large_subtraction(self):
  body=dump(self.bodies['twcm_editor_clear_tyranny'])
  self.assertIn('value = tyranny',body);self.assertIn('multiply = -1',body)
  self.assertIn('tyranny > 0',self.valid('clear_tyranny'))
 def test_dread_input_has_explicit_bounds(self):
  valid=self.valid('exact_dread')
  self.assertIn('root.var:twcm_editor_number >= 0',valid)
  self.assertIn('root.var:twcm_editor_number <= 100',valid)


class NativeLogReview(unittest.TestCase):
 def test_adjacent_startup_parser_errors_are_not_hidden_by_a_later_native_trace(self):
  text='[00:00:00][E][reader]: Unexpected token in file: "common/casus_belli_types/twcm_test.txt"\n[00:00:01][E][script]: native error\n  Script location: file: common/on_action/game_start.txt line: 1\n    file: common/on_action/twcm_smoke.txt line: 1\n'
  mod,native=classify_errors(text)
  self.assertEqual(len(mod),1);self.assertEqual(len(native),1)
  self.assertIn('Unexpected token',mod[0])
 def test_script_error_is_classified_by_its_own_origin(self):
  text='[00:00:00][E][script]: failed\n  Script location: file: common/scripted_guis/twcm_window_guis.txt line: 1\n'
  mod,native=classify_errors(text)
  self.assertEqual(len(mod),1);self.assertFalse(native)


if __name__=='__main__':unittest.main()

"""Regressions for the full 1.5 editor review; exercise emitted state and payloads."""
import json,unittest
from pathlib import Path
from project_config import ROOT,MOD,GAME
from pdx_script import parse,dump,get,walk
from test_ui_state import SelectionScript,Character




class EditorReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.guis={e.key:e.value for e in parse((MOD/'common/scripted_guis/twcm_window_guis.txt').read_text(encoding='utf-8-sig'))}
  cls.meta=json.loads((ROOT/'tools/cheat_mod_metadata.json').read_text())['window']
  dispatch=get(get(cls.guis['twcm_ui_confirm'],'effect'),'if')
  cls.effects={name:get(next(e.value for e in dispatch if e.key=='if' and get(get(e.value,'limit'),'var:twcm_ui_pending')==ident),'if') for ident,name in cls.meta['confirmation_ids'].items()}
 def test_missing_pin_cannot_silently_select_the_player(self):
  script=SelectionScript();script.root.variables.update(twcm_ui_target=script.root,twcm_editor_pin_1=None)
  self.assertFalse(script.condition(get(script.guis['twcm_editor_pin_select_1'],'is_valid')))
 def test_missing_pin_cannot_silently_replace_other_with_the_player(self):
  script=SelectionScript();script.root.variables.update(twcm_ui_target=script.root,twcm_editor_pin_8=None)
  self.assertFalse(script.condition(get(script.guis['twcm_editor_pin_other_8'],'is_valid')))
 def test_missing_last_created_character_cannot_select_the_player(self):
  script=SelectionScript();script.root.variables.update(twcm_ui_target=script.root,twcm_editor_last_created=None)
  self.assertFalse(script.condition(get(script.guis['twcm_editor_select_created'],'is_valid')))
 def test_copy_religion_preserves_the_exact_rite(self):
  effect=dump(self.effects['twcm_editor_match_other_faith'])
  self.assertIn('set_character_rite = scope:twcm_editor_other_rite',effect)
  self.assertIn('other_rite',self.meta['editor']['snapshot_scopes'])
 def test_every_spawn_role_inherits_the_employers_rite(self):
  for name,data in self.meta['editor']['actions'].items():
   if data['group']!='spawn':continue
   create=next(e.value for e in walk(self.effects[name]) if e.key=='create_character')
   self.assertEqual(get(create,'rite'),'scope:twcm_target.rite',name)
 def test_xp_favourites_and_search_name_their_trait(self):
  actions=self.meta['editor']['actions']
  self.assertIn('Blademaster',actions['twcm_editor_trait_xp_lifestyle_blademaster_0']['title'])
  self.assertIn('Hunter',actions['twcm_editor_trait_xp_lifestyle_hunter_0']['title'])
 def test_age_limited_traits_have_matching_add_guards(self):
  for trait,limit in [('rowdy','age <= 15'),('sickly','age <= 6'),('education_diplomacy_4','age >= 16')]:
   self.assertIn(limit,dump(get(self.guis['twcm_editor_trait_add_'+trait],'is_valid')))
 def test_locked_tenets_require_the_native_dlc_flag(self):
  for tenet,flag in [('tenet_peace_of_god','by_god_alone'),('tenet_gruesome_festivals','the_northern_lords'),('tenet_benevolent_governance','all_under_heaven')]:
   self.assertIn('has_dlc_feature = '+flag,dump(get(self.guis['twcm_editor_tenet_add_'+tenet],'is_valid')))
 def test_artifact_creation_supplies_native_feature_selection_context(self):
  for name,data in self.meta['editor']['actions'].items():
   if data['group']!='artifact_create':continue
   entries=list(walk(self.effects[name]))
   self.assertTrue(any(e.key=='save_scope_as' and e.value=='owner' for e in entries),name)
   values={get(e.value,'name') for e in entries if e.key=='save_scope_value_as'}
   self.assertTrue({'quality','wealth','armor_type'}<=values,name)
 def test_missing_current_rite_cannot_leave_a_different_rite_selected(self):
  script=SelectionScript();script.root.variables.update(twcm_ui_target=script.root,twcm_editor_rite=Character('old rite'))
  script.run(script.helpers['twcm_ui_prepare_effect'])
  self.assertNotIn('twcm_editor_rite',script.root.variables)
  self.assertNotIn('twcm_editor_rite',script.scopes)
 def test_higher_title_transfer_requires_a_landed_recipient(self):
  for name in ['twcm_editor_transfer_title','twcm_editor_transfer_title_vassals']:
   trigger=get(next(e.value for e in get(self.guis[name],'is_valid') if e.key=='custom_tooltip' and get(e.value,'text')==name+'_requirements'),'OR')
   self.assertEqual(get(get(trigger,'root.var:twcm_editor_title'),'tier'),'tier_county')
   self.assertEqual(get(get(trigger,'root.var:twcm_ui_target'),'is_landed'),'yes')
 def test_new_reference_fields_are_rewritten_in_confirm_eligibility(self):
  valid=dump(get(self.guis['twcm_ui_confirm'],'is_valid'))
  self.assertIn('root.var:twcm_ui_pending_editor_other_rite',valid)
  self.assertNotIn('scope:twcm_editor_',valid)
 def test_missing_claim_references_do_not_enter_invalid_scopes(self):
  script=SelectionScript();script.root.variables.update(twcm_ui_claim_title=None,twcm_ui_claim_ruler=None)
  script.run(script.helpers['twcm_ui_prepare_effect'])
  self.assertNotIn('twcm_claim_title',script.scopes)
  self.assertNotIn('twcm_claim_ruler',script.scopes)
  self.assertNotIn('twcm_ui_claim_title',script.root.variables)
  self.assertNotIn('twcm_ui_claim_ruler',script.root.variables)
 def test_exact_shared_values_keep_the_original_dynasty_and_capital(self):
  for action,field in [('exact_renown','dynasty'),('exact_development','capital_province')]:
   entries=list(walk(self.effects['twcm_editor_'+action]))
   self.assertTrue(any(e.key=='scope:twcm_editor_'+field for e in entries),action)
   self.assertIn(field,self.meta['editor']['snapshot_scopes'])
   valid=dump(get(self.guis['twcm_ui_confirm'],'is_valid'))
   self.assertIn('root.var:twcm_ui_pending_editor_'+field,valid)
 def test_crown_visual_has_a_base_game_fallback_without_overriding_native_ids(self):
  p=MOD/'common/artifacts/visuals/twcm_editor_visuals.txt';entries=parse(p.read_text(encoding='utf-8-sig'))
  self.assertEqual([e.key for e in entries],['twcm_editor_crown'])
  fallback=[e.value for e in entries[0].value if e.key=='asset'][-1]
  self.assertTrue(get(get(fallback,'trigger'),'NOR'))
  self.assertEqual(get(fallback,'reference'),'male_headgear_secular_western_royalty_01_artifact_entity')

if __name__=='__main__':unittest.main()

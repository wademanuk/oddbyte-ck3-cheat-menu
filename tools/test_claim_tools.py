"""Structural regressions around claimant/title scope and claim-preservation rules."""
import unittest
from pathlib import Path
from project_config import ROOT,MOD,GAME
from pdx_script import parse,get,walk



class ClaimToolsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.effects={e.key:e.value for e in parse((MOD/'common/scripted_effects/twcm_claim_effects.txt').read_text(encoding='utf-8-sig'))}
  cls.interactions={e.key:e.value for e in parse((MOD/'common/character_interactions/twcm_claim_interactions.txt').read_text(encoding='utf-8-sig'))}
  cls.events={e.key:e.value for e in parse((MOD/'events/twcm_events.txt').read_text(encoding='utf-8-sig')) if isinstance(e.value,list)}
 def test_grants_run_on_claimant_not_current_title_holder(self):
  for strength in ['pressed','unpressed']:
   effect=get(self.effects[f'twcm_add_{strength}_claim_effect'],'if')
   claimant=get(effect,'scope:twcm_target')
   grant=get(claimant,'if')
   self.assertEqual(get(grant,f'add_{strength}_claim'),'scope:twcm_claim_title_work')
   self.assertEqual(get(effect,'save_scope_as'),'twcm_claim_title_work')
 def test_unpressed_grants_preserve_pressed_claims(self):
  outer=get(self.effects['twcm_add_unpressed_claim_effect'],'if')
  action=get(get(outer,'scope:twcm_target'),'if')
  condition=get(get(get(action,'limit'),'NOT'),'any_claim')
  self.assertEqual(get(condition,'explicit'),'yes')
  self.assertIsNone(get(condition,'pressed'))
  self.assertEqual(get(condition,'this'),'scope:twcm_claim_title_work')
 def test_owned_baronial_and_landless_titles_are_excluded(self):
  for effect in self.effects.values():
   guard=get(get(effect,'if'),'limit')
   self.assertTrue(any(e.key=='tier' and e.op=='>=' and e.value=='tier_county' for e in guard))
   self.assertEqual(get(guard,'is_landless_type_title'),'no')
   self.assertTrue(any(e.key=='holder' and e.op=='!=' and e.value=='scope:twcm_target' for e in guard))
   self.assertEqual(get(guard,'exists'),'holder')
 def test_portrait_tools_resolve_living_pin_or_fall_back_to_player_and_only_open_menu(self):
  for interaction in self.interactions.values():
   accept=get(interaction,'on_accept')
   actor_scopes=[e.value for e in accept if e.key=='scope:actor']
   prepare=actor_scopes[0]
   condition=get(get(prepare,'if'),'limit')
   self.assertEqual(get(condition,'has_variable'),'twcm_claim_beneficiary')
   pin=next(e for e in condition if e.key=='var:twcm_claim_beneficiary')
   self.assertEqual(pin.op,'?=')
   self.assertEqual(get(pin.value,'is_alive'),'yes')
   self.assertEqual(get(get(prepare,'else'),'save_scope_as'),'twcm_target')
   mutations=[e for e in walk(accept) if e.key in ['add_pressed_claim','add_unpressed_claim','remove_claim']]
   self.assertEqual(mutations,[])
   self.assertEqual(get(actor_scopes[-1],'twcm_ui_open_effect'),'yes')
   self.assertEqual(get(get(actor_scopes[-1],'set_variable'),'name'),'twcm_ui_target')
 def test_title_picker_uses_owners_personal_titles(self):
  picker=self.interactions['twcm_claim_title_interaction']
  self.assertEqual(get(picker,'target_type'),'title')
  self.assertEqual(get(picker,'target_filter'),'recipient_domain_titles')
  picked=get(get(picker,'can_be_picked_title'),'scope:target')
  self.assertEqual(get(picked,'is_landless_type_title'),'no')
  self.assertEqual(get(get(get(picker,'on_accept'),'scope:target'),'save_scope_as'),'twcm_claim_title')
 def test_bulk_removal_requires_review_and_preserves_implicit_claims(self):
  before=self.events['twcm.0405'];review=self.events['twcm.0406']
  self.assertFalse(any(e.key=='remove_claim' for e in walk(before)))
  removals=[e for e in walk(review) if e.key=='every_claim']
  self.assertEqual(len(removals),1)
  self.assertEqual(get(removals[0].value,'explicit'),'yes')
  self.assertEqual(get(get(removals[0].value,'scope:twcm_target'),'remove_claim'),'scope:twcm_claim_remove_title')
 def test_claim_tools_never_transfer_ownership_or_start_wars(self):
  prohibited={'create_title_and_vassal_change','change_title_holder','change_title_holder_include_vassals','start_war','destroy_title'}
  for entries in list(self.effects.values())+list(self.interactions.values())+[v for k,v in self.events.items() if k.startswith('twcm.04')]:
   self.assertFalse({e.key for e in walk(entries)}&prohibited)

if __name__=='__main__':unittest.main()

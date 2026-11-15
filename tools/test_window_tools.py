"""Regressions for event-to-window adaptation and two-character diplomacy scopes."""
import json,re,unittest
from pathlib import Path
from project_config import ROOT,MOD,GAME
from pdx_script import parse,get,walk


class WindowTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.guis={e.key:e.value for e in parse((MOD/'common/scripted_guis/twcm_window_guis.txt').read_text(encoding='utf-8-sig'))}
  cls.events={int(e.key.split('.')[1]):e.value for e in parse((MOD/'events/twcm_events.txt').read_text(encoding='utf-8-sig')) if e.key.startswith('twcm.')}
  cls.meta=json.loads((ROOT/'tools/cheat_mod_metadata.json').read_text())['window']
  cls.gui=(MOD/'gui/twcm_window.gui').read_text()
 def test_every_legacy_option_has_an_adapter(self):
  for number,event in self.events.items():
   options=[e for e in event if e.key=='option']
   self.assertEqual(len(options),len(self.meta['source_options'][str(number)]))
   for index in range(len(options)):self.assertIn(f'twcm_ui_{number}_{index}',self.guis)
 def test_every_adapter_keeps_the_legacy_effect_payload(self):
  pending={name:str(ident) for ident,name in self.meta['confirmation_ids'].items()}
  dispatcher=get(get(self.guis['twcm_ui_confirm'],'effect'),'if')
  for number,event in self.events.items():
   for index,option in enumerate(e.value for e in event if e.key=='option'):
    name=f'twcm_ui_{number}_{index}';payload=[];navigation=None
    for entry in option:
     if entry.key in ['name','trigger','is_cancel_option']:continue
     if entry.key=='hidden_effect' and len(entry.value)==1 and entry.value[0].key=='trigger_event':
      navigation=int(get(entry.value[0].value,'id').split('.')[1]);continue
     payload.append(entry)
    if name in pending:
     branch=next(e.value for e in dispatcher if e.key=='if' and get(get(e.value,'limit'),'var:twcm_ui_pending')==pending[name])
     actual=get(branch,'if')
    else:actual=get(get(self.guis[name],'effect'),'if')
    effects=[e for e in actual if e.key!='limit']
    if not payload and navigation is None:
     self.assertEqual([(e.key,e.value) for e in effects],[('remove_variable','twcm_ui_open')],name)
    else:self.assertEqual(effects,payload,name)
    self.assertEqual(get(actual,'limit'),get(option,'trigger',parse('always = yes')),name)
 def test_all_gui_buttons_resolve_to_scripted_guis(self):
  refs=set(re.findall(r"GetScriptedGui\( '([^']+)' \)",self.gui))
  self.assertTrue(refs)
  self.assertFalse(refs-self.guis.keys())
  self.assertEqual(len(self.meta['scripted_gui_ids']),len(set(self.meta['scripted_gui_ids'])))
 def test_normal_navigation_does_not_open_events(self):
  for name,body in self.guis.items():
   if name=='twcm_ui_legacy':continue
   self.assertFalse(any(e.key=='trigger_event' for e in walk(get(body,'effect',[]))),name)
 def test_review_snapshots_subject_title_and_other(self):
  for name in self.meta['confirmation_ids'].values():
   body=get(self.guis[name],'effect')
   assignments={get(e.value,'name'):get(e.value,'value') for e in walk(body) if e.key=='set_variable'}
   for field,source in [('target','target'),('other','other'),('title','claim_title'),('ruler','claim_ruler')]:
    self.assertEqual(assignments['twcm_ui_pending_'+field],'var:twcm_ui_'+source)
  effect=get(self.guis['twcm_ui_confirm'],'effect')
  self.assertEqual(get(get(get(effect,'if'),'var:twcm_ui_pending_target'),'save_scope_as'),'twcm_target')
  self.assertFalse(any(e.key=='twcm_ui_prepare_effect' for e in walk(effect)))
 def test_modal_blocks_underlying_actions_but_allows_cancel(self):
  for name in ['twcm_ui_gold_plus','twcm_ui_nav_10','twcm_ui_500_3']:
   self.assertTrue(any(e.key=='NOT' and get(e.value,'has_variable')=='twcm_ui_pending' for e in walk(get(self.guis[name],'is_valid'))))
  for name in ['twcm_ui_cancel','twcm_ui_close','twcm_ui_confirm']:
   self.assertFalse(any(e.key=='NOT' and get(e.value,'has_variable')=='twcm_ui_pending' for e in get(self.guis[name],'is_valid')))
 def test_gold_subtraction_uses_payment_effect(self):
  effect=get(self.guis['twcm_ui_gold_minus'],'effect')
  self.assertTrue(any(e.key=='remove_short_term_gold' and e.value=='root.var:twcm_ui_step' for e in walk(effect)))
  self.assertFalse(any(e.key=='add_gold' for e in walk(effect)))
 def test_confirmation_copy_names_the_operation_and_snapshot(self):
  lines=(MOD/'localization/english/twcm_l_english.yml').read_text(encoding='utf-8-sig').splitlines()[1:]
  labels={line.split(':0 ',1)[0].strip():json.loads(line.split(':0 ',1)[1]) for line in lines}
  for event_number in sorted(set(self.events)&set([97,98,99,350,351,406]+list(range(310,324)))):
   options=[e.value for e in self.events[event_number] if e.key=='option']
   for index,opt in enumerate(options):
    adapter=f'twcm_ui_{event_number}_{index}'
    if adapter not in self.meta['confirmation_ids'].values():continue
    text=labels[f'twcm_ui_confirm_desc_{event_number}_{index}']
    operation=labels[get(self.events[event_number],'title')] if 310<=event_number<=323 else labels[get(opt,'name')]
    self.assertTrue(text.startswith(operation))
    self.assertNotIn('Editing:',text)  # The name is already in the snapshot header.
    self.assertIn('text = "twcm_ui_pending_name"',self.gui)
    self.assertIn("Var('twcm_ui_pending_target').Char.GetFullName",labels['twcm_ui_pending_name'])
    self.assertNotIn("Var('twcm_ui_target')",text)
 def test_window_registry_adds_only_own_file(self):
  registry=(MOD/'gui/scripted_widgets/twcm_widgets.txt').read_text()
  self.assertEqual(registry.count('gui/twcm_window.gui'),2)
  self.assertEqual(sorted(p.name for p in (MOD/'gui').glob('*.gui')),['twcm_window.gui'])
 def test_opinion_changes_other_towards_actor_and_only_own_modifier(self):
  event=self.events[502]
  mutations=[e for e in walk(event) if e.key=='add_opinion']
  self.assertEqual(len(mutations),4)
  for e in mutations:
   self.assertEqual(get(e.value,'target'),'scope:twcm_target')
   self.assertEqual(get(e.value,'modifier'),'twcm_cheat_opinion')
  removals=[e for e in walk(event) if e.key=='remove_opinion']
  self.assertTrue(all(get(e.value,'modifier')=='twcm_cheat_opinion' for e in removals))
  for e in walk(event):
   if e.key=='scope:twcm_other' and isinstance(e.value,list) and any(x.key=='add_opinion' for x in e.value):break
  else:self.fail('Opinion effect must run on the other character')
 def test_weak_hook_does_not_downgrade_existing_hook(self):
  hook=get(next(e.value for e in self.events[501] if e.key=='option'),'scope:twcm_target')
  action=get(hook,'if');self.assertEqual(get(get(get(action,'limit'),'NOT'),'has_hook'),'scope:twcm_other')
  self.assertEqual(get(get(action,'add_hook'),'type'),'twcm_weak_hook')
 def test_romantic_additions_require_unrelated_adults_but_removal_does_not(self):
  for number in [514,515]:
   options=[e.value for e in self.events[number] if e.key=='option']
   add=get(get(options[0],'trigger'),'scope:twcm_target')
   self.assertEqual(get(add,'age'),'18')
   self.assertTrue(any(e.key=='scope:twcm_other' and get(e.value,'age')=='18' for e in add))
   self.assertTrue(any(e.key=='NOT' and get(e.value,'is_close_or_extended_family_of')=='scope:twcm_other' for e in add))
   remove=get(get(options[1],'trigger'),'scope:twcm_target')
   self.assertIsNone(get(remove,'age'))
if __name__=='__main__':unittest.main()

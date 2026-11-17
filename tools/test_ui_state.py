"""Execute the emitted selection/visibility subset to check cross-click state transitions.

This models PDX variable and scope operations only; it is not a CK3 engine emulator.
Unknown effects fail rather than being silently treated as successful game actions.
"""
from dataclasses import dataclass,field
from pathlib import Path
from project_config import ROOT,MOD,GAME
import math
import unittest
from pdx_script import parse,get


@dataclass(eq=False)
class Character:
 name:str
 alive:bool=True
 variables:dict=field(default_factory=dict)

class SelectionScript:
 def __init__(self):
  self.root=Character('player');self.scopes={}
  self.helpers={e.key:e.value for e in parse((MOD/'common/scripted_effects/twcm_window_effects.txt').read_text(encoding='utf-8-sig'))}
  self.guis={e.key:e.value for e in parse((MOD/'common/scripted_guis/twcm_window_guis.txt').read_text(encoding='utf-8-sig'))}
 def resolve(self,value,here):
  if isinstance(value,list):
   result=0
   for e in value:
    if e.key=='floor':result=math.floor(result);continue
    operand=self.resolve(e.value,here)
    if e.key=='value':result=operand
    elif e.key=='add':result+=operand
    elif e.key=='subtract':result-=operand
    elif e.key=='multiply':result*=operand
    elif e.key=='divide':result/=operand
    elif e.key=='max':result=min(result,operand)
    elif e.key=='min':result=max(result,operand)
    else:raise NotImplementedError(e)
   return result
  if value=='root':return self.root
  if value=='this':return here
  if value.startswith('root.var:'):return self.root.variables.get(value.split(':',1)[1])
  if value.startswith('var:'):return here.variables.get(value[4:])
  if value.startswith('scope:'):return self.scopes.get(value[6:])
  try:return int(value)
  except ValueError:return None
 def condition(self,entries,here=None):
  here=here or self.root
  def one(e):
   if e.key in ['AND','OR','NOT','NOR','NAND']:
    parts=(one(x) for x in e.value)
    if e.key=='AND':return all(parts)
    if e.key=='OR':return any(parts)
    if e.key=='NOR':return not any(parts)
    return not all(parts)
   if e.key in ['custom_description','custom_tooltip']:return self.condition([x for x in e.value if x.key!='text'],here)
   if e.key=='always':return e.value=='yes'
   if e.key=='is_ai':return e.value=='no'
   if e.key=='is_alive':return here.alive==(e.value=='yes')
   if e.key=='has_variable':return e.value in here.variables
   if e.key=='exists':return self.resolve(e.value,here) is not None
   subject=self.resolve(e.key,here)
   if isinstance(e.value,list):
    # Optional PDX scope entry skips an absent object; it does not make a useful
    # existence guard. Model that distinction so expired weak references are tested.
    if subject is None:return e.op=='?='
    return self.condition(e.value,subject)
   if e.key.startswith(('var:','root.var:','scope:')):
    other=self.resolve(e.value,here)
    if e.op=='=':return subject==other
    if e.op=='!=':return subject!=other
    if subject is None or other is None:return False
    return {'>':subject>other,'>=':subject>=other,'<':subject<other,'<=':subject<=other}[e.op]
   raise NotImplementedError(e)
  return all(one(e) for e in entries)
 def run(self,entries,here=None):
  here=here or self.root
  branch=None
  for e in entries:
   if e.key=='if':
    branch=self.condition(get(e.value,'limit'),here)
    if branch:self.run([x for x in e.value if x.key!='limit'],here)
   elif e.key=='else':
    if branch is False:self.run(e.value,here)
   elif e.key=='else_if':
    if branch is False:
     branch=self.condition(get(e.value,'limit'),here)
     if branch:self.run([x for x in e.value if x.key!='limit'],here)
   elif e.key=='set_variable':here.variables[get(e.value,'name')]=self.resolve(get(e.value,'value'),here)
   elif e.key=='remove_variable':here.variables.pop(e.value,None)
   elif e.key=='save_scope_as':self.scopes[e.value]=here
   elif e.key=='clear_saved_scope':self.scopes.pop(e.value,None)
   elif e.key=='save_scope_value_as':self.scopes[get(e.value,'name')]=self.resolve(get(e.value,'value'),here)
   elif e.key in self.helpers:self.run(self.helpers[e.key],here)
   elif e.key.startswith(('scope:','var:','root.var:')):
    subject=self.resolve(e.key,here)
    if subject is None:raise AssertionError('Tried to enter a missing scope: '+e.key)
    self.run(e.value,subject)
   else:raise NotImplementedError(e)
 def click(self,name):
  self.assert_valid(name)
  self.scopes={} # Saved scopes do not persist between separate GUI executions.
  self.run(get(self.guis[name],'effect'))
 def assert_valid(self,name):
  assert self.condition(get(self.guis[name],'is_valid')),name+' disabled'

class SelectionStateTests(unittest.TestCase):
 def setUp(self):
  self.script=SelectionScript();self.player=self.script.root
  self.edited=Character('courtier');self.player.variables.update(twcm_ui_target=self.edited,twcm_ui_other=self.player)
 def test_expired_character_variables_recover_to_the_current_player(self):
  self.player.variables.update(twcm_ui_target=None,twcm_ui_other=None)
  self.script.run(self.script.helpers['twcm_ui_prepare_effect'])
  self.assertIs(self.player.variables['twcm_ui_target'],self.player)
  self.assertIs(self.player.variables['twcm_ui_other'],self.player)
 def test_unset_initial_selection_uses_the_calling_character_context(self):
  self.player.variables.clear()
  self.script.run(self.script.helpers['twcm_ui_prepare_effect'])
  self.assertIs(self.script.scopes['twcm_target'],self.player)
  self.assertIs(self.script.scopes['twcm_other'],self.player)
 def test_select_my_ruler_persists_across_the_next_click(self):
  self.script.click('twcm_ui_2_5')
  self.script.run(self.script.helpers['twcm_ui_prepare_effect'])
  self.assertIs(self.player.variables['twcm_ui_target'],self.player)
  self.assertIs(self.script.scopes['twcm_target'],self.player)
 def test_claimant_reset_updates_the_window_subject(self):
  self.player.variables['twcm_claim_beneficiary']=self.edited
  self.script.click('twcm_ui_403_1')
  self.script.run(self.script.helpers['twcm_ui_prepare_effect'])
  self.assertNotIn('twcm_claim_beneficiary',self.player.variables)
  self.assertIs(self.script.scopes['twcm_target'],self.player)
 def test_confirmation_validity_uses_the_original_subject(self):
  self.script.click('twcm_ui_97_0')
  self.player.variables['twcm_ui_target']=Character('other selection',False)
  self.script.assert_valid('twcm_ui_confirm')
 def test_confirmation_is_disabled_if_the_original_subject_dies(self):
  self.script.click('twcm_ui_97_0')
  self.script.assert_valid('twcm_ui_confirm')
  self.edited.alive=False
  self.player.variables['twcm_ui_target']=self.player
  self.assertFalse(self.script.condition(get(self.script.guis['twcm_ui_confirm'],'is_valid')))
 def test_swap_persists_both_sides_for_the_next_action(self):
  self.script.click('twcm_ui_500_3')
  self.script.run(self.script.helpers['twcm_ui_prepare_effect'])
  self.assertIs(self.script.scopes['twcm_target'],self.player)
  self.assertIs(self.script.scopes['twcm_other'],self.edited)
if __name__=='__main__':unittest.main()

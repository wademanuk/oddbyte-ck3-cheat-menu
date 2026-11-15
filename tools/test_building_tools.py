"""Behavioral generation checks for bulk tools without launching or changing a campaign."""
import tempfile
import unittest
from pathlib import Path
from pdx_script import parse,dump,get,walk
from building_tools import generate

class BuildingToolsTests(unittest.TestCase):
 def fixture(self,buildings):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
  game=Path(temp.name)
  for path in ['common/buildings','common/scripted_triggers']:(game/path).mkdir(parents=True)
  (game/'common/buildings/test.txt').write_text(buildings)
  (game/'common/scripted_triggers/test.txt').write_text('''
building_coastal = { is_coastal = yes }
building_holding_level = { has_holding_type = castle_holding has_building_or_higher = castle_$LEVEL$ }
''')
  return game
 def test_parser_keeps_comments_out_of_strings_and_round_trips(self):
  original=parse('x = { label = "#not comment" #comment\n scope:a ?= { value >= 3 } values = { a b } }')
  self.assertEqual(original,parse(dump(original)))
 def test_expands_helpers_and_bypasses_only_intended_requirements(self):
  game=self.fixture('''
castle_01 = { next_building = castle_02 }
castle_02 = { can_construct = { culture = { has_innovation = innovation_castle } } }
port_01 = {
 next_building = port_02
 can_construct_potential = { building_coastal = yes building_holding_level = { LEVEL = 01 } }
 can_construct = { scope:holder.culture = { has_innovation = innovation_port } }
}
port_02 = {
 can_construct_potential = { building_holding_level = { LEVEL = 02 } }
 can_construct = { building_coastal = yes root = { is_riverside_province = yes } }
}
''')
  text,meta=generate(game)
  self.assertIn('is_coastal = yes',text)
  self.assertIn('has_holding_type = castle_holding',text)
  self.assertIn('has_building_or_higher = castle_01',text)
  self.assertNotIn('has_building_or_higher = castle_02',text)
  self.assertIn('scope:twcm_build_province = {',text)
  self.assertNotIn('root =',text)
  self.assertNotIn('has_innovation',text)
  self.assertEqual(meta['fill_roots'],['port_01'])
  self.assertEqual(parse(text),parse(dump(parse(text))))
 def test_existing_chain_guard_prevents_downgrades_and_new_builds_require_space(self):
  game=self.fixture('a_01 = { next_building = a_02 } a_02 = { next_building = a_03 } a_03 = {}')
  text,meta=generate(game);effects={e.key:e.value for e in parse(text)}
  upgrade=effects['twcm_upgrade_buildings_effect']
  steps=[e for e in upgrade if e.key=='if']
  self.assertEqual([get(get(e.value,'limit'),'has_building') for e in steps],['a_01','a_02'])
  self.assertEqual([get(e.value,'add_building') for e in steps],['a_02','a_03'])
  fill=next(e for e in effects['twcm_fill_buildings_effect'] if e.key=='if')
  guards=get(fill.value,'limit')
  self.assertTrue(any(e.key=='free_building_slots' and e.op=='>' and e.value=='0' for e in guards))
  self.assertEqual(get(get(guards,'NOT'),'has_building_or_higher'),'a_01')
 def test_special_slots_are_not_created_but_existing_chains_are_upgraded(self):
  game=self.fixture('special_01 = { type = special next_building = special_02 } special_02 = { type = special }')
  text,meta=generate(game)
  self.assertEqual(meta['fill_roots'],[])
  self.assertIn('add_special_building = special_02',text)
  self.assertIn('has_building = special_01',text)
 def test_technology_only_branch_keeps_legal_condition_chain(self):
  game=self.fixture('''a_01 = { can_construct = {
trigger_if = { limit = { culture = { has_innovation = innovation_a } } is_coastal = yes }
trigger_else = { is_riverside_province = yes }
} }''')
  text,meta=generate(game)
  self.assertIn('always = yes',text)
  self.assertIn('trigger_else = {',text)
  self.assertIn('is_coastal = yes',text)
 def eligible(self,entries,coastal=True):
  def one(e):
   if e.key=='always':return e.value=='yes'
   if e.key in ['AND','OR','NOT','NOR','NAND']:
    values=[one(x) for x in e.value]
    return {'AND':all(values),'OR':any(values),'NOT':not all(values),'NOR':not any(values),'NAND':not all(values)}[e.key]
   if e.key in ['culture','scope:holder']:return self.eligible(e.value,coastal)
   if e.key=='is_coastal':return coastal==(e.value=='yes')
   if e.key=='is_riverside_province':return False
   if e.key=='has_building_or_higher':return False
   if e.key=='free_building_slots':return True
   raise AssertionError('Unknown eligibility condition: '+str(e))
  return all(one(e) for e in entries)
 def fill_guard(self,script):
  text,_=generate(self.fixture('a_01 = { '+script+' }'))
  effects={e.key:e.value for e in parse(text)}
  return get(next(e.value for e in effects['twcm_fill_buildings_effect'] if e.key=='if'),'limit')
 def test_bypassed_innovation_keeps_an_or_branch_true(self):
  guard=self.fill_guard('can_construct_potential = { is_coastal = yes } can_construct = { OR = { culture = { has_innovation = windmills } is_riverside_province = yes } }')
  self.assertTrue(self.eligible(guard,True))
  self.assertFalse(self.eligible(guard,False))
 def test_bypassed_innovation_in_tribal_alternative_allows_upgrade(self):
  text,_=generate(self.fixture('a_01 = { next_building = a_02 } a_02 = { can_construct = { OR = { is_riverside_province = yes scope:holder = { culture = { has_innovation = barracks } } } } }'))
  effect=next(e.value for e in parse(text) if e.key=='twcm_upgrade_buildings_effect')
  guard=get(next(e.value for e in effect if e.key=='if'),'limit')
  guard=[e for e in guard if e.key!='has_building']
  self.assertTrue(self.eligible(guard))
 def test_bypassed_gate_under_negation_preserves_terrain(self):
  guard=self.fill_guard('can_construct = { NOT = { OR = { culture = { has_innovation = old_technology } is_coastal = yes } } }')
  self.assertTrue(self.eligible(guard,False))
  self.assertFalse(self.eligible(guard,True))
 def test_cycles_and_missing_upgrade_ids_fail_before_writing_mod(self):
  for script in ['a = { next_building = b }', 'a = { next_building = a }']:
   game=self.fixture(script)
   with self.assertRaises((AssertionError,ValueError)):generate(game)
 def test_slot_expansion_is_bounded_and_does_not_reduce_existing_capacity(self):
  text,meta=generate(self.fixture('a_01 = {}'))
  effects={e.key:e.value for e in parse(text)}
  loop=get(effects['twcm_expand_slots_effect'],'while')
  self.assertEqual(get(loop,'count'),'7')
  condition=get(loop,'limit')[0]
  self.assertEqual((condition.key,condition.op,condition.value),('building_slots','<','7'))
  self.assertNotIn('remove_building',text)

if __name__=='__main__':unittest.main()

"""Relation regressions checked against CK3's installed aliases and opposites."""
from pathlib import Path
from project_config import ROOT,MOD,GAME
import unittest
from pdx_script import parse,get,walk



class RelationshipTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.events={int(e.key.split('.')[1]):e.value for e in parse((MOD/'events/twcm_events.txt').read_text(encoding='utf-8-sig')) if e.key.startswith('twcm.')}
  cls.native={e.key:e.value for p in (GAME/'common/scripted_relations').glob('*.txt') for e in parse(p.read_text(encoding='utf-8-sig')) if isinstance(e.value,list)}
 def options(self,number):return [e.value for e in self.events[number] if e.key=='option']
 def test_advanced_relations_do_not_create_a_throwaway_basic_relation(self):
  for number,kind,basic in [(511,'best_friend','friend'),(513,'nemesis','rival'),(515,'soulmate','lover')]:
   with self.subTest(kind=kind):
    self.assertIn(basic,{e.key for e in get(self.native[kind],'opposites')})
    setters=[e.key for e in walk(self.options(number)[0]) if e.key.startswith('set_relation_')]
    self.assertEqual(setters,['set_relation_'+kind])
 def test_basic_controls_are_disabled_for_the_advanced_alias(self):
  for number,advanced in [(510,'best_friend'),(512,'nemesis'),(514,'soulmate')]:
   for option in self.options(number)[:2]:
    trigger=get(get(option,'trigger'),'scope:twcm_target')
    self.assertTrue(any(e.key=='NOT' and get(e.value,'has_relation_'+advanced)=='scope:twcm_other' for e in trigger))
 def test_removing_a_relation_never_creates_a_replacement(self):
  for number in range(510,516):
   effects=[e.key for e in walk(self.options(number)[1])]
   self.assertFalse(any(k.startswith('set_relation_') for k in effects))
if __name__=='__main__':unittest.main()

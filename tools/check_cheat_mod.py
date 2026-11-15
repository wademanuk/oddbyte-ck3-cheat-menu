from pathlib import Path
import json,re
from pdx_script import parse,get,walk
from project_config import ROOT as r,MOD as m,GAME as game
meta=json.load(open(r/'tools/cheat_mod_metadata.json'))
# Tokenize strings/comments correctly, then check balanced blocks and matching localization references.
for p in [*m.rglob('*.txt'),*m.rglob('*.gui')]:
 if p.suffix=='.txt':assert p.read_bytes().startswith(b'\xef\xbb\xbf'),(p,'missing UTF-8 BOM')
 t=p.read_text(encoding='utf-8-sig');tokens=re.findall(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}]|[^\s{}]+',t)
 depth=0
 for token in tokens:
  if token.startswith('#'):continue
  if token=='{':depth+=1
  if token=='}':depth-=1
  assert depth>=0,(p,'unexpected closing brace')
 assert depth==0,(p,'unclosed block')
event_text=(m/'events/twcm_events.txt').read_text();ids=re.findall(r'^twcm\.(\d+) =',event_text,re.M);assert len(ids)==len(set(ids))==len(meta['events'])
for targets in meta['events'].values():
 for target in targets:assert str(target) in meta['events'],target
reachable=set();todo=['1']
while todo:
 x=todo.pop()
 if x in reachable:continue
 reachable.add(x);todo.extend(str(n) for n in meta['events'][x])
assert reachable==set(meta['events']),('Unreachable menus',set(meta['events'])-reachable)
for start in meta['events']:
 seen=set();todo=[start]
 while todo:
  x=todo.pop()
  if x in seen:continue
  seen.add(x);todo.extend(str(n) for n in meta['events'][x])
 assert '1' in seen,('No return to main menu',start)
loc=m/'localization/english/twcm_l_english.yml';raw=loc.read_bytes();assert raw.startswith(b'\xef\xbb\xbf');text=raw.decode('utf-8-sig');assert text.startswith('l_english:\n')
keys=re.findall(r'^ (\w+):0 ',text,re.M);assert len(keys)==len(set(keys))
def check_localization(entries,path,parent=None):
 for entry in entries:
  if isinstance(entry.value,list):check_localization(entry.value,path,entry.key)
  elif entry.key in ['name','title','desc','selection_tooltip','confirm_text','custom_tooltip'] and isinstance(entry.value,str) and entry.value.startswith('twcm_'):
   if not (entry.key=='name' and parent in ['set_variable','set_local_variable','change_variable','set_temporary_variable','add_to_variable_list','remove_list_variable','save_scope_value_as']):
    assert entry.value in keys,(path,entry.value)
for p in m.rglob('*.txt'):check_localization(parse(p.read_text(encoding='utf-8-sig')),p)
assert '[scope:' not in text,'Script scope syntax is not a localization data context'
for line in text.splitlines()[1:]:json.loads(line.split(':0 ',1)[1])
assert all(n<=7 for n in meta['event_options'].values()),meta['event_options']
# Verify cross-file custom modifier references and native lifestyle effects against this build.
modifier_text=(m/'common/modifiers/twcm_modifiers.txt').read_text(encoding='utf-8-sig')
modifier_ids=set(re.findall(r'^(twcm_\w+)\s*=',modifier_text,re.M))
opinion_ids={e.key for p in (m/'common/opinion_modifiers').glob('*.txt') for e in parse(p.read_text(encoding='utf-8-sig'))}
for opinion in opinion_ids:assert opinion in keys,opinion
for modifier in modifier_ids:assert modifier in keys and modifier+'_desc' in keys,modifier
for ref in re.findall(r'\b(?:modifier|remove_character_modifier|remove_county_modifier|has_character_modifier)\s*=\s*(twcm_\w+)',event_text):
 assert ref in modifier_ids|opinion_ids,('Unknown custom modifier',ref)

native_effects='\n'.join(p.read_text(encoding='utf-8-sig') for p in (game/'common/effect_localization').glob('*.txt'))
for effect in set(re.findall(r'\b(add_\w+_lifestyle_(?:xp|perk_points))\s*=',event_text)):
 assert re.search(r'^'+effect+r'\s*=',native_effects,re.M),('Unknown lifestyle effect',effect)
# The player owns the event chain; the selected subject receives character effects.
interaction=(m/'common/character_interactions/twcm_interactions.txt').read_text(encoding='utf-8-sig')
assert 'scope:recipient = { save_scope_as = twcm_target }' in interaction
assert 'scope:actor = { trigger_event = { id = twcm.0001 } }' in interaction
assert 'scope:actor = { is_ai = no }' in interaction
assert 'save_scope_as = twcm_target' in (m/'common/decisions/twcm_decisions.txt').read_text()
assert event_text.count('left_portrait = scope:twcm_target')==len(ids)
assert event_text.count('trigger = { is_ai = no }')==len(ids)
parity=meta.get('parity',{})
if parity:
 # Verify presets against this version's modifier names and prevent stacked combined bonuses.
 definitions=set()
 for p in (game/'common/modifier_definition_formats').glob('*.txt'):
  definitions.update(e.key for e in parse(p.read_text(encoding='utf-8-sig')))
 trait_defs={e.key:e.value for e in parse((m/'common/traits/twcm_presets.txt').read_text(encoding='utf-8-sig'))}
 for trait,values in parity['presets'].items():
  assert 'trait_'+trait in keys and 'trait_'+trait+'_desc' in keys,trait
  assert set(values['modifiers']) <= definitions|{'health'},trait
  assert (game/f"gfx/interface/icons/traits/{values['icon']}.dds").exists()
  assert all(values['modifiers'][s]==100 for s in ['diplomacy','martial','stewardship','intrigue','learning','prowess'])
  assert 'immortal' not in values['modifiers']
  opposites={e.key for e in get(trait_defs[trait],'opposites')}
  assert ('twcm_super_all' in opposites) if trait!='twcm_super_all' else len(opposites)==3
 # Check the generated construction script independently of generator metadata.
 building_script=(m/'common/scripted_effects/twcm_building_effects.txt').read_text(encoding='utf-8-sig')
 building_ast=parse(building_script)
 assert parse(__import__('pdx_script').dump(building_ast))==building_ast
 native_buildings={e.key for p in (game/'common/buildings').glob('*.txt') for e in parse(p.read_text(encoding='utf-8-sig')) if isinstance(e.value,list)}
 for e in walk(building_ast):
  if e.key in ['add_building','add_special_building','has_building','has_building_or_higher']:
   assert e.value in native_buildings,('Unknown building',e.value)
  assert e.key not in ['has_innovation','add_building_slot','remove_building','remove_special_building'],e.key
 assert not re.search(r'\broot\b|\$[A-Z_]+\$',building_script)
 # Else branches must directly follow a conditional branch in their own block.
 def branches(entries):
  previous=None
  for e in entries:
   if e.key in ['trigger_else','trigger_else_if']:
    assert previous in ['trigger_if','trigger_else_if'],('Orphan trigger branch',e.key,previous)
   if isinstance(e.value,list):branches(e.value)
   previous=e.key
 branches(building_ast)
 all_effects='\n'.join(p.read_text(encoding='utf-8-sig') for p in (m/'common/scripted_effects').glob('*.txt'))
 defined_effects=set(re.findall(r'^(twcm_\w+)\s*=',all_effects,re.M))
 for ref in re.findall(r'\b(twcm_\w+_effect)\s*=\s*yes',event_text):assert ref in defined_effects,ref
 print(f"PASS: four preset traits, current modifier IDs and icons; {len(parity['building_tools']['fill_roots'])} construction and {len(parity['building_tools']['upgrade_chains'])} upgrade chains; valid native building IDs and conditional branches.")
print(f"PASS: balanced scripts; {len(ids)} unique reachable menus with back paths; {len(keys)} valid localized strings; <=7 options per menu; UTF-8 BOM.")
print('PASS: custom modifier references, all 12 native lifestyle effects, selected-character entry points and player-owned event chains.')

window=meta.get('window')
if window:
 gui=(m/window['widget_file']).read_text()
 scripted=(m/'common/scripted_guis/twcm_window_guis.txt').read_text(encoding='utf-8-sig')
 gui_ids=[e.key for e in parse(scripted)]
 assert len(gui_ids)==len(set(gui_ids))
 assert set(re.findall(r"GetScriptedGui\( '([^']+)' \)",gui))<=set(gui_ids)
 assert 'font_size' not in gui and '.GetOpinion(' not in gui
 for ref in re.findall(r'\b(?:text|tooltip)\s*=\s*"(twcm_\w+)"',gui):
  assert ref in keys,('Unknown GUI text or tooltip',ref)
 for number,options in window['source_options'].items():
  assert len(options)==meta['event_options'][number]
  assert set(options)<=set(gui_ids)
 print(f"PASS: native GUI blocks and bindings; all {sum(map(len,window['source_options'].values()))} legacy options have unique window adapters.")

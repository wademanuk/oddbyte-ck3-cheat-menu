from pathlib import Path
import json,re,shutil,hashlib
from project_config import ROOT,GAME,PACKAGE,MOD,USERMOD,NAME,VERSION,SUPPORTED_VERSION
NS='twcm'
loc={};events=[];trait_meta={};graph={};event_options={}
def write(rel,text,bom=False):
 p=MOD/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8-sig' if bom or p.suffix=='.txt' else 'utf-8')
def label(key,value):loc[key]=value;return key
def jump(n):return f'hidden_effect = {{ trigger_event = {{ id = {NS}.{n:04d} }} }}'
def option(key,text,body='',target=None,trigger=None,cancel=False,raw=False):
 label(key,text);parts=[f'name = {key}']
 if trigger:parts.append(f'trigger = {{ scope:twcm_target = {{ {trigger} }} }}' if not raw else f'trigger = {{ {trigger} }}')
 if cancel:parts.append('is_cancel_option = yes')
 if body:parts.append(body if raw else 'scope:twcm_target = {\n'+body+'\n}')
 if target is not None:parts.append(jump(target))
 return '    option = {\n'+''.join('        '+line+'\n' for part in parts for line in part.splitlines())+'    }\n'
def back(target):return option('twcm_back','Back',target=target,cancel=True)
def event(n,title,desc,opts):
 desc="Editing: [twcm_target.GetFullName] (age [twcm_target.GetAge]). "+desc
 label(f'twcm_{n}_title',title);label(f'twcm_{n}_desc',desc)
 text=f'''{NS}.{n:04d} = {{
    type = character_event
    title = twcm_{n}_title
    desc = twcm_{n}_desc
    theme = stewardship
    left_portrait = scope:twcm_target
    trigger = {{ is_ai = no }}
    soundeffect = none
    immediate = {{
        if = {{
            limit = {{ has_variable = twcm_ui_other exists = var:twcm_ui_other var:twcm_ui_other ?= {{ is_alive = yes }} }}
            var:twcm_ui_other = {{ save_scope_as = twcm_other }}
        }}
        else = {{ save_scope_as = twcm_other }}
        if = {{
            limit = {{ NOT = {{ exists = scope:twcm_target }} }}
            save_scope_as = twcm_target
        }}
        if = {{
            limit = {{ scope:twcm_target = {{ is_alive = no }} }}
            save_scope_as = twcm_target
        }}
    }}
'''+''.join(opts)+'}\n'
 events.append(text);event_options[n]=len(opts)
 graph[n]=[int(x) for x in re.findall(r'id = twcm\.(\d+)',text)]

# Read the installed trait definitions, including opposite groups, rather than guessing IDs.
for file in sorted((GAME/'common/traits').glob('*.txt')):
 text=file.read_text(encoding='utf-8-sig');text=re.sub(r'#.*','',text)
 starts=list(re.finditer(r'(?m)^([a-zA-Z0-9_]+)\s*=\s*\{',text))
 for i,m in enumerate(starts):
  body=text[m.end():starts[i+1].start() if i+1<len(starts) else len(text)]
  opposite=re.search(r'\bopposites\s*=\s*\{([^}]+)\}',body)
  group=re.search(r'(?m)^\s*group\s*=\s*([a-zA-Z0-9_]+)',body)
  trait_meta[m[1]]={'opposites':re.findall(r'\b[a-zA-Z0-9_]+\b',opposite[1]) if opposite else [],'group':group[1] if group else None}
def opposites(trait):
 result=set()
 for opposite in trait_meta[trait]['opposites']:
  if opposite in trait_meta:result.add(opposite)
  result.update(k for k,v in trait_meta.items() if v['group']==opposite)
 return sorted(result-{trait})

event(1,'Classic Cheat Menu','Choose a cheat for the named character. To switch characters, right-click a portrait and choose Cheat Menu: Open Classic Menu.',[
 option('twcm_resources','Resources',target=10),
 option('twcm_stress','Remove all stress','add_stress = -1000',target=1),
 option('twcm_skills','Skills',target=20),
 option('twcm_traits','Change traits',target=30),
 option('twcm_construction','Construction speed',target=40),
 option('twcm_more','More cheats',target=2),
 option('twcm_close','Close menu',cancel=True)])
event(10,'Resources','Add resources to the selected character. Renown goes to their dynasty.',[
 option('twcm_gold','Gold',target=11),option('twcm_prestige','Prestige',target=12),option('twcm_piety','Piety',target=13),option('twcm_renown_bundle','Renown and resource bundle',target=14),back(1)])
for n,resource in [(11,'gold'),(12,'prestige'),(13,'piety')]:
 event(n,resource.title(),f'Add {resource} to the selected character. Each click adds the amount shown.',[
  option(f'twcm_{resource}_{amount}',f'Add {amount:,} {resource}',f'add_{resource} = {amount}',target=n) for amount in [100,1000,10000,100000]]+[back(10)])
skills=['diplomacy','martial','stewardship','intrigue','learning','prowess']
event(20,'Skills','Permanently change skills. Each click adds the amount shown.',[
 option('twcm_all_skills_1','Add 1 to all six skills','\n'.join(f'add_{s}_skill = 1' for s in skills),target=20),
 option('twcm_all_skills_5','Add 5 to all six skills','\n'.join(f'add_{s}_skill = 5' for s in skills),target=20),
 option('twcm_individual_skills','Individual skills',target=21),back(1)])
event(21,'Individual Skills','Choose the skill to increase.',[
 option('twcm_skill_'+s,s.title(),target=22+i) for i,s in enumerate(skills)]+[back(20)])
for i,s in enumerate(skills):
 event(22+i,s.title(),f'Increase the selected character\'s base {s}.',[
  option(f'twcm_{s}_{amount}',f'Add {amount} {s}',f'add_{s}_skill = {amount}',target=22+i) for amount in [1,5,10]]+[back(21)])
trait_summaries={
 'intellect_good_3':'Genius: +5 to diplomacy, martial, stewardship, intrigue and learning; +30% lifestyle experience.',
 'physique_good_3':'Herculean / Amazonian: +8 prowess, +1 health and greater attraction.',
 'beauty_good_3':'Beautiful: +3 diplomacy, +30% fertility and greater attraction.',
 'fecund':'Fecund: +50% fertility, five extra fertile years and longer life expectancy.',
 'pure_blooded':'Pure-blooded: lowers inbreeding risk and improves health and fertility.',
 'brave':'Brave: +2 martial and +3 prowess, with a higher risk of dying in battle.',
 'diligent':'Diligent: +2 diplomacy, +3 stewardship and +3 learning, but slower stress recovery.',
 'temperate':'Temperate: +2 stewardship and a small health boost.',
 'patient':'Patient: +2 learning and slower hostile schemes against this character.',
 'gregarious':'Gregarious: +2 diplomacy, faster personal schemes and greater attraction.',
 'ambitious':'Ambitious: +1 to all six skills, but +25% stress gain.',
 'strong':'Strong: +4 prowess and +0.5 health.',
 'shrewd':'Shrewd: +2 to diplomacy, martial, stewardship, intrigue and learning.',
 'athletic':'Athletic: +1 prowess, a small health boost and faster stress recovery.',
 'immortal':'Prevent natural death; make adult portraits look 25. Scripted deaths can still happen. Remove Immortal to end the effect.',
 'aggressive_attacker':'Inflict more fatal casualties when commanding an army.',
 'unyielding_defender':'Lose fewer soldiers to fatal casualties when commanding an army.',
 'logistician':'Stretch army supplies further and improve travel safety.',
 'military_engineer':'Speed up sieges when commanding an army.',
 'organizer':'Move armies faster and lose fewer soldiers when retreating.',
 'flexible_leader':"Reduce the enemy's terrain advantage when commanding an army.",
}

categories=[(31,'Inherited Traits',[
 ('intellect_good_3','Genius'),('physique_good_3','Herculean / Amazonian'),('beauty_good_3','Beautiful'),('fecund','Fecund'),('pure_blooded','Pure-blooded')]),
 (32,'Personality Traits',[
 ('brave','Brave'),('diligent','Diligent'),('temperate','Temperate'),('patient','Patient'),('gregarious','Gregarious'),('ambitious','Ambitious')]),
 (33,'Other Traits',[
 ('strong','Strong'),('shrewd','Shrewd'),('athletic','Athletic'),('immortal','Immortal')])]
event(30,'Trait Changes','Add or remove traits. Adding a trait replaces opposing traits; removing it does not bring them back.',[
 option('twcm_congenital','Inherited traits',target=31),option('twcm_personality','Personality traits',target=32),option('twcm_other_traits','Other traits and ailments',target=33),back(1)])
trait_id=100
for n,title,traits in categories:
 opts=[]
 for trait,display in traits:
  assert trait in trait_meta,trait
  opts.append(option('twcm_trait_'+trait,display,target=trait_id))
  remove='\n'.join('remove_trait = '+x for x in opposites(trait))
  add=(remove+'\n' if remove else '')+'add_trait = '+trait
  if trait=='immortal':add+='\nif = { limit = { age >= 16 } set_immortal_age = 25 }'
  desc=trait_summaries[trait]+' Adding it replaces opposing traits. Removing it does not bring them back.'
  # Immortal has its own explanation; no opposing-trait paragraph is needed.
  if trait=='immortal':desc=trait_summaries[trait]
  event(trait_id,display,desc,[
   option('twcm_add_'+trait,'Add '+display,add,target=trait_id,trigger=f'NOT = {{ has_trait = {trait} }}'),
   option('twcm_remove_'+trait,'Remove '+display,'remove_trait = '+trait,target=trait_id,trigger=f'has_trait = {trait}'),back(n)])
  trait_id+=1
 if n==33:opts.append(option('twcm_ailments','Heal common ailments',target=34))
 opts.append(back(30));event(n,title,'Choose a trait to add or remove.',opts)
ailments=['ill','wounded_1','wounded_2','wounded_3','infirm','incapable','depressed_1','depressed_genetic','lunatic_1','lunatic_genetic','possessed_1','possessed_genetic']
ailments=[x for x in ailments if x in trait_meta]
event(34,'Heal Common Ailments','Remove illness, wounds, infirmity, incapability, depression, lunacy and possession. Other diseases and injuries may remain.',[
 option('twcm_clear_ailments','Heal common ailments','\n'.join('remove_trait = '+x for x in ailments),target=33),back(33)])
modifier='twcm_near_instant_construction'
event(40,'Construction Speed','Build almost instantly for this character: buildings, districts, holdings and domicile upgrades. Costs still apply. Existing work may need restarting. Enable again after succession.',[
 option('twcm_build_on','Enable near-instant construction',f'add_character_modifier = {{ modifier = {modifier} }}',target=40,trigger=f'NOT = {{ has_character_modifier = {modifier} }}'),
 option('twcm_build_off','Disable near-instant construction',f'remove_character_modifier = {modifier}',target=40,trigger=f'has_character_modifier = {modifier}'),back(1)])
exec((ROOT/'tools/cheat_mod_expansion.py').read_text(),globals())
exec((ROOT/'tools/parity_tools.py').read_text(),globals())
exec((ROOT/'tools/claim_tools.py').read_text(),globals())
exec((ROOT/'tools/diplomacy_tools.py').read_text(),globals())
exec((ROOT/'tools/window_tools.py').read_text(),globals())
label(modifier,'Near-instant Construction')
label(modifier+'_desc','Buildings, districts, holdings and domicile upgrades finish much faster. Normal costs apply. Turn off in Construction speed.')
label('twcm_open_decision','Open Classic Cheat Menu')
label('twcm_open_decision_desc','Open the original menu of cheats for your ruler.')
label('twcm_open_decision_tooltip','Open the classic menu for your ruler.')
label('twcm_open_decision_confirm','Open menu')
label('twcm_open_decision_effect','Choose a cheat after opening the menu.')
write('common/decisions/twcm_decisions.txt','''twcm_open_decision = {
    picture = { reference = "gfx/interface/illustrations/decisions/decision_castle_view.dds" }
    desc = twcm_open_decision_desc
    selection_tooltip = twcm_open_decision_tooltip
    confirm_text = twcm_open_decision_confirm
    ai_check_interval = 0
    sort_order = 1
    is_shown = { is_ai = no }
    effect = {
        custom_tooltip = twcm_open_decision_effect
        hidden_effect = {
            save_scope_as = twcm_target
            trigger_event = { id = twcm.0001 }
        }
    }
    ai_potential = { always = no }
    ai_will_do = { base = 0 }
}
''')
write('events/twcm_events.txt','namespace = twcm\n\n'+'\n'.join(events))
write('common/modifiers/twcm_modifiers.txt',f'''# Build-speed modifiers reduce construction time; negative values are faster.
# A deliberately large reduction overcomes ordinary positive time penalties.
{modifier} = {{
    build_speed = -10
    holding_build_speed = -10
    domicile_build_speed = -10
    district_build_speed = -10
}}
'''+extra_modifiers)
write('localization/english/twcm_l_english.yml','l_english:\n'+''.join(f' {key}:0 '+json.dumps(value,ensure_ascii=False)+'\n' for key,value in loc.items()),bom=True)
descriptor='\n'.join(['version='+json.dumps(VERSION), 'tags={ "Utilities" }', 'name='+json.dumps(NAME,ensure_ascii=False), 'supported_version='+json.dumps(SUPPORTED_VERSION)])+'\n'
write('descriptor.mod',descriptor)
(PACKAGE/'tw_basic_cheat_menu.mod').write_text(descriptor+'path="mod/tw_basic_cheat_menu"\n')
(ROOT/'tools/cheat_mod_metadata.json').write_text(json.dumps({'events':graph,'event_options':event_options,'traits':{k:opposites(k) for k,_ in [t for _,_,ts in categories for t in ts]+commander_traits},'ailments':ailments,'localization_keys':sorted(loc),'parity':parity_meta,'claims':claims_meta,'diplomacy':diplomacy_meta,'window':window_meta},indent=2))
print(f'Built {len(events)} events, {len(loc)} localization entries, {sum(len(ts) for _,_,ts in categories)+len(commander_traits)} editable traits.')
print(MOD)

# Executed by build_cheat_mod.py after the original menus.
from pdx_script import parse,dump,get,Entry
from building_tools import generate as generate_buildings

event(90,'Major Boosts and Realm Tools','Choose stronger character boosts, healing, building upgrades or changes to faith and culture.',[
 option('twcm_presets','Character, realm and commander boosts',target=91),
 option('twcm_diplomacy','Hooks, opinion and relationships',target=500),
 option('twcm_conversion','Change faith and culture',target=95),
 option('twcm_bulk_building','Instant building upgrades',target=300),
 option('twcm_full_healing','Diseases and inherited traits',target=98),option('twcm_claim_tools','Claims and titles',target=400),back(2)])

stats={s:100 for s in skills}
character={**stats,'no_prowess_loss_from_age':'yes','fertility':500,'health':100,
 'monthly_income':1000,'monthly_piety':1000,'monthly_prestige':30,'monthly_dynasty_prestige':30,
 'stress_gain_mult':-10,'monthly_dread':100,'dread_loss_mult':-100,'dread_baseline_add':200,
 'domain_limit':200,'vassal_limit':200,'years_of_fertility':100,'attraction_opinion':1000,
 'ignore_negative_culture_opinion':'yes','enemy_hostile_scheme_phase_duration_add':1000,'owned_scheme_secrecy_add':1000}
# CK3's current scheme system uses success growth and caps instead of old scheme power.
for scheme_kind in ['hostile','personal','political','contract']:
 for suffix in ['add','growth_add','max_add']:
  character[f'owned_{scheme_kind}_scheme_success_chance_{suffix}']=1000
governor={**stats,'levy_size':1,'build_speed':-1000,'build_gold_cost':-1000,
 'holding_build_speed':-1000,'holding_build_gold_cost':-1000,'tax_mult':10,
 'development_growth':1000,'monthly_county_control_growth_add':100,'county_opinion_add':100}
commander={**stats,'min_combat_roll':20,'max_combat_roll':40,'naval_movement_speed_mult':1000,
 'siege_phase_time':-100,'siege_morale_loss':10,'movement_speed':1000,'retreat_losses':-1,
 'hard_casualty_modifier':-1,'enemy_hard_casualty_modifier':10,'advantage':100,
 'enemy_terrain_advantage':-1,'no_water_crossing_penalty':'yes','raid_speed':10,
 'hostile_county_attrition':-1,'supply_duration':10,'supply_limit_mult':10,
 'supply_capacity_mult':10,'siege_weapon_max_size_mult':3}
presets=[('twcm_super_character','Character boost','intellect_good_3',character,92),
 ('twcm_super_governor','Realm boost','administrator',governor,93),
 ('twcm_super_commander','Commander boost','military_engineer',commander,94),
 ('twcm_super_all','All boosts','august',{**character,**governor,**commander},96)]
trait_blocks=[]
modifier_definitions=set()
for p in (GAME/'common/modifier_definition_formats').glob('*.txt'):
 modifier_definitions.update(e.key for e in parse(p.read_text(encoding='utf-8-sig')))
for trait,title,icon,values,n in presets:
 assert set(values)<=(modifier_definitions|{'health'}),('Unrecognized preset modifiers',set(values)-modifier_definitions-{'health'})
 assert (GAME/f'gfx/interface/icons/traits/{icon}.dds').exists(),icon
 label('trait_'+trait,title)
 label('trait_'+trait+'_desc',title+': +100 to all six skills, plus the bonuses listed below. Remove in Major boosts. Immortality is separate.')
 conflicts=[x[0] for x in presets if x[0]!=trait] if trait=='twcm_super_all' else ['twcm_super_all']
 trait_blocks.append(trait+' = {\n'+dump([
  Entry('icon','=',f'"gfx/interface/icons/traits/{icon}.dds"'),
  Entry('shown_in_ruler_designer','=','no'),Entry('shown_in_encyclopedia','=','no'),
  Entry('opposites','=',[Entry(x) for x in conflicts]),
 ]+[Entry(k,'=',str(v)) for k,v in values.items()])+'\n}')
write('common/traits/twcm_presets.txt','\n\n'.join(trait_blocks)+'\n')

def add_preset(trait):
 conflicts=[x[0] for x in presets if x[0]!=trait] if trait=='twcm_super_all' else ['twcm_super_all']
 return '\n'.join('remove_trait = '+x for x in conflicts)+'\nadd_trait = '+trait
clear_presets='\n'.join('remove_trait = '+x[0] for x in presets)
def family(body):
 return body+'\nevery_close_family_member = { limit = { is_alive = yes }\n'+body+'\n}\nevery_spouse = { limit = { is_alive = yes }\n'+body+'\n}'
building_action_help={
 'slots':'Add regular building slots up to seven. Larger holdings stay unchanged. Added slots need this mod enabled.',
 'upgrade':'Upgrade existing buildings, including existing special and duchy buildings, to their highest level. Free and instant; no undo button.',
 'fill':'Fill empty regular slots with fully upgraded, eligible buildings. Existing buildings stay. Free and instant; no undo button.',
 'all':'Expand regular slots to seven, upgrade existing buildings and fill empty slots. Free and instant; no undo button. Added slots need this mod enabled.',
}
def bulk_help(target,key):
 if target in [301,302]:
  area='All holdings under this character, including vassals.' if target==302 else 'Only directly owned holdings.'
  return area+' '+building_action_help[key.rsplit('_',1)[-1]]
 if target in [350,351]:
  return 'Match the selected character in '+('all their counties and vassals.' if target==351 else 'directly owned counties only.')+' No undo button.'
 if target==405:return 'Affects this character\'s held claims; family and succession rights stay.'
 raise ValueError(('Missing action explanation',target,key))

def bulk_option(key,text,body,target):
 explanation=bulk_help(target,key)
 tip=label(key+'_effect',explanation if target in [301,302] else text+'. '+explanation)
 return option(key,text,'custom_tooltip = '+tip+'\nhidden_effect = {\n'+body+'\n}',target=target)
event(91,'Major Boosts','Each boost adds +100 to all six skills, plus extra bonuses. All boosts combines the three sets. Bonuses last until removed; immortality is separate.',[
 option('twcm_preset_'+trait,title,target=n) for trait,title,icon,values,n in presets
]+[option('twcm_family_presets','Give boosts to family',target=97),
 option('twcm_clear_presets','Remove all boosts',clear_presets,target=91),back(90)])
for trait,title,icon,values,n in presets:
 detail={'twcm_super_character':'+100 to all six skills; huge health, fertility and income bonuses; less stress and stronger schemes.',
 'twcm_super_governor':'+100 to all six skills; almost instant, cheaper building; larger levies, more taxes and faster county growth.',
 'twcm_super_commander':'+100 to all six skills; much stronger armies, faster movement and sieges, fewer losses and better supplies.',
 'twcm_super_all':'Combine Character, Realm and Commander boosts. The +100 skill bonus applies once. This replaces individual boosts.'}[trait]
 event(n,title,detail+' Remove to end these bonuses; separate skill edits stay.',[
  option('twcm_enable_'+trait,'Apply '+title,add_preset(trait),target=n,trigger=f'NOT = {{ has_trait = {trait} }}'),
  option('twcm_disable_'+trait,'Remove '+title,'remove_trait = '+trait,target=n,trigger=f'has_trait = {trait}'),back(91)])
event(97,'Family Boosts','Give boosts to this character, living close family and spouses. Future family members are not included.',[
 option('twcm_family_'+trait,'Give family: '+title,family(add_preset(trait)),target=97) for trait,title,icon,values,n in presets
]+[option('twcm_family_immortal','Family immortality',target=99),
 option('twcm_family_remove','Remove family boosts',family(clear_presets),target=97),back(91)])
event(99,'Family Immortality','Prevent natural death for this character, close family and spouses. Adult portraits look 25. Scripted deaths can still happen.',[
 option('twcm_family_immortal_on','Make family immortal (look 25)',family('add_trait = immortal\nif = { limit = { age >= 16 } set_immortal_age = 25 }'),target=99),
 option('twcm_family_immortal_off','Remove family immortality',family('remove_trait = immortal'),target=99),back(97)])

event(14,'Renown and Resource Bundle','Add renown to this character\'s dynasty. The bundle gives this character 100,000 each of gold, prestige and piety, plus 100,000 dynasty renown if they have a dynasty.',[
 option(f'twcm_renown_{v}',f'Add {v:,} dynasty renown',f'dynasty = {{ add_dynasty_prestige = {v} }}',target=14,trigger='exists = dynasty') for v in [1000,10000,100000]
]+[option('twcm_bundle_100k','Add 100,000 gold, prestige, piety and renown','add_gold = 100000\nadd_prestige = 100000\nadd_piety = 100000\nif = { limit = { exists = dynasty } dynasty = { add_dynasty_prestige = 100000 } }',target=14),back(10)])

event(95,'Change Faith and Culture','Make counties follow this character\'s faith or culture. Choose only directly owned counties, or include all counties and vassals under this character.',[
 option('twcm_convert_domain','Directly owned counties only',target=350,trigger='any_held_title = { tier = tier_county }'),
 option('twcm_convert_subrealm','All counties and vassals under this character',target=351,trigger='is_landed = yes'),back(90)])
for n,realm in [(350,False),(351,True)]:
 opts=[]
 for kind,title in [('faith','faith'),('culture','culture'),('both','faith and culture')]:
  county='';people=''
  if kind in ['faith','both']:
   county+='set_county_faith = scope:twcm_target.faith\n';people+='set_character_faith = scope:twcm_target.faith\n'
  if kind in ['culture','both']:
   county+='set_county_culture = scope:twcm_target.culture\n';people+='set_culture = scope:twcm_target.culture\n'
  body=('every_sub_realm_county = {\n'+county+'}\nevery_vassal_or_below = {\n'+people+'}' if realm else 'every_held_title = { limit = { tier = tier_county }\n'+county+'}')
  opts.append(bulk_option(f'twcm_conversion_{n}_{kind}','Match '+title,body,target=n))
 event(n,'Match Faith or Culture: '+('Include Vassals' if realm else 'Owned Counties'),'Match this character\'s faith or culture in '+('all counties and vassals under them.' if realm else 'directly owned counties only.')+' These changes have no undo button.',opts+[back(95)])

native_traits={e.key:e.value for p in (GAME/'common/traits').glob('*.txt') for e in parse(p.read_text(encoding='utf-8-sig')) if isinstance(e.value,list)}
diseases=sorted(k for k,v in native_traits.items() if any(e.key=='flag' and e.value=='illness' for e in v))
genetic_conditions=sorted(k for k,v in native_traits.items() if get(v,'genetic')=='yes' and get(v,'good')!='yes' and k!='giant')
genetic_conditions=sorted(set(genetic_conditions)|({'inbred'}&native_traits.keys()))
def remove_traits(ids):return '\n'.join('remove_trait = '+x for x in ids)
full_heal=remove_traits(sorted(set(diseases+genetic_conditions+ailments)))
event(98,'Diseases and Inherited Traits','Cure diseases or remove harmful inherited traits, including Inbred. Giant stays. These cheats do not prevent future illness.',[
 option('twcm_heal_diseases','Cure diseases and common ailments',remove_traits(sorted(set(diseases+ailments))),target=98),
 option('twcm_heal_genetic','Remove harmful inherited traits',remove_traits(genetic_conditions),target=98),
 option('twcm_heal_everything','Cure diseases and harmful inherited traits',full_heal,target=98),
 option('twcm_heal_family','Cure family: diseases and harmful traits',family(full_heal),target=98),back(90)])

building_text,building_meta=generate_buildings(GAME)
write('common/scripted_effects/twcm_building_effects.txt',building_text)
extra_modifiers+='\ntwcm_extra_building_slot = { stacking = yes building_slot_add = 1 }\n'
label('twcm_extra_building_slot','Cheat: Additional Building Slot')
label('twcm_extra_building_slot_desc','One extra regular building slot. Keep this mod enabled to retain added slots.')
event(300,'Instant Building Upgrades','Upgrade buildings or add slots, free and instantly. Choose directly owned holdings or include vassals. Building placement rules still apply; technology and holding-level requirements are skipped. Great projects and domiciles are excluded.',[
 option('twcm_build_personal','Directly owned holdings only',target=301,trigger='is_landed = yes'),
 option('twcm_build_realm','Include vassal holdings',target=302,trigger='is_landed = yes'),back(90)])
for page,realm in [(301,False),(302,True)]:
 scope=('every_sub_realm_county = { every_county_province = { limit = { has_holding = yes exists = barony.holder }\n%s\n} }' if realm else 'every_held_title = { limit = { tier = tier_barony } title_province = {\n%s\n} }')
 desc=('Affects all existing holdings under this character, including vassals.' if realm else 'Affects only holdings this character owns directly.')
 choices=[('slots','Expand to seven building slots','twcm_expand_slots_effect = yes'),
  ('upgrade','Fully upgrade existing buildings','twcm_upgrade_buildings_effect = yes'),
  ('fill','Fill empty building slots','twcm_fill_buildings_effect = yes'),
  ('all','Expand slots, fill and fully upgrade','twcm_expand_slots_effect = yes\ntwcm_upgrade_buildings_effect = yes\ntwcm_fill_buildings_effect = yes')]
 opts=[]
 for i,(key,title,effect) in enumerate(choices):
  confirm=310+(page-301)*10+i
  opts.append(option(f'twcm_build_choice_{page}_{key}',title,target=confirm))
  event(confirm,title,desc+' '+building_action_help[key],[
   bulk_option(f'twcm_build_confirm_{page}_{key}','Apply to '+('all holdings, including vassals' if realm else 'directly owned holdings'),scope%effect,target=page),back(page)])
 event(page,'Buildings Including Vassals' if realm else 'Directly Owned Buildings',desc+' Choose a free, instant upgrade. Added slots need this mod enabled; other building changes have no undo button.',opts+[back(300)])

parity_meta={'presets':{t:{'modifiers':v,'icon':icon} for t,title,icon,v,n in presets},'diseases':diseases,'genetic_conditions':genetic_conditions,'building_tools':building_meta}

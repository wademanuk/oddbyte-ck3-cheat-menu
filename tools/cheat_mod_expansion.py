# Executed by build_cheat_mod.py with its menu-building helpers and installed trait IDs.
event(2,'More Cheats','Choose a cheat for the selected character, their counties or their troops.',[
 option('twcm_lifestyles','Lifestyle XP and perk points',target=50),
 option('twcm_vitals','Age, health and fertility',target=60),
 option('twcm_counties','County improvements',target=70),
 option('twcm_military','Troops and commanders',target=80),
 option('twcm_power_tools','Major boosts and realm tools',target=90),
 option('twcm_select_self','Select my ruler','save_scope_as = twcm_target\nset_variable = { name = twcm_ui_target value = root }',target=2,raw=True),back(1)])

lifestyles=['diplomacy','martial','stewardship','intrigue','learning','wanderer']
event(50,'Lifestyle XP and Perks','Add experience (XP) or unspent perk points. Spend points in the Lifestyle screen. Some lifestyles require the right character or DLC.',[
 option('twcm_lifestyle_'+s,s.title(),target=51+i) for i,s in enumerate(lifestyles)]+[back(2)])
for i,s in enumerate(lifestyles):
 event(51+i,s.title()+' Lifestyle','Experience fills the perk progress bar. Perk points can be spent immediately in this lifestyle.',[
  option(f'twcm_xp_{s}_{v}',f'Add {v:,} experience',f'add_{s}_lifestyle_xp = {v}',target=51+i) for v in [250,1000,5000]
 ]+[
  option(f'twcm_perks_{s}_{v}',f'Add {v} perk point'+('s' if v!=1 else ''),f'add_{s}_lifestyle_perk_points = {v}',target=51+i) for v in [1,5,10]
 ]+[back(50)])

event(60,'Age, Health and Fertility','Make this character older, younger, healthier or more fertile.',[
 option('twcm_age','Change age',target=61),option('twcm_health','Health and healing',target=62),option('twcm_fertility','Fertility controls',target=63),back(2)])
event(61,'Change Age','Change age by the amount shown. Younger options stop at age 16. Family ties and past events stay unchanged.',[
 option(f'twcm_age_{"younger" if v<0 else "older"}_{abs(v)}',f'Make {abs(v)} year'+('s' if abs(v)!=1 else '')+(' younger' if v<0 else ' older'),f'change_age = {v}',target=61,trigger=f'age >= {16-v}' if v<0 else None)
 for v in [-1,-5,-10,1,5,10]]+[back(60)])
event(62,'Health and Healing','Add +5 health until turned off, or heal common ailments such as wounds and illness. Other diseases or disabilities may remain.',[
 option('twcm_health_on','Add +5 health','add_character_modifier = { modifier = twcm_health_boost }',target=62,trigger='NOT = { has_character_modifier = twcm_health_boost }'),
 option('twcm_health_off','Remove health boost','remove_character_modifier = twcm_health_boost',target=62,trigger='has_character_modifier = twcm_health_boost'),
 option('twcm_heal_now','Heal common ailments','\n'.join('remove_trait = '+x for x in ailments),target=62),back(60)])
event(63,'Fertility Controls','Add or subtract 100% fertility until turned off. Normal age and pregnancy rules still apply.',[
 option('twcm_fertility_high','Add +100% fertility','remove_character_modifier = twcm_low_fertility\nadd_character_modifier = { modifier = twcm_high_fertility }',target=63,trigger='NOT = { has_character_modifier = twcm_high_fertility }'),
 option('twcm_fertility_low','Apply -100% fertility','remove_character_modifier = twcm_high_fertility\nadd_character_modifier = { modifier = twcm_low_fertility }',target=63,trigger='NOT = { has_character_modifier = twcm_low_fertility }'),
 option('twcm_fertility_reset','Turn off fertility changes','remove_character_modifier = twcm_high_fertility\nremove_character_modifier = twcm_low_fertility',target=63),back(60)])

event(70,'Counties and Buildings','Improve the selected character\'s counties or buildings. Choose their capital or all counties they own directly.',[
 option('twcm_county_capital','Capital county',target=71,trigger='is_landed = yes exists = capital_province'),
 option('twcm_county_domain','All directly owned counties',target=72,trigger='any_held_title = { tier = tier_county }'),back(2)])
for n,title,scope in [(71,'Capital County','capital_province.county = {\n%s\n}'),(72,'All Directly Owned Counties','every_held_title = { limit = { tier = tier_county }\n%s\n}')]:
 event(n,title,('Improve the capital county.' if n==71 else 'Improve all counties owned directly; excludes vassals.')+' Development and control stop at normal limits. The +100 popular-opinion bonus lasts until removed and does not stack.',[
  option(f'twcm_dev_{n}_{v}',f'Add {v} development',scope%f'change_development_level = {v}',target=n) for v in [1,5,10]
 ]+[
  option(f'twcm_control_{n}','Restore control to 100',scope%'change_county_control = 100',target=n),
  option(f'twcm_pop_on_{n}','Add +100 popular opinion',scope%'add_county_modifier = { modifier = twcm_popular_support }',target=n),
  option(f'twcm_pop_off_{n}','Remove popular-opinion boost',scope%'remove_county_modifier = twcm_popular_support',target=n),back(70)])

event(80,'Troops and Commanders','Restore missing troops or improve this character as a commander. Refills affect existing forces only; they do not create regiments.',[
 option('twcm_refill_maa','Refill men-at-arms','every_maa_regiment = { change_maa_troops_count = { value = maa_max_troops_count subtract = maa_current_troops_count min = 0 } }',target=80,trigger='any_maa_regiment = { always = yes }'),
 option('twcm_refill_levies','Refill levies and garrisons in owned holdings','every_held_title = { limit = { tier = tier_barony } title_province = { refill_levy = yes refill_garrison = yes } }',target=80,trigger='is_landed = yes'),
 option('twcm_commanders','Commander skills and traits',target=81),back(2)])
event(81,'Improve Commander','Increase martial or prowess, or change commander traits. These affect the selected character.',[
 option('twcm_commander_martial','Add 5 martial','add_martial_skill = 5',target=81),
 option('twcm_commander_prowess','Add 5 prowess','add_prowess_skill = 5',target=81),
 option('twcm_commander_both','Add 5 martial and 5 prowess','add_martial_skill = 5\nadd_prowess_skill = 5',target=81),
 option('twcm_commander_traits','Commander traits',target=83),back(80)])
commander_traits=[('aggressive_attacker','Aggressive Attacker'),('unyielding_defender','Unyielding Defender'),('logistician','Logistician'),('military_engineer','Military Engineer'),('organizer','Organizer'),('flexible_leader','Flexible Leader')]
event(83,'Commander Traits','Choose a commander trait to add or remove.',[
 option('twcm_commander_'+trait,title,target=200+i) for i,(trait,title) in enumerate(commander_traits)]+[back(81)])
for i,(trait,title) in enumerate(commander_traits):
 assert trait in trait_meta,trait
 removal='\n'.join('remove_trait = '+x for x in opposites(trait))
 event(200+i,title,trait_summaries[trait]+' Adding it replaces opposing traits.',[
  option('twcm_add_'+trait,'Add '+title,(removal+'\n' if removal else '')+'add_trait = '+trait,target=200+i,trigger=f'NOT = {{ has_trait = {trait} }}'),
  option('twcm_remove_'+trait,'Remove '+title,'remove_trait = '+trait,target=200+i,trigger=f'has_trait = {trait}'),back(83)])

label('twcm_edit_character_interaction','Cheat Menu: Open Classic Menu')
label('twcm_edit_character_interaction_desc','Open the classic menu for [recipient.GetTitledFirstName]. Choose a cheat there.')
write('common/character_interactions/twcm_interactions.txt','''twcm_edit_character_interaction = {
    category = interaction_category_friendly
    common_interaction = yes
    interface_priority = 100
    icon = icon_contract_modification_single
    desc = twcm_edit_character_interaction_desc
    use_diplomatic_range = no
    ignores_pending_interaction_block = yes
    auto_accept = yes
    is_shown = {
        scope:actor = { is_ai = no }
        scope:recipient = { is_alive = yes }
    }
    on_accept = {
        scope:recipient = { save_scope_as = twcm_target }
        scope:actor = { trigger_event = { id = twcm.0001 } }
    }
    ai_will_do = { base = 0 }
}
''')

extra_modifiers='''
twcm_health_boost = { health = 5 }
twcm_high_fertility = { fertility = 1 }
twcm_low_fertility = { fertility = -1 }
twcm_popular_support = { county_opinion_add = 100 }
'''
for key,title,desc in [
 ('twcm_health_boost','Cheat: Health Boost','+5 health until turned off in Health and healing.'),
 ('twcm_high_fertility','Cheat: High Fertility','+100% fertility until turned off in Fertility.'),
 ('twcm_low_fertility','Cheat: Low Fertility','-100% fertility until turned off in Fertility.'),
 ('twcm_popular_support','Cheat: Popular Support','+100 popular opinion until removed in Counties and buildings.')]:
 label(key,title);label(key+'_desc',desc)

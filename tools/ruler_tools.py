"""Ruler standing, languages, legacies, education and alliances.

Executed before favourite registration and confirmation dispatch. Shared edits use
the existing runtime-object snapshots, with identity checks again at Apply.
"""

playable = 'is_alive = yes is_playable_character = yes'
for amount in [100,500,-100,-500]:
 single('legitimacy_'+('add_' if amount>0 else 'remove_')+str(abs(amount)),
  ('Add ' if amount>0 else 'Remove ')+str(abs(amount))+' legitimacy',
  'add_legitimacy = '+str(amount), playable, group='standing',
  help_text=('Add ' if amount>0 else 'Remove ')+str(abs(amount))+' legitimacy points for the selected playable ruler. Normal legitimacy limits apply. This changes points, not a fixed number of legitimacy levels.')
for amount in [10,-10]:
 single('dread_'+('add' if amount>0 else 'remove'),('Add ' if amount>0 else 'Remove ')+'10 dread',
  'add_dread = '+str(amount),'is_alive = yes is_ruler = yes',group='standing',
  help_text=('Add ' if amount>0 else 'Remove ')+'10 dread for the selected ruler. Normal limits apply; active traits and boosts can raise dread again.')
single('exact_dread','Set dread to chosen number',
 'add_dread = { value = scope:twcm_editor_number subtract = dread }',
 'is_alive = yes is_ruler = yes scope:twcm_editor_number >= 0 scope:twcm_editor_number <= 100',group='standing',
 help_text='Set the selected ruler’s dread to '+number_text+' (0–100). Active traits and boosts can raise dread again.')
single('clear_tyranny','Clear tyranny','add_tyranny = { value = tyranny multiply = -1 }',
 'is_alive = yes is_ruler = yes tyranny > 0',group='standing',
 help_text='Remove the selected ruler’s current tyranny. Other opinion penalties, rivals and grievances remain.')

# Current values are read directly from the character rather than cached by navigation.
value_path=MOD/'common/script_values/twcm_window_values.txt'
write('common/script_values/twcm_window_values.txt',value_path.read_text(encoding='utf-8-sig')+''.join(
 'twcm_editor_'+stat+'_value = { value = '+stat+' }\n' for stat in ['legitimacy','dread','tyranny']))

# Preserve the actual pair of cultures, including hybrid/divergent campaign objects.
culture_pair = (pair+' exists = scope:twcm_editor_culture exists = scope:twcm_editor_other_culture '
 'scope:twcm_target.culture = scope:twcm_editor_culture scope:twcm_other.culture = scope:twcm_editor_other_culture')
other_culture_text="[GetPlayer.MakeScope.Var('twcm_editor_other_culture').Culture.GetName]"
editor_action('learn_other_language','Learn Other’s cultural language',
 'scope:twcm_target = { learn_language_of_culture = scope:twcm_editor_other_culture }',
 culture_pair+' scope:twcm_target = { age >= 6 NOT = { knows_language_of_culture = scope:twcm_editor_other_culture } }',
 group='languages',help_text='Teach the selected character the language of '+other_culture_text+', Other’s current culture. Requires age 6+. No language-learning scheme or culture conversion. Apply is disabled if either culture changes during review.')
for amount in [10,25]:
 editor_action('acceptance_'+str(amount),'Add '+str(amount)+' cultural acceptance',
  'scope:twcm_editor_culture = { change_cultural_acceptance = { target = scope:twcm_editor_other_culture value = '+str(amount)+' desc = twcm_editor_acceptance_reason } }',
  culture_pair+' NOT = { scope:twcm_editor_culture = scope:twcm_editor_other_culture } scope:twcm_editor_culture = { cultural_acceptance = { target = scope:twcm_editor_other_culture value < 100 } }',
  group='languages',help_text='Add '+str(amount)+' acceptance points between '+culture_text+' and '+other_culture_text+', up to 100. This shared relationship affects both cultures. Both characters must keep their cultures during review.')
editor_action('acceptance_max','Set cultural acceptance to 100',
 'scope:twcm_editor_culture = { set_cultural_acceptance = { target = scope:twcm_editor_other_culture value = 100 } }',
 culture_pair+' NOT = { scope:twcm_editor_culture = scope:twcm_editor_other_culture } scope:twcm_editor_culture = { cultural_acceptance = { target = scope:twcm_editor_other_culture value < 100 } }',
 group='languages',help_text='Set acceptance between '+culture_text+' and '+other_culture_text+' to 100. This affects everyone of both cultures. Apply is disabled if either character changes culture.')
label('twcm_editor_acceptance_reason','Oddbyte cultural acceptance adjustment')

# Native files are not consistently ordered (the activity track starts with _2).
# Native perk IDs carry their tier, so sort by that rather than file position.
legacy_tracks={}
for perk,values in catalog['dynasty_perks'].items():
 legacy_tracks.setdefault(get(values,'legacy'),[]).append(perk)
for perks in legacy_tracks.values():
 perks.sort(key=lambda key:int(key.rsplit('_',1)[1]))
legacy_entries={}
dynasty_guard='exists = scope:twcm_editor_dynasty scope:twcm_target.dynasty = scope:twcm_editor_dynasty exists = scope:twcm_editor_dynasty.dynast scope:twcm_editor_dynasty.dynast = { is_alive = yes }'
dynasty_text="[GetPlayer.MakeScope.Var('twcm_editor_dynasty').Dynasty.GetName]"
for track,perks in legacy_tracks.items():
 legacy_entries[track]=[]
 for index,perk in enumerate(perks):
  values=catalog['dynasty_perks'][perk]
  choices=[e.key for e in get(values,'traits',[])] or [None]
  # Native track visibility and perk eligibility run on the dynasty head, as in CK3.
  visibility=dump(get(catalog['dynasty_legacies'][track],'is_shown',[]))
  eligibility=('OR = { dynasty = { has_dynasty_perk = '+perks[0]+' } AND = { '+visibility+' } }\n' if visibility else '')+dump(get(values,'can_be_picked',[]))
  guard=(dynasty_guard+' scope:twcm_editor_dynasty = { NOT = { has_dynasty_perk = '+perk+' } '+
    ('has_dynasty_perk = '+perks[index-1] if index else '')+' dynast = { '+eligibility+' } }')
  for trait in choices:
   key='legacy_'+perk+('_'+trait if trait else '')
   title=catalog['name'](track)+': '+str(index+1)+' — '+catalog['name'](perk)
   extra=''
   if trait:
    title+=' ('+catalog['name'](trait,'trait_')+')'
    # Native birth/education effects read this exact dynasty variable. Clearing all
    # alternatives makes a chosen perk deterministic, including imported saves.
    extra=' '.join('remove_variable = '+perk+'_'+t for t in choices)+' set_variable = { name = '+perk+'_'+trait+' value = 1 }'
   entry=editor_action(key,'Unlock '+title,
    'scope:twcm_editor_dynasty = { save_scope_value_as = { name = twcm_legacy_renown_before value = dynasty_prestige } save_scope_value_as = { name = twcm_legacy_level_before value = dynasty_prestige_level } add_dynasty_perk = '+perk+' '+extra+' add_dynasty_prestige = { value = scope:twcm_legacy_renown_before subtract = dynasty_prestige } add_dynasty_prestige_level = { value = scope:twcm_legacy_level_before subtract = dynasty_prestige_level } }',guard,
    group='legacies',help_text='Unlock '+catalog['name'](perk)+' for the '+dynasty_text+' dynasty without spending renown. '+
    ('Chosen legacy trait: '+catalog['name'](trait,'trait_')+'. ' if trait else '')+
    'Requires the previous perk in this track and the dynasty head’s normal DLC/culture/government eligibility. The whole dynasty benefits. Already unlocked perks cannot be granted again. No undo.')
   legacy_entries[track].append({'perk':perk,'trait':trait,'entry':entry})

# No travel is fabricated: this editor handles available people at the same court.
# Reassignment is explicitly remove-then-assign, so a pending review cannot remove
# a guardian who was appointed after it opened.
ward_available='is_alive = yes age < 16 is_imprisoned = no is_at_home = yes is_travelling = no NOT = { has_character_flag = under_offer_as_ward_flag } NOT = { exists = var:ward_waiting_for_guardian } NOT = { exists = var:ward_travelling_to_guardian }'
guardian_available='is_alive = yes age >= 18 is_imprisoned = no is_at_home = yes is_travelling = no NOT = { has_trait = incapable } NOT = { has_character_flag = under_offer_as_guardian_flag } NOT = { exists = var:guardian_waiting_for_ward } NOT = { exists = var:guardian_travelling_to_ward }'
same_court='exists = scope:twcm_target.court_owner exists = scope:twcm_other.court_owner scope:twcm_target.court_owner = scope:twcm_other.court_owner'
editor_action('guardian_assign','Make Other the guardian',
 'scope:twcm_target = { set_relation_guardian = scope:twcm_other add_character_flag = player_educated }',
 pair+' '+same_court+' scope:twcm_target = { '+ward_available+' num_of_relation_guardian = 0 } scope:twcm_other = { '+guardian_available+' num_of_relation_ward < 2 }',
 group='education',help_text='Make Other the selected child’s guardian. Requires a child under 16 with no guardian and a free adult aged 18+ with fewer than two wards. Both must be home at the same court, with no pending education travel/offer. No forced culture or faith conversion. Remove an existing guardian first.')
editor_action('guardian_remove','Remove Other as guardian',
 'scope:twcm_target = { remove_relation_guardian = scope:twcm_other }',
 pair+' '+same_court+' scope:twcm_target = { '+ward_available+' has_relation_guardian = scope:twcm_other } scope:twcm_other = { '+guardian_available+' }',
 group='education',help_text='End the guardianship between the selected child and Other. Both must be home at the same court with no pending education travel/offer. The child’s education focus stays. Other guardianships are unchanged.')
for skill in skills[:-1]:
 single('education_'+skill,'Choose '+skill+' education',
  'set_focus = education_'+skill,
  'is_alive = yes age >= 6 age < 16 NOT = { has_focus = education_'+skill+' }',group='education',
  help_text='Set the selected child’s education focus to '+skill+'. Requires age 6–15. Native focus-change effects run and can adjust existing education progress. This does not grant a completed education trait.')

alliance_rulers=pair+' scope:twcm_target = { is_landed = yes is_imprisoned = no } scope:twcm_other = { is_landed = yes is_imprisoned = no }'
editor_action('alliance_create','Create alliance with Other',
 'scope:twcm_target = { allow_alliance = scope:twcm_other create_alliance = scope:twcm_other }',
 alliance_rulers+' scope:twcm_target = { NOT = { is_allied_to = scope:twcm_other } NOT = { is_at_war_with = scope:twcm_other } NOT = { is_vassal_or_below_of = scope:twcm_other } } scope:twcm_other = { NOT = { is_vassal_or_below_of = scope:twcm_target } }',
 group='alliances',help_text='Create an alliance between the two named landed rulers without negotiation or marriage. Requires different free rulers who are not enemies in a war or in each other’s liege chain. The alliance is tied to these rulers and follows normal death/succession rules. No war is joined automatically.')
editor_action('alliance_break','Break alliance with Other',
 'scope:twcm_target = { break_alliance = scope:twcm_other }',
 pair+' scope:twcm_target = { is_allied_to = scope:twcm_other }',group='alliances',
 help_text='Break the alliance between the two named characters. Other alliances stay. Native alliance-breaking consequences apply; existing wars are not ended.')

ruler_tools_meta={'legacies':legacy_entries,'perk_count':len(catalog['dynasty_perks']),
 'groups':['standing','languages','legacies','education','alliances']}

"""Extended editor actions. Executed by window_tools before confirmation dispatch is built."""
from editor_catalog import load_catalog, search_expression
catalog = load_catalog(GAME)
editor_actions = {}
editor_groups = {}
editor_pages = {}
editor_scope_fields = ['title', 'title_owner', 'war', 'artifact', 'culture', 'faith', 'rite', 'other_culture', 'other_faith', 'other_rite', 'dynasty', 'capital_province']
editor_number_fields = ['number', 'spawn_age', 'spawn_female'] + ['spawn_' + skill for skill in skills]
editor_traits = {}
editor_pins = 8

# These aliases are refreshed on every click, including a change from the classic menu.
editor_prepare = '''twcm_editor_prepare_effect = {
 if = { limit = { NOT = { has_variable = twcm_editor_number } } set_variable = { name = twcm_editor_number value = 25 } }
 if = { limit = { NOT = { has_variable = twcm_editor_spawn_age } } set_variable = { name = twcm_editor_spawn_age value = 25 } }
 if = { limit = { NOT = { has_variable = twcm_editor_spawn_female } } set_variable = { name = twcm_editor_spawn_female value = 0 } }
 if = { limit = { exists = scope:twcm_target.culture } set_variable = { name = twcm_editor_culture value = scope:twcm_target.culture } }
 else = { remove_variable = twcm_editor_culture }
 if = { limit = { exists = scope:twcm_target.faith } set_variable = { name = twcm_editor_faith value = scope:twcm_target.faith } }
 else = { remove_variable = twcm_editor_faith }
 if = { limit = { exists = scope:twcm_target.rite } set_variable = { name = twcm_editor_rite value = scope:twcm_target.rite } }
 else = { remove_variable = twcm_editor_rite }
 if = { limit = { exists = scope:twcm_other.culture } set_variable = { name = twcm_editor_other_culture value = scope:twcm_other.culture } }
 else = { remove_variable = twcm_editor_other_culture }
 if = { limit = { exists = scope:twcm_other.faith } set_variable = { name = twcm_editor_other_faith value = scope:twcm_other.faith } }
 else = { remove_variable = twcm_editor_other_faith }
 if = { limit = { exists = scope:twcm_other.rite } set_variable = { name = twcm_editor_other_rite value = scope:twcm_other.rite } }
 else = { remove_variable = twcm_editor_other_rite }
 if = { limit = { exists = scope:twcm_target.dynasty } set_variable = { name = twcm_editor_dynasty value = scope:twcm_target.dynasty } }
 else = { remove_variable = twcm_editor_dynasty }
 if = { limit = { exists = scope:twcm_target.capital_province } set_variable = { name = twcm_editor_capital_province value = scope:twcm_target.capital_province } }
 else = { remove_variable = twcm_editor_capital_province }
'''
for skill in skills:
 editor_prepare += f' if = {{ limit = {{ NOT = {{ has_variable = twcm_editor_spawn_{skill} }} }} set_variable = {{ name = twcm_editor_spawn_{skill} value = 10 }} }}\n'
for field in editor_scope_fields:
 editor_prepare += f' clear_saved_scope = twcm_editor_{field}\n if = {{ limit = {{ has_variable = twcm_editor_{field} exists = var:twcm_editor_{field} }} var:twcm_editor_{field} = {{ save_scope_as = twcm_editor_{field} }} }}\n else = {{ remove_variable = twcm_editor_{field} }}\n'
for field in editor_number_fields:
 editor_prepare += f' save_scope_value_as = {{ name = twcm_editor_{field} value = var:twcm_editor_{field} }}\n'
editor_prepare += '}\n'
prepare = prepare.replace('    var:twcm_ui_other = { save_scope_as = twcm_other }', '    var:twcm_ui_other = { save_scope_as = twcm_other }\n    twcm_editor_prepare_effect = yes')
write('common/scripted_effects/twcm_window_effects.txt', prepare + editor_prepare)


def editor_action(key, title, body, trigger='', group='utility', help_text='', confirm=True):
 name = 'twcm_editor_' + key
 text_key = label(name + '_label', title)
 help_text = help_text or title + '.'
 tip = label(name + '_requirements', help_text)
 # Native tooltips explain an unavailable button with this sentence rather than raw variables.
 condition = f'custom_tooltip = {{ text = {tip} {trigger or "always = yes"} }}'
 desc = ui_loc(name + '_review', title + '\n\n' + help_text + ('\n\nOther: [twcm_other.GetFullName].' if 'scope:twcm_other' in body else ''))
 loc[desc] = loc[desc].replace('twcm_ui_target', 'twcm_ui_pending_target').replace('twcm_ui_other', 'twcm_ui_pending_other')
 for field in editor_scope_fields:
  loc[desc] = loc[desc].replace("Var('twcm_editor_" + field + "')", "Var('twcm_ui_pending_editor_" + field + "')")
 for field in editor_number_fields:
  loc[desc] = loc[desc].replace("Var('twcm_editor_" + field + "')", "Var('twcm_ui_pending_editor_" + field + "')")
 register(name, body, condition, confirm=confirm, description=desc)
 entry = {'id': name, 'key': text_key, 'title': title, 'help': tip, 'group': group, 'trigger': trigger}
 editor_actions[name] = entry
 editor_groups.setdefault(group, []).append(entry)
 return entry


def single(key, title, effect, trigger='', **kwargs):
 return editor_action(key, title, 'scope:twcm_target = { ' + effect + ' }',
                      'scope:twcm_target = { ' + trigger + ' }' if trigger else '', **kwargs)


pair = 'scope:twcm_target = { is_alive = yes } scope:twcm_other = { is_alive = yes } NOT = { scope:twcm_target = scope:twcm_other }'
landed = 'scope:twcm_target = { is_landed = yes }'
court_pair = pair + ' scope:twcm_target = { is_landed = yes } scope:twcm_other = { is_landed = no is_imprisoned = no is_adult = yes is_courtier_of = scope:twcm_target }'
num = 'scope:twcm_editor_number'
number_text = "[GetPlayer.MakeScope.Var('twcm_editor_number').GetValue|0]"
title_text = "[GetPlayer.MakeScope.Var('twcm_editor_title').Title.GetName]"
title_owner_text = "[GetPlayer.MakeScope.Var('twcm_editor_title_owner').Char.GetFullName]"
war_text = "[GetPlayer.MakeScope.Var('twcm_editor_war').War.GetName]"
artifact_text = "[GetPlayer.MakeScope.Var('twcm_editor_artifact').Artifact.GetName]"
culture_text = "[GetPlayer.MakeScope.Var('twcm_editor_culture').Culture.GetName]"
faith_text = "[GetPlayer.MakeScope.Var('twcm_editor_faith').Faith.GetName]"
rite_text = "[GetPlayer.MakeScope.Var('twcm_editor_rite').Rite.GetNameNoTooltip]"

# Full native trait inventory: categories, active state, incompatible groups and track XP.
for trait, values in catalog['traits'].items():
 title = catalog['name'](trait, 'trait_')
 oppos = set()
 for e in get(values, 'opposites', []):
  if e.key in catalog['traits']: oppos.add(e.key)
  oppos.update(k for k, v in catalog['traits'].items() if get(v, 'group') == e.key)
 # Education changes replace existing education traits, including other skill branches.
 if catalog['trait_categories'][trait] == 'education':
  oppos.update(k for k in catalog['traits'] if catalog['trait_categories'][k] == 'education' and k.startswith('education_prowess_') == trait.startswith('education_prowess_'))
 oppos.discard(trait)
 add = '\n'.join('remove_trait = ' + key for key in sorted(oppos)) + '\nadd_trait = ' + trait + '\nforce_character_skill_recalculation = yes'
 if trait == 'immortal': add += '\nif = { limit = { age >= 16 } set_immortal_age = 25 }'
 age_guard = ''
 age_help = ''
 for field,comparison,caption in [('minimum_age','>=','at least'),('maximum_age','<=','at most')]:
  age = get(values,field)
  if age is not None:
   age_guard += ' age '+comparison+' '+age
   age_help += ' Requires age '+caption+' '+age+'.'
 a = single('trait_add_' + trait, 'Add ' + title, add, 'NOT = { has_trait = ' + trait + ' }'+age_guard, group='traits', confirm=False,
            help_text='Add this trait to the selected character. Incompatible traits are removed; removing it later will not restore them.'+age_help)
 r = single('trait_remove_' + trait, 'Remove ' + title, 'remove_trait = ' + trait + '\nforce_character_skill_recalculation = yes', 'has_trait = ' + trait, group='traits', confirm=False,
            help_text='Remove this trait from the selected character. Requires that they currently have it.')
 xp = []
 for i, track in enumerate(catalog['trait_tracks'][trait]):
  xp.append(single('trait_xp_' + trait + '_' + str(i), title + ': +100 XP' + (' — ' + track.replace('_', ' ').title() if track else ''),
      'add_trait_xp = { trait = ' + trait + (' track = ' + track if track else '') + ' value = 100 }',
      'has_trait = ' + trait, group='trait_xp', confirm=False, help_text='Add 100 experience to this trait track. Requires the selected character to have the trait.'))
 editor_traits[trait] = {'title': title, 'category': catalog['trait_categories'][trait], 'add': a, 'remove': r, 'xp': xp}

# Court / prisoners. The selected character is the employer or jailer; Other is the person.
editor_action('recruit', 'Bring other character to court', 'scope:twcm_target = { add_courtier = scope:twcm_other } scope:twcm_other = { return_to_court = yes }',
 pair + ' ' + landed + ' scope:twcm_other = { is_landed = no is_ruler = no is_imprisoned = no NOT = { is_courtier_of = scope:twcm_target } }',
 group='court', help_text='Move the other character into the selected ruler\'s court. Requires a landed ruler and an unlanded, free person outside that court.')
editor_action('imprison', 'Imprison other character', 'scope:twcm_target = { imprison = { target = scope:twcm_other type = dungeon } }',
 pair + ' ' + landed + ' scope:twcm_other = { is_imprisoned = no }', group='court',
 help_text='Put the other character in the selected ruler\'s dungeon. Requires a free person and a landed ruler. Native imprisonment consequences can follow.')
editor_action('release', 'Release other character', 'scope:twcm_other = { release_from_prison = yes }',
 pair + ' scope:twcm_other = { is_imprisoned_by = scope:twcm_target }', group='court',
 help_text='Release the other character without a ransom. Requires them to be imprisoned by the selected character.')
for position, title in [('chancellor', 'Chancellor'), ('marshal', 'Marshal'), ('steward', 'Steward'), ('spymaster', 'Spymaster')]:
 editor_action('appoint_' + position, 'Appoint other as ' + title, f'scope:twcm_target = {{ assign_councillor_type = {{ type = councillor_{position} target = scope:twcm_other remove_existing_councillor = yes }} }}',
 court_pair + ' scope:twcm_other = { is_councillor = no }', group='court', help_text='Replace the selected ruler\'s ' + title.lower() + ' with the other character. Requires a free adult courtier in that ruler\'s court who is not already a councillor. This overrides normal appointment preferences.')
editor_action('dismiss_councillor', 'Dismiss other from council', 'scope:twcm_target = { fire_councillor = scope:twcm_other }',
 pair + ' scope:twcm_other = { is_councillor_of = scope:twcm_target }', group='court',
 help_text="Remove the other character from the selected ruler's council. Requires them to hold a council position for that ruler. They remain at court unless a native event moves them.")
for status, title in [('force', 'Force knight service'), ('disallow', 'Forbid knight service'), ('default', 'Restore normal knight choice')]:
 editor_action('knight_' + status, title, 'scope:twcm_other = { set_knight_status = ' + {'force':'force','disallow':'forbid','default':'allow'}[status] + ' }', court_pair,
 group='court', help_text='Change the other adult courtier\'s knight preference in the selected ruler\'s court. Normal knight eligibility still applies.')
editor_action('physician', 'Appoint other as physician', 'scope:twcm_target = { if = { limit = { employs_court_position = court_physician_court_position } revoke_court_position = { court_position = court_physician_court_position } } appoint_court_position = { recipient = scope:twcm_other court_position = court_physician_court_position } }',
 court_pair + ' scope:twcm_other = { NOT = { has_court_position = court_physician_court_position } }', group='court',
 help_text='Appoint the other adult courtier as court physician for the selected ruler. Replaces an existing physician.')
editor_action('physician_remove', 'Remove other as physician', 'scope:twcm_target = { revoke_court_position = { recipient = scope:twcm_other court_position = court_physician_court_position } }',
 court_pair + ' scope:twcm_other = { has_court_position = court_physician_court_position }', group='court',
 help_text='Remove the other character from the selected ruler\'s physician position. Requires them to hold that position.')

# Family: exclude close-family/child marriage and use the native direct-child heir effect.
marriage = pair + ' scope:twcm_target = { age >= 18 is_married = no } scope:twcm_other = { age >= 18 is_married = no } NOT = { scope:twcm_target = { is_close_or_extended_family_of = scope:twcm_other } }'
for effect, title in [('marry', 'Marry the two characters'), ('marry_matrilineal', 'Marry matrilineally')]:
 editor_action(effect, title, 'scope:twcm_target = { ' + effect + ' = scope:twcm_other }', marriage + ' OR = { AND = { scope:twcm_target = { is_female = yes } scope:twcm_other = { is_female = no } } AND = { scope:twcm_target = { is_female = no } scope:twcm_other = { is_female = yes } } }',
 group='family', help_text='Marry these two unrelated, unmarried adults aged 18+. Matrilineal marriage follows the female spouse\'s dynasty. Native family and succession consequences apply.')
editor_action('divorce', 'Divorce the two characters', 'scope:twcm_target = { divorce = scope:twcm_other }',
 pair + ' scope:twcm_target = { is_spouse_of = scope:twcm_other }', group='family', help_text='End the marriage between these two characters. Requires that they are spouses; children and existing family links remain.')
editor_action('join_house', 'Join other character\'s house', 'scope:twcm_target = { set_house = scope:twcm_other.house }',
 pair + ' scope:twcm_other = { exists = house } NOT = { scope:twcm_target.house = scope:twcm_other.house }', group='family',
 help_text='Move the selected character into the other character\'s house and dynasty. Requires a different existing house. Descendants are not moved automatically; inheritance can change.')
editor_action('adopt', 'Adopt other character', 'scope:twcm_target = { adopt = scope:twcm_other if = { limit = { exists = house } scope:twcm_other = { set_house = scope:twcm_target.house } } }',
 pair + ' scope:twcm_target = { age >= 18 age >= { value = scope:twcm_other.age add = 16 } NOT = { is_close_or_extended_family_of = scope:twcm_other } } scope:twcm_other = { age < 16 is_landed = no }',
 group='family', help_text='Make the selected adult a parent of the other child. Requires an unrelated, unlanded child under 16 and an age gap of at least 16 years. The child joins the parent\'s house if one exists. Existing parentage and inheritance may change.')
editor_action('designate_heir', 'Designate other as heir', 'scope:twcm_target = { set_designated_heir = scope:twcm_other }',
 pair + ' ' + landed + ' scope:twcm_other = { is_child_of = scope:twcm_target }', group='family',
 help_text='Designate this direct child as the selected ruler\'s heir. Requires a living direct child. Title-specific succession laws can still affect which titles they inherit.')

# Actual title ownership is separate from the existing claims picker.
title_guard = 'exists = scope:twcm_editor_title exists = scope:twcm_editor_title_owner scope:twcm_editor_title = { tier >= tier_county is_landless_type_title = no exists = holder holder = scope:twcm_editor_title_owner holder != scope:twcm_target } OR = { scope:twcm_editor_title = { tier = tier_county } scope:twcm_target = { is_landed = yes } }'
for include in [False, True]:
 effect = 'change_title_holder_include_vassals' if include else 'change_title_holder'
 editor_action('transfer_title' + ('_vassals' if include else ''), 'Take selected title' + (' and its vassals' if include else ' only'),
 f'''create_title_and_vassal_change = {{ type = granted save_scope_as = twcm_editor_change add_claim_on_loss = no }}
 scope:twcm_editor_title = {{ {effect} = {{ holder = scope:twcm_target government_base = scope:twcm_editor_title_owner change = scope:twcm_editor_change }} }}
 resolve_title_and_vassal_change = scope:twcm_editor_change''', title_guard, group='titles',
 help_text='Transfer ' + title_text + ' from ' + title_owner_text + ' to the selected character' + (' with its vassals.' if include else '; direct vassals are not explicitly transferred.') + ' For a duchy or higher, the recipient must already hold land: give them a county first. Choose a title using the portrait title picker. Ownership, government, rank and succession can change. No undo.')
editor_action('vassalize', 'Make other character a vassal', '''create_title_and_vassal_change = { type = granted save_scope_as = twcm_editor_change }
 scope:twcm_other = { change_liege = { liege = scope:twcm_target change = scope:twcm_editor_change } }
 resolve_title_and_vassal_change = scope:twcm_editor_change''',
 pair + ' ' + landed + ' scope:twcm_other = { is_landed = yes highest_held_title_tier < scope:twcm_target.highest_held_title_tier NOT = { is_liege_or_above_of = scope:twcm_target } NOT = { is_vassal_of = scope:twcm_target } }',
 group='titles', help_text='Move the other ruler and their realm under the selected ruler. Requires a lower-rank landed ruler who is not already a direct vassal or an ancestor in the liege chain. Native realm changes apply.')
single('independence', 'Make selected ruler independent', '''create_title_and_vassal_change = { type = granted save_scope_as = twcm_editor_change }
 becomes_independent = { change = scope:twcm_editor_change }
 resolve_title_and_vassal_change = scope:twcm_editor_change''', 'is_landed = yes exists = liege', group='titles',
 help_text='Remove the selected ruler\'s liege, taking their sub-realm with them. Requires a landed vassal. Realm borders and political relationships change; no undo.')
for kind, contract in [('tax', 'feudal_government_taxes'), ('levies', 'feudal_government_levies')]:
 levels = [('exempt', 'None'), ('low', 'Low'), ('normal', 'Normal'), ('high', 'High'), ('extortionate', 'Maximum')]
 for level_index, (level, caption) in enumerate(levels):
  single('contract_' + kind + '_' + level, kind.title() + ': ' + caption,
   f'vassal_contract_set_obligation_level = {{ type = {contract} level = {level_index} }}',
   'is_landed = yes exists = liege government_has_flag = government_is_feudal vassal_contract_has_modifiable_obligations = yes',
   group='contracts', help_text='Set the selected feudal vassal\'s ' + kind + ' obligation to ' + caption.lower() + '. Requires a modifiable feudal vassal contract. This changes the contract with their own liege, not the other character.')

# Selected active war only, with winner relative to the edited character's actual side.
war_guard = 'exists = scope:twcm_editor_war scope:twcm_target = { any_character_war = { this = scope:twcm_editor_war } }'
for outcome, title in [('victory', 'Win selected war'), ('defeat', 'Lose selected war'), ('white_peace', 'White peace in selected war')]:
 if outcome == 'white_peace': body = 'scope:twcm_editor_war = { end_war = white_peace }'
 else:
  win_attack = 'attacker' if outcome == 'victory' else 'defender'
  win_defend = 'defender' if outcome == 'victory' else 'attacker'
  body = f'scope:twcm_editor_war = {{ if = {{ limit = {{ is_attacker = scope:twcm_target }} end_war = {win_attack} }} else = {{ end_war = {win_defend} }} }}'
 editor_action('war_' + outcome, title, body, war_guard + (' scope:twcm_editor_war = { is_white_peace_possible = yes }' if outcome == 'white_peace' else ''), group='wars',
 help_text='End ' + war_text + ' with ' + outcome.replace('_', ' ') + ' for the selected character\'s side. Requires a selected active war they participate in' + (' that allows white peace.' if outcome == 'white_peace' else '.') + ' Native war rewards, title changes and truces apply. No undo.')
editor_action('clear_truces', 'Clear truces between the two characters', 'scope:twcm_target = { cancel_truce_both_ways = scope:twcm_other }',
 pair + ' OR = { scope:twcm_target = { has_truce = scope:twcm_other } scope:twcm_other = { has_truce = scope:twcm_target } }', group='wars',
 help_text='Remove truces in both directions between the two named characters. Requires an existing truce. Other rulers\' truces remain.')

# Choice catalogs use native static IDs. Shared culture / faith edits get explicit reviews.
for culture in catalog['cultures']:
 single('culture_' + culture, 'Become ' + catalog['name'](culture), 'set_culture = culture:' + culture,
 'NOT = { culture = culture:' + culture + ' }', group='cultures', help_text='Change only the selected character\'s culture to ' + catalog['name'](culture) + '. Counties and relatives stay as they are.')
for faith in catalog['faiths']:
 single('faith_' + faith, 'Convert to ' + catalog['name'](faith), 'set_character_faith = faith:' + faith,
 'NOT = { faith = faith:' + faith + ' }', group='faiths', help_text='Change only the selected character\'s faith to ' + catalog['name'](faith) + '. Counties and other people are not forcibly converted; native conversion consequences can follow.')
for field, title, effect in [('culture','culture','set_culture'),('faith','faith','set_character_faith')]:
 destination="[GetPlayer.MakeScope.Var('twcm_editor_other_"+field+"')."+('Culture' if field=='culture' else 'Faith')+".GetName]"
 extra_effect = ' set_character_rite = scope:twcm_editor_other_rite' if field=='faith' else ''
 different = 'NOT = { '+field+' = scope:twcm_editor_other_'+field+' }'
 extra_guard = ''
 if field=='faith':
  title += ' and rite'
  destination += " / [GetPlayer.MakeScope.Var('twcm_editor_other_rite').Rite.GetNameNoTooltip]"
  different = 'OR = { '+different+' NOT = { rite = scope:twcm_editor_other_rite } }'
  extra_guard = ' exists = scope:twcm_editor_other_rite'
 editor_action('match_other_'+field,'Match other character\'s '+title,'scope:twcm_target = { '+effect+' = scope:twcm_editor_other_'+field+extra_effect+' }',
 pair+' exists = scope:twcm_editor_other_'+field+extra_guard+' scope:twcm_target = { '+different+' }',group=field+'_match',
 help_text='Change only the selected character to '+destination+', copied from the other character. Supports campaign-created cultures and rites. Counties and relatives stay unchanged.')
for innovation in catalog['innovations']:
 editor_action('innovation_' + innovation, 'Discover ' + catalog['name'](innovation), 'scope:twcm_editor_culture = { add_innovation = ' + innovation + ' }',
 'exists = scope:twcm_editor_culture scope:twcm_editor_culture = { NOT = { has_innovation = ' + innovation + ' } }', group='innovations',
 help_text='Unlock this innovation for ' + culture_text + '. This affects everyone of that culture, not just the selected character. Regional/era technology gates are bypassed.')
editor_action('innovations_all', 'Discover every innovation', 'scope:twcm_editor_culture = { ' + '\n'.join('if = { limit = { NOT = { has_innovation = ' + i + ' } } add_innovation = ' + i + ' }' for i in catalog['innovations']) + ' }',
 'exists = scope:twcm_editor_culture', group='innovation_bulk', help_text='Unlock all installed innovations for ' + culture_text + ', including regional ones. Everyone of that culture benefits. This cannot be undone here.')
for tradition in catalog['traditions']:
 title = catalog['name'](tradition, '')
 for add in [True, False]:
  editor_action(('tradition_add_' if add else 'tradition_remove_') + tradition, ('Add ' if add else 'Remove ') + title,
   'scope:twcm_editor_culture = { ' + ('add_culture_tradition' if add else 'remove_culture_tradition') + ' = ' + tradition + ' }',
   'exists = scope:twcm_editor_culture scope:twcm_editor_culture = { ' + ('free_tradition_slot > 0 NOT = { has_cultural_tradition = ' + tradition + ' }' if add else 'has_cultural_tradition = ' + tradition) + ' }',
   group='traditions', help_text=('Add this tradition to ' if add else 'Remove this tradition from ') + culture_text + '. Affects everyone of this culture. Adding requires a free tradition slot; normal adoption costs and time are bypassed.')
for group, data in catalog['doctrine_groups'].items():
 for doctrine in data['choices']:
  clean = '\n'.join(f'if = {{ limit = {{ rite_has_doctrine = {d} }} remove_rite_doctrine = {d} }}' for d in data['choices'] if d != doctrine)
  editor_action('doctrine_' + doctrine, 'Set ' + catalog['name'](doctrine, '') , 'scope:twcm_editor_rite = { ' + clean + '\nadd_rite_doctrine = ' + doctrine + ' }',
   'exists = scope:twcm_editor_rite scope:twcm_editor_rite = { NOT = { rite_has_doctrine = ' + doctrine + ' } }', group='doctrines',
   help_text='Replace the doctrine in the ' + catalog['name'](group) + ' group for ' + rite_text + '. Followers of this rite are affected; other rites keep their own rules. No undo.')
for tenet in catalog['tenets']:
 dlc = get(catalog['tenets'][tenet],'requires_dlc_flag')
 dlc_guard = ' has_dlc_feature = '+dlc if dlc else ''
 dlc_help = ' Adding requires the '+dlc.replace('_',' ').title()+' DLC.' if dlc else ''
 for add in [True, False]:
  editor_action(('tenet_add_' if add else 'tenet_remove_') + tenet, ('Add ' if add else 'Remove ') + catalog['name'](tenet, ''),
   'scope:twcm_editor_rite = { ' + ('add_rite_tenet' if add else 'remove_rite_tenet') + ' = ' + tenet + ' }',
   'exists = scope:twcm_editor_rite'+(dlc_guard if add else '')+' scope:twcm_editor_rite = { ' + ('NOT = { rite_has_tenet = ' + tenet + ' } NOT = { any_rite_tenet = { count >= pam_faith_core_tenets_cap_value } }' if add else 'rite_has_tenet = ' + tenet) + ' }', group='tenets',
   help_text=('Add this tenet to ' if add else 'Remove this tenet from ') + rite_text + '. This edits the selected character\'s rite for all its followers. Other rites stay unchanged. Adding requires a free core-tenet slot; remove an existing one first. Normal reformation costs are bypassed.'+dlc_help)

# Artifacts: explicit creation and per-item changes, never implicit inventory-wide transfers.
# Native crown models can all reject a culture whose cosmetic DLC is unavailable.
# Preserve the native variants under a new ID and use a base-game crown only when
# none of their triggers pass. Never replace a vanilla visual definition.
from editor_catalog import definitions
crown_visual = copy.deepcopy(definitions(GAME/'common/artifacts/visuals')['crown'])
native_crown_conditions = [Entry('AND','=',get(e.value,'trigger',[])) for e in crown_visual if e.key=='asset']
fallback = [Entry('trigger','=',[Entry('NOR','=',native_crown_conditions)]),Entry('reference','=','male_headgear_secular_western_royalty_01_artifact_entity')]
crown_visual.append(Entry('asset','=',fallback))
write('common/artifacts/visuals/twcm_editor_visuals.txt',dump([Entry('twcm_editor_crown','=',crown_visual)]))
artifact_mods = '''twcm_editor_artifact_basic = { prowess = 2 monthly_prestige = 0.25 }
 twcm_editor_artifact_fine = { prowess = 4 diplomacy = 1 monthly_prestige = 0.5 }
 twcm_editor_artifact_great = { prowess = 6 diplomacy = 2 monthly_prestige = 1 }
 twcm_editor_artifact_best = { prowess = 10 diplomacy = 3 monthly_prestige = 2 }
'''
write('common/modifiers/twcm_editor_artifact_modifiers.txt', artifact_mods)
for key, _ in [(e.key, e.value) for e in parse(artifact_mods)]:
 label(key, key.rsplit('_', 1)[-1].title() + ' cheat craftsmanship')
 label(key + '_desc', 'Bonuses apply while this artifact is equipped.')
for kind, native_type, visual in [('Sword','sword','sword'), ('Armor','armor_mail','armor'), ('Crown','helmet','twcm_editor_crown'), ('Regalia','regalia','regalia'), ('Ring','ring','ring')]:
 for rarity, caption, quality, mod in [('common','Common',10,'basic'), ('masterwork','Masterwork',40,'fine'), ('famed','Famed',70,'great'), ('illustrious','Illustrious',100,'best')]:
  key = 'artifact_create_' + kind.lower() + '_' + rarity
  artifact_name = label('twcm_' + key + '_name', caption + ' ' + kind)
  artifact_desc = label('twcm_' + key + '_desc', 'Created with the Cheat Menu. Its craftsmanship bonuses apply while equipped.')
  single(key, 'Create ' + caption.lower() + ' ' + kind.lower(),
   f'''save_scope_as = owner
   save_scope_value_as = {{ name = quality value = {quality} }}
   save_scope_value_as = {{ name = wealth value = {quality} }}
   save_scope_value_as = {{ name = armor_type value = flag:armor_type_mail }}
   create_artifact = {{ name = {artifact_name} description = {artifact_desc} type = {native_type} visuals = {visual} rarity = {rarity} quality = scope:quality wealth = scope:wealth modifier = twcm_editor_artifact_{mod} }}''',
   group='artifact_create', help_text='Create a new ' + caption.lower() + ' ' + kind.lower() + ' in the selected character\'s inventory. It is not automatically equipped. Normal equipment and DLC rules apply.')
artifact_guard = 'exists = scope:twcm_editor_artifact scope:twcm_editor_artifact = { artifact_owner = scope:twcm_target }'
editor_action('artifact_repair', 'Repair selected artifact', 'scope:twcm_editor_artifact = { add_durability = 100000 }', artifact_guard,
 group='artifacts', help_text='Restore ' + artifact_text + ' to its maximum durability. Requires the selected character to own that artifact.')
editor_action('artifact_improve', 'Improve selected artifact', '''scope:twcm_editor_artifact = {
 remove_artifact_modifier = twcm_editor_artifact_basic remove_artifact_modifier = twcm_editor_artifact_fine
 remove_artifact_modifier = twcm_editor_artifact_great remove_artifact_modifier = twcm_editor_artifact_best
 add_artifact_modifier = twcm_editor_artifact_best set_artifact_rarity = illustrious
 }''', artifact_guard, group='artifacts', help_text='Give ' + artifact_text + ' illustrious rarity and a single cheat craftsmanship bonus: +10 prowess, +3 diplomacy and +2 monthly prestige while equipped. Native bonuses remain; repeating does not stack this bonus. The model and original quality score stay unchanged.')
editor_action('artifact_transfer', 'Give artifact to other character', 'scope:twcm_editor_artifact = { set_owner = { target = scope:twcm_other } }', artifact_guard + ' ' + pair,
 group='artifacts', help_text='Transfer ' + artifact_text + ' from the selected character to the other character. Requires ownership of the selected artifact and a different living recipient. No copies are created.')

# Configurable spawner: six independent base skills, age, sex and a role-specific education.
spawn_skills = ' '.join(skill + ' = scope:twcm_editor_spawn_' + skill for skill in skills)
spawn_limits = ' '.join('scope:twcm_editor_spawn_' + skill + ' >= 0 scope:twcm_editor_spawn_' + skill + ' <= 100' for skill in skills)
spawn_summary = ', '.join(skill.title() + ": [GetPlayer.MakeScope.Var('twcm_editor_spawn_" + skill + "').GetValue|0]" for skill in skills)
spawn_sex = "[SelectLocalization(EqualTo_CFixedPoint(GetPlayer.MakeScope.Var('twcm_editor_spawn_female').GetValue,'(CFixedPoint)1'),'twcm_editor_spawn_sex_label_1','twcm_editor_spawn_sex_label_0')]"
for role, title, education in [('courtier','Courtier','education_diplomacy_3'), ('commander','Commander','education_martial_4'), ('physician','Physician','education_learning_4'), ('councillor','Councillor','education_stewardship_4'), ('knight','Knight','education_martial_3')]:
 create = f'''create_character = {{ age = scope:twcm_editor_spawn_age gender_female_chance = {{ value = scope:twcm_editor_spawn_female multiply = 100 }}
 employer = scope:twcm_target culture = scope:twcm_target.culture faith = scope:twcm_target.faith rite = scope:twcm_target.rite dynasty = none random_traits = yes
 trait = {education} {spawn_skills}
 after_creation = {{ save_scope_as = twcm_editor_created {'add_trait = lifestyle_physician' if role == 'physician' else ''} }}
 }}
 set_variable = {{ name = twcm_editor_last_created value = scope:twcm_editor_created }}'''
 editor_action('spawn_' + role, 'Create ' + title.lower(), create,
 landed + ' ' + spawn_limits + ' scope:twcm_editor_spawn_age >= 18 scope:twcm_editor_spawn_age <= 80', group='spawn',
 help_text='Create one ' + title.lower() + " at the selected ruler's court, sharing their culture and faith. Requires age 18–80 and base skills 0–100. Age: [GetPlayer.MakeScope.Var('twcm_editor_spawn_age').GetValue|0]. Sex: " + spawn_sex + '. ' + spawn_summary + '. Education adds its usual bonuses. Not automatically appointed or married.')
for skill in skills:
 sgui('twcm_editor_spawn_skill_set_' + skill, f'twcm_ui_prepare_effect = yes set_variable = {{ name = twcm_editor_spawn_{skill} value = var:twcm_editor_number }}', 'root.var:twcm_editor_number >= 0 root.var:twcm_editor_number <= 100')

# Exact values: keypad input only. No entered text is interpolated into effects or console commands.
for digit in range(10):
 sgui('twcm_editor_digit_' + str(digit), f'twcm_ui_prepare_effect = yes set_variable = {{ name = twcm_editor_number value = {{ value = var:twcm_editor_number multiply = 10 add = {digit} max = 999999 }} }}')
sgui('twcm_editor_number_clear', 'set_variable = { name = twcm_editor_number value = 0 }')
sgui('twcm_editor_number_back', 'set_variable = { name = twcm_editor_number value = { value = var:twcm_editor_number divide = 10 floor = yes } }')
for amount in [0, 1, 5, 10, 25, 50, 100, 1000, 10000]:
 sgui('twcm_editor_number_' + str(amount), f'set_variable = {{ name = twcm_editor_number value = {amount} }}')
for resource, expression in [('gold','gold'), ('prestige','prestige'), ('piety','piety')]:
 body = f'save_scope_value_as = {{ name = twcm_editor_delta value = {{ value = scope:twcm_editor_number subtract = {expression} }} }}'
 if resource == 'gold':
  body += f' if = {{ limit = {{ gold > scope:twcm_editor_number }} remove_short_term_gold = {{ value = gold subtract = scope:twcm_editor_number }} }} else = {{ add_gold = scope:twcm_editor_delta }}'
 else: body += f' add_{resource} = scope:twcm_editor_delta'
 single('exact_' + resource, 'Set ' + resource + ' to chosen number', body, group='exact',
 help_text='Set the selected character\'s ' + resource + ' balance to ' + number_text + '. Existing prestige/fame or piety/devotion progression is not reset. Native balance limits apply.')
editor_action('exact_renown', 'Set dynasty renown to chosen number', 'scope:twcm_editor_dynasty = { add_dynasty_prestige = { value = scope:twcm_editor_number subtract = dynasty_prestige } }', 'exists = scope:twcm_editor_dynasty scope:twcm_target.dynasty = scope:twcm_editor_dynasty', group='exact',
 help_text="Set [GetPlayer.MakeScope.Var('twcm_editor_dynasty').Dynasty.GetName] dynasty renown to " + number_text + '. Affects the whole dynasty; unlocked legacies remain. Apply is disabled if the selected character changes dynasty during review.')
single('exact_age', 'Set age to chosen number', 'set_age = scope:twcm_editor_number', 'scope:twcm_editor_number >= 16 scope:twcm_editor_number <= 120', group='exact',
 help_text='Set the selected character\'s age to ' + number_text + '. Requires 16–120. Family ties stay; birthday events are bypassed. Age-related health may not recalculate immediately.')
for skill in skills:
 single('exact_' + skill, 'Set base ' + skill + ' to chosen number', f'add_{skill}_skill = -1000 add_{skill}_skill = scope:twcm_editor_number force_character_skill_recalculation = yes',
 'scope:twcm_editor_number >= 0 scope:twcm_editor_number <= 100', group='exact',
 help_text='Replace the selected character\'s base ' + skill + ' with ' + number_text + ' (0–100). Trait and modifier bonuses remain, so the displayed total can be higher. Previous base edits are replaced; no undo.')
editor_action('exact_development', 'Set capital settlement size', 'scope:twcm_editor_capital_province = { change_province_size = { value = scope:twcm_editor_number subtract = province_size_level } }',
 'exists = scope:twcm_editor_capital_province scope:twcm_target = { is_landed = yes capital_province = scope:twcm_editor_capital_province } scope:twcm_editor_number >= 0 scope:twcm_editor_number <= 10', group='exact',
 help_text="Set [GetPlayer.MakeScope.Var('twcm_editor_capital_province').Province.GetName] settlement size to " + number_text + ' (0–10). Apply is disabled if the selected ruler moves their capital during review.')
sgui('twcm_editor_spawn_age_set', 'twcm_ui_prepare_effect = yes set_variable = { name = twcm_editor_spawn_age value = var:twcm_editor_number }', 'root.var:twcm_editor_number >= 18 root.var:twcm_editor_number <= 80')
for value in [0, 1]:
 sgui('twcm_editor_spawn_sex_' + str(value), f'set_variable = {{ name = twcm_editor_spawn_female value = {value} }}')
sgui('twcm_editor_select_created', 'set_variable = { name = twcm_ui_target value = var:twcm_editor_last_created } twcm_ui_prepare_effect = yes', 'has_variable = twcm_editor_last_created exists = var:twcm_editor_last_created var:twcm_editor_last_created ?= { is_alive = yes }', require_subject=False)

# Pins are explicit fixed slots, persisted on the current player ruler and never silently overwritten.
for slot in range(1, editor_pins + 1):
 field = 'twcm_editor_pin_' + str(slot)
 sgui('twcm_editor_pin_save_' + str(slot), f'set_variable = {{ name = {field} value = var:twcm_ui_target }}')
 sgui('twcm_editor_pin_select_' + str(slot), f'set_variable = {{ name = twcm_ui_target value = var:{field} }} twcm_ui_prepare_effect = yes', f'has_variable = {field} exists = var:{field} var:{field} ?= {{ is_alive = yes }}', require_subject=False)
 sgui('twcm_editor_pin_other_' + str(slot), f'set_variable = {{ name = twcm_ui_other value = var:{field} }} twcm_ui_prepare_effect = yes', f'has_variable = {field} exists = var:{field} var:{field} ?= {{ is_alive = yes }}')
 sgui('twcm_editor_pin_clear_' + str(slot), f'remove_variable = {field}')
sgui('twcm_editor_pins_clear', '\n'.join('remove_variable = twcm_editor_pin_' + str(i) for i in range(1, editor_pins+1)))
for field, iterator in [('wars', 'every_character_war'), ('artifacts', 'every_character_artifact')]:
 choice = 'twcm_war_choice' if field == 'wars' else 'twcm_artifact_choice'
 sgui('twcm_editor_refresh_' + field, f'''twcm_ui_prepare_effect = yes clear_variable_list = twcm_editor_{field}
 scope:twcm_target = {{ {iterator} = {{ save_scope_as = {choice} root = {{ add_to_variable_list = {{ name = twcm_editor_{field} target = prev }} }} }} }}''')
# Dynamic list buttons pass a native scope; they cannot substitute a text-created identifier.
sgui('twcm_editor_choose_war', 'set_variable = { name = twcm_editor_war value = scope:twcm_war_choice }', 'exists = scope:twcm_war_choice root.var:twcm_ui_target = { any_character_war = { this = scope:twcm_war_choice } }')
sgui('twcm_editor_choose_artifact', 'set_variable = { name = twcm_editor_artifact value = scope:twcm_artifact_choice }', 'exists = scope:twcm_artifact_choice scope:twcm_artifact_choice = { artifact_owner = root.var:twcm_ui_target }')

# Active, removable boosts. This does not claim to undo resources, traits lost to opposites or titles.
active_boosts = []
for modifier_id, title in [('twcm_near_instant_construction','Near-instant construction'), ('twcm_health_boost','Health boost'), ('twcm_high_fertility','High fertility'), ('twcm_low_fertility','Low fertility')]:
 active_boosts.append(single('remove_' + modifier_id, 'Remove ' + title, 'remove_character_modifier = ' + modifier_id,
 'has_character_modifier = ' + modifier_id, group='active', confirm=False, help_text='Remove this mod\'s ' + title.lower() + ' modifier from the selected character. Requires that it is active.'))
for trait, title in [('twcm_super_character','Character boost'), ('twcm_super_governor','Realm boost'), ('twcm_super_commander','Commander boost'), ('twcm_super_all','All boosts')]:
 active_boosts.append(single('remove_' + trait, 'Remove ' + title, 'remove_trait = ' + trait + '\nforce_character_skill_recalculation = yes', 'has_trait = ' + trait,
 group='active', confirm=False, help_text='Remove this preset from the selected character. Separate base skill and resource changes remain.'))

# Adjustable currency/skill controls are also searchable favourites, with their current amount.
for kind, fields, variable in [('resource',['gold','prestige','piety','renown'],'twcm_ui_step'),('skill',skills,'twcm_ui_skill_step')]:
 for field in fields:
  for sign,verb in [('plus','Add'),('minus','Subtract')]:
   name='twcm_ui_'+('skill_' if kind=='skill' else '')+field+'_'+sign
   caption=field.title()+': '+verb.lower()+" [GetPlayer.MakeScope.Var('"+variable+"').GetValue|0]"+(' base points' if kind=='skill' else '')
   entry={'id':name,'key':ui_loc('twcm_editor_quick_'+name,caption),'title':field.title()+' '+verb+' chosen amount','group':'quick','help':None}
   editor_actions[name]=entry;editor_groups.setdefault('quick',[]).append(entry)
name='twcm_ui_clear_stress'
editor_actions[name]={'id':name,'key':label('twcm_editor_quick_stress','Remove all stress'),'title':'Remove all stress','group':'quick','help':None}

exec((ROOT/'tools/ruler_tools.py').read_text(),globals())

# A shared star toggle works for every catalogued action, including legacy adapters.
for action in list(editor_actions.values()):
 field = 'twcm_fav_' + action['id']
 sgui('twcm_star_' + action['id'], f'if = {{ limit = {{ has_variable = {field} }} remove_variable = {field} }} else = {{ set_variable = {{ name = {field} value = 1 }} }}')
legacy_search_actions = []
for page, data in ui_pages.items():
 for opt in data['options']:
  if not opt['body']: continue
  title = loc[data['title']] + ' — ' + loc[opt['key']]
  entry = {'id': opt['id'], 'key': ui_loc('twcm_editor_find_'+opt['id'],title), 'title': title, 'group': 'classic', 'help': None}
  legacy_search_actions.append(entry)
  field = 'twcm_fav_' + opt['id']
  sgui('twcm_star_' + opt['id'], f'if = {{ limit = {{ has_variable = {field} }} remove_variable = {field} }} else = {{ set_variable = {{ name = {field} value = 1 }} }}')

# Separate native title picker for ownership edits; claims keep their existing beneficiary model.
label('twcm_editor_title_interaction', 'Cheat Menu: Edit a Title')
label('twcm_editor_title_interaction_desc', 'Choose a title to transfer to the selected character. No ownership changes until you review and apply a transfer in the editor.')
write('common/character_interactions/twcm_editor_interactions.txt', '''twcm_editor_title_interaction = {
 category = interaction_category_friendly common_interaction = yes interface_priority = 109 icon = vassal_claim_liege_title_interaction
 desc = twcm_editor_title_interaction_desc use_diplomatic_range = no ignores_pending_interaction_block = yes auto_accept = yes
 target_type = title target_filter = recipient_domain_titles show_all_targets = no
 can_be_picked_title = { scope:target = { tier >= tier_county is_landless_type_title = no exists = holder } }
 is_shown = { scope:actor = { is_ai = no } scope:recipient = { is_alive = yes is_landed = yes } }
 on_accept = { scope:actor = {
  set_variable = { name = twcm_editor_title value = scope:target }
  set_variable = { name = twcm_editor_title_owner value = scope:recipient }
  twcm_ui_open_effect = yes set_variable = { name = twcm_ui_page value = 630 }
 } }
 ai_will_do = { base = 0 }
}
''')
editor_meta = {'pages': [600,601,602,603,604,605,610,620,630,640,650,651,652,653,654,655,660,670,680,700,710,720,730,740],
 'traits': len(editor_traits), 'cultures': len(catalog['cultures']), 'faiths': len(catalog['faiths']),
 'innovations': len(catalog['innovations']), 'traditions': len(catalog['traditions']),
 'doctrines': sum(len(v['choices']) for v in catalog['doctrine_groups'].values()), 'tenets': len(catalog['tenets']),
 'pin_slots': editor_pins, 'actions': {k: {'group':v['group'], 'title':v['title']} for k,v in editor_actions.items()},
 'snapshot_scopes': editor_scope_fields, 'snapshot_values': editor_number_fields,
 'ruler_tools': ruler_tools_meta}

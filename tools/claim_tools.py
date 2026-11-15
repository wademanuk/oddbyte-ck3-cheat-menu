# Executed by build_cheat_mod.py. The human player owns menus; twcm_target is the claimant.
claim_title_guard='tier >= tier_county is_landless_type_title = no exists = holder holder != scope:twcm_target'
claims_effects=[]
for strength in ['pressed','unpressed']:
 # Adding an unpressed claim never replaces an existing pressed claim.
 existing=('pressed = yes' if strength=='pressed' else 'explicit = yes')
 claims_effects.append(f'''twcm_add_{strength}_claim_effect = {{
    if = {{
        limit = {{ {claim_title_guard} }}
        save_scope_as = twcm_claim_title_work
        scope:twcm_target = {{
            if = {{
                limit = {{ NOT = {{ any_claim = {{ this = scope:twcm_claim_title_work {existing} }} }} }}
                add_{strength}_claim = scope:twcm_claim_title_work
            }}
        }}
    }}
}}
''')
write('common/scripted_effects/twcm_claim_effects.txt','\n'.join(claims_effects))

event(400,'Claims and Titles','Give this character claims to titles. A claim lets them press their right to land; it does not give them the land.',[
 option('twcm_claimant_settings','Who receives portrait claims?',target=403),
 option('twcm_claim_picker_help','Choose a title or ruler',target=404),
 option('twcm_claim_liege','Claims on their liege\'s titles',target=401,trigger='exists = liege'),
 option('twcm_claim_neighbors','Claims on neighboring rulers\' titles',target=402,trigger='is_landed = yes'),
 option('twcm_claim_existing','Upgrade or remove existing claims',target=405),back(90)])
event(403,'Choose Claimant','Portrait claim tools give claims to your ruler by default. Use the selected character instead, or reset to your ruler. The choice lasts until reset or the chosen character dies.',[
 option('twcm_claim_pin','Use this character for portrait claims','set_variable = { name = twcm_claim_beneficiary value = scope:twcm_target }',target=403,raw=True),
 option('twcm_claim_reset','Use my ruler for portrait claims','remove_variable = twcm_claim_beneficiary\nsave_scope_as = twcm_target\nset_variable = { name = twcm_ui_target value = root }',target=403,raw=True),back(400)])
event(404,'Choose a Title or Ruler','Right-click a title owner. Choose Cheat Menu: Claim a Title for one title, or Claims on This Ruler for several. Then choose which claims to grant.',[
 option('twcm_claim_last_title','Last chosen title',target=420,trigger='exists = scope:twcm_claim_title'),
 option('twcm_claim_last_ruler','Last chosen ruler',target=410,trigger='exists = scope:twcm_claim_ruler scope:twcm_claim_ruler = { is_alive = yes }'),
 option('twcm_claim_close_picker','Close and choose a ruler',cancel=True),back(400)])

for page,kind in [(401,'liege'),(402,'neighbors'),(410,'ruler')]:
 if kind=='liege':
  title='Claims on Their Liege';desc='Give this character claims on their liege\'s main title or all titles that liege owns directly.'
  scope='liege';condition='exists = liege'
 elif kind=='neighbors':
  title='Claims on Neighboring Rulers';desc='Give this character claims on neighboring realm rulers\' main titles or directly owned titles. Vassal titles are excluded. Requires a landed character.'
  scope='every_neighboring_top_liege_realm_owner';condition='is_landed = yes'
 else:
  title='Claims on [twcm_claim_ruler.GetFullName]';desc='Give the selected character claims on this ruler\'s main title or directly owned titles. Vassal titles are excluded.'
  scope='scope:twcm_claim_ruler';condition='exists = scope:twcm_claim_ruler scope:twcm_claim_ruler = { is_alive = yes }'
 opts=[]
 for area in ['primary','all']:
  for strength in ['pressed','unpressed']:
   title_scope='primary_title' if area=='primary' else 'every_held_title'
   body=f'{scope} = {{ {title_scope} = {{ twcm_add_{strength}_claim_effect = yes }} }}'
   text='Grant '+strength+' claims: '+('main title'+('s' if kind=='neighbors' else '') if area=='primary' else 'all owned titles')
   tip=label(f'twcm_claim_bulk_{page}_{area}_{strength}_effect',text+'. Excludes titles the claimant already owns, baronies and landless titles. Existing pressed claims stay pressed.')
   opts.append(option(f'twcm_claim_bulk_{page}_{area}_{strength}',text,'custom_tooltip = '+tip+'\nhidden_effect = { '+body+' }',target=page,trigger=condition))
 event(page,title,desc+' Existing pressed claims stay pressed.',opts+[back(400)])

event(420,'Claim [twcm_claim_title.GetName]','Give this character a claim on [twcm_claim_title.GetName], or remove their held claim. Land stays with its current owner. Existing pressed claims stay pressed.',[
 option('twcm_claim_title_pressed','Grant pressed claim','scope:twcm_claim_title = { twcm_add_pressed_claim_effect = yes }',target=420,trigger='exists = scope:twcm_claim_title scope:twcm_claim_title = { '+claim_title_guard+' }'),
 option('twcm_claim_title_unpressed','Grant unpressed claim','scope:twcm_claim_title = { twcm_add_unpressed_claim_effect = yes }',target=420,trigger='exists = scope:twcm_claim_title scope:twcm_claim_title = { '+claim_title_guard+' }'),
 option('twcm_claim_title_remove','Remove this claim','remove_claim = scope:twcm_claim_title',target=420,trigger='exists = scope:twcm_claim_title any_claim = { explicit = yes this = scope:twcm_claim_title }'),back(400)])
event(405,'Manage Existing Claims','Make held unpressed claims pressed, or remove held claims. Automatic family and succession rights stay.',[
 bulk_option('twcm_claim_upgrade_all','Make all unpressed claims pressed','every_claim = { explicit = yes pressed = no save_scope_as = twcm_claim_upgrade_title scope:twcm_target = { add_pressed_claim = scope:twcm_claim_upgrade_title } }',target=405),
 option('twcm_claim_remove_review','Remove all held claims...',target=406),back(400)])
event(406,'Remove All Held Claims','Remove every pressed and unpressed claim this character holds. Automatic family and succession rights stay. Land is unchanged. There is no undo button.',[
 bulk_option('twcm_claim_remove_all','Remove all held claims','every_claim = { explicit = yes save_scope_as = twcm_claim_remove_title scope:twcm_target = { remove_claim = scope:twcm_claim_remove_title } }',target=405),back(405)])

prepare_claimant='''scope:actor = {
    if = {
        limit = { has_variable = twcm_claim_beneficiary exists = var:twcm_claim_beneficiary var:twcm_claim_beneficiary ?= { is_alive = yes } }
        var:twcm_claim_beneficiary = { save_scope_as = twcm_target }
    }
    else = { save_scope_as = twcm_target }
}
'''
claim_interactions=[]
for key,title,picker,event_id in [('twcm_claim_title_interaction','Cheat Menu: Claim a Title',True,420),('twcm_claim_ruler_interaction','Cheat Menu: Claims on This Ruler',False,410)]:
 label(key,title)
 label(key+'_desc','Open claim options for your ruler or your chosen claimant. Choose which claims to grant in the menu.')
 selection='''target_type = title
    target_filter = recipient_domain_titles
    show_all_targets = no
    can_be_picked_title = { scope:target = { tier >= tier_county is_landless_type_title = no exists = holder } }
''' if picker else ''
 saved='scope:target = { save_scope_as = twcm_claim_title }' if picker else 'scope:recipient = { save_scope_as = twcm_claim_ruler }'
 claim_interactions.append(f'''{key} = {{
    category = interaction_category_friendly
    common_interaction = yes
    interface_priority = {99 if picker else 98}
    icon = vassal_claim_liege_title_interaction
    desc = {key}_desc
    use_diplomatic_range = no
    ignores_pending_interaction_block = yes
    auto_accept = yes
    {selection}
    is_shown = {{ scope:actor = {{ is_ai = no }} scope:recipient = {{ is_alive = yes is_landed = yes }} }}
    on_accept = {{
        {prepare_claimant}
        {saved}
        scope:actor = {{
            set_variable = {{ name = twcm_ui_target value = scope:twcm_target }}
            {'set_variable = { name = twcm_ui_claim_title value = scope:twcm_claim_title }' if picker else 'set_variable = { name = twcm_ui_claim_ruler value = scope:twcm_claim_ruler }'}
            set_variable = {{ name = twcm_ui_page value = {event_id} }}
            twcm_ui_open_effect = yes
        }}
    }}
    ai_will_do = {{ base = 0 }}
}}
''')
write('common/character_interactions/twcm_claim_interactions.txt','\n'.join(line.rstrip() for line in '\n'.join(claim_interactions).splitlines())+'\n')
claims_meta={'main_event':400,'title_picker_event':420,'ruler_event':410,'beneficiary_variable':'twcm_claim_beneficiary','grant_effects':['twcm_add_pressed_claim_effect','twcm_add_unpressed_claim_effect'],'scope':'Selected menu subject; portrait tools use player-ruler or pinned living beneficiary. Claims do not transfer titles.'}

"""Window pages for the extended editors. All actions were registered before dispatch."""
for n in editor_meta['pages']:
 extra = ''
 if n in [640,660]:
  field = 'wars' if n == 640 else 'artifacts'
  extra = 'clear_variable_list = twcm_editor_' + field + '\nscope:twcm_target = { ' + ('every_character_war' if n == 640 else 'every_character_artifact') + ' = { root = { add_to_variable_list = { name = twcm_editor_' + field + ' target = prev } } } }'
 sgui('twcm_editor_nav_' + str(n), 'twcm_ui_prepare_effect = yes set_variable = { name = twcm_ui_page value = ' + str(n) + ' }\n' + extra)
label('twcm_editor_trait_browser_label', 'Browse all traits')
for key, text in [('tools','Tools & editors'),('pins','Pinned characters'),('search','Search'),('favourites','Favourites'),('active','Active boosts')]:
 label('twcm_editor_tab_' + key, text)
label('twcm_editor_star', '☆')
label('twcm_editor_star_on', '★')
label('twcm_editor_add', 'Add')
label('twcm_editor_remove', 'Remove')
label('twcm_editor_clear', 'Clear')
label('twcm_editor_backspace', 'Delete last digit')
label('twcm_editor_refresh', 'Refresh list')
label('twcm_editor_search_help', 'Click letters to search a word start, for example GEN, COURT or GOLD. Clear shows all choices.')
label('twcm_editor_fav_help', 'Click a star beside an action to save it here. Favourites use the names above when clicked; they do not pin a character. Normal requirements and reviews still apply.')
label('twcm_editor_active_help', 'Only removable boosts active on the selected character appear below. Resource, base-skill, age and ownership changes are not undoable here. County boosts have removal buttons in Realm & buildings.')
label('twcm_editor_pin_help', 'Save the selected character into a slot. Select edits that person; Other uses them for two-character tools. Slots are saved with your current ruler. Dead characters cannot be selected.')
label('twcm_editor_number_header', 'Chosen number: ' + number_text)
label('twcm_editor_number_help', 'Clear, then click digits to enter any whole number from 0 to 999,999. Each action shows its allowed range. Review the value and recipient before applying.')


def editor_note(key, text, h=80):
 return note(label('twcm_editor_note_' + key, text), h)


def search_box(variable='twcm_search'):
 # Generic text callbacks are not exposed to custom windows in this CK3 build.
 # A compact A-Z selector uses native string functions and never evaluates user text.
 query = label('twcm_editor_query_' + variable, "Search: [GetVariableSystem.Get('" + variable + "')]")
 content = textline(query,w=600,h=30)
 content += 'widget = { size = { 610 108 } '
 for index,letter in enumerate('abcdefghijklmnopqrstuvwxyz'):
  content += 'button_standard = { position = { ' + str((index%10)*59) + ' ' + str((index//10)*35) + ' } size = { 53 31 } text = "' + label('twcm_editor_letter_' + letter,letter.upper()) + '" onclick = "[GetVariableSystem.Set(\'' + variable + '\',Concatenate(GetVariableSystem.Get(\'' + variable + '\'),\'' + letter + '\'))]" }\n'
 content += 'button_standard = { position = { 354 70 } size = { 230 31 } text = "twcm_editor_clear" onclick = "[GetVariableSystem.Clear(\'' + variable + '\')]" } }\n'
 return content


def star(entry, x=553):
 action = entry['id']
 text = "[SelectLocalization( GetPlayer.MakeScope.Var('twcm_fav_" + action + "').IsSet, 'twcm_editor_star_on', 'twcm_editor_star' )]"
 return button('star_' + action, text, 'twcm_star_' + action, x, 0, 44, 36,
 tooltip=label('twcm_star_help', 'Save or remove this action in Favourites.'))


def action_row(entry, favourite=False, search=False):
 conditions = []
 if favourite:
  conditions.append("GetPlayer.MakeScope.Var('twcm_fav_" + entry['id'] + "').IsSet")
 if search:
  conditions.append(search_expression(entry['title']))
 visible = conditions[0] if len(conditions) == 1 else ('And( ' + ', '.join(conditions) + ' )' if conditions else None)
 return 'widget = { size = { 610 39 } ' + ('visible = "[' + visible + ']" ' if visible else '') + button('action_' + entry['id'], entry['key'], entry['id'], 0, 0, 542, 36) + star(entry) + '}\n'


def group_rows(group, search=False):
 return ''.join(action_row(e, search=search) for e in editor_groups.get(group, []))


def link(page, text):
 key='twcm_editor_link_'+str(page)+'_'+re.sub(r'\W+','_',text).strip('_').lower()
 return button(key, label(key, text), 'twcm_editor_nav_' + str(page))


def add_page(page, title, content):
 editor_pages[page] = {'title': title, 'content': content}
 rendered_pages.append('''widget = {
 name = "twcm_page_''' + str(page) + '''" position = { 204 150 } size = { 650 510 }
 visible = "[EqualTo_CFixedPoint( GetPlayer.MakeScope.Var('twcm_ui_page').GetValue, '(CFixedPoint)''' + str(page) + '''' )]"
 ''' + textline(label('twcm_editor_page_' + str(page), title), 0, 0, 625, 25, 42) + flow(content) + '}\n')


hub = editor_note('hub','Choose a focused editor. Use Selected character and Other character above for two-person tools. Large changes open a review before they happen.',70)
for dest, title in [(601,'Browse all traits'),(605,'Set exact values'),(610,'Court and prisoners'),(620,'Family and dynasty'),(630,'Titles, vassals and contracts'),(640,'Wars and truces'),(650,'Culture picker'),(651,'Faith picker'),(652,'Discover innovations'),(653,'Culture traditions'),(654,'Rite doctrines'),(655,'Rite tenets'),(660,'Artifacts'),(670,'Create a character')]:
 hub += link(dest, title)
add_page(600,'Tools & editors',hub)

# Trait filters use their native categories. Each row shows actual ownership and optional XP tracks.
trait_content = note('twcm_editor_search_help',45) + search_box('twcm_trait_search')
trait_content += 'widget = { size = { 610 142 } '
for filter_index,(category, caption) in enumerate([('all','All'),('active','Active'),('education','Education'),('personality','Personality'),('inherited','Inherited'),('commander','Commander'),('lifestyle','Lifestyle'),('health','Health'),('other','Other')]):
 sgui('twcm_editor_trait_filter_' + category, '')  # UI-only category: no gameplay mutation.
 # VariableSystem filters are local presentation state, not saved character changes.
 trait_content += 'button_standard = { position = { ' + str((filter_index%3)*198) + ' ' + str((filter_index//3)*34) + ' } size = { 190 30 } text = "' + label('twcm_editor_filter_' + category, caption) + '" onclick = "[GetVariableSystem.Set(\'twcm_trait_filter\',\'' + category + '\')]" }\n'
trait_content += '}\n'
for trait, entry in sorted(editor_traits.items(), key=lambda item:item[1]['title'].casefold()):
 active = subject + ".HasTrait( GetTrait('" + trait + "') )"
 filter_expr = "Or( Or( StringIsEmpty(GetVariableSystem.Get('twcm_trait_filter')), GetVariableSystem.HasValue('twcm_trait_filter','all') ), Or( GetVariableSystem.HasValue('twcm_trait_filter','" + entry['category'] + "'), And(GetVariableSystem.HasValue('twcm_trait_filter','active'), " + active + ') ) )'
 visible = 'And( ' + search_expression(entry['title'] + ' ' + trait, 'twcm_trait_search') + ', ' + filter_expr + ' )'
 row = textline("[GetTrait('" + trait + "').GetNameNoTooltip(" + subject + ')]', 0, 0, 350, 18, 34)
 row += button('trait_add_' + trait, 'twcm_editor_add', entry['add']['id'], 352, 0, 78, 34)
 row += button('trait_remove_' + trait, 'twcm_editor_remove', entry['remove']['id'], 438, 0, 105, 34)
 row += star(entry['add'])
 row += textline("[SelectLocalization( " + active + ", 'twcm_editor_owned', 'twcm_editor_missing' )]", 0, 34, 540, 14, 25)
 for i, xp in enumerate(entry['xp']):
  row += button('trait_xp_' + trait + str(i),xp['key'],xp['id'],0,62+i*36,542,32)
 trait_content += 'widget = { size = { 610 ' + str(64+36*len(entry['xp'])) + ' } visible = "[' + visible + ']" ' + row + '}\n'
label('twcm_editor_owned','Active on selected character')
label('twcm_editor_missing','Not on selected character')
add_page(601,'All traits',trait_content)

pins = note('twcm_editor_pin_help',92)
for slot in range(1,editor_pins+1):
 field = 'twcm_editor_pin_' + str(slot)
 has = "GetPlayer.MakeScope.Var('" + field + "').IsSet"
 title = label('twcm_editor_pin_name_' + str(slot), str(slot) + ": [GetPlayer.MakeScope.Var('" + field + "').Char.GetFullName]")
 name_widget = 'widget = { size = { 610 30 } visible = "[' + has + ']" ' + textline(title,0,0,600,18,28) + '}\n'
 name_widget += 'widget = { size = { 610 30 } visible = "[Not(' + has + ')]" ' + textline(label('twcm_editor_pin_empty_' + str(slot),str(slot)+': Empty'),0,0,600,18,28) + '}\n'
 pins += name_widget + 'widget = { size = { 610 40 } '
 for index,(suffix,caption) in enumerate([('save','Save selected'),('select','Select'),('other','Other'),('clear','Clear')]):
  pins += button('pin_' + suffix + str(slot), label('twcm_editor_pin_button_' + suffix,caption), 'twcm_editor_pin_' + suffix + '_' + str(slot),index*150,0,140,34)
 pins += '}\n'
pins += button('clear_pins',label('twcm_editor_clear_pins','Clear all pins'),'twcm_editor_pins_clear')
add_page(602,'Pinned characters',pins)

# Full action lists retain their real guards, confirmation snapshots and target model.
all_entries = list(editor_actions.values()) + legacy_search_actions
favourites = note('twcm_editor_fav_help',84) + ''.join(action_row(e,favourite=True) for e in all_entries)
add_page(603,'Favourites',favourites)
search = link(603,'Open favourites') + note('twcm_editor_search_help',66) + search_box()
search += editor_note('search_names','Search covers action names and trait names. Traits and world editors also have their own filtered lists.',50)
search += ''.join(action_row(e,search=True) for e in sorted(all_entries,key=lambda e:e['title'].casefold()))
add_page(680,'Search actions',search)

active = note('twcm_editor_active_help',105)
for entry in active_boosts:
 active += 'widget = { size = { 610 39 } visible = "' + ui_expr(entry['id'],'IsValid') + '" ' + button('active_' + entry['id'],entry['key'],entry['id']) + '}\n'
active += link(601,'Browse current traits') + link(70,'County boosts and buildings')
# County navigation is an existing page, not an extended editor page.
active = active.replace("GetScriptedGui( 'twcm_editor_nav_70' )", "GetScriptedGui( 'twcm_ui_nav_70' )")
add_page(604,'Active boosts',active)

keypad = textline('twcm_editor_number_header',size=24,h=42)+note('twcm_editor_number_help',68)
keypad += 'widget = { size = { 610 82 } '
for digit in range(10):
 keypad += button('number_digit_' + str(digit), label('twcm_editor_digit_label_' + str(digit),str(digit)), 'twcm_editor_digit_' + str(digit), (digit%5)*118, (digit//5)*40,108,34)
keypad += '}\nwidget = { size = { 610 40 } ' + button('number_clear','twcm_editor_clear','twcm_editor_number_clear',0,0,280,34) + button('number_back','twcm_editor_backspace','twcm_editor_number_back',300,0,280,34) + '}\n'
keypad += editor_note('number_quick','Quick values:',28)
keypad += 'widget = { size = { 610 72 } '
for index,amount in enumerate([0,1,5,10,25,50,100,1000,10000]):
 keypad += button('number_quick_' + str(amount), label('twcm_editor_quick_' + str(amount),str(amount)), 'twcm_editor_number_' + str(amount),(index%5)*118,(index//5)*36,108,32)
keypad += '}\n'
add_page(605,'Set exact values',keypad + group_rows('exact'))
add_page(610,'Court and prisoners',editor_note('court','Selected character is the ruler or jailer. Other character is the person to recruit, appoint, imprison or release. Choose Other by portrait or from Pinned characters.',84)+group_rows('court'))
add_page(620,'Family and dynasty',editor_note('family','These tools act on the two named characters. Marriage, adoption and dynasty changes can alter inheritance. Read the review before applying.',75)+group_rows('family'))
add_page(630,'Titles and vassals',editor_note('titles','Right-click a title owner > Cheat Menu: Edit a Title. Pick a county-or-higher title, then review a transfer here. These buttons change actual ownership; the existing claim tools remain separate.',104)+textline(label('twcm_editor_chosen_title','Chosen title: '+title_text),h=42)+group_rows('titles')+editor_note('contracts','Contracts below belong to the selected feudal vassal and their own liege. Other character is not used.',60)+group_rows('contracts'))


def choice_list(kind):
 singular = 'war' if kind == 'wars' else 'artifact'
 promote = 'War' if singular == 'war' else 'Artifact'
 context = "GuiScope.SetRoot(GetPlayer.MakeScope).AddScope('twcm_" + singular + "_choice', Scope." + promote + '.MakeScope).End'
 action = 'twcm_editor_choose_' + singular
 return 'vbox = { datamodel = "[GetPlayer.MakeScope.GetList(\'twcm_editor_' + kind + '\')]" spacing = 5 item = { button_standard = { size = { 600 36 } text = "[Scope.' + promote + '.GetName]" onclick = "[GetScriptedGui(\'' + action + '\').Execute(' + context + ')]" enabled = "[GetScriptedGui(\'' + action + '\').IsValid(' + context + ')]" } } }\n'

wars = editor_note('wars','Choose one of the selected character\'s active wars below. Win and Lose refer to their side, including when they are an ally. Outcomes run the normal war settlement.',87)
wars += button('refresh_wars','twcm_editor_refresh','twcm_editor_refresh_wars')+choice_list('wars')
wars += textline(label('twcm_editor_war_selected','Chosen war: '+war_text),h=42)+group_rows('wars')
add_page(640,'Wars and truces',wars)
for page, title, group in [(650,'Choose culture','cultures'),(651,'Choose faith','faiths'),(652,'Discover innovations','innovations'),(653,'Culture traditions','traditions'),(654,'Rite doctrines','doctrines'),(655,'Rite tenets','tenets')]:
 scope_text = 'Only the selected character changes.' if group in ['cultures','faiths'] else ('Shared culture: '+culture_text+'. Everyone of this culture is affected.' if group in ['innovations','traditions'] else 'Rite: '+rite_text+'. Followers of this rite are affected; other rites keep their own rules.')
 content = editor_note('scope_'+group,scope_text,76)+note('twcm_editor_search_help',68)+search_box()
 if group=='cultures':content+=group_rows('culture_match')
 if group=='faiths':content+=group_rows('faith_match')
 if group=='innovations':content+=group_rows('innovation_bulk')
 if group=='tenets':
  content+=editor_note('tenet_current','Current core tenets: remove one to make room before adding a replacement.',54)
  for entry in editor_groups['tenets']:
   if '_remove_' in entry['id']:
    content+='widget = { size = { 610 39 } visible = \"'+ui_expr(entry['id'],'IsValid')+'\" '+button('current_'+entry['id'],entry['key'],entry['id'])+' }\n'
  content+=textline(label('twcm_editor_tenet_choices','All tenet choices'),size=22,h=36)
 content+=group_rows(group,search=True)
 add_page(page,title,content)
artifacts = editor_note('artifacts','Choose an owned artifact to repair, improve or give away. Creation below makes a new item in the selected character\'s inventory. Equipment and DLC rules still apply.',90)
artifacts += button('refresh_artifacts','twcm_editor_refresh','twcm_editor_refresh_artifacts')+choice_list('artifacts')
artifacts += textline(label('twcm_editor_artifact_selected','Chosen artifact: '+artifact_text),h=42)+group_rows('artifacts')
artifacts += textline(label('twcm_editor_artifact_create_heading','Create an artifact'),size=22,h=36)+group_rows('artifact_create')
add_page(660,'Artifacts',artifacts)
spawn = editor_note('spawn','Create one new person at the selected ruler\'s court. Choose their age, sex and all six base skills below. They share the ruler\'s faith and culture and are not automatically appointed.',105)
spawn += textline(label('twcm_editor_spawn_values',"Age: [GetPlayer.MakeScope.Var('twcm_editor_spawn_age').GetValue|0]   Chosen number: "+number_text),h=36)
spawn += keypad
for skill in skills:
 spawn += textline(label('twcm_editor_spawn_current_' + skill,skill.title() + ": [GetPlayer.MakeScope.Var('twcm_editor_spawn_" + skill + "').GetValue|0]"),h=28)
 spawn += button('spawn_set_' + skill,label('twcm_editor_spawn_set_' + skill,'Set base ' + skill + ' to chosen number'),'twcm_editor_spawn_skill_set_' + skill)
spawn += button('spawn_age_set',label('twcm_editor_spawn_age_set_label','Use chosen number as age (18–80)'),'twcm_editor_spawn_age_set')
for value, title in [(0,'Male'),(1,'Female')]:
 spawn += button('spawn_sex_' + str(value),label('twcm_editor_spawn_sex_label_' + str(value),title),'twcm_editor_spawn_sex_' + str(value),down="[EqualTo_CFixedPoint(GetPlayer.MakeScope.Var('twcm_editor_spawn_female').GetValue,'(CFixedPoint)" + str(value) + "')]")
spawn += group_rows('spawn')+button('select_created',label('twcm_editor_select_created_label','Select the last created character'),'twcm_editor_select_created')
add_page(670,'Create a character',spawn)

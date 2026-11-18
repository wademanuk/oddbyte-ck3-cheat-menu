"""Native Jomini window and ScriptedGui adapters for every legacy event action."""
# Executed inside build_cheat_mod.py after all event menus have been constructed.
import copy
from pdx_script import parse,dump,get,Entry,walk

ui_sguis=[];ui_actions={};ui_pending={};ui_pages={};ui_option_ids={}
confirmation_revision=int(''.join(part.zfill(2) for part in VERSION.split('.')))
confirmation_guard=f'has_variable = twcm_ui_pending_revision var:twcm_ui_pending_revision = {confirmation_revision}'
player="GetPlayer"
subject="GetPlayer.MakeScope.Var('twcm_ui_target').Char"
other="GetPlayer.MakeScope.Var('twcm_ui_other').Char"
gui_context='GuiScope.SetRoot( GetPlayer.MakeScope ).End'

prepare='''twcm_ui_prepare_effect = {
    save_scope_as = twcm_view_player
    if = { limit = { NOT = { has_variable = twcm_ui_target } } set_variable = { name = twcm_ui_target value = this } }
    else_if = { limit = { NOT = { exists = var:twcm_ui_target } } set_variable = { name = twcm_ui_target value = this } }
    else_if = { limit = { var:twcm_ui_target = { is_alive = no } } set_variable = { name = twcm_ui_target value = this } }
    if = { limit = { NOT = { has_variable = twcm_ui_other } } set_variable = { name = twcm_ui_other value = this } }
    else_if = { limit = { NOT = { exists = var:twcm_ui_other } } set_variable = { name = twcm_ui_other value = this } }
    else_if = { limit = { var:twcm_ui_other = { is_alive = no } } set_variable = { name = twcm_ui_other value = this } }
    if = { limit = { NOT = { has_variable = twcm_ui_page } } set_variable = { name = twcm_ui_page value = 10 } }
    if = { limit = { NOT = { has_variable = twcm_ui_step } } set_variable = { name = twcm_ui_step value = 1000 } }
    if = { limit = { NOT = { has_variable = twcm_ui_skill_step } } set_variable = { name = twcm_ui_skill_step value = 1 } }
    var:twcm_ui_target = { save_scope_as = twcm_target }
    var:twcm_ui_other = { save_scope_as = twcm_other }
    if = { limit = { has_variable = twcm_ui_claim_title exists = var:twcm_ui_claim_title } var:twcm_ui_claim_title = { save_scope_as = twcm_claim_title } }
    else = { remove_variable = twcm_ui_claim_title }
    if = { limit = { has_variable = twcm_ui_claim_ruler exists = var:twcm_ui_claim_ruler } var:twcm_ui_claim_ruler = { save_scope_as = twcm_claim_ruler } }
    else = { remove_variable = twcm_ui_claim_ruler }
}
twcm_ui_open_effect = {
    twcm_ui_prepare_effect = yes
    set_variable = { name = twcm_ui_open value = 1 }
}
'''
write('common/scripted_effects/twcm_window_effects.txt',prepare)
write('common/script_values/twcm_window_values.txt','twcm_ui_stress_value = { value = stress }\n')

def ui_expr(name,method='Execute'):
 context="GuiScope.AddScope('twcm_view_player',GetPlayer.MakeScope).End" if name in ['twcm_ui_visible','twcm_ui_modal_visible'] else gui_context
 return f"[GetScriptedGui( '{name}' ).{method}( {context} )]"
def rewrite_trigger(text):
 fields=[('scope:twcm_target','root.var:twcm_ui_target'),('scope:twcm_other','root.var:twcm_ui_other'),('scope:twcm_claim_title','root.var:twcm_ui_claim_title'),('scope:twcm_claim_ruler','root.var:twcm_ui_claim_ruler')]
 fields += [('scope:twcm_editor_'+f, 'root.var:twcm_editor_'+f) for f in globals().get('editor_scope_fields',[]) + globals().get('editor_number_fields',[])]
 for old,new in fields:
  text=re.sub(re.escape(old)+r'\b',new,text)
 return text
def ui_loc(key,value):
 value=value.replace('[twcm_target.GetFullName]',f'[{subject}.GetFullName]').replace('[twcm_target.GetAge]',f'[{subject}.GetAge]')
 value=value.replace('[twcm_other.GetFullName]',f'[{other}.GetFullName]')
 value=value.replace('[twcm_claim_title.GetName]',"[GetPlayer.MakeScope.Var('twcm_ui_claim_title').Title.GetName]")
 value=value.replace('[twcm_claim_ruler.GetFullName]',"[GetPlayer.MakeScope.Var('twcm_ui_claim_ruler').Char.GetFullName]")
 return label(key,value)
def sgui(name,effect='',trigger='',shown=None,require_subject=True,allow_pending=False,global_scope=False):
 label('twcm_ui_finish_review','Finish or cancel the current review first.')
 label('twcm_ui_select_living','Select a living character first.')
 valid='always = yes' if global_scope else 'is_ai = no '+('custom_tooltip = { text = twcm_ui_finish_review NOT = { has_variable = twcm_ui_pending } } ' if not allow_pending else '')+('custom_tooltip = { text = twcm_ui_select_living has_variable = twcm_ui_target exists = var:twcm_ui_target var:twcm_ui_target ?= { is_alive = yes } } ' if require_subject else '')+rewrite_trigger(trigger)
 ui_sguis.append(f'''{name} = {{
    {'' if global_scope else 'scope = character'}
    is_shown = {{ {shown if shown is not None else 'is_ai = no'} }}
    is_valid = {{ {valid} }}
    effect = {{ {effect} }}
}}
''')
def register(name,body,trigger='',page=None,confirm=False,description=None):
 action={'body':body,'trigger':trigger,'page':page,'confirm':confirm}
 ui_actions[name]=action
 guarded=f'if = {{ limit = {{ {trigger or "always = yes"} }}\n{body}\n}}'
 if page is not None:guarded+=f'\nset_variable = {{ name = twcm_ui_page value = {page} }}'
 if confirm:
  ident=len(ui_pending)+1
  ui_pending[ident]={'name':name,**action,'description':description or 'twcm_ui_confirm_desc'}
  snapshot=f'''remove_variable = twcm_ui_pending_title
remove_variable = twcm_ui_pending_ruler
twcm_ui_prepare_effect = yes
set_variable = {{ name = twcm_ui_pending value = {ident} }}
set_variable = {{ name = twcm_ui_pending_revision value = {confirmation_revision} }}
set_variable = {{ name = twcm_ui_pending_target value = var:twcm_ui_target }}
set_variable = {{ name = twcm_ui_pending_other value = var:twcm_ui_other }}
if = {{ limit = {{ has_variable = twcm_ui_claim_title exists = var:twcm_ui_claim_title }} set_variable = {{ name = twcm_ui_pending_title value = var:twcm_ui_claim_title }} }}
if = {{ limit = {{ has_variable = twcm_ui_claim_ruler exists = var:twcm_ui_claim_ruler }} set_variable = {{ name = twcm_ui_pending_ruler value = var:twcm_ui_claim_ruler }} }}'''
  for field in globals().get('editor_scope_fields',[]) + globals().get('editor_number_fields',[]):
   snapshot+=f'\nremove_variable = twcm_ui_pending_editor_{field}\nif = {{ limit = {{ has_variable = twcm_editor_{field} }} set_variable = {{ name = twcm_ui_pending_editor_{field} value = var:twcm_editor_{field} }} }}'
  sgui(name,snapshot,trigger)
 else:sgui(name,'twcm_ui_prepare_effect = yes\n'+guarded,trigger)
 return name

sgui('twcm_ui_visible',shown='exists = scope:twcm_view_player scope:twcm_view_player ?= { has_variable = twcm_ui_open var:twcm_ui_open = 1 }',global_scope=True)
sgui('twcm_ui_modal_visible',shown='exists = scope:twcm_view_player scope:twcm_view_player ?= { has_variable = twcm_ui_pending }',global_scope=True)
sgui('twcm_ui_open','twcm_ui_open_effect = yes',require_subject=False)
sgui('twcm_ui_close','remove_variable = twcm_ui_open remove_variable = twcm_ui_pending',require_subject=False,allow_pending=True)
sgui('twcm_ui_cancel','remove_variable = twcm_ui_pending',require_subject=False,allow_pending=True)
sgui('twcm_ui_self','set_variable = { name = twcm_ui_target value = root } twcm_ui_prepare_effect = yes',require_subject=False)
sgui('twcm_ui_legacy','twcm_ui_prepare_effect = yes remove_variable = twcm_ui_open trigger_event = { id = twcm.0001 }')
for n in [10,20,30,50,60,91,97,70,80,400,500]:
 sgui(f'twcm_ui_nav_{n}',f'twcm_ui_prepare_effect = yes set_variable = {{ name = twcm_ui_page value = {n} }}')

def page_help(text):
 return re.sub(r'^Editing: .*?\. ','',text)

def confirmation_copy(number,key,title,description):
 action=loc[key]
 detail=page_help(description)
 if number in range(310,324):
  return title+'\n\n'+detail
 if number==97:
  if key=='twcm_family_remove':detail='Remove Character, Realm and Commander boosts from this character, living close family and spouses. Other traits and separate skill edits stay.'
  else:
   preset=key.removeprefix('twcm_family_')
   page=next(n for trait,_,_,_,n in presets if trait==preset)
   detail=page_help(loc[f'twcm_{page}_desc']).split(' Remove to end')[0]
   detail+=' Applies to this character, living close family and spouses. Future family members are excluded.'
 elif number in [350,351]:
  kind={'faith':'faith','culture':'culture','both':'faith and culture'}[key.rsplit('_',1)[-1]]
  area='all their counties and vassals' if number==351 else 'directly owned counties only'
  detail=f'Match this character\'s {kind} in {area}. There is no undo button.'
 elif number==99 and key=='twcm_family_immortal_off':
  detail='Remove the Immortal trait from this character, living close family and spouses.'
 elif number==98:
  detail={
   'twcm_heal_diseases':'Cure diseases, wounds and common ailments in this character. Future illness is still possible.',
   'twcm_heal_genetic':'Remove harmful inherited traits, including Inbred, from this character. Giant stays.',
   'twcm_heal_everything':'Cure diseases and common ailments, and remove harmful inherited traits. Giant stays. Future illness is still possible.',
   'twcm_heal_family':'Cure diseases, common ailments and harmful inherited traits in this character, living close family and spouses. Giant stays. Future illness is still possible.',
  }[key]
 return action+'\n\n'+detail

# Preserve every option's real effect and condition; replace event navigation with page state.
for source in events:
 entry=parse(source)[0];n=int(entry.key.split('.')[1]);options=[e.value for e in entry.value if e.key=='option']
 ui_pages[n]={'title':get(entry.value,'title'),'description':get(entry.value,'desc'),'options':[]}
 for index,entries in enumerate(options):
  key=get(entries,'name');trigger=dump(get(entries,'trigger',[]));nav=None;body=[]
  for e in entries:
   if e.key in ['name','trigger','is_cancel_option']:continue
   if e.key=='hidden_effect' and isinstance(e.value,list) and len(e.value)==1 and e.value[0].key=='trigger_event':
    event_id=get(e.value[0].value,'id')
    if event_id and event_id.startswith('twcm.'):
     nav=int(event_id.split('.')[1]);continue
   body.append(e)
  name=f'twcm_ui_{n}_{index}'
  action_text=dump(body)
  # All short-lived scopes used by actions have been restored by prepare_effect.
  confirmation=n in [97,98,99,350,351,406] or 310<=n<=323
  if not body and nav is None:action_text='remove_variable = twcm_ui_open'
  description=None
  if confirmation and body:
   description_text=confirmation_copy(n,key,loc[get(entry.value,'title')],loc[get(entry.value,'desc')])
   description=ui_loc(f'twcm_ui_confirm_desc_{n}_{index}',description_text)
   loc[description]=loc[description].replace('twcm_ui_target','twcm_ui_pending_target').replace('twcm_ui_other','twcm_ui_pending_other').replace('twcm_ui_claim_title','twcm_ui_pending_title').replace('twcm_ui_claim_ruler','twcm_ui_pending_ruler')
  register(name,action_text,trigger,nav,confirm=confirmation and bool(body),description=description)
  ui_pages[n]['options'].append({'id':name,'key':key,'nav':nav,'body':bool(body)})
  ui_option_ids.setdefault(key,[]).append(name)

# In-place resource and skill controls use an explicit increment, independent of menu paging.
for step in [100,1000,10000,100000]:sgui(f'twcm_ui_step_{step}',f'set_variable = {{ name = twcm_ui_step value = {step} }}')
for step in [1,5,10]:sgui(f'twcm_ui_skill_step_{step}',f'set_variable = {{ name = twcm_ui_skill_step value = {step} }}')
for resource in ['gold','prestige','piety','renown']:
 for sign in [-1,1]:
  value='root.var:twcm_ui_step' if sign==1 else '{ value = root.var:twcm_ui_step multiply = -1 }'
  body=f'add_{resource} = {value}' if resource!='renown' else f'dynasty = {{ add_dynasty_prestige = {value} }}'
  if resource=='gold' and sign==-1:body='remove_short_term_gold = root.var:twcm_ui_step'
  register(f'twcm_ui_{resource}_{"plus" if sign>0 else "minus"}','scope:twcm_target = { '+body+' }', 'scope:twcm_target = { exists = dynasty }' if resource=='renown' else '')
for skill in skills:
 for sign in [-1,1]:
  value='root.var:twcm_ui_skill_step' if sign==1 else '{ value = root.var:twcm_ui_skill_step multiply = -1 }'
  register(f'twcm_ui_skill_{skill}_{"plus" if sign>0 else "minus"}',f'scope:twcm_target = {{ add_{skill}_skill = {value} force_character_skill_recalculation = yes }}')

register('twcm_ui_clear_stress','scope:twcm_target = { add_stress = -1000 }')
legacy_confirmation_count=len(ui_pending)
exec((ROOT/'tools/editor_actions.py').read_text(),globals())

# Confirmation snapshots are independent of subsequent selection changes.
confirm_branches=[]
for ident,action in ui_pending.items():
 body=action['body']
 guarded=f'if = {{ limit = {{ {action["trigger"] or "always = yes"} }}\n{body}\n}}'
 if action['page'] is not None:guarded+=f'\nset_variable = {{ name = twcm_ui_page value = {action["page"]} }}'
 confirm_branches.append(f'''if = {{
 limit = {{ var:twcm_ui_pending = {ident} }}
 {guarded}
}}''')
pending_guard='has_variable = twcm_ui_pending '+confirmation_guard+' has_variable = twcm_ui_pending_target exists = var:twcm_ui_pending_target var:twcm_ui_pending_target ?= { is_alive = yes }'
confirm_effect='''if = {
 limit = { '''+pending_guard+''' }
 var:twcm_ui_pending_target = { save_scope_as = twcm_target }
 if = { limit = { exists = var:twcm_ui_pending_other } var:twcm_ui_pending_other = { save_scope_as = twcm_other } }
 if = { limit = { has_variable = twcm_ui_pending_title exists = var:twcm_ui_pending_title } var:twcm_ui_pending_title = { save_scope_as = twcm_claim_title } }
 if = { limit = { has_variable = twcm_ui_pending_ruler exists = var:twcm_ui_pending_ruler } var:twcm_ui_pending_ruler = { save_scope_as = twcm_claim_ruler } }
'''
for field in editor_scope_fields:
 confirm_effect+=f'if = {{ limit = {{ has_variable = twcm_ui_pending_editor_{field} exists = var:twcm_ui_pending_editor_{field} }} var:twcm_ui_pending_editor_{field} = {{ save_scope_as = twcm_editor_{field} }} }}\n'
for field in editor_number_fields:
 confirm_effect+=f'if = {{ limit = {{ has_variable = twcm_ui_pending_editor_{field} }} save_scope_value_as = {{ name = twcm_editor_{field} value = var:twcm_ui_pending_editor_{field} }} }}\n'
confirm_effect+='\n'.join(confirm_branches)+'\n}\nremove_variable = twcm_ui_pending'
pending_valid=[f'AND = {{ var:twcm_ui_pending >= 1 var:twcm_ui_pending <= {legacy_confirmation_count} }}']
for ident,action in ui_pending.items():
 if ident<=legacy_confirmation_count:continue
 trigger=rewrite_trigger(action['trigger'])
 trigger=re.sub(r'text = twcm_editor_\w+_requirements', 'text = '+action['description'], trigger)
 for normal,snapshot in [('twcm_ui_target','twcm_ui_pending_target'),('twcm_ui_other','twcm_ui_pending_other')]+[('twcm_editor_'+f,'twcm_ui_pending_editor_'+f) for f in editor_scope_fields+editor_number_fields]:
  trigger=re.sub(r'root\.var:'+re.escape(normal)+r'\b','root.var:'+snapshot,trigger)
 pending_valid.append(f'AND = {{ var:twcm_ui_pending = {ident} {trigger} }}')
sgui('twcm_ui_confirm',confirm_effect,trigger=pending_guard+' OR = { '+'\n'.join(pending_valid)+' }',require_subject=False,allow_pending=True)

def button(name,text,action,x=0,y=0,w=600,h=38,down=None,tooltip=None):
 hint=tooltip
 if not hint and action in ui_actions:
  # Plain explanations when usable; native localized requirements when unavailable.
  key=editor_actions.get(action,{}).get('help') or text
  hint=f"[Select_CString(GetScriptedGui('{action}').IsValid({gui_context}),Localize('{key}'),GetScriptedGui('{action}').IsValidTooltip({gui_context}))]"
 hover=f' tooltip = "{hint}"\n' if hint else ''
 return f'''button_standard = {{
 name = "{name}" position = {{ {x} {y} }} size = {{ {w} {h} }}
 text = "{text}"
 onclick = "{ui_expr(action)}"
 enabled = "{ui_expr(action,'IsValid')}"
{hover} {('down = "'+down+'"') if down else ''}
}}
'''
def textline(key,x=0,y=0,w=600,size=18,h=32):
 return f'text_single = {{ position = {{ {x} {y} }} size = {{ {w} {h} }} text = "{key}" fontsize = {size} max_width = {w} }}\n'
def note(key,h=78,w=610):
 return f'text_multi = {{ size = {{ {w} {h} }} text = "{key}" fontsize = 16 }}\n'
def option_button(opt,n,label_override=None):
 name=opt['id'];label_key=label_override or opt['key']
 return button(name+'_button',label_key,name)
def actions_for(n,skip_nav=True):
 return ''.join(option_button(o,n) for o in ui_pages[n]['options'] if not(skip_nav and not o['body']))
def flow(content):
 return '''scrollbox = { position = { 0 50 } size = { 640 460 }
 blockoverride "scrollbox_content" { vbox = { layoutpolicy_horizontal = expanding spacing = 7
'''+content+'\n} } }\n'
def short_description(n):
 # The selected name is already in the persistent header.
 s=loc[ui_pages[n]['description']]
 s=re.sub(r'^Editing: .*?\. ','',s)
 return ui_loc(f'twcm_ui_short_{n}',s)

label('twcm_ui_title',NAME)
label('twcm_ui_open_button','Cheats')
label('twcm_ui_close_label','Close')
label('twcm_ui_legacy_label','Classic menu')
label('twcm_ui_me_label','My ruler')
label('twcm_ui_actor_label','Selected character')
label('twcm_ui_other_label','Other character')
label('twcm_ui_footer','v'+VERSION+' • Check the names above before applying cheats')
label('twcm_ui_confirm_title','Confirm cheat')
label('twcm_ui_confirm_desc','Apply this cheat to the character named above?')
label('twcm_ui_confirm_apply','Apply cheat')
label('twcm_ui_confirm_cancel','Cancel')
label('twcm_ui_step','Amount per click')
label('twcm_ui_skill_step_label','Points per click')
label('twcm_ui_plus','+')
label('twcm_ui_minus','−')
label('twcm_ui_resources','Resources')
label('twcm_ui_character','Character')
label('twcm_ui_claims','Claims & titles')
label('twcm_ui_realm','Realm & buildings')
label('twcm_ui_military','Military')
label('twcm_ui_diplomacy','Diplomacy')
label('twcm_ui_character_help','Use + or - to change base skills. Totals may refresh when time advances. More character cheats are below.')
label('twcm_ui_diplomacy_help','Cheats act between the two characters above. To change the other character, right-click their portrait and choose Cheat Menu: Set Other Character.')
label('twcm_ui_selected_name',f'[{subject}.GetFullName]  ·  [{subject}.GetAge]')
label('twcm_ui_other_name',f'[{other}.GetFullName]')
label('twcm_ui_pending_name',"[GetPlayer.MakeScope.Var('twcm_ui_pending_target').Char.GetFullName]")
label('twcm_ui_dip_current',f"Other's opinion: [{other}.GetOpinionOf( {subject} )|0]     Selected character's opinion: [{subject}.GetOpinionOf( {other} )|0]")

resource_step="GetPlayer.MakeScope.Var('twcm_ui_step').GetValue"
skill_step="GetPlayer.MakeScope.Var('twcm_ui_skill_step').GetValue"
for resource in ['gold','prestige','piety','renown']:
 for sign in ['plus','minus']:
  verb='Add' if sign=='plus' else 'Subtract'
  recipient=f"[{subject}.GetFullName]"+("'s dynasty" if resource=='renown' else '')
  label(f'twcm_ui_{resource}_{sign}_tip',f'{verb} [{resource_step}|0] {resource} '+('to ' if sign=='plus' else 'from ')+recipient+'.')
for skill in skills:
 for sign in ['plus','minus']:
  verb='Add' if sign=='plus' else 'Subtract'
  label(f'twcm_ui_skill_{skill}_{sign}_tip',f'{verb} [{skill_step}|0] base {skill} '+('to ' if sign=='plus' else 'from ')+f'[{subject}.GetFullName].')

rendered_pages=[]
for n,data in ui_pages.items():
 title_key=ui_loc(f'twcm_ui_title_{n}',loc[data['title']])
 content=''
 if n==10:
  step_buttons=''
  for i,step in enumerate([100,1000,10000,100000]):
   k=label(f'twcm_ui_step_label_{step}',f'{step:,}')
   step_buttons+=button(f'step_{step}',k,f'twcm_ui_step_{step}',i*145,0,136,34,down=f"[EqualTo_CFixedPoint( GetPlayer.MakeScope.Var('twcm_ui_step').GetValue, '(CFixedPoint){step}' )]")
  content+=textline('twcm_ui_step')+'widget = { size = { 610 36 } '+step_buttons+' }\n'
  for resource,getter in [('gold','GetGold'),('prestige','GetPrestige'),('piety','GetPiety'),('renown','GetDynasty.GetPrestige')]:
   key=label('twcm_ui_resource_'+resource,resource.title() if resource!='renown' else 'Dynasty renown')
   content+='widget = { size = { 610 48 }\n'+textline(key,5,5,190)+textline(f'[{subject}.{getter}|0]',200,5,210,20)+button(resource+'_minus','twcm_ui_minus',f'twcm_ui_{resource}_minus',450,1,68,38,tooltip=f'twcm_ui_{resource}_minus_tip')+button(resource+'_plus','twcm_ui_plus',f'twcm_ui_{resource}_plus',530,1,68,38,tooltip=f'twcm_ui_{resource}_plus_tip')+'}\n'
  content+=button('clear_stress','twcm_stress','twcm_ui_clear_stress')
  content+=textline(label('twcm_ui_stress',f'Stress: [{subject}.MakeScope.ScriptValue(\'twcm_ui_stress_value\')|0]'))
  sgui('twcm_ui_nav_14','set_variable = { name = twcm_ui_page value = 14 }')
  content+=button('resource_bundle','twcm_14_title','twcm_ui_nav_14')
  content+=button('resource_exact','twcm_editor_page_605','twcm_editor_nav_605')
 elif n==20:
  content+=button('standing_tools','twcm_editor_page_700','twcm_editor_nav_700')+button('education_tools','twcm_editor_page_730','twcm_editor_nav_730')
  content+=note('twcm_ui_character_help',45)
  step_buttons=''
  for i,step in enumerate([1,5,10]):
   k=label(f'twcm_ui_skill_step_label_{step}',str(step))
   step_buttons+=button(f'skill_step_{step}',k,f'twcm_ui_skill_step_{step}',i*95,0,86,34,down=f"[EqualTo_CFixedPoint( GetPlayer.MakeScope.Var('twcm_ui_skill_step').GetValue, '(CFixedPoint){step}' )]")
  content+=textline('twcm_ui_skill_step_label')+'widget = { size = { 610 36 } '+step_buttons+' }\n'
  for skill in skills:
   key=label('twcm_ui_skill_label_'+skill,skill.title())
   content+='widget = { size = { 610 44 }\n'+textline(key,5,3,200)+textline(f"[{subject}.GetSkill( '{skill}' )]",240,3,160,20)+button(skill+'_minus','twcm_ui_minus',f'twcm_ui_skill_{skill}_minus',450,0,68,38,tooltip=f'twcm_ui_skill_{skill}_minus_tip')+button(skill+'_plus','twcm_ui_plus',f'twcm_ui_skill_{skill}_plus',530,0,68,38,tooltip=f'twcm_ui_skill_{skill}_plus_tip')+'}\n'
  content+=button('character_exact','twcm_editor_page_605','twcm_editor_nav_605')
  content+=button('full_trait_browser','twcm_editor_trait_browser_label','twcm_editor_nav_601')
  for dest in [30,50,60,91,97]:content+=button('char_sub_'+str(dest),ui_pages[dest]['title'],f'twcm_ui_nav_{dest}')
  content+=actions_for(20)
 elif n==70:
  content+=note(short_description(70),74)
  content+=''.join(option_button(o,n) for o in data['options'] if o['nav'] in [71,72])
  for dest in [40,300,95]:
   sgui(f'twcm_ui_nav_realm_{dest}',f'set_variable = {{ name = twcm_ui_page value = {dest} }}')
   content+=button('realm_sub_'+str(dest),ui_pages[dest]['title'],f'twcm_ui_nav_realm_{dest}')
 elif n==500:
  content+=button('alliance_tools','twcm_editor_page_740','twcm_editor_nav_740')
  content+=note('twcm_ui_diplomacy_help',88)+textline('twcm_ui_dip_current',w=610,size=17,h=35)
  content+=actions_for(500)
  for dest in [501,502,503]:
   sgui(f'twcm_ui_dip_nav_{dest}',f'set_variable = {{ name = twcm_ui_page value = {dest} }}')
   content+=button('dip_sub_'+str(dest),ui_pages[dest]['title'],f'twcm_ui_dip_nav_{dest}')
  # Expose the actual controls in one persistent page, not repeated event cards.
  for section in [501,502]+list(range(510,516)):
   content+=textline(ui_pages[section]['title'],size=20,h=32)+actions_for(section)
 else:
  content+=note(short_description(n),100)
  content+=''.join(option_button(o,n) for o in data['options'])
 if n==400:content+=button('ownership_editor','twcm_editor_page_630','twcm_editor_nav_630')
 if n==80:content+=button('war_editor','twcm_editor_page_640','twcm_editor_nav_640')
 # Page widgets share a stable window and scroll region; changing state never recreates events.
 rendered_pages.append(f'''widget = {{
 name = "twcm_page_{n}" position = {{ 204 150 }} size = {{ 650 510 }}
 visible = "[EqualTo_CFixedPoint( GetPlayer.MakeScope.Var('twcm_ui_page').GetValue, '(CFixedPoint){n}' )]"
 {textline(title_key,0,0,625,25,42)}
 {flow(content)}
}}
''')

exec((ROOT/'tools/editor_ui.py').read_text(),globals())

sidebar=''
for i,(n,key) in enumerate([(10,'resources'),(20,'character'),(400,'claims'),(70,'realm'),(80,'military'),(500,'diplomacy')]):
 sidebar+=button('tab_'+key,'twcm_ui_'+key,f'twcm_ui_nav_{n}',20,150+i*45,165,42)
for i,(n,key) in enumerate([(600,'tools'),(602,'pins'),(680,'search'),(603,'favourites'),(604,'active')],start=6):
 sidebar+=button('tab_'+key,'twcm_editor_tab_'+key,f'twcm_editor_nav_{n}',20,150+i*45,165,42)
modal_desc=[]
for ident,action in ui_pending.items():
 import math
 detail=loc[action['description']]
 detail_height=max(170,math.ceil(len(detail)/48)*21+detail.count('\n')*20)
 modal_desc.append(f'''scrollbox = {{ position = {{ 20 80 }} size = {{ 500 285 }}
 visible = "[EqualTo_CFixedPoint( GetPlayer.MakeScope.Var('twcm_ui_pending').GetValue, '(CFixedPoint){ident}' )]"
 blockoverride "scrollbox_content" {{ vbox = {{ layoutpolicy_horizontal = expanding
 {note(action['description'],detail_height,w=470)}
 }} }}
}}''')
gui=f'''window = {{
 name = "twcm_main_window"
 widgetid = "twcm_main_window"
 gfxtype = windowgfx alwaystransparent = no filter_mouse = all focuspolicy = click
 parentanchor = center size = {{ 890 720 }} layer = top
 using = Window_Background using = Window_Decoration using = Window_Movable
 visible = "{ui_expr('twcm_ui_visible','IsShown')}"
 {textline('twcm_ui_title',25,12,650,27,45)}
 {button('close_window','twcm_ui_close_label','twcm_ui_close',785,12,82,34)}
 portrait_head_small = {{ datacontext = "[{subject}]" position = {{ 22 56 }} size = {{ 72 78 }} }}
 {textline('twcm_ui_actor_label',115,57,450,16,26)}
 {textline('twcm_ui_selected_name',115,81,530,20,32)}
 {button('select_self','twcm_ui_me_label','twcm_ui_self',665,63,92,34)}
 {button('legacy_menu','twcm_ui_legacy_label','twcm_ui_legacy',765,63,102,34)}
 {textline('twcm_ui_other_label',115,112,165,14,28)}
 {textline('twcm_ui_other_name',285,110,565,16,30)}
 {sidebar}
 {''.join(rendered_pages)}
 {textline('twcm_ui_footer',24,678,842,14,28)}
 widget = {{
  name = "twcm_modal_overlay" size = {{ 890 720 }}
  visible = "{ui_expr('twcm_ui_modal_visible','IsShown')}"
  background = {{ using = Background_Area_Solid }}
  widget = {{ position = {{ 175 130 }} size = {{ 540 455 }} using = Window_Background_Popup
   {textline('twcm_ui_confirm_title',20,12,485,24,35)}
   {textline('twcm_ui_pending_name',20,47,485,18,28)}
   {''.join(modal_desc)}
   {button('cancel_pending','twcm_ui_confirm_cancel','twcm_ui_cancel',225,395,135,38)}
   {button('apply_pending','twcm_ui_confirm_apply','twcm_ui_confirm',375,395,135,38)}
  }}
 }}
}}
window = {{
 name = "twcm_hud_button" parentanchor = bottom|right position = {{ -210 -175 }} size = {{ 125 40 }} layer = hud_layer
 # The floating button otherwise intercepts clicks on the Decisions panel beneath it.
 visible = "[And(GetPlayer.IsValid, Not(IsGameViewOpen('decisions')))]"
 {button('open_cheats','twcm_ui_open_button','twcm_ui_open',0,0,125,40)}
}}
'''
write('gui/twcm_window.gui','\n'.join(line.rstrip() for line in gui.splitlines())+'\n')
write('gui/scripted_widgets/twcm_widgets.txt','gui/twcm_window.gui = twcm_main_window\ngui/twcm_window.gui = twcm_hud_button\n')
write('common/scripted_guis/twcm_window_guis.txt','\n'.join(line.rstrip() for line in '\n'.join(ui_sguis).splitlines())+'\n')

# New entry points preserve the old descriptor, event namespace and script IDs.
label('twcm_window_decision','Open Cheat Menu')
label('twcm_window_decision_desc','Open cheats for your ruler. To edit someone else, right-click their portrait and choose Cheat Menu: Open Editor.')
label('twcm_window_decision_tooltip','Open cheats for your current ruler.')
label('twcm_window_decision_confirm','Open window')
label('twcm_window_edit_interaction','Cheat Menu: Open Editor')
label('twcm_window_edit_interaction_desc','Select this character and open their cheats.')
label('twcm_window_other_interaction','Cheat Menu: Set Other Character')
label('twcm_window_other_interaction_desc','Choose the other character for diplomacy, court, family, vassal and artifact tools. The selected character stays the same.')
label('twcm_ui_open_window_legacy','Open cheat window')
new_decision='''twcm_window_decision = {
 picture = { reference = "gfx/interface/illustrations/decisions/decision_castle_view.dds" }
 desc = twcm_window_decision_desc selection_tooltip = twcm_window_decision_tooltip confirm_text = twcm_window_decision_confirm
 sort_order = 2 ai_check_interval = 0 is_shown = { is_ai = no }
 effect = { set_variable = { name = twcm_ui_target value = root } twcm_ui_open_effect = yes }
 ai_potential = { always = no } ai_will_do = { base = 0 }
}
'''
write('common/decisions/twcm_window_decision.txt',new_decision)
new_interactions=[]
for suffix,var in [('edit','twcm_ui_target'),('other','twcm_ui_other')]:
 key='twcm_window_'+suffix+'_interaction'
 new_interactions.append(f'''{key} = {{
 category = interaction_category_friendly common_interaction = yes interface_priority = 110
 icon = icon_contract_modification_single desc = {key}_desc use_diplomatic_range = no ignores_pending_interaction_block = yes auto_accept = yes
 is_shown = {{ scope:actor = {{ is_ai = no }} scope:recipient = {{ is_alive = yes }} }}
 on_accept = {{
  scope:actor = {{ set_variable = {{ name = {var} value = scope:recipient }} twcm_ui_open_effect = yes {'set_variable = { name = twcm_ui_page value = 500 }' if suffix=='other' else ''} }}
 }}
 ai_will_do = {{ base = 0 }}
}}
''')
write('common/character_interactions/twcm_window_interactions.txt','\n'.join(new_interactions))
window_meta={'widget_file':'gui/twcm_window.gui','pages':sorted(ui_pages)+editor_meta['pages'],'source_options':{str(n):[x['id'] for x in p['options']] for n,p in ui_pages.items()},'scripted_gui_ids':[parse(t)[0].key for t in ui_sguis],'confirmation_ids':{str(k):v['name'] for k,v in ui_pending.items()},'target_variable':'twcm_ui_target','other_variable':'twcm_ui_other','version':VERSION,'editor':editor_meta}

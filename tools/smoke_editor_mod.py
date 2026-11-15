"""Exercise emitted effects in a disposable 1066 game; never load a campaign save.

Runs the installed engine with a temporary profile and a test-only overlay. The overlay
is never packaged or installed. It calls the same generated snapshot/dispatch effects as
the editor, logs explicit PASS/FAIL markers, and exits after history. This checks effects,
not mouse interaction or rendering. Availability checks use emitted ScriptedGui guards,
excluding only the human-player gate because the history fixture is AI controlled.
"""
from pathlib import Path
from project_config import ROOT,MOD,GAME_ROOT as GAME
import argparse,json,re,shutil,subprocess,tempfile
from pdx_script import parse,dump,get






def build_overlay(destination,review=False):
 destination=Path(destination)
 for folder in ['events','common/on_action','common/scripted_effects','common/scripted_triggers','common/casus_belli_types','localization/english']:(destination/folder).mkdir(parents=True,exist_ok=True)
 guis={e.key:e.value for e in parse((MOD/'common/scripted_guis/twcm_window_guis.txt').read_text(encoding='utf-8-sig'))}
 meta=json.loads((ROOT/'tools/cheat_mod_metadata.json').read_text())['window']
 confirmed=set(meta['confirmation_ids'].values())
 apply=get(guis['twcm_ui_confirm'],'effect')
 (destination/'common/scripted_effects/twcm_smoke.txt').write_text('twcm_smoke_apply_effect = {\n'+dump(apply)+'\n}\n',encoding='utf-8-sig')
 tests=[];chunks=[];guards={};action_counts={}
 def guard(name):
  key='twcm_smoke_valid_'+name
  guards[key]=dump([e for e in get(guis[name],'is_valid') if e.key!='is_ai'])
  return key+' = yes'
 def add(text):chunks.append(text)
 def action(name):
  action_counts[name]=action_counts.get(name,0)+1
  case=name+'_'+str(action_counts[name])
  expect('enabled_'+case,guard('twcm_editor_'+name))
  add(dump(get(guis['twcm_editor_'+name],'effect')))
  if 'twcm_editor_'+name in confirmed:
   expect('review_'+case,guard('twcm_ui_confirm'))
   add('twcm_smoke_apply_effect = yes')
 def expect(name,trigger):
  assert name not in tests,name
  tests.append(name)
  add('if = { limit = { '+trigger+' } debug_log = "TWCM_PASS '+name+'" } else = { debug_log = "TWCM_FAIL '+name+'" }')
 def subjects(edited,other='scope:twcm_smoke_root'):
  add('set_variable = { name = twcm_ui_target value = '+edited+' } set_variable = { name = twcm_ui_other value = '+other+' } twcm_ui_prepare_effect = yes')
 def number(value):add('set_variable = { name = twcm_editor_number value = '+str(value)+' } twcm_ui_prepare_effect = yes')
 def make(scope,gender='male',age=30,employer=True):
  add('create_character = { age = '+str(age)+' gender = '+gender+' '+('employer = scope:twcm_smoke_root' if employer else 'location = scope:twcm_smoke_root.location')+' culture = scope:twcm_smoke_root.culture faith = scope:twcm_smoke_root.faith dynasty = none random_traits = no diplomacy = 10 martial = 10 stewardship = 10 intrigue = 10 learning = 10 prowess = 10 after_creation = { save_scope_as = '+scope+' } }')
 add('debug_log = "TWCM_SMOKE_BEGIN" save_scope_as = twcm_smoke_root')
 make('twcm_smoke_subject');make('twcm_smoke_spouse','female');make('twcm_smoke_outsider',employer=False);make('twcm_smoke_child',age=10)
 subjects('scope:twcm_smoke_subject','scope:twcm_smoke_spouse');number(37);action('exact_diplomacy')
 add('scope:twcm_smoke_subject = { save_scope_value_as = { name = twcm_smoke_actual_skill value = diplomacy } } debug_log_scopes = yes')
 expect('base_skill_reset','scope:twcm_smoke_subject = { diplomacy = 37 }')
 add('scope:twcm_smoke_subject = { add_trait = intellect_good_3 }');number(32);action('exact_diplomacy')
 expect('base_skill_preserves_trait_bonus','scope:twcm_smoke_subject = { diplomacy = 37 has_trait = intellect_good_3 }')
 number(5000);action('exact_gold');expect('exact_gold_increase','scope:twcm_smoke_subject = { gold = 5000 }')
 number(5);action('exact_gold');expect('exact_gold_decrease','scope:twcm_smoke_subject = { gold = 5 }')
 for resource in ['prestige','piety']:
  number(1200);action('exact_'+resource);expect('exact_'+resource+'_increase','scope:twcm_smoke_subject = { '+resource+' = 1200 }')
  number(50);action('exact_'+resource);expect('exact_'+resource+'_decrease','scope:twcm_smoke_subject = { '+resource+' = 50 }')
 number(22);action('exact_age');expect('exact_age','scope:twcm_smoke_subject = { age = 22 }')
 action('trait_add_lifestyle_blademaster');action('trait_xp_lifestyle_blademaster_0')
 expect('trait_browser_and_xp','scope:twcm_smoke_subject = { has_trait = lifestyle_blademaster has_trait_xp = { trait = lifestyle_blademaster value >= 100 } }')
 action('pin_save_1');subjects('scope:twcm_smoke_root');action('pin_select_1')
 expect('pin_selection','var:twcm_ui_target = scope:twcm_smoke_subject')
 # Snapshot must retain both the original target and amount after external selection changes.
 subjects('scope:twcm_smoke_subject');number(123)
 add(dump(get(guis['twcm_editor_exact_gold'],'effect')))
 subjects('scope:twcm_smoke_root');number(999)
 add('twcm_smoke_apply_effect = yes')
 expect('confirmation_snapshot','scope:twcm_smoke_subject = { gold = 123 }')
 subjects('scope:twcm_smoke_root','scope:twcm_smoke_outsider');action('recruit')
 expect('recruit','scope:twcm_smoke_outsider = { is_courtier_of = scope:twcm_smoke_root }')
 for position in ['chancellor','marshal','steward','spymaster']:
  action('appoint_'+position)
  expect('appoint_'+position,'scope:twcm_smoke_outsider = { has_council_position = councillor_'+position+' }')
  action('dismiss_councillor')
  expect('dismiss_'+position,'scope:twcm_smoke_outsider = { is_councillor = no }')
 action('knight_disallow')
 action('knight_force')
 action('knight_default')
 action('physician');expect('physician','scope:twcm_smoke_outsider = { has_court_position = court_physician_court_position }')
 action('physician_remove');expect('remove_physician','scope:twcm_smoke_outsider = { NOT = { has_court_position = court_physician_court_position } }')
 action('imprison');expect('imprison','scope:twcm_smoke_outsider = { is_imprisoned_by = scope:twcm_smoke_root }')
 action('release');expect('release','scope:twcm_smoke_outsider = { is_imprisoned = no }')
 subjects('scope:twcm_smoke_subject','scope:twcm_smoke_spouse');action('marry')
 expect('marry','scope:twcm_smoke_subject = { is_spouse_of = scope:twcm_smoke_spouse }')
 action('divorce');expect('divorce','scope:twcm_smoke_subject = { NOT = { is_spouse_of = scope:twcm_smoke_spouse } }')
 subjects('scope:twcm_smoke_subject','scope:twcm_smoke_root');action('join_house')
 expect('join_house','scope:twcm_smoke_subject.house = scope:twcm_smoke_root.house')
 subjects('scope:twcm_smoke_root','scope:twcm_smoke_child');action('adopt')
 expect('adopt','scope:twcm_smoke_child = { is_child_of = scope:twcm_smoke_root }')
 action('designate_heir');expect('designate_heir','designated_heir = scope:twcm_smoke_child')
 subjects('scope:twcm_smoke_root');number(4321);action('exact_renown');expect('exact_renown','dynasty = { dynasty_prestige = 4321 }')
 number(35);action('exact_development');expect('exact_development','capital_province.county = { development_level = 35 }')
 number(24)
 for skill in ['diplomacy','martial','stewardship','intrigue','learning','prowess']:action('spawn_skill_set_'+skill)
 action('spawn_age_set')
 for role in ['courtier','commander','physician','councillor','knight']:
  action('spawn_'+role)
  expect('spawn_'+role,'has_variable = twcm_editor_last_created var:twcm_editor_last_created = { age = 24 is_courtier_of = scope:twcm_smoke_root }')
 subjects('scope:twcm_smoke_subject');action('artifact_create_sword_common')
 expect('artifact_create','scope:twcm_smoke_subject = { any_character_artifact = { always = yes } }')
 add('scope:twcm_smoke_subject = { random_character_artifact = { save_scope_as = twcm_smoke_artifact root = { set_variable = { name = twcm_editor_artifact value = prev } } } }')
 add('scope:twcm_smoke_artifact = { add_durability = -10 }')
 expect('artifact_before_upgrade','scope:twcm_smoke_artifact = { has_artifact_modifier = twcm_editor_artifact_basic NOT = { has_artifact_modifier = twcm_editor_artifact_best } }')
 action('artifact_repair');expect('artifact_repair','scope:twcm_smoke_artifact = { artifact_durability = artifact_max_durability }')
 action('artifact_improve');action('artifact_improve')
 expect('artifact_improve','scope:twcm_smoke_artifact = { has_artifact_modifier = twcm_editor_artifact_best }')
 subjects('scope:twcm_smoke_subject','scope:twcm_smoke_spouse');action('artifact_transfer')
 expect('artifact_transfer','scope:twcm_smoke_artifact.artifact_owner = scope:twcm_smoke_spouse')
 subjects('scope:twcm_smoke_subject')
 add('set_variable = { name = twcm_editor_title value = title:c_desmond } set_variable = { name = twcm_editor_title_owner value = title:c_desmond.holder }')
 action('transfer_title')
 expect('title_transfer','title:c_desmond.holder = scope:twcm_smoke_subject')
 add('if = { limit = { scope:twcm_smoke_subject = { NOT = { is_vassal_of = scope:twcm_smoke_root } } } create_title_and_vassal_change = { type = granted save_scope_as = twcm_smoke_change } scope:twcm_smoke_subject = { change_liege = { liege = scope:twcm_smoke_root change = scope:twcm_smoke_change } } resolve_title_and_vassal_change = scope:twcm_smoke_change }')
 action('independence');expect('independence','scope:twcm_smoke_subject = { is_independent_ruler = yes }')
 subjects('scope:twcm_smoke_root','scope:twcm_smoke_subject');action('vassalize')
 expect('vassalize','scope:twcm_smoke_subject = { is_vassal_of = scope:twcm_smoke_root }')
 add('scope:twcm_smoke_subject = { change_government = feudal_government }')
 subjects('scope:twcm_smoke_subject');action('contract_tax_low')
 expect('contract_tax','scope:twcm_smoke_subject = { vassal_contract_obligation_level:feudal_government_taxes = 1 }')
 action('contract_levies_high')
 expect('contract_levies','scope:twcm_smoke_subject = { vassal_contract_obligation_level:feudal_government_levies = 3 }')
 action('culture_norse');expect('culture_picker','scope:twcm_smoke_subject = { culture = culture:norse }')
 action('faith_akom_pagan');expect('faith_picker','scope:twcm_smoke_subject = { faith = faith:akom_pagan }')
 subjects('scope:twcm_smoke_subject')
 add('culture:norse = { if = { limit = { has_innovation = innovation_battlements } remove_innovation = innovation_battlements } }')
 action('innovation_innovation_battlements');expect('innovation','culture:norse = { has_innovation = innovation_battlements }')
 add('culture:norse = { if = { limit = { has_cultural_tradition = tradition_astute_diplomats } remove_culture_tradition = tradition_astute_diplomats } if = { limit = { free_tradition_slot <= 0 } random_tradition = { save_scope_as = twcm_smoke_old_tradition prev = { remove_culture_tradition = scope:twcm_smoke_old_tradition } } } }')
 action('tradition_add_tradition_astute_diplomats');expect('tradition_add','culture:norse = { has_cultural_tradition = tradition_astute_diplomats }')
 action('tradition_remove_tradition_astute_diplomats');expect('tradition_remove','culture:norse = { NOT = { has_cultural_tradition = tradition_astute_diplomats } }')
 action('doctrine_doctrine_polygamy');expect('doctrine_replace','scope:twcm_smoke_subject.rite = { rite_has_doctrine = doctrine_polygamy }')
 add('scope:twcm_smoke_subject.rite = { random_rite_tenet = { save_scope_as = twcm_smoke_old_tenet prev = { remove_rite_tenet = scope:twcm_smoke_old_tenet } } }')
 action('tenet_add_tenet_ritual_cannibalism');expect('tenet_add','scope:twcm_smoke_subject.rite = { rite_has_tenet = tenet_ritual_cannibalism }')
 action('tenet_remove_tenet_ritual_cannibalism');expect('tenet_remove','scope:twcm_smoke_subject.rite = { NOT = { rite_has_tenet = tenet_ritual_cannibalism } }')
 subjects('scope:twcm_smoke_subject','scope:twcm_smoke_root');action('match_other_culture');action('match_other_faith')
 expect('match_custom_culture','scope:twcm_smoke_subject.culture = scope:twcm_smoke_root.culture')
 expect('match_custom_faith','scope:twcm_smoke_subject.faith = scope:twcm_smoke_root.faith')
 add('scope:twcm_smoke_subject = { add_truce_both_ways = { character = scope:twcm_smoke_root years = 1 name = TRUCE_GRANT_INDEPENDENCE } }')
 expect('truce_fixture','scope:twcm_smoke_subject = { has_truce = scope:twcm_smoke_root } has_truce = scope:twcm_smoke_subject')
 action('clear_truces');expect('clear_truces','scope:twcm_smoke_subject = { NOT = { has_truce = scope:twcm_smoke_root } } NOT = { has_truce = scope:twcm_smoke_subject }')
 # Use actual 1066 wars, with an explicit marker if that bookmark has no eligible fixture.
 for outcome in ['victory','white_peace','defeat']:
  add('random_ruler = { limit = { any_character_war = { '+('is_white_peace_possible = yes' if outcome=='white_peace' else 'always = yes')+' } } save_scope_as = twcm_smoke_war_subject random_character_war = { limit = { '+('is_white_peace_possible = yes' if outcome=='white_peace' else 'always = yes')+' } save_scope_as = twcm_smoke_war } }')
  subjects('scope:twcm_smoke_war_subject')
  add('set_variable = { name = twcm_editor_war value = scope:twcm_smoke_war }')
  action('war_'+outcome)
  expect('war_'+outcome,'exists = scope:twcm_smoke_war_subject scope:twcm_smoke_war_subject = { NOT = { any_character_war = { this = scope:twcm_smoke_war } } }')
  add('clear_saved_scope = twcm_smoke_war clear_saved_scope = twcm_smoke_war_subject')
 if review:
  from review_editor_cases import append_review_cases
  append_review_cases(add,action,expect,subjects,number,make,guard,guis,meta,destination)
 add('debug_log = "TWCM_SMOKE_END"')
 (destination/'common/scripted_triggers/twcm_smoke_guards.txt').write_text('\n'.join(k+' = {\n'+v+'\n}' for k,v in guards.items()),encoding='utf-8-sig')
 (destination/'events/twcm_smoke_events.txt').write_text('namespace = twcmsmoke\ntwcmsmoke.1 = { type = character_event hidden = yes immediate = {\n'+'\n'.join(chunks)+'\n} }\n',encoding='utf-8-sig')
 (destination/'common/on_action/twcm_smoke_on_action.txt').write_text('on_game_start = { on_actions = { twcm_expansion_smoke } }\ntwcm_expansion_smoke = { effect = { title:d_munster.holder = { trigger_event = { id = twcmsmoke.1 } } } }\n',encoding='utf-8-sig')
 return tests


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--timeout',type=int,default=180);parser.add_argument('--review',action='store_true');args=parser.parse_args()
 work=ROOT/('work/editor-review' if args.review else 'work/expansion');work.mkdir(parents=True,exist_ok=True)
 profile=Path(tempfile.mkdtemp(prefix='ck3-editor-smoke.'))
 overlay=profile/'test-overlay';tests=build_overlay(overlay,args.review)
 (profile/'mod').mkdir()
 for name,path in [('twcm',MOD),('smoke',overlay)]:
  (profile/'mod'/f'{name}.mod').write_text('name="'+name+'"\npath='+json.dumps(str(path))+'\n')
 (profile/'dlc_load.json').write_text(json.dumps({'enabled_mods':['mod/twcm.mod','mod/smoke.mod'],'disabled_dlcs':[]}))
 settings=Path.home()/'Documents/Paradox Interactive/Crusader Kings III/pdx_settings.txt'
 if settings.exists():(profile/'pdx_settings.txt').write_text(settings.read_text().replace('display_mode="fullscreen"','display_mode="windowed"').replace('display_mode="borderless_fullscreen"','display_mode="windowed"'))
 binary=GAME/'binaries/ck3.app/Contents/MacOS/ck3'
 with (work/'effect-smoke-stdout.log').open('w') as out:
  process=subprocess.Popen([str(binary),'-debug_mode','-suppress_error_log','-userdir='+str(profile),'-skip','-bookmark=bm_1066_hastings','-play=d_munster','-shutdown_after_history','-window_title=CK3 Editor Effect Checks'],cwd=GAME/'binaries',stdout=out,stderr=subprocess.STDOUT)
  (work/'effect-smoke-runtime.json').write_text(json.dumps({'pid':process.pid,'profile':str(profile),'binary':str(binary),'expected':tests},indent=2));print('Effect checks PID',process.pid,'profile',profile,flush=True)
  try:code=process.wait(timeout=args.timeout)
  except subprocess.TimeoutExpired:process.kill();process.wait();raise SystemExit('Engine check timed out; logs kept at '+str(profile))
 logs=profile/'logs';shutil.copytree(logs,work/'effect-smoke-logs',dirs_exist_ok=True)
 text=(logs/'debug.log').read_text(errors='replace')
 passed=re.findall(r'TWCM_PASS (\w+)',text);failed=re.findall(r'TWCM_FAIL (\w+)',text)
 errors=(logs/'error.log').read_text(errors='replace')
 mod_errors=[];native_errors=[]
 for block in errors.split('\n\n'):
  location=re.search(r'Script location: file: ([^ \n]+)',block)
  if not block.strip():continue
  if (location and 'twcm' in location[1]) or (not location and 'twcm' in block.lower()):mod_errors.append(block)
  else:native_errors.append(block)
 gui_warnings=(logs/'gui_warnings.log').read_text(errors='replace')
 report={'manual_only':['Knight preference saved-state inspection in the Knights window'],'mod_errors':mod_errors,'native_errors':native_errors,'gui_warnings':gui_warnings,'exit':code,'profile':str(profile),'expected':tests,'passed':passed,'failed':failed,'completed':'TWCM_SMOKE_END' in text}
 (work/'effect-smoke-results.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({'exit':code,'profile':str(profile),'passed':len(passed),'expected':len(tests),'failed':failed,'mod_errors':len(mod_errors),'gui_warnings':len(gui_warnings),'completed':report['completed']},indent=2))
 if code!=0 or mod_errors or gui_warnings.strip() or failed or set(passed)!=set(tests) or len(passed)!=len(tests) or not report['completed']:raise SystemExit(1)

if __name__=='__main__':main()

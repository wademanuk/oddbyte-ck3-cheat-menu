# Executed by build_cheat_mod.py. Both actors are restored on every GUI/event action.
dip_valid='is_alive = yes scope:twcm_other = { is_alive = yes } NOT = { this = scope:twcm_other }'
label('twcm_diplomacy','Hooks, opinion and relationships')
write('common/hook_types/twcm_hooks.txt','''twcm_weak_hook = { expiration_days = 3650 }
twcm_strong_hook = { strong = yes expiration_days = 7300 }
''')
label('twcm_weak_hook','Cheat Favor');label('twcm_strong_hook','Strong Cheat Favor')
write('common/opinion_modifiers/twcm_opinions.txt','''twcm_cheat_opinion = { opinion = 0 years = 10 decaying = no stacking = no }
''')
label('twcm_cheat_opinion','Cheat opinion adjustment')
event(500,'Diplomacy','Change dealings between the selected character and [twcm_other.GetFullName]. To choose someone else, right-click their portrait and use Cheat Menu: Set Other Character.',[
 option('twcm_dip_hooks','Hooks',target=501,trigger=dip_valid),
 option('twcm_dip_opinion','Opinion',target=502,trigger=dip_valid),
 option('twcm_dip_relationships','Relationships',target=503,trigger=dip_valid),
 option('twcm_dip_swap','Swap the two characters','scope:twcm_target = { save_scope_as = twcm_dip_temp }\nscope:twcm_other = { save_scope_as = twcm_target }\nscope:twcm_dip_temp = { save_scope_as = twcm_other }\nset_variable = { name = twcm_ui_target value = scope:twcm_target }\nset_variable = { name = twcm_ui_other value = scope:twcm_other }',target=500,raw=True),back(90)])
event(501,'Hooks','Give the selected character leverage over the other character. Weak hooks last 10 years; strong hooks last 20. Weak grants keep existing hooks; strong grants upgrade weaker hooks. Removal clears any hook on this person, including existing game hooks.',[
 option('twcm_hook_weak','Gain a weak hook (10 years)','if = { limit = { NOT = { has_hook = scope:twcm_other } } add_hook = { target = scope:twcm_other type = twcm_weak_hook } }',target=501,trigger=dip_valid),
 option('twcm_hook_strong','Gain a strong hook (20 years)','if = { limit = { NOT = { has_strong_hook = scope:twcm_other } } if = { limit = { has_hook = scope:twcm_other } remove_hook = { target = scope:twcm_other } } add_hook = { target = scope:twcm_other type = twcm_strong_hook } }',target=501,trigger=dip_valid),
 option('twcm_hook_remove','Remove hook on other character','if = { limit = { has_hook = scope:twcm_other } remove_hook = { target = scope:twcm_other } }',target=501,trigger=dip_valid),back(500)])
opinion_options=[]
for value in [100,50,-50,-100]:
 body=f'scope:twcm_other = {{ remove_opinion = {{ target = scope:twcm_target modifier = twcm_cheat_opinion }} add_opinion = {{ target = scope:twcm_target modifier = twcm_cheat_opinion opinion = {value} }} }}'
 opinion_options.append(option(f'twcm_opinion_{"plus" if value>0 else "minus"}_{abs(value)}',f'Set their opinion {"bonus" if value>0 else "penalty"} to {value:+}',body,target=502,trigger=dip_valid))
opinion_options.append(option('twcm_opinion_remove','Remove this opinion bonus or penalty','scope:twcm_other = { remove_opinion = { target = scope:twcm_target modifier = twcm_cheat_opinion } }',target=502,trigger=dip_valid))
event(502,'Opinion','Change the other character\'s opinion of the selected character for 10 years. Each choice replaces this cheat\'s previous bonus or penalty. Other opinion factors still count.',opinion_options+[back(500)])
relations=[('friend','Friend'),('best_friend','Best friend'),('rival','Rival'),('nemesis','Nemesis'),('lover','Lover'),('soulmate','Soulmate')]
event(503,'Relationships','Make these characters friends, rivals or romantic partners. Friendship replaces rivalry and vice versa. Romance requires unrelated adults aged 18+. Normal relationship events and consequences can follow.',[
 option('twcm_relation_'+kind,title,target=510+i) for i,(kind,title) in enumerate(relations)]+[back(500)])
relation_end={'friend':'End friendship','best_friend':'End best-friend bond','rival':'End rivalry','nemesis':'End nemesis bond','lover':'End affair','soulmate':'End soulmate bond'}
relation_help={
 'friend':'Make them friends or end the friendship. Adding friendship removes rivalry and nemesis ties.',
 'best_friend':'Make them best friends or end that bond. Adding it removes rivalry and nemesis ties; ending it removes the best-friend bond.',
 'rival':'Make them rivals or end the rivalry. Adding rivalry removes friend and best-friend ties.',
 'nemesis':'Make them sworn enemies or end that bond. Adding it removes friendship; ending it removes the nemesis bond.',
 'lover':'Make them lovers or end the affair. Adding requires unrelated adults aged 18+.',
 'soulmate':'Make them soulmates or end that bond. Adding requires unrelated adults aged 18+; ending it removes the soulmate bond.',
}

for i,(kind,title) in enumerate(relations):
 cleanup=''
 if kind in ['friend','best_friend']:cleanup='if = { limit = { has_relation_nemesis = scope:twcm_other } remove_relation_nemesis = scope:twcm_other }\nif = { limit = { has_relation_rival = scope:twcm_other } remove_relation_rival = scope:twcm_other }\n'
 if kind in ['rival','nemesis']:cleanup='if = { limit = { has_relation_best_friend = scope:twcm_other } remove_relation_best_friend = scope:twcm_other }\nif = { limit = { has_relation_friend = scope:twcm_other } remove_relation_friend = scope:twcm_other }\n'
 stronger={'friend':'best_friend','rival':'nemesis','lover':'soulmate'}.get(kind)
 exact_guard=f' NOT = {{ has_relation_{stronger} = scope:twcm_other }}' if stronger else ''
 trigger=dip_valid+f' NOT = {{ has_relation_{kind} = scope:twcm_other }}'+exact_guard
 if kind in ['lover','soulmate']:trigger+=' age >= 18 scope:twcm_other = { age >= 18 } NOT = { is_close_or_extended_family_of = scope:twcm_other }'
 event(510+i,title,'With [twcm_other.GetFullName]: '+relation_help[kind],[
  option('twcm_relation_add_'+kind,'Make '+title.lower()+'s' if kind not in ['nemesis'] else 'Make nemeses',cleanup+f'set_relation_{kind} = scope:twcm_other',target=510+i,trigger=trigger),
  option('twcm_relation_remove_'+kind,relation_end[kind],f'remove_relation_{kind} = scope:twcm_other',target=510+i,trigger=dip_valid+f' has_relation_{kind} = scope:twcm_other'+exact_guard),back(503)])
diplomacy_meta={'root':500,'relations':[x[0] for x in relations],'actor_scope':'twcm_target','other_scope':'twcm_other','opinion_modifier':'twcm_cheat_opinion'}

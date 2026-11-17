"""Generate bounded bulk-building effects from this CK3 installation's definitions."""
import copy
import re
from pdx_script import Entry,parse,dump,get,walk

GUARDS=['can_construct_potential','can_construct_showing_failures_only','can_construct','is_enabled']
PRIMARY={'castle_01','city_01','temple_01','temple_citadel_01','tribe_01','nomadic_camp_01','herder_camp_01'}

def load_buildings(game):
    result={}
    for path in sorted((game/'common/buildings').rglob('*.txt')):
        for entry in parse(path.read_text(encoding='utf-8-sig')):
            if isinstance(entry.value,list):result[entry.key]=entry.value
    return result

def generate(game):
    buildings=load_buildings(game)
    if (game/'common/districts').is_dir():
        return generate_district_tools(game,buildings)
    helpers={}
    for path in sorted((game/'common/scripted_triggers').glob('*.txt')):
        for e in parse(path.read_text(encoding='utf-8-sig')):
            if isinstance(e.value,list):helpers[e.key]=e.value
    removed=set()
    def sanitize(entries,params=None,stack=(),positive=True):
        params=params or {}
        out=[]
        for original in entries:
            e=copy.deepcopy(original)
            def subst(s):
                for k,v in params.items():s=s.replace('$'+k+'$',v)
                return re.sub(r'\broot\b','scope:twcm_build_province',s,flags=re.I)
            e.key=subst(e.key)
            if isinstance(e.value,str):e.value=subst(e.value)
            # Ignore technology gates and space checks (space is checked only for new builds).
            if e.key in ['has_innovation','has_all_innovations','culture_era','has_culture_era','free_building_slots','has_free_building_slot']:
                removed.add(e.key)
                # Keep a true branch in ORs instead of accidentally deleting it.
                # Under negation use false, so the enclosing NOT still bypasses the gate.
                out.append(Entry('always','=','yes' if positive else 'no'))
                continue
            if e.key in helpers and (e.key.startswith('building_') or e.key=='japan_castle_construction_trigger'):
                if e.key in stack:raise ValueError('Recursive building helper: '+e.key)
                args={x.key:x.value for x in e.value} if isinstance(e.value,list) else {}
                # Max-level cheats bypass holding-tier requirements while preserving type checks.
                if 'LEVEL' in args:args['LEVEL']='01'
                expanded=sanitize(helpers[e.key],args,stack+(e.key,),not positive if e.value=='no' else positive)
                if expanded:out.append(Entry('NOT' if e.value=='no' else 'AND','=',expanded))
                continue
            if isinstance(e.value,list):
                e.value=sanitize(e.value,params,stack,not positive if e.key in ['NOT','NOR','NAND'] else positive)
                if not e.value:
                    if e.key=='limit':e.value=[Entry('always','=','yes')]
                    else:continue
            # Direct holding-level checks should not prevent a regular chain reaching its top.
            if e.key=='has_building_or_higher' and isinstance(e.value,str):
                for base in PRIMARY:
                    if re.fullmatch(re.escape(base[:-2])+r'\d+',e.value):e.value=base
            out.append(e)
        return out

    def guard(name):
        result=[]
        for key in GUARDS:
            result.extend(sanitize(get(buildings[name],key,[])))
        return result

    next_ids={get(b,'next_building') for b in buildings.values()}-{None}
    assert next_ids<=buildings.keys(),('Unknown next-building IDs',next_ids-buildings.keys())
    for start in buildings:
        seen=set();cur=start
        while cur:
            if cur in seen:raise ValueError('Building upgrade cycle: '+start)
            seen.add(cur);cur=get(buildings[cur],'next_building')
    roots=[k for k in buildings if k not in next_ids and get(buildings[k],'is_graphical_background')!='yes']
    chains={}
    for root in roots:
        chain=[];cur=root
        while cur:
            if cur in chain:raise ValueError('Building upgrade cycle: '+root)
            chain.append(cur);cur=get(buildings[cur],'next_building')
        chains[root]=chain

    def upgrade(chain):
        lines=[]
        kind=get(buildings[chain[0]],'type','regular')
        effect='add_special_building' if kind=='special' else 'add_building'
        for old,new in zip(chain,chain[1:]):
            conditions=[Entry('has_building','=',old)]+guard(new)
            lines.append('if = {\nlimit = {\n'+dump(conditions)+'\n}\n'+effect+' = '+new+'\n}')
        return '\n'.join(lines)

    # Primary holding chains first, so their upgraded holding exists for ordinary chains.
    upgrade_roots=sorted((r for r,c in chains.items() if len(c)>1 and get(buildings[r],'type')!='great_building'),key=lambda r:(r not in PRIMARY,r))
    fill_roots=[r for r in roots if r not in PRIMARY and get(buildings[r],'type','regular')=='regular']
    priority=['farm_estates_01','cereal_fields_01','pastures_01','hospices_01','common_tradeport_01','watermills_01','windmills_01','barracks_01','military_camps_01']
    fill_roots=sorted(fill_roots,key=lambda r:(priority.index(r) if r in priority else len(priority),r))
    setup='''save_scope_as = twcm_build_province
barony.holder = { save_scope_as = holder save_scope_as = build_owner }
county = { save_scope_as = county }
'''
    fill=[]
    for root in fill_roots:
        cond=[Entry('free_building_slots','>','0'),Entry('NOT','=',[Entry('has_building_or_higher','=',root)])]+guard(root)
        fill.append('if = {\nlimit = {\n'+dump(cond)+'\n}\nadd_building = '+root+'\n'+upgrade(chains[root])+'\n}')
    text='''# Generated against installed CK3 building graphs; never replaces vanilla definitions.
twcm_expand_slots_effect = {
    while = {
        count = 7
        limit = { building_slots < 7 }
        add_province_modifier = twcm_extra_building_slot
    }
}
twcm_upgrade_buildings_effect = {
'''+setup+'\n'.join(upgrade(chains[r]) for r in upgrade_roots)+'''
}
twcm_fill_buildings_effect = {
'''+setup+'\n'.join(fill)+'''
}
'''
    # All expanded triggers refer to the actual province rather than the player's event root.
    assert not re.search(r'\broot\b',text,re.I)
    assert not re.search(r'\$(?:[A-Z_]+)\$',text), 'Unexpanded building helper parameter'
    meta={'definitions':len(buildings),'fill_roots':fill_roots,'upgrade_chains':{r:chains[r] for r in upgrade_roots},'removed_gates':sorted(removed),'placement_rules':'All four native construction/enabled trigger groups; technology and holding-level thresholds bypassed. Regular empty slots only; existing special/duchy chains upgraded in place; great projects excluded.'}
    return text,meta


def generate_district_tools(game,buildings):
    districts={entry.key:entry.value for path in sorted((game/'common/districts').glob('*.txt'))
               for entry in parse(path.read_text(encoding='utf-8-sig')) if isinstance(entry.value,list)}
    priority=['villages_district','military_district','urban_housing_district','market_district']
    regular=sorted((key for key,body in districts.items() if get(body,'type','regular')=='regular'),
                   key=lambda key:(priority.index(key) if key in priority else len(priority),key))
    primary={key:get(districts[key],'primary_building') for key in regular}
    assert set(primary.values())<=buildings.keys(),('Missing district primary buildings',set(primary.values())-buildings.keys())
    holdings={entry.key:entry.value for path in sorted((game/'common/holdings').glob('*.txt'))
              for entry in parse(path.read_text(encoding='utf-8-sig')) if isinstance(entry.value,list)}
    visits=['holding_district ?=', 'resource_district ?=', 'special_district ?=',
            'duchy_capital_district ?=', 'every_built_regular_district =']
    def placement(key):
        types=[Entry('has_holding_type','=',holding) for holding,body in holdings.items()
               if any(item.key==key for item in get(body,'districts',[]))]
        if not types:return ''
        allowed=[Entry('OR','=',types)]
        prerequisite=get(districts[key],'unlocked_by')
        if prerequisite:allowed.append(Entry('province_has_district','=',prerequisite))
        for body in (districts[key],buildings[primary[key]]):
            for field in GUARDS:allowed.extend(get(body,field,[]))
        guards=re.sub(r'\broot\b','scope:twcm_build_province',dump(allowed),flags=re.I)
        return f'''if = {{
    limit = {{ has_free_district_slot = yes NOT = {{ province_has_district = {key} }} {guards} }}
    add_regular_district = {key}
}}'''
    place='\n'.join(filter(None,map(placement,regular)))
    eligible='can_building_be_upgraded = yes is_building_being_upgraded = no'
    text=f'''twcm_expand_slots_effect = {{
    while = {{
        count = 7
        limit = {{ district_slots < 7 }}
        add_province_modifier = twcm_extra_building_slot
    }}
}}
twcm_upgrade_district_effect = {{
    while = {{
        count = 64
        limit = {{ any_district_building = {{ {eligible} }} }}
        random_district_building = {{ limit = {{ {eligible} }} upgrade_this_building = yes }}
    }}
}}
twcm_upgrade_buildings_effect = {{
    {' '.join(scope+' { twcm_upgrade_district_effect = yes }' for scope in visits)}
}}
twcm_fill_buildings_effect = {{
    save_scope_as = twcm_build_province
    barony.holder = {{ save_scope_as = holder save_scope_as = build_owner }}
    county = {{ save_scope_as = county }}
    while = {{
        count = 7
        limit = {{ has_free_district_slot = yes }}
        {place}
    }}
    every_built_regular_district = {{
        twcm_upgrade_district_effect = yes
        save_scope_as = twcm_build_district
        while = {{
            count = 12
            limit = {{ free_building_slots > 0 }}
            scope:twcm_build_province = {{ build_random_district_building = {{ district = scope:twcm_build_district }} }}
        }}
        twcm_upgrade_district_effect = yes
    }}
}}
'''
    return text,{'definitions':len(buildings),'fill_roots':list(primary.values()),'upgrade_chains':{},
                 'regular_districts':regular,'removed_gates':[],
                 'placement_rules':'Native district and building eligibility; free instant construction and upgrades. Great projects excluded.'}

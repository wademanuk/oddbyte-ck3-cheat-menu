"""Read editor choices from the installed game; keep search independent of gameplay."""
from pathlib import Path
import re
import unicodedata
from pdx_script import parse, get


def definitions(folder):
    def read(path):
        # The editor never uses colors; normalize their typed block syntax for the parser.
        text = path.read_text(encoding='utf-8-sig')
        return re.sub(r'=\s*(?:hsv|hsv360|rgb)\s*\{', '= {', text)
    return {entry.key: entry.value
            for path in sorted(Path(folder).glob('*.txt'))
            for entry in parse(read(path))
            if isinstance(entry.value, list)}


def load_catalog(game):
    game = Path(game)
    names = {}
    for path in sorted((game / 'localization/english').rglob('*.yml')):
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            match = re.match(r'\s*([\w.\-]+):\d*\s+"(.*)"\s*(?:#.*)?$', line)
            if match:
                names[match[1]] = match[2]

    def name(key, prefix=''):
        fallback = re.sub(r'^(?:trait_|tradition_|innovation_|doctrine_|tenet_)', '', key).replace('_', ' ').title()
        value = names.get(prefix + key, names.get(key, names.get(key + '_name', fallback)))
        for _ in range(5):
            value = re.sub(r'\$([\w.\-]+)\$', lambda m: names.get(m[1], m[1]), value)
        value = re.sub(r'#[\w;:]+\s*|#!', '', value)
        # Dynamic character names are rendered with native GetTrait in the GUI.
        if '[' in value:
            value = key.replace('_', ' ').title()
        return value.replace('\\n', ' ').replace('\\"', '"')

    traits = definitions(game / 'common/traits')
    categories = {}
    tracks = {}
    for key, values in traits.items():
        category = get(values, 'category', 'other')
        if category not in ['education', 'personality', 'commander', 'lifestyle']:
            category = 'other'
        for flag, label in [('physical', 'health'), ('disease', 'health'),
                            ('lifestyle', 'lifestyle'), ('commander', 'commander'),
                            ('genetic', 'inherited'), ('congenital', 'inherited'),
                            ('personality', 'personality'), ('education', 'education')]:
            if get(values, flag) == 'yes':
                category = label
        if key.startswith('education_'):
            category = 'education'
        categories[key] = category
        named = get(values, 'tracks', [])
        tracks[key] = [e.key for e in named] if named else ([None] if get(values, 'track') is not None else [])

    faiths = definitions(game / 'common/religion/faith_types')
    for values in definitions(game / 'common/religion/religions').values():
        for entry in get(values, 'faiths', []):
            if isinstance(entry.value, list):
                faiths[entry.key] = entry.value

    doctrine_groups = {}
    for key, values in definitions(game / 'common/religion/doctrine_types').items():
        group = get(values, 'doctrine_group_type')
        if group:
            doctrine_groups.setdefault(group, {'choices': [], 'multiple': False})['choices'].append(key)
    return {'names': names, 'name': name, 'traits': traits, 'trait_categories': categories,
            'trait_tracks': tracks, 'cultures': definitions(game / 'common/culture/cultures'),
            'faiths': faiths, 'innovations': definitions(game / 'common/culture/innovations'),
            'traditions': definitions(game / 'common/culture/traditions'),
            'doctrine_groups': doctrine_groups,
            'dynasty_perks': definitions(game / 'common/dynasty_perks'),
            'dynasty_legacies': definitions(game / 'common/dynasty_legacies'),
            'tenets': definitions(game / 'common/religion/tenet_types')}


def search_terms(text):
    """Word-start and full-label prefixes for the native lowercase letter selector."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    clean = re.sub(r'[^\w\s-]', '', text).strip().lower()
    terms = set()
    for word in [clean, *re.findall(r'\w+', clean)]:
        for length in range(1, len(word) + 1):
            prefix = word[:length]
            terms.add(prefix)
    return sorted(terms)


def search_expression(text, variable='twcm_search'):
    """Use the native GUI string store. Search never executes entered text as script."""
    terms = search_terms(text)
    expressions = [f"GetVariableSystem.HasValue( '{variable}', '{term}' )" for term in terms]
    expressions.insert(0, f"StringIsEmpty( GetVariableSystem.Get( '{variable}' ) )")
    # A balanced tree keeps native GUI expression nesting bounded for long labels.
    while len(expressions) > 1:
        expressions = [f'Or( {expressions[i]}, {expressions[i+1]} )' if i+1 < len(expressions)
                       else expressions[i] for i in range(0, len(expressions), 2)]
    return expressions[0]

"""Build the donor library shipped with the skill (maintainer tool).

Scans a blueprints root, and for every object version writes library/donors-v<NN>.sbp holding one
clean sample of each building type: one with custom paint (PrimaryColor) when available, and one
without. "Clean" means the building and its components reference nothing outside themselves, so
the sample can be cloned anywhere. Samples are laid out on a grid, so rendering a library file
gives a visual catalogue.

  python -I build_library.py "<blueprints root>" [<library dir>]
"""
import copy, json, re, struct, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sbp import Blueprint, short, swatch, replace_string

REF = re.compile(rb'Persistent_Level:PersistentLevel\.([\w.]+)')
# Some pieces (e.g. signs since 1.1) store the builder's online account: id, display name and
# platform. Never ship those samples.
PERSONAL = re.compile(rb'AccountId\w*\x00|DisplayName\x00|BackendName\x00|PlayerName\x00|UserName\x00')
RECIPE = re.compile(rb'(/Game/FactoryGame/[^\x00]*?/Recipe_\w+\.Recipe_\w+_C)\x00')
GRID = 2400  # cm between samples


def is_clean(bp, actor, comps):
    own = {actor['path'].split('.', 1)[1]} | {c['path'].split('.', 1)[1] for c in comps}
    for o in [actor] + comps:
        if PERSONAL.search(o['data']):
            return False
        for ref in REF.findall(o['data']):
            r = ref.decode()
            if r == 'BuildableSubsystem' or r in own or r.split('.')[0] in own:
                continue
            return False
    return True


def main(root, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    by_version = defaultdict(dict)     # version -> {(type, custom): (bp, actor, comps)}
    bases = {}
    items = {}                         # 'Desc_SteelPlate' -> item class path, for cost lists
    for f in sorted(Path(root).rglob('*.sbp')):
        try:
            bp = Blueprint.load(f)
        except Exception as e:
            print('skip', f.name, e, file=sys.stderr)
            continue
        v = bp.object_version
        bases.setdefault(v, bp)
        for item, _ in bp.cost:
            items.setdefault(short(item), item)
        comp_index = defaultdict(list)
        for o in bp.objects:
            if o['type'] == 0:
                comp_index[o['outer']].append(o)
        for a in bp.actors():
            key = (short(a['cls']), b'PrimaryColor' in a['data'])
            if key in by_version[v]:
                continue
            comps = comp_index.get(a['path'], [])
            if is_clean(bp, a, comps):
                by_version[v][key] = (bp, a, comps)

    index = {}
    for v, picks in sorted(by_version.items()):
        base = bases[v]
        lib = Blueprint()
        for attr in ('header_version', 'object_version', 'build_version', 'extra_header',
                     'object_flags', 'chunk_v2'):
            setattr(lib, attr, getattr(base, attr))
        recipes, entries = set(), {}
        next_id = 2140000000
        keys = sorted(picks)
        cols = max(1, int(len(keys) ** 0.5))
        for i, key in enumerate(keys):
            src_bp, actor, comps = picks[key]
            new_actor_path = '%s_%d' % (actor['path'].rsplit('_', 1)[0], next_id)
            next_id += 1
            a = copy.deepcopy(actor)
            a['pos'] = [(i % cols) * GRID, (i // cols) * GRID, 0.0]
            for c in comps:
                a['data'] = replace_string(a['data'], c['path'], c['path'].replace(actor['path'], new_actor_path))
            a['data'] = replace_string(a['data'], actor['path'], new_actor_path)
            a['path'] = new_actor_path
            lib.objects.append(a)
            for c in comps:
                nc = copy.deepcopy(c)
                nc['data'] = replace_string(nc['data'], actor['path'], new_actor_path)
                nc['path'] = c['path'].replace(actor['path'], new_actor_path)
                nc['outer'] = new_actor_path
                lib.objects.append(nc)
            m = RECIPE.search(actor['data'])
            if m:
                recipes.add(m.group(1).decode())
            t, custom = key
            e = entries.setdefault(t, dict(paints=[], recipe=m.group(1).decode() if m else None,
                                            components=len(comps)))
            e['paints'].append('custom' if custom else (swatch(actor) or 'none'))
        span = cols * GRID / 800 + 1
        lib.dims = [int(span) + 1, int((len(keys) // cols + 1) * GRID / 800) + 1, 4]
        lib.recipes = sorted(recipes)
        path = out_dir / ('donors-v%d.sbp' % v)
        lib.save(path)
        check = Blueprint.load(path)
        assert len(check.objects) == len(lib.objects)
        index[str(v)] = dict(file=path.name, types=entries)
        print('v%d: %d types, %d objects, %.0f KB' % (v, len(entries), len(lib.objects), path.stat().st_size / 1024))
    (out_dir / 'index.json').write_text(json.dumps(index, indent=1, sort_keys=True))
    (out_dir / 'items.json').write_text(json.dumps(items, indent=1, sort_keys=True))
    (out_dir / 'CATALOG.md').write_text(catalog_markdown(index), encoding='utf-8')


CATEGORIES = [
    ('Beams & frames', r'Beam|Frame'),
    ('Foundations & ramps', r'Foundation|Ramp|QuarterPipe|InvertedRamp'),
    ('Walls', r'Wall(?!.*Window)|Fence|Railing'),
    ('Glass & windows', r'Window|Glass'),
    ('Pillars', r'Pillar'),
    ('Roofs', r'Roof'),
    ('Walkways, stairs & catwalks', r'Walkway|Catwalk|Stair|Ladder'),
    ('Lights & signs', r'Light|Sign|Billboard'),
    ('Logistics (belts, lifts, splitters, pipes)', r'Conveyor|Pipe|Pump|Valve|Hyper|Splitter|Merger|Lift'),
    ('Power', r'Power|Generator|Battery|Wire|Switch'),
    ('Production', r'Constructor|Assembler|Manufacturer|Smelter|Foundry|Refinery|Blender|Packager|Converter|Accelerator|Collider|Encoder|Miner|Extractor'),
    ('Storage & stations', r'Storage|Station|Dock|Container|Tank'),
]


def category(name):
    for cat, pattern in CATEGORIES:
        if re.search(pattern, name):
            return cat
    return 'Other'


def catalog_markdown(index):
    """Human/Claude-readable list of every shipped piece type."""
    rows = defaultdict(dict)   # type -> info merged across versions
    for v, d in index.items():
        for t, e in d['types'].items():
            r = rows[t].setdefault('versions', [])
            r.append(int(v))
            rows[t]['custom'] = rows[t].get('custom', False) or 'custom' in e['paints']
            rows[t]['components'] = e['components']
    lines = [
        '# Piece catalogue',
        '',
        'Every building piece shipped in this library, generated by `scripts/build_library.py`.',
        'Load pieces with `Library.load(needs=[...])` and copy them with `Blueprint.add_copy`.',
        '',
        '- **Name**: the game class without `Build_`/`_C`; sizes like `8x4` are width x height in metres.',
        '- **Versions**: blueprint object versions that have a clean sample (36 = Update 8, 42-46 = 1.0,',
        '  52-60 = 1.1/1.2). Build each blueprint from a single version.',
        '- **Any colour**: a sample with custom paint exists, so `set_color` can make it any RGB colour.',
        '  Otherwise the piece uses a palette slot (its in-game colour depends on the player).',
        '- **Parts**: number of components (connectors, inventories). Machines with parts still need',
        '  belts/power hooked up in game.',
        '',
    ]
    groups = defaultdict(list)
    for t in rows:
        groups[category(t)].append(t)
    order = [c for c, _ in CATEGORIES] + ['Other']
    for cat in order:
        if cat not in groups:
            continue
        lines += ['## ' + cat, '', '| Name | Versions | Any colour | Parts |', '|---|---|---|---|']
        for t in sorted(groups[cat]):
            r = rows[t]
            lines.append('| `%s` | %s | %s | %s |' % (t, ', '.join(map(str, sorted(r['versions']))),
                                                    'yes' if r['custom'] else '', r['components'] or ''))
        lines.append('')
    return '\n'.join(lines)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / 'library')

"""Build the list of every buildable piece in the game (maintainer tool).

Reads the game's own data file for modders, <game>/CommunityResources/Docs/en-US.json, and writes:
  library/assets.json   every buildable: name, category, size, build cost, unlock; plus every item
  library/ASSETS.md     the same as a readable table, with a "ready" column for pieces that have
                        a sample in the donor library (so Claude can place them today)

  python -I build_assets.py ["<path to en-US.json>"]

Only names and numbers are taken from the game file, not its description text.
"""
import codecs, json, re, sys
from collections import defaultdict
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / 'library'
GUESSES = [
    r'C:/Program Files (x86)/Steam/steamapps/common/Satisfactory',
    r'C:/Program Files/Epic Games/SatisfactoryEarlyAccess',
    r'C:/Program Files/Epic Games/Satisfactory',
] + ['%s:/SteamLibrary/steamapps/common/Satisfactory' % d for d in 'CDEFG']


def find_docs():
    for g in GUESSES:
        p = Path(g) / 'CommunityResources' / 'Docs' / 'en-US.json'
        if p.exists():
            return p
    raise SystemExit('Could not find CommunityResources/Docs/en-US.json; pass its path.')


def load_docs(path):
    raw = Path(path).read_bytes()
    enc = 'utf-16' if raw[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE) else 'utf-8-sig'
    return {g['NativeClass'].split('.')[-1].rstrip("'"): g['Classes'] for g in json.loads(raw.decode(enc))}


def short(name):
    name = name.split('.')[-1].strip('"\'')
    for pre in ('Build_', 'Desc_', 'Recipe_'):
        if name.startswith(pre):
            name = name[len(pre):]
    return name[:-2] if name.endswith('_C') else name


ITEM_PATHS = {}   # 'SteelPlate' -> '/Game/.../Desc_SteelPlate.Desc_SteelPlate_C' (for blueprint cost lists)


def amounts(s):
    """'((ItemClass="...'/Game/.../Desc_SteelPlate.Desc_SteelPlate_C'",Amount=1),...)' -> [('SteelPlate', 1)]"""
    out = []
    for m in re.finditer(r"ItemClass=\"[^\"']*'?(/Game/[^\"']+?\.([\w]+))'?\",Amount=([\d.]+)", s or ''):
        ITEM_PATHS.setdefault(short(m.group(2)), m.group(1))
        out.append((short(m.group(2)), float(m.group(3))))
    return out


def num(v):
    try:
        f = float(v)
        return f if f else None
    except (TypeError, ValueError):
        return None


CATEGORIES = [  # (category, regex on short class name, regex on native class)
    ('Production', r'Constructor|Assembler|Manufacturer|Smelter|Foundry|Refinery|Blender|Packager|Converter|Accelerator|Collider|Encoder|QuantumEncoder', r'Manufacturer|Factory$'),
    ('Extraction', r'Miner|Extractor|WaterPump|Fracking|Geothermal', r'Extractor|Fracking|WaterPump'),
    ('Power', r'Generator|PowerPole|PowerLine|PowerStorage|PowerSwitch|PriorityPowerSwitch|PowerBooster|Wire', r'Generator|PowerPole|Wire|PowerStorage|Switch|PowerBooster'),
    ('Belts & lifts', r'Conveyor|Splitter|Merger', r'Conveyor|Splitter|Merger|Attachment'),
    ('Pipes & pumps', r'Pipeline|PipeSupport|Pump|Valve|PipeStorageTank|IndustrialTank|PipeJunction', r'Pipeline|PipeReservoir|PolePipe'),
    ('Hypertubes', r'PipeHyper|Hyper', r'Hyper'),
    ('Trains, vehicles & drones', r'Railroad|Train|Station|Dock|Drone|Truck|Vehicle|Rail', r'Railroad|Train|Docking|Drone|Vehicle'),
    ('Storage', r'Storage|Container|Shelf|Locker', r'Storage|Shelf'),
    ('Glass & windows', r'Window|Glass', r'^$'),
    ('Roofs', r'^Roof', r'^$'),
    ('Foundations, floors & ramps', r'Foundation|Ramp|QuarterPipe|Floor|Frame_Inverted', r'Foundation|Ramp'),
    ('Walls, doors & gates', r'Wall|Door|Gate|Fence|Barrier|Tris|Angular', r'Wall|Door|Barrier'),
    ('Beams & pillars', r'Beam|Pillar', r'Beam|Pillar'),
    ('Walkways, stairs & catwalks', r'Walkway|Catwalk|Stair|Ladder|Railing|Jump|Elevator', r'Walkway|Stair|Ladder|Jumppad|Elevator'),
    ('Lights & signs', r'Light|Sign|Billboard|Floodlight|Lamp', r'Light|Sign'),
]


def category(name, native):
    for cat, rn, rc in CATEGORIES:
        if re.search(rn, name) or (rc != r'^$' and re.search(rc, native)):
            return cat
    return 'Special & other'


def unlock_text(s):
    t, name, tier = s.get('mType', ''), s.get('mDisplayName', ''), s.get('mTechTier', '')
    if t == 'EST_Milestone':
        return 'Tier %s: %s' % (tier, name)
    if t == 'EST_ResourceSink':
        return 'AWESOME Shop: %s' % name
    if t == 'EST_MAM':
        return 'MAM: %s' % name
    if t == 'EST_Tutorial':
        return 'Onboarding: %s' % name
    if t == 'EST_Alternate':
        return 'Hard drive: %s' % name
    if t == 'EST_Custom':
        return 'Start'
    return '%s: %s' % (t.replace('EST_', ''), name)


def build(docs_path):
    by = load_docs(docs_path)
    items = {}
    for native, classes in by.items():
        if 'Descriptor' in native or native in ('FGItemDescriptorBiomass', 'FGItemDescriptorNuclearFuel'):
            for c in classes:
                if c['ClassName'].startswith('Desc_'):
                    items[short(c['ClassName'])] = c.get('mDisplayName', '')
    # build-gun recipes: building descriptor -> ingredients
    recipe_for = {}
    for r in by.get('FGRecipe', []):
        if 'BuildGun' not in r.get('mProducedIn', ''):
            continue
        for prod, _ in amounts(r.get('mProduct')):
            recipe_for.setdefault(prod, (short(r['ClassName']), amounts(r.get('mIngredients'))))
    # unlocks: recipe -> how it's unlocked (prefer milestones / shop over tutorials)
    unlock = {}
    rank = {'EST_Custom': 0, 'EST_Tutorial': 1, 'EST_Milestone': 2, 'EST_ResourceSink': 3, 'EST_MAM': 4}
    for s in by.get('FGSchematic', []):
        for rec in re.findall(r'Recipe_(\w+?)_C', json.dumps(s.get('mUnlocks', ''))):
            prev = unlock.get(rec)
            if prev is None or rank.get(s.get('mType'), 9) < rank.get(prev[0], 9):
                unlock[rec] = (s.get('mType'), unlock_text(s))
    assets = {}
    for native, classes in by.items():
        for c in classes:
            cn = c.get('ClassName', '')
            if not cn.startswith('Build_'):
                continue
            name = short(cn)
            rec = recipe_for.get(name)
            size = {k: num(c.get(k)) for k in ('mWidth', 'mDepth', 'mHeight', 'mSize', 'mDefaultLength', 'mMaxLength')}
            size = {k[1:].lower(): v / 100 for k, v in size.items() if v}       # metres
            per = num(c.get('mLengthPerCost'))
            assets[name] = dict(
                name=c.get('mDisplayName', '') or name,
                category=category(name, native),
                native=native,
                size_m=size,
                cost=[[i, n] for i, n in rec[1]] if rec else [],
                cost_per_m=round(100 / per, 4) if per else None,   # cost list applies per this many m
                recipe=rec[0] if rec else None,
                unlock=unlock.get(rec[0], (None, ''))[1] if rec else '',
            )
    item_paths = {k: v for k, v in ITEM_PATHS.items()}
    return dict(assets=assets, items=items, item_paths=item_paths,
                source='CommunityResources/Docs/en-US.json')


def library_status():
    ix = json.loads((LIB / 'index.json').read_text())
    ready = defaultdict(lambda: dict(versions=[], custom=False))
    for v, d in ix.items():
        for t, e in d['types'].items():
            ready[t]['versions'].append(int(v))
            ready[t]['custom'] |= 'custom' in e['paints']
    return ready


def fmt_size(s):
    if 'width' in s and 'depth' in s:
        return '%g × %g × %g m' % (s['width'], s['depth'], s.get('height', 0))
    if 'defaultlength' in s:
        return 'length %g–%g m' % (s.get('defaultlength', 0), s.get('maxlength', 0))
    if 'size' in s:
        return '%g m' % s['size']
    return ''


def fmt_cost(a, items):
    parts = ['%g %s' % (n, items.get(i, i)) for i, n in a['cost']]
    if a.get('cost_per_m') and parts:
        return ', '.join(parts) + ' per %g m' % (1 / a['cost_per_m'])
    return ', '.join(parts)


def write_markdown(data):
    ready = library_status()
    assets, items = data['assets'], data['items']
    n_ready = sum(1 for k in assets if k in ready)
    order = [c for c, _, _ in CATEGORIES] + ['Special & other']
    groups = defaultdict(list)
    for k, a in assets.items():
        groups[a['category']].append(k)
    lines = [
        '# Every buildable piece in Satisfactory',
        '',
        'Generated from the game\'s own modding data (`CommunityResources/Docs/en-US.json`) by',
        '`scripts/build_assets.py`; machine-readable copy in `assets.json`.',
        '',
        '**%d pieces** in the game. **%d are ready**: the donor library has a sample, so Claude can' % (len(assets), n_ready),
        'place them in a blueprint today. The rest need a sample first (see `CLAUDE.md`).',
        '',
        '- **Ready**: ✅ = sample in the library, 🎨 = also takes any colour.',
        '  Versions are blueprint object versions (36 = Update 8, 42–46 = 1.0, 52–60 = 1.1/1.2).',
        '- **Class**: the name used in code (`Build_<Class>_C` in the game).',
        '- **Cost**: what the build gun charges. Beams and similar pieces cost per length.',
        '- **Unlock**: the milestone, AWESOME Shop pack or MAM research that unlocks the piece.',
        '',
        '## Contents',
        '',
    ]
    for cat in order:
        if groups.get(cat):
            anchor = re.sub(r'[^a-z0-9 -]', '', cat.lower()).replace(' ', '-')
            r = sum(1 for k in groups[cat] if k in ready)
            lines.append('- [%s](#%s): %d pieces, %d ready' % (cat, anchor, len(groups[cat]), r))
    lines.append('')
    for cat in order:
        ks = groups.get(cat)
        if not ks:
            continue
        lines += ['## ' + cat, '', '| Ready | Piece | Class | Size | Cost | Unlock |', '|---|---|---|---|---|---|']
        for k in sorted(ks, key=lambda k: (k not in ready, assets[k]['name'])):
            a, r = assets[k], ready.get(k)
            mark = ''
            if r:
                mark = '✅' + ('🎨' if r['custom'] else '') + ' ' + ','.join(map(str, sorted(r['versions'])))
            lines.append('| %s | %s | `%s` | %s | %s | %s |' % (
                mark, a['name'].replace('|', '/'), k, fmt_size(a['size_m']), fmt_cost(a, items), a['unlock']))
        lines.append('')
    (LIB / 'ASSETS.md').write_text('\n'.join(lines), encoding='utf-8')
    return len(assets), n_ready


def main():
    docs = Path(sys.argv[1]) if len(sys.argv) > 1 else find_docs()
    data = build(docs)
    (LIB / 'assets.json').write_text(json.dumps(data, indent=1, sort_keys=True, ensure_ascii=False), encoding='utf-8')
    total, ready = write_markdown(data)
    print('%d buildable pieces, %d ready in the library -> %s' % (total, ready, LIB / 'ASSETS.md'))


if __name__ == '__main__':
    main()

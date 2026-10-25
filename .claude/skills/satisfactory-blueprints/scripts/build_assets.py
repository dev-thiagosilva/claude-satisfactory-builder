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


# Categories by what a builder wants to do, in the order a building is usually designed.
# First match on the class name wins, so specific groups (glass, doors, logistics walls) come
# before broad ones (walls, foundations). Each has guidance for choosing pieces.
CATEGORIES = [
    dict(title='Special & unique buildings',
         match=r'^(TradingPost|SpaceElevator|MAM|Mam|ResourceSink|ResourceSinkShop|BlueprintDesigner|RadarTower|Portal|PortalSatellite|AlienPowerBuilding|Workshop|WorkBench|CentralStorage)',
         use='Game-progression buildings. Rarely part of a design.',
         tips='The HUB and Space Elevator are one per world, and blueprint designers can\'t go inside a blueprint. Leave these out unless the player asks.',
         goto=[]),
    dict(title='Production machines',
         match=r'^(ConstructorMk|AssemblerMk|ManufacturerMk|SmelterMk|FoundryMk|OilRefinery|Blender|Packager|Converter|HadronCollider|QuantumEncoder)',
         use='Factories: turning resources into parts.',
         tips='Samples come with empty belt/pipe ports and no power. The player connects them in game. Leave clearance for belts on the input/output sides.',
         goto=['ConstructorMk1', 'AssemblerMk1', 'SmelterMk1']),
    dict(title='Extraction',
         match=r'^(MinerMk|OilPump|Fracking|WaterPump)',
         use='Mining and pumping resources.',
         tips='Must sit on a resource node in game, so they rarely suit a free-standing blueprint.',
         goto=[]),
    dict(title='Power',
         match=r'^(Generator|PowerPole|PowerTower|PowerLine|PowerStorage|PowerSwitch|PriorityPowerSwitch|CircuitSwitch|XmassLightsLine)',
         use='Generating and distributing electricity.',
         tips='Power lines need two ends, so the player draws them in game. Wall poles mount on walls; Mk2/Mk3 poles allow more connections.',
         goto=['PowerPoleMk1', 'PowerPoleWall', 'PowerStorageMk1']),
    dict(title='Belts, lifts & sorting',
         match=r'^(Conveyor|Wall_Conveyor|Wall_Concrete_8x4_ConveyorHole)',
         use='Moving items: belts, lifts, splitters/mergers, belt supports and wall/floor pass-throughs.',
         tips='Belt and lift samples are short pieces with cut ends. Long runs are easier to draw in game. Mk number = speed tier.',
         goto=['ConveyorAttachmentSplitter', 'ConveyorAttachmentMerger', 'ConveyorPole']),
    dict(title='Pipes & fluids',
         match=r'^(Pipeline|PipeSupport|PipeStorage|IndustrialTank|Valve|FoundationPassthrough_Pipe)',
         use='Moving and storing liquids and gases.',
         tips='Mk2 pipes carry twice as much. Pumps add head lift for vertical runs.',
         goto=['PipelineSupport', 'PipeStorageTank']),
    dict(title='Hypertubes',
         match=r'^(PipeHyper|Hyper|HyperTube|FoundationPassthrough_Hypertube)',
         use='Player transport tubes.',
         tips='Entrances need power in game.',
         goto=[]),
    dict(title='Trains, vehicles & drones',
         match=r'^(Railroad|Train|TruckStation|FluidTruckStation|DroneStation|VehiclePath|LandingPad)',
         use='Rail, truck and drone logistics.',
         tips='Stations depend on their built-in track and are best placed in game. Railway samples work as decorative track.',
         goto=['RailroadTrack']),
    dict(title='Storage',
         match=r'^(Storage|StoragePlayer|StorageMedkit|StorageHazard|StackableShelf)',
         use='Item storage: containers, lockers.',
         tips='Mk2 containers hold twice as much in the same 2 m footprint.',
         goto=['StorageContainerMk1', 'StorageContainerMk2']),
    dict(title='Floors & foundations',
         match=r'^(Foundation|Flat_Frame|FoundationGlass)',
         use='Ground, floors, plazas, platforms and slabs between storeys.',
         tips='8 × 8 m grid, 1/2/4 m thick. Materials: concrete, polished concrete (light, smooth), asphalt (dark, roads), metal/grip, Ficsit (orange). Glass foundations make glass floors and skylights; frame foundations are see-through.',
         goto=['Foundation_Concrete_8x1', 'Foundation_ConcretePolished_8x1', 'FoundationGlass_01', 'Foundation_Frame_01']),
    dict(title='Ramps, slopes & rounded edges',
         match=r'^(Ramp|InvertedRamp|RampDouble|RampInverted|QuarterPipe|DownQuarterPipe)',
         use='Slopes, sloped roofs and tiers, and rounded 90° edges between a floor and a wall (quarter pipes).',
         tips='Ramp 8x1/8x2/8x4 rise 1/2/4 m over 8 m; double ramps rise 2× over 16 m; inverted ramps slope the underside. Quarter pipes curve up (QuarterPipe) or down (DownQuarterPipe); In/OutCorner pieces round the corners.',
         goto=['Ramp_Concrete_8x2', 'QuarterPipeMiddle_Concrete_8x4', 'DownQuarterPipe_Concrete_8x4', 'InvertedRamp_Concrete_8x2']),
    dict(title='Glass & windows',
         match=r'(Window|Glass)',
         use='Curtain walls, shop fronts, greenhouses, glass roofs.',
         tips='Full Frame Window (Wall_Window_Thin_8x4_01) is the cleanest glass wall: a fine mullion grid that takes any colour. Wall_*_Window_0X are solid walls with window openings. Roof_Window_* are glass roofs.',
         goto=['Wall_Window_Thin_8x4_01', 'Wall_Window_8x4_03', 'Wall_Concrete_8x4_Window_01', 'Roof_Window_01']),
    dict(title='Doors & gates',
         match=r'(Door|Gate)',
         use='Entrances: personnel doors, automatic gates, big garage doors for vehicles.',
         tips='Doors fill a standard 8 × 4 m wall slot; garage doors are 16 × 8 m.',
         goto=['Wall_Door_8x4_01', 'Gate_Automated_8x4', 'BigGarageDoor_16x8']),
    dict(title='Roofs',
         match=r'^Roof',
         use='Pitched and flat roofs.',
         tips='_01/_02/_03 are three pitches; In/OutCorner pieces turn corners. Materials: metal, orange (Ficsit), tar, glass (Roof_Window).',
         goto=['Roof_Metal_01', 'Roof_A_01', 'Roof_Window_01']),
    dict(title='Walls & facades',
         match=r'(Wall|Tris|Angular|Corner_0|Corner_2)',
         use='Building envelopes and facades.',
         tips='8 × 4 m (or 8 × 1 m strips). Tris/FlipTris are triangles for gables, Angular are diagonals, Corner pieces turn 90°. Materials: concrete, steel, orange (Ficsit, Wall_8x4_01).',
         goto=['Wall_Concrete_8x4', 'SteelWall_8x4', 'Wall_8x4_01', 'Wall_Concrete_Tris_8x4']),
    dict(title='Beams, pillars & structure',
         match=r'^(Beam|Pillar)',
         use='Frames, columns, trusses, outlines, and free-form curves.',
         tips='Painted Beam is the most flexible piece in the game: any length (up to 40 m), any angle, any colour. Lay beams side by side to make smooth curved surfaces (see the Heydar example). Pillars make columns; connectors and supports join beams.',
         goto=['Beam_Painted', 'Beam', 'PillarMiddle_Concrete', 'Pillar_Small_Concrete']),
    dict(title='Walkways, stairs, railings & fences',
         match=r'^(Walkway|Catwalk|Stairs|Stair_|Ladder|Railing|Fence|ChainLinkFence|TarpFence|Barrier|Concrete_Barrier|Elevator|JumpPad)',
         use='Getting around and edging: walkways, catwalks, stairs, ladders, elevators, railings, fences, barriers.',
         tips='Catwalks are 4 m wide with railings; walkways are open. Stair_* are foundation-sized stairs (8 × 8 m, rising 1/2/4 m) that match the foundation materials. Barriers and fences line roads and plazas.',
         goto=['CatwalkStraight', 'WalkwayStraight', 'Stairs_Left_01', 'Railing_01', 'Barrier_Low_01']),
    dict(title='Lights, signs & decoration',
         match=r'(Light|Sign|Floodlight|Xmas|Snowman|Snow|TreeGift|CandyCane|Wreath|PortalPotty|LookoutTower|LargeFan|LargeVent)',
         use='Lighting, labels and decoration.',
         tips='Signs show "Set Text Here" until the player edits them in game. Lights need power.',
         goto=['CeilingLight', 'StreetLight', 'FloodlightWall', 'StandaloneWidgetSign_Medium']),
]

QUICK_PICKER = [
    ('A flat floor, plaza or platform', 'Foundation_Concrete_8x1, Foundation_ConcretePolished_8x1'),
    ('A glass floor or skylight', 'FoundationGlass_01'),
    ('A slope, ramp or tiered seating', 'Ramp_Concrete_8x1 / 8x2 / 8x4, RampDouble_*'),
    ('A rounded 90° edge', 'QuarterPipeMiddle_* (curves up), DownQuarterPipe_* (curves down), *InCorner/*OutCorner'),
    ('Free-form curves, organic shapes, outlines, lattices', 'Beam_Painted (any length/angle/colour), laid side by side'),
    ('A solid wall', 'Wall_Concrete_8x4, SteelWall_8x4, Wall_8x4_01 (Ficsit orange)'),
    ('A triangle (gable) or diagonal wall', '*_Tris_*, *_FlipTris_*, *_Angular_*'),
    ('A glass wall / curtain wall', 'Wall_Window_Thin_8x4_01 (any colour)'),
    ('A wall with windows', 'Wall_Concrete_8x4_Window_01…04, SteelWall_8x4_Window_*'),
    ('A pitched roof', 'Roof_Metal_01…03 + In/OutCorner; glass: Roof_Window_*'),
    ('A flat roof', 'Roof_A_01, or foundations'),
    ('Columns', 'PillarMiddle_Concrete, Pillar_Small_*'),
    ('A door or garage door', 'Wall_Door_8x4_01, Gate_Automated_8x4, BigGarageDoor_16x8'),
    ('Walkways and stairs', 'CatwalkStraight/Stairs, WalkwayStraight, Stairs_Left_01'),
    ('Railings, fences, road barriers', 'Railing_01, Fence_01, Barrier_Low_01'),
    ('Lights', 'CeilingLight, StreetLight, FloodlightWall'),
    ('A label or sign', 'StandaloneWidgetSign_*'),
    ('A factory floor', 'Production machines + Belts, lifts & sorting (player connects them in game)'),
]


def category(name, native=''):
    for c in CATEGORIES:
        if re.search(c['match'], name):
            return c['title']
    return 'Other'


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
    unlock, recipe_paths = {}, {}
    rank = {'EST_Custom': 0, 'EST_Tutorial': 1, 'EST_Milestone': 2, 'EST_ResourceSink': 3, 'EST_MAM': 4}
    for s in by.get('FGSchematic', []):
        text = json.dumps(s.get('mUnlocks', '')).replace('\\', '')
        names = []
        for m in re.finditer(r"(/Game/[\w/\-]+/Recipe_(\w+)\.Recipe_\2_C)", text):
            recipe_paths.setdefault(m.group(2), m.group(1))
            names.append(m.group(2))
        for rec in names:
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
            desc = ITEM_PATHS.get(name)   # the building's descriptor, e.g. .../Desc_X.Desc_X_C
            class_path = re.sub(r'Desc_(\w+)\.Desc_\1_C$', r'Build_\1.Build_\1_C', desc) if desc else None
            assets[name] = dict(
                class_path=class_path,
                recipe_path=recipe_paths.get(rec[0]) if rec else None,
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
    ready = defaultdict(lambda: dict(versions=[], custom=False, real=False))
    for v, d in ix.items():
        for t, e in d['types'].items():
            ready[t]['versions'].append(int(v))
            ready[t]['custom'] |= 'custom' in e['paints']
            ready[t]['real'] |= not e.get('synthetic')
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
    # design categories first (in the order a building is designed), factory groups after
    design = [c for c in CATEGORIES[9:]]
    factory = [c for c in CATEGORIES[1:9]]
    cats = design + factory + [CATEGORIES[0]]
    order = [c['title'] for c in cats] + ['Other']
    groups = defaultdict(list)
    for k, a in assets.items():
        a['category'] = category(k, a.get('native', ''))   # always from the current scheme
        groups[a['category']].append(k)
    lines = [
        '# Every buildable piece in Satisfactory',
        '',
        'Generated from the game\'s own modding data (`CommunityResources/Docs/en-US.json`) by',
        '`scripts/build_assets.py`; machine-readable copy in `assets.json`.',
        '',
        '**%d pieces** in the game. **%d are ready** (%d from real builds, %d made from similar pieces):' % (
            len(assets), n_ready, sum(1 for k in assets if ready.get(k, {}).get('real')),
            sum(1 for k in assets if k in ready and not ready[k]['real'])),
        'the donor library has a sample, so Claude can place them in a blueprint today.',
        '',
        '- **Ready**: ✅ = sample taken from a real build; 🧪 = sample made from a similar piece of the',
        '  same kind (should work, not yet confirmed in game); 🎨 = also takes any colour;',
        '  ⛔ legacy = no build recipe in the current game (old or event pieces).',
        '  Versions are blueprint object versions (36 = Update 8, 42–46 = 1.0, 52–60 = 1.1/1.2).',
        '- **Class**: the name used in code (`Build_<Class>_C` in the game).',
        '- **Cost**: what the build gun charges. Beams and similar pieces cost per length.',
        '- **Unlock**: the milestone, AWESOME Shop pack or MAM research that unlocks the piece.',
        '',
        '## Quick picker',
        '',
        '| I want… | Use |',
        '|---|---|',
    ] + ['| %s | %s |' % row for row in QUICK_PICKER] + [
        '',
        'Combine materials from one family for a consistent look (e.g. concrete walls + polished',
        'concrete floors + concrete pillars). Use painted beams wherever a shape doesn\'t fit the 8 m',
        'grid.',
        '',
        '## Contents',
        '',
    ]
    def anchor(t):
        return re.sub(r'[^a-z0-9 -]', '', t.lower()).replace(' ', '-')
    lines.append('**Building design**')
    lines.append('')
    for c in design:
        ks = groups.get(c['title'], [])
        if ks:
            lines.append('- [%s](#%s): %d pieces, %d ready' % (c['title'], anchor(c['title']), len(ks), sum(1 for k in ks if k in ready)))
    lines += ['', '**Factory & logistics**', '']
    for c in factory + [CATEGORIES[0]]:
        ks = groups.get(c['title'], [])
        if ks:
            lines.append('- [%s](#%s): %d pieces, %d ready' % (c['title'], anchor(c['title']), len(ks), sum(1 for k in ks if k in ready)))
    if groups.get('Other'):
        lines.append('- [Other](#other): %d pieces' % len(groups['Other']))
    lines.append('')
    info = {c['title']: c for c in CATEGORIES}
    for cat in order:
        ks = groups.get(cat)
        if not ks:
            continue
        lines += ['## ' + cat, '']
        c = info.get(cat)
        if c:
            lines += ['**Use for:** ' + c['use'], '', '**Tips:** ' + c['tips'], '']
            goto = [g for g in c['goto'] if g in assets]
            if goto:
                lines += ['**Go-to pieces:** ' + ', '.join('%s (`%s`)%s' % (
                    assets[g]['name'], g, '' if g in ready else ' – not ready yet') for g in goto), '']
        lines += ['| Ready | Piece | Class | Size | Cost | Unlock |', '|---|---|---|---|---|---|']
        for k in sorted(ks, key=lambda k: (k not in ready, assets[k]['name'])):
            a, r = assets[k], ready.get(k)
            mark = '⛔ legacy' if not a['recipe'] and not r else ''
            if r:
                mark = ('✅' if r['real'] else '🧪') + ('🎨' if r['custom'] else '') + ' ' + \
                    ','.join(map(str, sorted(r['versions'])))
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

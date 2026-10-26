"""Build the donor library shipped with the skill (maintainer tool). Game 1.2 only.

Writes library/donors-v60.sbp with one sample of each building type (palette paint, and custom
RGB paint when possible), taken from game-1.1/1.2 blueprints and save files:
  - clean samples (referencing nothing outside themselves) are taken as they are;
  - pieces only ever seen wired up get their links to other buildings removed (empty ports);
  - every lightweight structure (foundations, ramps, walls, roofs, beams, pillars, walkways…)
    is made from a real 1.2 structure sample by swapping class and recipe, since in 1.2 they all
    share one property set;
  - anything carrying a player's account data, and signs/stations from saves (player-typed
    text), is skipped.
Samples are laid out on a grid, so rendering the library file gives a visual catalogue.

  python -I build_library.py "<blueprints root>" [--save world.sav ...] [--out library]
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


# ---------- tagged properties (both layouts) ----------
# 1.0 layout (object versions <= 52): name, type, int32 size, int32 array index, a type-specific
# header (struct name + GUID + flag, enum/inner type name + flag, ...), then the value.
# 1.2 layout (object versions >= 53): name, the type as a tree (FString + int32 child count,
# recursively), int32 size, uint8 flags (+ int32 index / 16-byte GUID when flagged), the value.
NEW_TAGS_FROM = 53


def _fstr(s):
    b = (s + '\0').encode('latin1') if s else b''
    return struct.pack('<i', len(b)) + b


def _type_tree(r):
    name = r.string()
    return [name] + [_type_tree(r) for _ in range(r.i32())]


def prop_spans(blob, new=False):
    """Top-level tagged properties of a blob: list of dicts (name, type, start, size_at, value,
    end) and the offset of the closing 'None'. Raises if the list doesn't parse cleanly."""
    from sbp import Reader
    m = re.search(rb'\x00\x00\x00([A-Za-z]\w+)\x00.{4}(\w+Property)\x00', blob, re.S)
    if not m:
        return [], None
    start = blob.rfind(_fstr(m.group(1).decode()), 0, m.end())
    r, spans = Reader(blob, start), []
    while True:
        s = r.o
        name = r.string()
        if name == 'None':
            return spans, s
        if new:
            t = _type_tree(r)[0]
            size_at = r.o; size = r.i32()
            flags = blob[r.o]; r.o += 1
            if flags & 0x01: r.o += 4
            if flags & 0x02: r.o += 16
            if flags & 0x04:
                raise ValueError('property extensions not supported (%s)' % name)
        else:
            t = r.string(); size_at = r.o; size = r.i32(); r.i32()
            if t == 'StructProperty': r.string(); r.o += 17
            elif t == 'BoolProperty': r.o += 2; size = 0
            elif t in ('ByteProperty', 'EnumProperty', 'ArrayProperty', 'SetProperty'): r.string(); r.o += 1
            elif t == 'MapProperty': r.string(); r.string(); r.o += 1
            else: r.o += 1
        if size < 0 or r.o + size > len(blob):
            raise ValueError('bad property list at %s' % name)
        v = r.o
        r.o += size
        spans.append(dict(name=name, type=t, start=s, size_at=size_at, value=v, end=r.o))


def _span(blob, name, new):
    spans, _ = prop_spans(blob, new)
    return next((sp for sp in spans if sp['name'] == name), None)


def none_offset(blob, new=True):
    """Offset of the 'None' that closes a blob's top-level property list, where new properties
    go. Works for blobs with no properties yet (prop_spans finds no list to walk there)."""
    spans, none_at = prop_spans(blob, new)
    if none_at is None:
        none_at = blob.index(_fstr('None'))
    return none_at


def add_prop(blob, tag_and_value, new=True):
    """Append one tagged property (tag + value bytes) to a blob's property list."""
    at = none_offset(blob, new)
    return blob[:at] + tag_and_value + blob[at:]


def set_object_prop(blob, name, path, new=False):
    sp = _span(blob, name, new)
    if not sp:
        raise KeyError(name)
    if sp['type'] != 'ObjectProperty':
        raise ValueError('%s is %s' % (name, sp['type']))
    value = _fstr('') + _fstr(path)
    head = bytearray(blob[:sp['value']])
    struct.pack_into('<i', head, sp['size_at'], len(value))
    return bytes(head) + value + blob[sp['end']:]


def drop_prop(blob, name, new=False):
    sp = _span(blob, name, new)
    return blob if not sp else blob[:sp['start']] + blob[sp['end']:]


def cut_links(actor, comps, new=False, extra=()):
    """Copy of (actor, comps) with every property that points outside them removed (belt/pipe
    connections, wires, snapped attachments). `extra` are companion (actor, comps) pairs kept in
    the sample, e.g. a station's built-in track; links between group members stay. Returns
    (actor, comps, [(companion, comps)...]) or None if that isn't possible cleanly."""
    group = [(actor, comps)] + list(extra)
    own = {o['path'].split('.', 1)[1] for a, cs in group for o in [a] + cs}

    def external(b):
        return any(r.decode() != 'BuildableSubsystem' and r.decode() not in own and
                   r.decode().split('.')[0] not in own for r in REF.findall(b))

    out = []
    for o in [o for a, cs in group for o in [a] + cs]:
        o = copy.deepcopy(o)
        if external(o['data']):
            try:
                spans, _ = prop_spans(o['data'], new)
            except (ValueError, struct.error):
                return None
            blob = o['data']
            for sp in reversed(spans):
                if external(blob[sp['start']:sp['end']]):
                    blob = blob[:sp['start']] + blob[sp['end']:]
            if external(blob):
                return None
            o['data'] = blob
            o['_cut'] = True
        out.append(o)
    res, i = [], 0
    for a, cs in group:
        res.append((out[i], out[i + 1:i + 1 + len(cs)]))
        i += 1 + len(cs)
    return res[0][0], res[0][1], res[1:]


# A wire with no ends makes no sense: power lines are kept as a template with both ends blanked
# (factory.py fills in where each one runs and what it joins).
NO_CUT = {'PowerLine'}
WIRE_VEC = re.compile(rb'(Locations|CachedRelativeLocations)\x00.*?/Script/CoreUObject\x00\x00\x00\x00\x00\x18\x00\x00\x00[\x08\x09]', re.S)


def blank_wire(actor):
    """Copy of a power line with no ends: zero positions and length, empty end references."""
    from sbp import find_prop
    a = copy.deepcopy(actor)
    spans, none_at = prop_spans(a['data'], True)
    blob = bytearray(a['data'][:none_at + len(_fstr('None'))] + bytes(4) + (_fstr('') + _fstr('')) * 2)
    sp = _span(bytes(blob), 'mWireInstances', True)
    for m in WIRE_VEC.finditer(bytes(blob), sp['value'], sp['end']):
        struct.pack_into('<3d', blob, m.end() + (4 if blob[m.end() - 1] & 1 else 0), 0.0, 0.0, 0.0)
    off, t = find_prop(bytes(blob), 'mCachedLength')
    if off is not None:
        struct.pack_into('<f', blob, off, 0.0)
    a['data'] = bytes(blob)
    return a
# Train platforms only work together with their built-in track: sample them as a group.
GROUPED = {'TrainStation', 'TrainDockingStation', 'TrainDockingStationLiquid',
           'TrainPlatformEmpty', 'TrainPlatformEmpty_02'}
COMPANION = re.compile(r'/Build_RailroadTrackIntegrated\.')


TARGET_VERSION = 60      # game 1.2: the library holds only this format


def _float_prop(name, value):
    """A 1.2-layout FloatProperty tag + value."""
    return _fstr(name) + _fstr('FloatProperty') + struct.pack('<iiBf', 0, 4, 0, value)


def _with_props(blob, drop=(), replace=None, add=b''):
    """Rebuild a 1.2-layout blob: drop named properties, replace whole property spans
    ({name: tag+value bytes}), and append extra tags before the closing 'None'."""
    spans, none_at = prop_spans(blob, True)
    out, last = [], spans[0]['start'] if spans else none_at
    head = blob[:last]
    for sp in spans:
        if sp['name'] in drop:
            continue
        out.append(replace.get(sp['name'], blob[sp['start']:sp['end']]) if replace else blob[sp['start']:sp['end']])
    return head + b''.join(out) + add + blob[none_at:]


def synthesize(picks, assets, custom_struct):
    """Samples for every lightweight structure (foundations, ramps, walls, roofs, beams, pillars,
    walkways…) from a real 1.2 structure sample of the closest kind. In 1.2 these all share one
    property set (paint slot, customization, recipe, + length for beams). A custom-RGB variant
    is made by copying a real 1.2 customization block (custom_struct). Returns names added."""
    import difflib
    # templates: real samples without parts or companions
    real = [(t, c, p) for (t, c), p in picks.items()
            if t in assets and not p[2] and not p[1].get('_template') and not p[1].get('_companions')]
    lw = [r for r in real if assets[r[0]].get('lightweight')]
    has_parts = {t for (t, _), p in picks.items() if p[2]}
    # Model variants of one machine (MinerMk1/2/3) share their part layout: a real sample of one
    # model can stand in for the others.
    variants = {}
    for (t, c), p in picks.items():
        if p[2] and not p[1].get('_companions') and not p[1].get('_template') and t in assets:
            variants.setdefault((re.sub(r'Mk\d', 'Mk', t), assets[t]['native']), (t, c, p))
    added = []
    for name, a in sorted(assets.items()):
        if not a.get('class_path') or not a.get('recipe_path'):
            continue
        comps_tpl = None
        if name in has_parts:
            continue
        v = variants.get((re.sub(r'Mk\d', 'Mk', name), a['native']))
        if v and v[0] != name and not any(t2 == name for (t2, _) in picks):
            pool = [v]
        else:
            same = [r for r in real if assets[r[0]]['native'] == a['native']]
            # lightweights share one property set, so any lightweight template will do; other
            # part-less pieces (doors, signs, corner walls) need a template of their own kind
            pool = same if same else (lw if a.get('lightweight') else [])
        if not pool:
            continue
        t, _, (src, actor, comps_tpl) = max(pool, key=lambda r: difflib.SequenceMatcher(None, r[0], name).ratio())
        for custom in (False, True):
            if (name, custom) in picks:
                continue
            if custom and not custom_struct:
                continue
            # keep the template's id so only the class part of the path changes
            new_path = 'Persistent_Level:PersistentLevel.Build_%s_C_%s' % (name, actor['path'].rsplit('_', 1)[1])
            data = replace_string(actor['data'], actor['path'], new_path)
            new_comps = []
            for c in comps_tpl or []:
                nc = copy.deepcopy(c)
                nc['path'] = c['path'].replace(actor['path'], new_path)
                nc['outer'] = new_path
                nc['data'] = replace_string(nc['data'], actor['path'], new_path)
                data = replace_string(data, c['path'], nc['path'])
                new_comps.append(nc)
            try:
                data = set_object_prop(data, 'mBuiltWithRecipe', a['recipe_path'], True)
                beam = a['native'] == 'FGBuildableBeam'
                has_len = _span(data, 'mLength', True) is not None
                data = _with_props(
                    data,
                    drop={'mOriginalBuildableVariant', 'BuiltBy'} | (set() if beam else {'mLength'}),
                    replace={'mCustomizationData': custom_struct} if custom else None,
                    add=_float_prop('mLength', 400.0) if beam and not has_len else b'')
            except (KeyError, ValueError, struct.error) as e:
                print('  cannot synthesize %s from %s (%s)' % (name, t, e), file=sys.stderr)
                continue
            s = dict(copy.deepcopy(actor), cls=a['class_path'], path=new_path, data=data,
                     _template=t if name != t else None)
            if name == t:          # same piece, only repainted
                s['_repainted'] = True
            picks[(name, custom)] = (src, s, new_comps)
            added.append(name)
    return sorted(set(added))


def modern_sources(root, saves):
    """(origin, actor, components, lookup) for every 1.2-format building in the blueprints under
    root and in the given save files, newest first. lookup maps a path to (actor, components)."""
    import sav as savmod
    bps = []
    for f in sorted(Path(root).rglob('*.sbp')):
        try:
            bp = Blueprint.load(f)
        except Exception as e:
            print('skip', f.name, e, file=sys.stderr)
            continue
        if bp.object_version >= NEW_TAGS_FROM:
            bps.append(bp)
    bps.sort(key=lambda b: -b.object_version)
    for bp in bps:
        comp_index = defaultdict(list)
        for o in bp.objects:
            if o['type'] == 0:
                comp_index[o['outer']].append(o)
        lookup = {a['path']: (a, comp_index.get(a['path'], [])) for a in bp.actors()}
        for a in bp.actors():
            yield bp, a, comp_index.get(a['path'], []), lookup
    for f in saves:
        s = savmod.Save(f)
        pairs = list(s.buildings())
        lookup = {a['path']: (a, comps) for a, comps in pairs}
        for a, comps in pairs:
            if a['object_version'] >= NEW_TAGS_FROM and all(c['object_version'] >= NEW_TAGS_FROM for c in comps):
                yield 'save', a, comps, lookup


# Free text players type on signs is theirs: never take signs from a save. (Station names live
# in a separate object, not on the station.)
SAVE_SKIP = re.compile(r'^(StandaloneWidgetSign|SignPole|Billboard)')


def _element_tags(blob, start, end):
    """Tags of one struct element inside an array value (1.2 layout): list of span dicts."""
    from sbp import Reader
    r, out = Reader(blob, start), []
    while r.o < end:
        s = r.o
        name = r.string()
        if name == 'None':
            return out, r.o
        _type_tree(r)
        size_at = r.o; size = r.i32()
        flags = blob[r.o]; r.o += 1
        if flags & 0x01: r.o += 4
        if flags & 0x02: r.o += 16
        v = r.o; r.o += size
        out.append(dict(name=name, start=s, size_at=size_at, value=v, end=r.o))
    raise ValueError('unterminated struct element')


def empty_inventory(blob):
    """Clear every slot of a 1.2 inventory component: no item, count 0. Slot layout and size
    limits stay; only the contents go (samples come from real worlds and saves)."""
    sp = _span(blob, 'mInventoryStacks', True)
    if not sp:
        return blob
    v0, end = sp['value'], sp['end']
    count = struct.unpack_from('<i', blob, v0)[0]
    pos, elems = v0 + 4, []
    for _ in range(count):
        tags, after = _element_tags(blob, pos, end)
        parts = []
        for t in tags:
            head = bytearray(blob[t['start']:t['value']])
            if t['name'] == 'Item':
                struct.pack_into('<i', head, t['size_at'] - t['start'], 12)
                parts.append(bytes(head) + bytes(12))          # empty InventoryItem
            elif t['name'] == 'NumItems':
                parts.append(bytes(head) + struct.pack('<i', 0))
            else:
                parts.append(blob[t['start']:t['end']])
        elems.append(b''.join(parts) + _fstr('None'))
        pos = after
    value = struct.pack('<i', count) + b''.join(elems)
    head = bytearray(blob[:v0])
    struct.pack_into('<i', head, sp['size_at'], len(value))
    return bytes(head) + value + blob[end:]


def sanitize(objs):
    """Make samples neutral: empty all inventories (no free items, shards or Somersloops) and
    reset clock speed and production boost to 100% / none."""
    from sbp import find_prop
    for o in objs:
        if 'Inventory' in o['cls']:
            o['data'] = empty_inventory(o['data'])
        for name in ('mCurrentPotential', 'mPendingPotential', 'mCurrentProductionBoost', 'mPendingProductionBoost'):
            off, t = find_prop(o['data'], name)
            if off is not None and t == 'FloatProperty':
                b = bytearray(o['data']); struct.pack_into('<f', b, off, 1.0); o['data'] = bytes(b)
    return objs


def learn_ports(saves, sample_comps):
    """Where each machine's belt/pipe ports and power connections sit, in the machine's own frame
    (cm), learned from the ends of belts, pipes and power lines plugged into it in the given saves. `sample_comps` maps a
    machine type to its port component names; ports never seen plugged in are filled by
    mirroring a sibling port across the machine's centre (marked inferred)."""
    import statistics
    import sav as savmod
    from sbp import qrotate, qconj
    obs = defaultdict(list)
    tags = re.compile(rb'(Location|ArriveTangent|LeaveTangent)\x00.*?/Script/CoreUObject\x00\x00\x00\x00\x00\x18\x00\x00\x00\x08', re.S)
    for f in saves:
        s = savmod.Save(f)
        pairs = list(s.buildings())
        actors = {a['path']: a for a, _ in pairs}
        for a, comps in pairs:
            if a['object_version'] < NEW_TAGS_FROM or not re.match(r'ConveyorBeltMk\d|Pipeline(MK2)?(_NoIndicator)?$', short(a['cls'])):
                continue
            sp = _span(a['data'], 'mSplineData', True)
            if not sp:
                continue
            v = a['data'][sp['value']:sp['end']]
            vals = [(m.group(1).decode(), struct.unpack_from('<3d', v, m.end())) for m in tags.finditer(v)]
            pts = [dict(vals[i:i + 3]) for i in range(0, len(vals), 3)]
            if len(pts) < 2:
                continue
            for c in comps:
                m = re.search(rb'PersistentLevel\.(Build_\w+?_C_\d+)\.(\w+)\x00', c['data'])
                target = m and actors.get('Persistent_Level:PersistentLevel.' + m.group(1).decode())
                if not target:
                    continue
                first = c['path'].endswith('0')
                p = pts[0] if first else pts[-1]
                world = [a['pos'][i] + d for i, d in enumerate(qrotate(a['rot'], p['Location']))]
                local = qrotate(qconj(target['rot']), [world[i] - target['pos'][i] for i in range(3)])
                tan = qrotate(qconj(target['rot']), qrotate(a['rot'], p['LeaveTangent'] if first else p['ArriveTangent']))
                obs[(short(target['cls']), m.group(2).decode())].append((local, tan))
        # power: where each wire end sits on the building it's plugged into
        for a, comps in pairs:
            if a['object_version'] < NEW_TAGS_FROM or short(a['cls']) != 'PowerLine':
                continue
            sp = _span(a['data'], 'mWireInstances', True)
            spans, none_at = prop_spans(a['data'], True)
            if not sp or none_at is None:
                continue
            v = a['data']
            locs = [struct.unpack_from('<3d', v, m.end() + (4 if v[m.end() - 1] & 1 else 0))
                    for m in WIRE_VEC.finditer(v, sp['value'], sp['end']) if m.group(1) == b'Locations'][:2]
            ends = re.findall(rb'PersistentLevel\.(Build_\w+?_C_\d+)\.(\w+)\x00', v[none_at:])
            for (path, comp), loc in zip(ends, locs):
                target = actors.get('Persistent_Level:PersistentLevel.' + path.decode())
                if target:
                    local = qrotate(qconj(target['rot']), [loc[i] - target['pos'][i] for i in range(3)])
                    obs[(short(target['cls']), comp.decode())].append((local, None))
    ports = defaultdict(dict)
    for (t, port), L in obs.items():
        pos = [round(statistics.median(o[0][i] for o in L), 1) for i in range(3)]
        spread = max(statistics.pstdev(o[0][i] for o in L) for i in range(3)) if len(L) > 1 else 0
        if spread > 5:          # belts/splitters snap anywhere along a belt: not a fixed port
            continue
        ports[t][port] = dict(pos=pos, seen=len(L))
    # mirror unseen ports from a sibling of the same kind (Input1 <- Input0 at -x)
    for t, names in sample_comps.items():
        known = ports.get(t, {})
        if not known:
            continue
        for n in names:
            if n in known:
                continue
            kind = re.sub(r'\d+$', '', n)
            sib = [k for k in known if re.sub(r'\d+$', '', k) == kind]
            for k in sib:
                p = known[k]['pos']
                cand = [-p[0], p[1], p[2]]
                if all(abs(cand[0] - q['pos'][0]) > 50 or abs(cand[1] - q['pos'][1]) > 50 for q in known.values()):
                    ports[t][n] = dict(pos=cand, seen=0, inferred=True)
                    break
    return {t: dict(sorted(p.items())) for t, p in sorted(ports.items())}


def main(root, out_dir, saves=()):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    assets = json.loads((out_dir / 'assets.json').read_text(encoding='utf-8'))['assets']
    picks, cut_picks = {}, {}
    base, custom_struct = None, None
    for origin, a, comps, lookup in modern_sources(root, saves):
        if base is None and origin != 'save' and origin.object_version == TARGET_VERSION:
            base = origin
        t = short(a['cls'])
        if '/Build_' not in a['cls'] or t not in assets:
            continue
        if PERSONAL.search(a['data']) or any(PERSONAL.search(c['data']) for c in comps):
            continue
        if origin == 'save' and SAVE_SKIP.search(t):
            continue
        custom = b'PrimaryColor' in a['data']
        if custom and custom_struct is None:
            sp = _span(a['data'], 'mCustomizationData', True)
            if sp:
                custom_struct = a['data'][sp['start']:sp['end']]
        key = (t, custom)
        if key in picks:
            continue
        extra = []
        if t in GROUPED:   # bring the built-in track(s) along
            for m in REF.finditer(b''.join(o['data'] for o in [a] + comps)):
                p = 'Persistent_Level:PersistentLevel.' + m.group(1).decode().split('.')[0]
                if p in lookup and COMPANION.search(lookup[p][0]['cls']) and lookup[p] not in extra:
                    extra.append(lookup[p])
            if not extra:
                continue
        if t in NO_CUT:
            picks[key] = (origin, blank_wire(a), comps)
        elif not extra and is_clean(None, a, comps):
            picks[key] = (origin, a, comps)
        elif t not in NO_CUT and key not in cut_picks:
            cut = cut_links(a, comps, True, extra)
            if cut:
                actor_c, comps_c, extra_c = cut
                if extra_c:
                    actor_c['_companions'] = extra_c
                cut_picks[key] = (origin, actor_c, comps_c)
    if base is None:
        raise SystemExit('need at least one game-1.2 blueprint (object version %d) for the header' % TARGET_VERSION)
    for key, pick in cut_picks.items():
        picks.setdefault(key, pick)
    added = synthesize(picks, assets, custom_struct)
    print('real samples: %d types | pieces made from similar samples: %d'
          % (len({t for (t, _), p in picks.items() if not p[1].get('_template')}), len(added)))

    lib = Blueprint()
    for attr in ('header_version', 'object_version', 'build_version', 'extra_header',
                 'object_flags', 'chunk_v2'):
        setattr(lib, attr, getattr(base, attr))
    recipes, entries = set(), {}
    next_id = 2140000000
    keys = sorted(picks)
    cols = max(1, int(len(keys) ** 0.5))
    def clean(o):
        return {k: v for k, v in copy.deepcopy(o).items() if not k.startswith('_')
                and k not in ('object_version', 'save_tail')}

    # New ids keep the original digit count: references also sit inside longer strings
    # (e.g. '...Track_C_550377992.TrackConnection1') whose stored sizes must not change.
    next_ids = {}

    def fresh_path(path):
        prefix, num = path.rsplit('_', 1)
        n = len(num)
        nxt = next_ids.get(n, 10 ** (n - 1) + 7000000 if n > 7 else 10 ** (n - 1))
        next_ids[n] = nxt + 1
        return '%s_%d' % (prefix, nxt)

    for i, key in enumerate(keys):
        origin, actor, comps = picks[key]
        group = [(actor, comps)] + list(actor.get('_companions', []))
        renames = {g['path']: fresh_path(g['path']) for g, _ in group}
        grid = [(i % cols) * GRID, (i // cols) * GRID, 0.0]
        for g, gcomps in group:
            a = clean(g)
            for old, new in renames.items():
                a['data'] = replace_string(a['data'], old, new)
            if g is actor:
                a['pos'], a['scale'] = list(grid), [1.0, 1.0, 1.0]
                if not group[1:]:
                    a['rot'] = [0.0, 0.0, 0.0, 1.0]
            else:    # companions keep their place relative to the main piece
                a['pos'] = [grid[k] + g['pos'][k] - actor['pos'][k] for k in range(3)]
            a['path'], a['level'] = renames[g['path']], 'Persistent_Level'
            lib.objects.append(a)
            for c in gcomps:
                nc = clean(c)
                for old, new in renames.items():
                    nc['data'] = replace_string(nc['data'], old, new)
                nc['path'] = c['path'].replace(g['path'], renames[g['path']])
                nc['outer'], nc['level'] = renames[g['path']], 'Persistent_Level'
                lib.objects.append(nc)
            if g is actor:
                main = a
        a = main
        m = RECIPE.search(a['data'])
        if m:
            recipes.add(m.group(1).decode())
        t, custom = key
        e = entries.setdefault(t, dict(paints=[], recipe=m.group(1).decode() if m else None,
                                        components=len(comps)))
        e['paints'].append('custom' if custom else (swatch(actor) or 'none'))
        if actor.get('_cut') or any(c.get('_cut') for c in comps):
            e['cut'] = True                     # links to other buildings removed
        if actor.get('_template'):
            e['synthetic'] = True               # made from a similar 1.2 sample
            e['template'] = actor['_template']
        e.setdefault('source', 'save' if origin == 'save' else 'blueprint')
        if group[1:]:
            e['companions'] = sorted({short(g['cls']) for g, _ in group[1:]})
    sanitize(lib.objects)
    lib.dims = [int(cols * GRID / 800) + 2, int((len(keys) // cols + 1) * GRID / 800) + 2, 4]
    lib.recipes = sorted(recipes)
    for old in out_dir.glob('donors-v*.sbp'):
        old.unlink()
    path = out_dir / ('donors-v%d.sbp' % TARGET_VERSION)
    lib.save(path)
    check = Blueprint.load(path)
    assert len(check.objects) == len(lib.objects)
    index = {str(TARGET_VERSION): dict(file=path.name, types=entries)}
    (out_dir / 'index.json').write_text(json.dumps(index, indent=1, sort_keys=True))
    print('v%d: %d types, %d objects, %.0f KB' % (TARGET_VERSION, len(entries), len(lib.objects),
                                                 path.stat().st_size / 1024))
    import build_assets
    build_assets.write_markdown(json.loads((out_dir / 'assets.json').read_text(encoding='utf-8')))
    if saves:
        sample_comps = {}
        for o in lib.actors():
            names = [c['path'].rsplit('.', 1)[1] for c in lib.components_of(o)
                     if re.search(r'FactoryConnection|PipeConnection', c['cls'])]
            if names:
                sample_comps[short(o['cls'])] = names
        ports = learn_ports(saves, sample_comps)
        (out_dir / 'ports.json').write_text(json.dumps(ports, indent=1))
        print('ports: %d machine types (%d ports, %d inferred)' % (
            len(ports), sum(len(p) for p in ports.values()),
            sum(1 for p in ports.values() for q in p.values() if q.get('inferred'))))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='Build the game-1.2 donor library.')
    ap.add_argument('blueprints_root', help='folder with blueprint session folders')
    ap.add_argument('--save', action='append', default=[], help='a .sav file to take samples from (repeatable)')
    ap.add_argument('--out', default=str(Path(__file__).resolve().parent.parent / 'library'))
    a = ap.parse_args()
    main(a.blueprints_root, a.out, a.save)

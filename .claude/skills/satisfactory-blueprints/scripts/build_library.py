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


# ---------- synthesis: samples for pieces nobody has built, from a sibling of the same kind ----------
# Only for the 1.0 property-tag format (object versions 36-46): name, type, int32 size,
# int32 array index, then for ObjectProperty a 1-byte GUID flag and the value
# (FString level + FString path). 1.1+ files use a different tag layout.

def _fstr(s):
    b = (s + '\0').encode('latin1') if s else b''
    return struct.pack('<i', len(b)) + b


def _prop_span(blob, name):
    """(start, value_start, end, type) of a top-level tagged property, or None."""
    key = _fstr(name)
    i = blob.find(key)
    if i < 0:
        return None
    p = i + len(key)
    tlen = struct.unpack_from('<i', blob, p)[0]
    ptype = blob[p + 4:p + 4 + tlen - 1].decode('latin1')
    p += 4 + tlen
    size = struct.unpack_from('<i', blob, p)[0]
    p += 8                                   # size + array index
    if ptype != 'ObjectProperty':
        raise ValueError('unsupported property type %s for %s' % (ptype, name))
    p += 1                                   # has-GUID flag
    return i, p, p + size, ptype


def set_object_prop(blob, name, path):
    span = _prop_span(blob, name)
    if not span:
        raise KeyError(name)
    i, v, end, _ = span
    value = _fstr('') + _fstr(path)
    size_at = v - 9                          # int32 size, int32 index, byte guid
    head = bytearray(blob[:v])
    struct.pack_into('<i', head, size_at, len(value))
    return bytes(head) + value + blob[end:]


def drop_prop(blob, name):
    span = _prop_span(blob, name)
    return blob if not span else blob[:span[0]] + blob[span[2]:]


def prop_spans(blob):
    """Spans (name, start, end) of the top-level tagged properties in a 1.0-format blob, plus the
    offset of the closing 'None'. Raises if the list doesn't parse cleanly."""
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
        t = r.string(); size = r.i32(); r.i32()
        if t == 'StructProperty': r.string(); r.o += 17
        elif t == 'BoolProperty': r.o += 2; size = 0
        elif t in ('ByteProperty', 'EnumProperty', 'ArrayProperty', 'SetProperty'): r.string(); r.o += 1
        elif t == 'MapProperty': r.string(); r.string(); r.o += 1
        else: r.o += 1
        if size < 0 or r.o + size > len(blob):
            raise ValueError('bad property list at %s' % name)
        r.o += size
        spans.append((name, s, r.o))


def cut_links(actor, comps):
    """Copy of (actor, comps) with every property that points outside them removed (belt/pipe
    connections, wires, snapped attachments). None if that isn't possible cleanly."""
    own = {actor['path'].split('.', 1)[1]} | {c['path'].split('.', 1)[1] for c in comps}

    def external(b):
        return any(r.decode() != 'BuildableSubsystem' and r.decode() not in own and
                   r.decode().split('.')[0] not in own for r in REF.findall(b))

    out = []
    for o in [actor] + comps:
        o = copy.deepcopy(o)
        if external(o['data']):
            try:
                spans, _ = prop_spans(o['data'])
            except (ValueError, struct.error):
                return None
            blob = o['data']
            for name, s, e in reversed(spans):
                if external(blob[s:e]):
                    blob = blob[:s] + blob[e:]
            if external(blob):
                return None
            o['data'] = blob
            o['_cut'] = True
        out.append(o)
    return out[0], out[1:]


# A wire/track with no ends makes no sense, and stations depend on their built-in track.
NO_CUT = {'PowerLine', 'RailroadTrackIntegrated', 'TrainStation', 'TrainDockingStation',
          'TrainDockingStationLiquid', 'TrainPlatformEmpty', 'TrainPlatformEmpty_02'}


def synthesize(picks, assets, version):
    """Add samples for every buildable whose kind (game native class) already has a sample in
    this version. Returns the names added."""
    have = {t for t, _ in picks}
    by_native = defaultdict(list)
    for (t, custom), pick in picks.items():
        a = assets.get(t)
        # Only part-less pieces (structures). Machines, storage, poles, belts carry components
        # (inventories, connectors) whose layout differs between models: those need real samples.
        if a and not pick[2] and not pick[1].get('_template'):
            by_native[a['native']].append((t, custom, pick))
    import difflib
    added = []
    for name, a in sorted(assets.items()):
        if name in have or not a.get('class_path') or not a.get('recipe_path'):
            continue
        cands = by_native.get(a['native'])
        if not cands:
            continue
        # prefer a custom-paint template, then the most similar name (e.g. Ramp_8x2 for Ramp_8x4)
        t, custom, (src_bp, actor, comps) = max(
            cands, key=lambda c: (c[1], difflib.SequenceMatcher(None, c[0], name).ratio()))
        new_path = 'Persistent_Level:PersistentLevel.Build_%s_C_1' % name
        s = copy.deepcopy(actor)
        s['cls'] = a['class_path']
        data = s['data']
        new_comps = []
        for c in comps:
            nc = copy.deepcopy(c)
            nc['path'] = c['path'].replace(actor['path'], new_path)
            nc['outer'] = new_path
            nc['data'] = replace_string(nc['data'], actor['path'], new_path)
            data = replace_string(data, c['path'], nc['path'])
            new_comps.append(nc)
        data = replace_string(data, actor['path'], new_path)
        try:
            data = set_object_prop(data, 'mBuiltWithRecipe', a['recipe_path'])
            data = drop_prop(data, 'mOriginalBuildableVariant')
        except (KeyError, ValueError) as e:
            print('  v%d: cannot synthesize %s from %s (%s)' % (version, name, t, e), file=sys.stderr)
            continue
        s['data'], s['path'] = data, new_path
        s['_template'] = t
        picks[(name, custom)] = (src_bp, s, new_comps)
        added.append(name)
    return added


def main(root, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    by_version = defaultdict(dict)     # version -> {(type, custom): (bp, actor, comps)}
    cut_candidates = defaultdict(dict)
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
            if key in by_version[v] or '/Build_' not in a['cls']:   # buildables only
                continue
            comps = comp_index.get(a['path'], [])
            if PERSONAL.search(a['data']) or any(PERSONAL.search(c['data']) for c in comps):
                continue
            if is_clean(bp, a, comps):
                by_version[v][key] = (bp, a, comps)
            elif not bp.object_flags and key[0] not in NO_CUT and key not in cut_candidates[v]:
                cut = cut_links(a, comps)
                if cut:
                    cut_candidates[v][key] = (bp, cut[0], cut[1])
    # pieces only ever seen wired up: use the link-cut copy when no clean sample exists
    for v, cands in cut_candidates.items():
        for key, pick in cands.items():
            by_version[v].setdefault(key, pick)

    assets_file = out_dir / 'assets.json'
    assets = json.loads(assets_file.read_text(encoding='utf-8'))['assets'] if assets_file.exists() else {}
    for v, picks in by_version.items():
        if assets and not bases[v].object_flags:     # 1.0 tag format only
            added = synthesize(picks, assets, v)
            print('v%d: synthesized %d pieces from same-kind samples' % (v, len(added)))

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
            if actor.get('_cut') or any(c.get('_cut') for c in comps):
                e['cut'] = True                # links to other buildings removed
            if actor.get('_template'):
                e['synthetic'] = True          # made from a sibling sample, not seen in game yet
                e['template'] = actor['_template']
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
    # Refresh the full piece list's "ready" column (needs library/assets.json from build_assets.py).
    if (out_dir / 'assets.json').exists():
        import build_assets
        build_assets.write_markdown(json.loads((out_dir / 'assets.json').read_text(encoding='utf-8')))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / 'library')

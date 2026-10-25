"""Read, edit, write and render Satisfactory blueprint (.sbp) files.

CLI:
  python sbp.py info   <file.sbp>                 summary: size, piece counts, cost, recipes
  python sbp.py dump   <file.sbp> <out.json>      every object's class, transform and extracted props
  python sbp.py render <file.sbp> <out.html>      interactive three.js 3D viewer
  python sbp.py roundtrip <file.sbp> <out.sbp>    load + save, then verify the body is identical
  python sbp.py catalog <folder> [out.json]       every piece type available as a donor, per version
  python sbp.py library                           piece types in the shipped donor library, per version

Library:
  from sbp import Blueprint
  bp = Blueprint.load(path); bp.objects[...]; bp.save(path)

Format notes live in ../references/format.md.
"""
import base64, copy, json, os, re, struct, sys, zlib
from pathlib import Path

CHUNK_TAG = 0x9E2A83C1
CHUNK_HEADER = 0x22222222
MAX_CHUNK = 131072
ZLIB = 3


class Reader:
    def __init__(self, data, pos=0):
        self.d, self.o = data, pos

    def i32(self):
        v = struct.unpack_from('<i', self.d, self.o)[0]; self.o += 4; return v

    def floats(self, n):
        v = struct.unpack_from('<%df' % n, self.d, self.o); self.o += 4 * n; return list(v)

    def string(self):
        n = self.i32()
        if n == 0:
            return ''
        if n < 0:
            b = self.d[self.o:self.o - 2 * n]; self.o += -2 * n
            return b.decode('utf-16le').rstrip('\0')
        b = self.d[self.o:self.o + n]; self.o += n
        return b.decode('latin1').rstrip('\0')

    def bytes(self, n):
        b = self.d[self.o:self.o + n]; self.o += n; return b


class Writer:
    def __init__(self):
        self.parts = []

    def i32(self, v):
        self.parts.append(struct.pack('<i', v))

    def floats(self, vs):
        self.parts.append(struct.pack('<%df' % len(vs), *vs))

    def string(self, s):
        if s == '':
            self.i32(0); return
        try:
            b = (s + '\0').encode('latin1'); self.i32(len(b))
        except UnicodeEncodeError:
            b = (s + '\0').encode('utf-16le'); self.i32(-(len(b) // 2))
        self.parts.append(b)

    def raw(self, b):
        self.parts.append(b)

    def getvalue(self):
        return b''.join(self.parts)


def short(cls_path):
    """'/Game/.../Build_Beam_Painted.Build_Beam_Painted_C' -> 'Beam_Painted'"""
    name = cls_path.split('.')[-1]
    if name.startswith('Build_'):
        name = name[len('Build_'):]
    return name[:-2] if name.endswith('_C') else name


class Blueprint:
    def __init__(self):
        self.header_version = 2
        self.object_version = 42
        self.build_version = 0
        self.dims = [4, 4, 4]
        self.cost = []      # [(item class path, amount)]
        self.recipes = []   # [recipe class path]
        self.extra_header = b''
        self.object_flags = False  # True for game 1.2+ files
        self.chunk_v2 = True       # False for pre-1.0 files
        self.objects = []   # see read_body for the keys

    # ---------- reading ----------
    @classmethod
    def load(cls, path):
        data = Path(path).read_bytes()
        bp = cls()
        r = Reader(data)
        bp.header_version, bp.object_version, bp.build_version = r.i32(), r.i32(), r.i32()
        bp.dims = [r.i32(), r.i32(), r.i32()]
        for _ in range(r.i32()):
            r.string()  # level name, always empty
            bp.cost.append((r.string(), r.i32()))
        for _ in range(r.i32()):
            r.string()
            bp.recipes.append(r.string())
        # Game 1.2+ (object version >= ~46) appends engine/custom-version info here; keep it verbatim.
        first_chunk = data.find(struct.pack('<I', CHUNK_TAG), r.o)
        bp.extra_header = data[r.o:first_chunk]
        r.o = first_chunk
        # 1.0+ chunks: tag, 0x22222222, max size, compressor byte (49-byte header).
        # Pre-1.0 chunks: tag, max size as int64, no compressor byte (48 bytes).
        bp.chunk_v2 = struct.unpack_from('<I', data, r.o + 4)[0] == CHUNK_HEADER
        hlen = 49 if bp.chunk_v2 else 48
        body = []
        while r.o < len(data):
            if struct.unpack_from('<I', data, r.o)[0] != CHUNK_TAG:
                raise ValueError('bad chunk tag at %d' % r.o)
            csize = struct.unpack_from('<q', data, r.o + hlen - 32)[0]
            body.append(zlib.decompress(data[r.o + hlen:r.o + hlen + csize]))
            r.o += hlen + csize
        bp.read_body(b''.join(body))
        return bp

    def read_body(self, body):
        # Game 1.2 added an object-flags int after each header's path. Try both layouts and keep
        # the one that ends exactly at the declared header-block size.
        hsize = struct.unpack_from('<i', body, 4)[0]
        for flags in (False, True):
            try:
                r, objs = self._read_headers(body, flags)
            except (struct.error, UnicodeDecodeError):
                continue
            if r.o == 8 + hsize:
                self.object_flags = flags
                break
        else:
            raise ValueError('unrecognised object header layout')
        r.i32()  # data block size
        n = r.i32()
        assert n == len(objs), (n, len(objs))
        for o in objs:
            o['data'] = r.bytes(r.i32())
        self.objects = objs

    @staticmethod
    def _read_headers(body, flags):
        r = Reader(body, 8)
        objs = []
        for _ in range(r.i32()):
            t = r.i32()
            o = dict(type=t, cls=r.string(), level=r.string(), path=r.string())
            if flags:
                o['flags'] = r.i32()
            if t == 1:
                o['need_transform'] = r.i32()
                o['rot'], o['pos'], o['scale'] = r.floats(4), r.floats(3), r.floats(3)
                o['placed'] = r.i32()
            else:
                o['outer'] = r.string()
            objs.append(o)
        return r, objs

    # ---------- writing ----------
    def body_bytes(self):
        h = Writer()
        h.i32(len(self.objects))
        for o in self.objects:
            h.i32(o['type']); h.string(o['cls']); h.string(o['level']); h.string(o['path'])
            if self.object_flags:
                h.i32(o.get('flags', 8))
            if o['type'] == 1:
                h.i32(o['need_transform'])
                h.floats(o['rot']); h.floats(o['pos']); h.floats(o['scale'])
                h.i32(o['placed'])
            else:
                h.string(o['outer'])
        hb = h.getvalue()
        dw = Writer()
        dw.i32(len(self.objects))
        for o in self.objects:
            dw.i32(len(o['data'])); dw.raw(o['data'])
        db = dw.getvalue()
        hblock = hb
        dblock = struct.pack('<i', len(db)) + db
        inner = struct.pack('<i', len(hblock)) + hblock + dblock
        return struct.pack('<i', len(inner)) + inner

    def save(self, path):
        w = Writer()
        w.i32(self.header_version); w.i32(self.object_version); w.i32(self.build_version)
        for v in self.dims:
            w.i32(v)
        w.i32(len(self.cost))
        for item, amount in self.cost:
            w.string(''); w.string(item); w.i32(amount)
        w.i32(len(self.recipes))
        for rec in self.recipes:
            w.string(''); w.string(rec)
        w.raw(self.extra_header)
        body = self.body_bytes()
        for i in range(0, len(body), MAX_CHUNK):
            chunk = body[i:i + MAX_CHUNK]
            comp = zlib.compress(chunk)
            if self.chunk_v2:
                w.raw(struct.pack('<IIqB', CHUNK_TAG, CHUNK_HEADER, MAX_CHUNK, ZLIB))
            else:
                w.raw(struct.pack('<IIq', CHUNK_TAG, 0, MAX_CHUNK))
            w.raw(struct.pack('<qqqq', len(comp), len(chunk), len(comp), len(chunk)))
            w.raw(comp)
        Path(path).write_bytes(w.getvalue())

    # ---------- object helpers ----------
    def actors(self):
        return [o for o in self.objects if o['type'] == 1]

    def next_path(self, template):
        """A fresh unique path name with the same class prefix and id width as `template`."""
        prefix, num = re.match(r'(.*_)(\d+)$', template['path']).groups()
        used = {int(m.group(1)) for o in self.objects
                for m in [re.search(r'_(\d+)$', o['path'])] if m}
        n = int(num)
        while n in used:
            n -= 1
        return prefix + str(n).rjust(len(num), '0')

    def clone(self, template, pos=None, rot=None, scale=None):
        """Copy a structural piece (no components) to a new transform; returns the new object.

        Machines own component objects (type 0) whose outer path points at the actor; clone
        those with clone_with_components instead.
        """
        o = copy.deepcopy(template)
        new_path = self.next_path(template)
        o['data'] = replace_string(o['data'], template['path'], new_path)
        o['path'] = new_path
        if pos is not None: o['pos'] = list(pos)
        if rot is not None: o['rot'] = list(rot)
        if scale is not None: o['scale'] = list(scale)
        self.objects.append(o)
        return o

    def components_of(self, actor):
        return [o for o in self.objects if o['type'] == 0 and o.get('outer') == actor['path']]

    def clone_with_components(self, template, pos=None, rot=None):
        comps = self.components_of(template)
        o = self.clone(template, pos, rot)
        for c in comps:
            nc = copy.deepcopy(c)
            nc['path'] = c['path'].replace(template['path'], o['path'])
            nc['outer'] = o['path']
            nc['data'] = replace_string(nc['data'], template['path'], o['path'])
            o['data'] = replace_string(o['data'], c['path'], nc['path'])
            self.objects.append(nc)
        return o

    def add_copy(self, actor, source, pos, rot=(0, 0, 0, 1), scale=None):
        """Copy `actor` (and its components) from Blueprint `source` into this one at a new
        transform, with fresh unique paths. Returns the new actor. Fast enough for 10k+ pieces."""
        if not hasattr(self, '_next_id'):
            used = [int(m.group(1)) for o in self.objects for m in [re.search(r'_(\d+)$', o['path'])] if m]
            self._next_id = max(used + [2130000000]) + 1
        new_path = '%s_%d' % (actor['path'].rsplit('_', 1)[0], self._next_id)
        self._next_id += 1
        comps = source.components_of(actor)
        a = copy.deepcopy(actor)
        for c in comps:
            a['data'] = replace_string(a['data'], c['path'], c['path'].replace(actor['path'], new_path))
        a['data'] = replace_string(a['data'], actor['path'], new_path)
        a['path'] = new_path
        a['pos'] = [float(v) for v in pos]
        a['rot'] = [float(v) for v in rot]
        if scale is not None:
            a['scale'] = [float(v) for v in scale]
        self.objects.append(a)
        for c in comps:
            nc = copy.deepcopy(c)
            nc['data'] = replace_string(nc['data'], actor['path'], new_path)
            nc['path'] = c['path'].replace(actor['path'], new_path)
            nc['outer'] = new_path
            self.objects.append(nc)
        return a

    def remove(self, actor):
        drop = {id(actor)} | {id(c) for c in self.components_of(actor)}
        self.objects = [o for o in self.objects if id(o) not in drop]


LIBRARY_DIR = Path(__file__).resolve().parent.parent / 'library'


class Library:
    """Donor pieces shipped with the skill: one clean sample per building type and game version.

        lib = Library.load(needs=['Beam_Painted', 'Wall_Window_Thin_8x4_01'], custom_paint=True)
        bp = lib.new_blueprint(dims=[6, 6, 6])
        beam = lib.donor('Beam_Painted', custom=True)
        b = bp.add_copy(beam, lib.bp, pos=[0, 0, 0]); set_float(b, 'mLength', 800); set_color(b, WHITE)
        bp.recipes = lib.recipes_for(['Beam_Painted', ...])
    """

    def __init__(self, version, bp, index):
        self.version, self.bp, self.index = version, bp, index

    @staticmethod
    def versions():
        return json.loads((LIBRARY_DIR / 'index.json').read_text())

    @classmethod
    def load(cls, version=None, needs=(), custom_paint=False):
        """Pick a library version that has every type in `needs` (custom-painted samples too when
        custom_paint=True). Among those, prefer the one with the most types, then the newest."""
        ix = cls.versions()
        if version is None:
            def ok(v):
                types = ix[v]['types']
                return all(t in types and (not custom_paint or 'custom' in types[t]['paints'])
                           for t in needs)
            candidates = [v for v in ix if ok(v)]
            if not candidates:
                missing = {t for t in needs if not any(t in ix[v]['types'] for v in ix)}
                raise LookupError('no library version has all of %s (never seen: %s)' % (list(needs), sorted(missing)))
            version = max(candidates, key=lambda v: (len(ix[v]['types']), int(v)))
        version = str(version)
        bp = Blueprint.load(LIBRARY_DIR / ix[version]['file'])
        return cls(int(version), bp, ix[version])

    def types(self):
        return sorted(self.index['types'])

    def donor(self, type_name, custom=None):
        """The sample actor of this type; custom=True wants one with editable PrimaryColor."""
        matches = [o for o in self.bp.actors() if short(o['cls']) == type_name]
        if custom is not None:
            matches = [o for o in matches if (b'PrimaryColor' in o['data']) == custom] or matches
        if not matches:
            raise KeyError('%s not in library v%d' % (type_name, self.version))
        return matches[0]

    def recipes_for(self, type_names):
        return sorted({self.index['types'][t]['recipe'] for t in type_names if self.index['types'][t]['recipe']})

    def new_blueprint(self, dims):
        bp = Blueprint()
        for attr in ('header_version', 'object_version', 'build_version', 'extra_header',
                     'object_flags', 'chunk_v2'):
            setattr(bp, attr, getattr(self.bp, attr))
        bp.dims = list(dims)
        return bp


def item(name):
    """Class path of a cost item, e.g. item('Desc_SteelPlate') (Steel Beam), for Blueprint.cost."""
    items = json.loads((LIBRARY_DIR / 'items.json').read_text())
    return items[name]


def blueprints_root():
    """The game's blueprint folder on this PC (one subfolder per save session)."""
    return Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local')) / \
        'FactoryGame' / 'Saved' / 'SaveGames' / 'blueprints'


def sessions():
    """Save sessions that have a blueprint folder, most recently changed first."""
    root = blueprints_root()
    if not root.is_dir():
        return []
    return sorted((p.name for p in root.iterdir() if p.is_dir()),
                  key=lambda n: (root / n).stat().st_mtime, reverse=True)


def install(sbp_path, session, overwrite=False):
    """Copy a .sbp and its .sbpcfg into a session's blueprint folder. Refuses to overwrite an
    existing blueprint unless overwrite=True (only for a file this project made earlier)."""
    import shutil
    dest = blueprints_root() / session
    if not dest.is_dir():
        raise FileNotFoundError('no blueprint folder for session %r (have: %s)' % (session, sessions()))
    src = Path(sbp_path)
    pairs = [(src, dest / src.name)]
    cfg = src.with_suffix('.sbpcfg')
    if cfg.exists():
        pairs.append((cfg, dest / cfg.name))
    for s, d in pairs:
        if d.exists() and not overwrite:
            raise FileExistsError('%s already exists; pick another name' % d)
    for s, d in pairs:
        shutil.copyfile(s, d)
    return dest / src.name


def write_sbpcfg(path, description, color=(0.6, 0.6, 0.6, 1.0), icon_id=437):
    """Companion .sbpcfg: version 0, description (length + bytes, no terminator), icon, colour."""
    desc = description.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8')
    Path(path).write_bytes(struct.pack('<ii', 0, len(desc)) + desc +
                           struct.pack('<i4f', icon_id, *color))


def replace_string(blob, old, new):
    """Swap an FString (length-prefixed, null-terminated) inside a serialized blob."""
    def enc(s):
        b = (s + '\0').encode('latin1')
        return struct.pack('<i', len(b)) + b
    blob = blob.replace(enc(old), enc(new))
    # references also appear as bare substrings, e.g. 'Path.Component' inside longer strings
    if len(old) == len(new):
        blob = blob.replace(old.encode('latin1'), new.encode('latin1'))
    return blob


def find_prop(blob, name):
    """Offset of a property's value and its type name, or (None, None)."""
    key = struct.pack('<i', len(name) + 1) + name.encode('latin1') + b'\0'
    i = blob.find(key)
    if i < 0:
        return None, None
    r = Reader(blob, i + len(key))
    ptype = r.string()
    r.o += 8  # int64 size
    if ptype in ('FloatProperty', 'IntProperty', 'DoubleProperty', 'Int64Property'):
        r.o += 1  # has-guid flag
    return r.o, ptype


def get_float(obj, name):
    off, t = find_prop(obj['data'], name)
    if off is None: return None
    fmt = {'FloatProperty': '<f', 'DoubleProperty': '<d', 'IntProperty': '<i'}[t]
    return struct.unpack_from(fmt, obj['data'], off)[0]


def set_float(obj, name, value):
    off, t = find_prop(obj['data'], name)
    if off is None:
        raise KeyError('%s has no %s property to edit' % (obj['path'], name))
    fmt = {'FloatProperty': '<f', 'DoubleProperty': '<d', 'IntProperty': '<i'}[t]
    b = bytearray(obj['data']); struct.pack_into(fmt, b, off, value); obj['data'] = bytes(b)


def swatch(obj):
    m = re.search(rb'Swatches/(\w+)\.', obj['data'])
    return m.group(1).decode().replace('SwatchDesc_', '') if m else ''


def get_color(obj, prop='PrimaryColor'):
    """Linear RGBA of a custom paint colour, or None. Struct value = 'LinearColor', GUID, flag, 4 floats."""
    off, _ = find_prop(obj['data'], prop)
    if off is None:
        return None
    i = obj['data'].find(b'LinearColor\x00', off) + len(b'LinearColor\x00') + 17
    return list(struct.unpack_from('<4f', obj['data'], i))


def set_color(obj, rgba, prop='PrimaryColor'):
    off, _ = find_prop(obj['data'], prop)
    if off is None:
        raise KeyError('%s has no %s; clone a donor painted with a Custom swatch' % (obj['path'], prop))
    i = obj['data'].find(b'LinearColor\x00', off) + len(b'LinearColor\x00') + 17
    b = bytearray(obj['data']); struct.pack_into('<4f', b, i, *rgba); obj['data'] = bytes(b)


def paint_key(obj):
    """Swatch name, or '#rrggbb' (sRGB) for custom colours, for grouping/colouring in the viewer."""
    s = swatch(obj)
    c = get_color(obj) if s == 'Custom' else None
    if c:
        srgb = [max(0, min(255, round(255 * (v ** (1 / 2.2))))) for v in c[:3]]
        return '#%02x%02x%02x' % tuple(srgb)
    return s


# ---------- summary / dump / render ----------
def summary(bp):
    from collections import Counter
    xs = [o['pos'] for o in bp.actors()]
    bounds = [(min(p[i] for p in xs), max(p[i] for p in xs)) for i in range(3)] if xs else []
    return dict(
        dims=bp.dims,
        bounds_m=[[round(a / 100, 2), round(b / 100, 2)] for a, b in bounds],
        pieces=dict(Counter(short(o['cls']) for o in bp.actors()).most_common()),
        components=sum(1 for o in bp.objects if o['type'] == 0),
        cost={short(i): n for i, n in bp.cost},
        recipes=[short(r) for r in bp.recipes],
    )


def dump(bp):
    out = []
    for o in bp.actors():
        out.append(dict(type=short(o['cls']), path=o['path'], pos=o['pos'], rot=o['rot'],
                        scale=o['scale'], length=get_float(o, 'mLength'), swatch=swatch(o)))
    return out


def qmat(x, y, z, w):
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]


def render(bp, out_html, title):
    groups = {}
    for o in bp.actors():
        R, t, s = qmat(*o['rot']), o['pos'], list(o['scale'])
        length = get_float(o, 'mLength')
        if length:
            s[0] *= length  # beams/pipes stretch along local X
        M = [[R[i][j] * s[j] for j in range(3)] + [t[i]] for i in range(3)]
        M3 = [M[0], M[2], M[1]]  # Unreal Z-up -> three.js Y-up (also mirrors; materials are double-sided)
        flat = [round(M3[r][c] * 0.01, 4) for c in range(4) for r in range(3)]
        groups.setdefault(short(o['cls']) + '|' + paint_key(o), []).extend(flat)
    s = summary(bp)
    (x0, x1), (y0, y1), (z0, z1) = s['bounds_m']
    meta = dict(
        title=title,
        subtitle='%.0f × %.0f × %.0f m · %d pieces' % (x1 - x0, y1 - y0, z1 - z0, len(bp.actors())),
        cost=' · '.join('<b>%s</b> %s' % (format(n, ','), k.replace('Desc_', '')) for k, n in s['cost'].items()),
        height=max(z1, 1),
    )
    tpl = (Path(__file__).parent.parent / 'assets' / 'viewer_template.html').read_text(encoding='utf-8')
    html = tpl.replace('__DATA__', json.dumps(groups, separators=(',', ':'))) \
              .replace('__META__', json.dumps(meta))
    Path(out_html).write_text(html, encoding='utf-8')


def catalog(folder):
    """Every piece type found in a blueprints folder (recursively), with a donor file for each.

    Prefer a donor whose object_version matches the blueprint you're building into, and one with
    a Custom swatch (it carries PrimaryColor, so set_color works on it).
    """
    from collections import defaultdict
    types = defaultdict(lambda: dict(count=0, donors={}, paints=set()))
    for f in sorted(Path(folder).rglob('*.sbp')):
        try:
            bp = Blueprint.load(f)
        except Exception as e:  # keep going; report unreadable files
            print('skip', f.name, e, file=sys.stderr)
            continue
        for o in bp.actors():
            t = types[short(o['cls'])]
            t['count'] += 1
            pk = paint_key(o) if swatch(o) != 'Custom' else 'Custom'
            t['paints'].add(pk)
            key = (bp.object_version, pk == 'Custom')
            t['donors'].setdefault(key, f.name)
    out = {}
    for name, t in sorted(types.items()):
        out[name] = dict(count=t['count'], paints=sorted(p for p in t['paints'] if p),
                         donors=[dict(version=v, custom_paint=c, file=fn)
                                 for (v, c), fn in sorted(t['donors'].items())])
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__); return
    if argv[1] == 'library':
        for v, d in sorted(Library.versions().items(), key=lambda kv: int(kv[0])):
            names = sorted(d['types'])
            print('v%s (%d types): %s' % (v, len(names), ', '.join(
                n + ('*' if 'custom' in d['types'][n]['paints'] else '') for n in names)))
        print('* = sample with custom paint (any colour via set_color)')
        return
    cmd, src = argv[1], argv[2]
    if cmd == 'catalog':
        cat = catalog(src)
        if len(argv) > 3:
            Path(argv[3]).write_text(json.dumps(cat, indent=1))
        for name, t in cat.items():
            vs = sorted({d['version'] for d in t['donors']})
            print('%6d  %-45s versions %s%s' % (t['count'], name, vs,
                  '  (custom paint)' if any(d['custom_paint'] for d in t['donors']) else ''))
        return
    bp = Blueprint.load(src)
    if cmd == 'info':
        print(json.dumps(summary(bp), indent=1))
    elif cmd == 'dump':
        Path(argv[3]).write_text(json.dumps(dump(bp), indent=1))
    elif cmd == 'render':
        render(bp, argv[3], Path(src).stem)
        print('wrote', argv[3])
    elif cmd == 'roundtrip':
        bp.save(argv[3])
        again = Blueprint.load(argv[3])
        same = again.body_bytes() == bp.body_bytes() and again.cost == bp.cost and again.recipes == bp.recipes
        orig = Path(src).read_bytes()
        print('body identical:', same, '| file bytes identical:', orig == Path(argv[3]).read_bytes())
    else:
        print(__doc__)


if __name__ == '__main__':
    main(sys.argv)

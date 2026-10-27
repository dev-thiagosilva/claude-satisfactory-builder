"""Build straight into a copy of a 1.2 save (.sav), without the blueprint designer.

  python -I world.py info  <file.sav>                          what's in the world
  python -I world.py roundtrip <file.sav>                      re-write unchanged, compare bytes
  python -I world.py place <file.sav> <build.sbp> x y z [yaw] [--name "new save"]

Structural pieces (foundations, walls, beams, roofs, ramps, pillars, walkways...) are stored by
the game in one compact list inside FGLightweightBuildableSubsystem, not as separate objects.
Adding to that list is what the game itself does when you build them, so a large creation goes
in without blueprint holograms or designer limits. Pieces that aren't lightweight (machines,
belts, lights...) aren't written yet: place() reports them as skipped.

Lightweight list (object version 60, after the subsystem's property list and its int32 0):
  int32 version (4), int32 class count, per class: int32 0, FString class path, int32 count,
  per instance:
    transform: 4 doubles rotation (x, y, z, w), 3 doubles position (cm), 3 doubles scale
    customization: refs (level FString + path FString) for swatch, material, pattern, skin,
                   8 floats primary + secondary linear colour, ref paint finish, byte pattern rotation
    ref recipe, ref blueprint proxy (empty when built by hand)
    int32 has data; if 1: ref data struct, int32 size, property list (beams: BeamLength float)
    byte 0, int32 -1
The header ends with a 16-byte MD5 of the compressed body, then int32 creative mode; a changed
save must carry the new hash. A save is never overwritten: write() refuses existing files.
"""
import hashlib, math, os, re, struct, sys, zlib
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sbp import Reader, Writer, Blueprint, assets, short, find_prop, get_float, qmul, qrotate
from sav import Save, CHUNK_TAG

MAX_CHUNK = 131072
SUBSYSTEM = '/Script/FactoryGame.FGLightweightBuildableSubsystem'
BEAM_DATA = '/Script/FactoryGame.BuildableBeamLightweightData'
CUSTOM_PAINT = ('SwatchDesc', 'MaterialDesc', 'PatternDesc', 'SkinDesc')
INSTANCE_TAIL = b'\x00' + struct.pack('<i', -1)


def save_games_root():
    return Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local')) / \
        'FactoryGame' / 'Saved' / 'SaveGames'


def save_files():
    """Every .sav of this PC's player(s), newest first: [{path, name, modified, mb}]."""
    root = save_games_root()
    out = []
    for p in root.glob('*/*.sav'):
        st = p.stat()
        out.append(dict(path=str(p), name=p.stem, modified=st.st_mtime, mb=round(st.st_size / 1e6, 1)))
    return sorted(out, key=lambda s: -s['modified'])


def _fstring(s):
    w = Writer(); w.string(s); return w.getvalue()


def _ref(path, level=''):
    return _fstring(level) + _fstring(path)


class Instance:
    """One lightweight piece. `raw` keeps the exact bytes of pieces read from a save."""
    __slots__ = ('cls', 'rot', 'pos', 'scale', 'length', 'raw')

    def __init__(self, cls, rot, pos, scale=(1, 1, 1), length=None, raw=None):
        self.cls, self.rot, self.pos, self.scale, self.length, self.raw = cls, rot, pos, scale, length, raw


def encode_instance(rot, pos, scale, recipe, swatch, paint=None, colors=None, length=None):
    """Bytes of a new lightweight piece. paint: {MaterialDesc|PatternDesc|SkinDesc: path}."""
    paint = paint or {}
    colors = colors or (0, 0, 0, 1, 0, 0, 0, 1)
    b = [struct.pack('<10d', *rot, *pos, *scale), _ref(swatch)]
    b += [_ref(paint.get(k, '')) for k in CUSTOM_PAINT[1:]]
    b += [struct.pack('<8f', *colors), _ref(paint.get('PaintFinishDesc', '')), b'\x00']
    b += [_ref(recipe), _ref('')]
    if length is None:
        b.append(struct.pack('<i', 0))
    else:
        props = (_fstring('BeamLength') + _fstring('FloatProperty') + struct.pack('<iiB', 0, 4, 0) +
                 struct.pack('<f', length) + _fstring('None'))
        b += [struct.pack('<i', 1), _ref(BEAM_DATA), struct.pack('<i', len(props)), props]
    b.append(INSTANCE_TAIL)
    return b''.join(b)


class World:
    def __init__(self, path):
        self.path = Path(path)
        self.file = self.path.read_bytes()
        self.chunks_at = self.file.find(struct.pack('<II', CHUNK_TAG, 0x22222222))
        if self.chunks_at < 0:
            raise ValueError('not a 1.0+ save')
        version = struct.unpack_from('<i', self.file, 4)[0]
        if version < 60:
            raise ValueError('save version %d is from an older game: load it in game 1.2 and save once first' % version)
        self.save = Save(self.path)
        self.sub = next(o for o in self.save.levels[-1][1] if o['cls'] == SUBSYSTEM)
        self._read_lightweight(self.sub['data'])
        self.added = 0

    # ---------- reading ----------
    def _read_lightweight(self, d):
        o = d.find(b'\x05\x00\x00\x00None\x00') + 9 + 4      # property list end + int32 0
        self.lw_prefix = d[:o]
        r = Reader(d, o)
        self.lw_version = r.i32()
        self.classes = {}                                     # class path -> [Instance]
        for _ in range(r.i32()):
            if r.i32() != 0:
                raise ValueError('unexpected lightweight class entry')
            cls = r.string()
            items = self.classes.setdefault(cls, [])
            for _ in range(r.i32()):
                st = r.o
                t = struct.unpack_from('<10d', d, r.o); r.o += 80
                for _ in range(4 * 2): r.string()
                r.o += 32; r.string(); r.string(); r.o += 1
                for _ in range(4): r.string()
                length = None
                if r.i32():
                    r.string(); r.string(); n = r.i32()
                    blob = d[r.o:r.o + n]; r.o += n
                    k = blob.find(b'BeamLength\x00')
                    if k >= 0:
                        length = struct.unpack_from('<f', blob, k + 11 + 4 + 14 + 9)[0]
                r.o += 5
                items.append(Instance(cls, t[0:4], t[4:7], t[7:10], length, d[st:r.o]))
        if r.o != len(d):
            raise ValueError('lightweight list: %d bytes left over' % (len(d) - r.o))

    def lightweight(self):
        for items in self.classes.values():
            yield from items

    def actors(self):
        """(class short name, pos, rot) of every building that is its own object."""
        for a, _ in self.save.buildings():
            yield short(a['cls']), a['pos'], a['rot']

    def summary(self):
        lw = Counter(short(c) for c, v in self.classes.items() for _ in v)
        ac = Counter(t for t, _, _ in self.actors())
        return dict(name=self.path.stem, session=self.session_name(), lightweight=sum(lw.values()),
                    buildings=sum(ac.values()), types=dict((lw + ac).most_common()))

    def removed_foliage(self):
        """[(x, y, z)] cm of every tree, bush or boulder the player removed (building clears them).
        FGFoliageRemovalSubsystem: mSaveData map of 64 m cells -> per foliage type RemovedLocations,
        an ArrayProperty of Vector: after its type tree, int32 0, int32 size, byte flags, int32 count, doubles."""
        sub = next((o for o in self.save.levels[-1][1] if o['cls'] == '/Script/FactoryGame.FGFoliageRemovalSubsystem'), None)
        out = []
        if not sub:
            return out
        d = sub['data']
        for m in re.finditer(re.escape(b'RemovedLocations\x00'), d):
            j = d.find(b'/Script/CoreUObject\x00', m.end()) + 20
            size, count = struct.unpack_from('<i', d, j + 4)[0], struct.unpack_from('<i', d, j + 9)[0]
            if size != 4 + count * 24:
                continue
            v = struct.unpack_from('<%dd' % (count * 3), d, j + 13)
            out += [v[k:k + 3] for k in range(0, len(v), 3)]
        return out

    def session_name(self):
        r = Reader(self.file, 12)
        r.string(); r.string(); r.string()
        return r.string()

    # ---------- adding ----------
    def add(self, cls, pos, rot=(0, 0, 0, 1), length=None, swatch=None, paint=None, colors=None, recipe=None):
        a = assets()['assets'].get(short(cls))
        if not a or not a.get('lightweight'):
            raise ValueError('%s is not a lightweight piece' % short(cls))
        swatch = swatch or '/Game/FactoryGame/Buildable/-Shared/Customization/Swatches/SwatchDesc_Slot0.SwatchDesc_Slot0_C'
        raw = encode_instance(rot, pos, (1, 1, 1), recipe or a['recipe_path'], swatch, paint, colors, length)
        cls = a.get('class_path') or cls
        self.classes.setdefault(cls, []).append(Instance(cls, rot, pos, (1, 1, 1), length, raw))
        self.added += 1

    def add_blueprint(self, bp, pos, yaw_deg=0.0):
        """Every lightweight piece of a Blueprint, its origin at world `pos` (cm), turned by yaw.
        Returns (added count, Counter of skipped piece types)."""
        th = math.radians(yaw_deg)
        q = (0.0, 0.0, math.sin(th / 2), math.cos(th / 2))
        table = assets()['assets']
        n, skipped = 0, Counter()
        for o in bp.actors():
            a = table.get(short(o['cls']))
            props = piece_props(o)
            if not a or not a.get('lightweight') or not (props['recipe'] or a.get('recipe_path')):
                skipped[short(o['cls'])] += 1
                continue
            p = qrotate(q, o['pos'])
            self.add(o['cls'], [pos[i] + p[i] for i in range(3)], qmul(q, o['rot']),
                     length=get_float(o, 'mLength') if short(o['cls']).startswith('Beam') else None,
                     **props)
            n += 1
        return n, skipped

    # ---------- writing ----------
    def lightweight_bytes(self):
        out = [self.lw_prefix, struct.pack('<ii', self.lw_version, len(self.classes))]
        for cls, items in self.classes.items():
            out += [struct.pack('<i', 0), _fstring(cls), struct.pack('<i', len(items))]
            out += [i.raw for i in items]
        return b''.join(out)

    def body_bytes(self):
        body, sub = self.save.body, self.sub
        old, new = len(sub['data']), self.lightweight_bytes()
        delta = len(new) - old
        if not delta and new == sub['data']:
            return body
        at = sub['data_at']
        b = bytearray(body[:at - 4]) + struct.pack('<i', len(new)) + new + body[at + old:]
        for off in (0, self.save.osize_at['Persistent_Level']):   # sizes that enclose the subsystem
            struct.pack_into('<q', b, off, struct.unpack_from('<q', b, off)[0] + delta)
        return bytes(b)

    def file_bytes(self, save_name=None):
        body = self.body_bytes()
        chunks = []
        for k in range(0, len(body), MAX_CHUNK):
            raw = body[k:k + MAX_CHUNK]
            c = zlib.compress(raw, 6)
            chunks.append(struct.pack('<IIqBqqqq', CHUNK_TAG, 0x22222222, MAX_CHUNK, 3,
                                      len(c), len(raw), len(c), len(raw)) + c)
        data = b''.join(chunks)
        head = self.file[:self.chunks_at]
        if save_name:
            r = Reader(head, 12); r.string()
            head = head[:12] + _fstring(save_name) + head[r.o:]
        head = head[:-20] + hashlib.md5(data).digest() + head[-4:]
        return head + data

    def write(self, out_path, save_name=None):
        out = Path(out_path)
        if out.exists():
            raise FileExistsError('%s already exists; pick another name' % out)
        b = self.file_bytes(save_name or out.stem)
        out.write_bytes(b)
        World(out)                                          # must read back
        return out


def _object_prop(d, name):
    off, _ = find_prop(d, name)
    if off is None:
        return None
    r = Reader(d, off); r.string()
    return r.string() or None


def piece_props(o):
    """Recipe, swatch, custom colours and material/pattern/finish of a blueprint piece, for World.add."""
    d, out, paint = o['data'], {'recipe': _object_prop(o['data'], 'mBuiltWithRecipe')}, {}
    for name in CUSTOM_PAINT + ('PaintFinishDesc',):
        path = _object_prop(d, name)
        if name == 'SwatchDesc':
            out['swatch'] = path
        elif path:
            paint[name] = path
    off, _ = find_prop(d, 'PrimaryColor')
    off2, _ = find_prop(d, 'SecondaryColor')
    if off is not None and off2 is not None:
        out['colors'] = struct.unpack_from('<4f', d, off) + struct.unpack_from('<4f', d, off2)
    out['paint'] = paint
    return out


def next_free_save(src, name):
    """A new save path next to `src`, named `name` (with ' 2', ' 3'... if taken)."""
    folder = Path(src).parent
    base = re.sub(r'[^\w .\-()&,+]', '', name).strip() or 'claude build'
    p, n = folder / (base + '.sav'), 2
    while p.exists():
        p = folder / ('%s %d.sav' % (base, n)); n += 1
    return p


def main(argv):
    if len(argv) >= 2 and argv[0] == 'info':
        import json
        print(json.dumps(World(argv[1]).summary(), indent=1)[:4000])
    elif len(argv) >= 2 and argv[0] == 'roundtrip':
        w = World(argv[1])
        same = w.file_bytes() == w.file
        print('byte-identical' if same else 'DIFFERENT')
        return 0 if same else 1
    elif len(argv) >= 6 and argv[0] == 'place':
        name = argv[argv.index('--name') + 1] if '--name' in argv else None
        args = [a for a in argv if a != '--name' and a != name]
        w = World(args[1])
        bp = Blueprint.load(args[2])
        pos = [float(v) * 100 for v in args[3:6]]
        n, skipped = w.add_blueprint(bp, pos, float(args[6]) if len(args) > 6 else 0)
        out = next_free_save(w.path, name or '%s - %s' % (w.path.stem, Path(args[2]).stem))
        w.write(out)
        print('added %d pieces -> %s' % (n, out))
        if skipped:
            print('skipped (not supported yet):', dict(skipped))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

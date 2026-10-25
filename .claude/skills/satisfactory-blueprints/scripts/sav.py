"""Read-only reader for Satisfactory 1.0+ save files (.sav), used to collect building samples.

  python -I sav.py <file.sav>            summary: version, levels, buildings per type

Only what the donor library needs is decoded: each level's object headers and object data.
Buildings come out in the same dict shape as Blueprint.objects, so blueprint tooling can use
them. Nothing is ever written back to a save.

Layout (save header version 14 / save version 60, game 1.2), all little-endian:
  header ... then zlib chunks exactly like .sbp (see references/format.md §3)
  body: int64 size, int32 0, version block, int32 grid count + grids (name, int32, uint32,
        int32 cells + (name, uint32) each), int32 level count, levels, persistent level
  level: FString name (absent for the persistent level), int64 header-block size,
         [int32 count + headers as in .sbp], int64 object-block size,
         [int32 count + per object: int32 object version, int32 flag, int32 size, data,
          and for object version >= 53 one more int32],
         int32 level save version, int32 collectables + (FString level, FString path) each,
         int32 has-version-block (+ int32 0 + version block)
  version block: int32 x2 package version, int32 licensee, uint16 x3 + uint32 engine version,
         FString branch, int32 count + (16-byte GUID, int32) custom versions
"""
import struct, sys, zlib
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sbp import Reader, short

CHUNK_TAG = 0x9E2A83C1


def decompress(path):
    d = Path(path).read_bytes()
    # The 4-byte tag can also occur by chance in the header (it holds a hash), so look for the
    # 8-byte 1.0+ chunk start first, then fall back to the pre-1.0 one.
    o = d.find(struct.pack('<II', CHUNK_TAG, 0x22222222))
    if o < 0:
        o = d.find(struct.pack('<IIq', CHUNK_TAG, 0, 131072))
    head = struct.unpack_from('<3i', d, 0)
    parts = []
    v2 = struct.unpack_from('<I', d, o + 4)[0] == 0x22222222
    hlen = 49 if v2 else 48
    while o < len(d):
        if struct.unpack_from('<I', d, o)[0] != CHUNK_TAG:
            raise ValueError('bad chunk at %d' % o)
        cs = struct.unpack_from('<q', d, o + hlen - 32)[0]
        parts.append(zlib.decompress(d[o + hlen:o + hlen + cs]))
        o += hlen + cs
    return head, b''.join(parts)


class Save:
    def __init__(self, path):
        (self.header_version, self.save_version, self.build_version), body = decompress(path)
        self.levels = []          # (name, [objects]) — objects shaped like Blueprint.objects
        r = Reader(body, 8)
        r.i32()
        self._version_block(r)
        for _ in range(r.i32()):              # world-partition grids
            r.string(); r.i32(); r.o += 4
            for _ in range(r.i32()):
                r.string(); r.o += 4
        for _ in range(r.i32()):
            self.levels.append(self._level(r, r.string()))
        self.levels.append(self._level(r, 'Persistent_Level'))

    @staticmethod
    def _version_block(r):
        r.o += 8; r.i32(); r.o += 10; r.string()
        n = r.i32()                 # (not `r.o += r.i32() * 20`: that reads r.o before i32 moves it)
        r.o += n * 20

    def _level(self, r, name):
        d = r.d
        hsize = struct.unpack_from('<q', d, r.o)[0]; r.o += 8; hend = r.o + hsize
        objs = []
        for _ in range(r.i32()):
            t = r.i32()
            o = dict(type=t, cls=r.string(), level=r.string(), path=r.string())
            if self.save_version >= 52:
                o['flags'] = r.i32()
            if t == 1:
                o['need_transform'] = r.i32()
                o['rot'], o['pos'], o['scale'] = r.floats(4), r.floats(3), r.floats(3)
                o['placed'] = r.i32()
            else:
                o['outer'] = r.string()
            objs.append(o)
        r.o = hend                             # skip collectables listed in the header block
        osize = struct.unpack_from('<q', d, r.o)[0]; r.o += 8; oend = r.o + osize
        n = r.i32()
        if n != len(objs):
            raise ValueError('level %s: %d headers but %d objects' % (name, len(objs), n))
        for o in objs:
            o['object_version'] = r.i32()
            r.i32()
            n = r.i32()
            o['data'] = r.bytes(n)
            if o['object_version'] >= 53:    # newer objects carry one extra int32 (seen as 0)
                o['save_tail'] = r.i32()
        r.o = oend
        if name != 'Persistent_Level':        # its trailer differs and holds nothing we need
            r.i32()                            # level save version
            for _ in range(r.i32()):
                r.string(); r.string()
            if r.i32():
                r.i32(); self._version_block(r)
        return name, objs

    def objects(self):
        for _, objs in self.levels:
            yield from objs

    def buildings(self):
        """(actor, components) for every placed building (Build_ classes)."""
        comps = {}
        for o in self.objects():
            if o['type'] == 0:
                comps.setdefault(o['outer'], []).append(o)
        for o in self.objects():
            if o['type'] == 1 and '/Build_' in o['cls']:
                yield o, comps.get(o['path'], [])


if __name__ == '__main__':
    s = Save(sys.argv[1])
    print('save version', s.save_version, '| levels', len(s.levels),
          '| objects', sum(len(o) for _, o in s.levels))
    c = Counter(short(a['cls']) for a, _ in s.buildings())
    print('building types', len(c), '| buildings', sum(c.values()))
    print(', '.join('%s %d' % kv for kv in c.most_common()))

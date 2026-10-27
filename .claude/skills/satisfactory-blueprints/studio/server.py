"""Blueprint Studio: a local web app to view, tweak and install the blueprints Claude made.

  python -I server.py [--port 8770] [--creations .local/blueprints]

Serves studio/index.html and a small JSON API on 127.0.0.1 only:
  GET  /api/creations                 builds in the creations folder
  GET  /api/creation?name=<folder>    pieces of one build (type, transform, paint)
  POST /api/save                      apply edits (keep/move/recolour/duplicate/delete); old file kept in history/
  GET  /api/sessions                  the game's save folders that hold blueprints
  POST /api/install                   copy a build into a save's blueprint folder
  GET  /map                           world map: a save's buildings in 3D; place a build into a copy
  GET  /api/saves                     the player's saves (ok = game 1.2, can be written)
  GET  /api/world?path=, /api/world.bin?path=   a save's pieces: meta JSON, then 9 floats per piece
  POST /api/place                     {path, build, pos (cm), yaw, name?} -> a NEW save next to it
  GET  /api/terrain, /api/terrain.bin the ground: tile list + 33 x 33 overview heights per tile (uint16)
  GET  /api/terrain/tile?i=           one tile's full 128 x 128 heights (1 m)
  GET  /api/rocks.bin, /api/water.json  cliffs/rocks (the game's far-view models) and water surfaces
  GET  /api/objects/meta, shapes.bin, big.bin, area?k=ax,ay   trees, boulders and objects: model list,
                                      model shapes, always-shown big models, copies of one 500 m area
  GET  /planner                       production planner page (machines, resources, power)
  GET  /api/items, /api/recipes?item= items that can be produced; recipes for one item
  POST /api/plan                      {targets: [[item, rate]], use: [recipe], clock, miner, purity}
Each build is a folder: <creations>/<folder>/<Name>.sbp (+ .sbpcfg, build.py, history/).
"""
import argparse, json, math, re, shutil, struct, sys, time
from array import array
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
from sbp import (Blueprint, spline_points, wire_ends, short, get_float, get_color, set_color, paint_key, sessions,
                 blueprints_root, install, size_name, qmul)
import calc
import world as worldlib

CREATIONS = None
SAFE = re.compile(r'^[\w .\-\[\]()&,+]+$')


def build_dir(name):
    if not name or not SAFE.match(name) or name in ('.', '..'):
        raise ValueError('bad build name')
    d = (CREATIONS / name).resolve()
    if d.parent != CREATIONS.resolve() or not d.is_dir():
        raise FileNotFoundError(name)
    return d


def sbp_in(d):
    files = sorted(d.glob('*.sbp'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError('no .sbp in %s' % d.name)
    return files[0]


def cfg_description(cfg):
    try:
        b = cfg.read_bytes()
        n = int.from_bytes(b[4:8], 'little', signed=True)
        return b[8:8 + n].decode('utf-8', 'replace')
    except Exception:
        return ''


def list_creations():
    out = []
    if not CREATIONS.is_dir():
        return out
    for d in sorted(CREATIONS.iterdir()):
        if not d.is_dir():
            continue
        try:
            f = sbp_in(d)
            bp = Blueprint.load(f)
        except Exception:
            continue
        out.append(dict(name=d.name, title=f.stem, pieces=len(bp.actors()), dims=bp.dims,
                        size=size_name(bp.dims),
                        modified=f.stat().st_mtime,
                        description=cfg_description(f.with_suffix('.sbpcfg'))))
    return sorted(out, key=lambda c: c['modified'], reverse=True)


def model(name):
    f = sbp_in(build_dir(name))
    bp = Blueprint.load(f)
    pieces = []
    for i, o in enumerate(bp.actors()):
        custom = get_color(o) is not None
        pieces.append(dict(i=i, type=short(o['cls']), pos=o['pos'], rot=o['rot'], scale=o['scale'],
                           len=get_float(o, 'mLength'), paint=paint_key(o), custom=custom,
                           spline=spline_points(o) or wire_ends(o)))
    return dict(name=name, title=f.stem, dims=bp.dims, size=size_name(bp.dims), version=bp.object_version,
                cost=[[short(i), n] for i, n in bp.cost], pieces=pieces,
                description=cfg_description(f.with_suffix('.sbpcfg')))


def hex_to_linear(h):
    h = h.lstrip('#')
    return tuple(((int(h[k:k + 2], 16) / 255.0) ** 2.2) for k in (0, 2, 4)) + (1.0,)


def save(req):
    """req: {name, pieces:[{i, pos, rot, color?}], clones:[{from, pos, rot, color?}]}.
    Pieces not listed are deleted. Clones copy piece `from` (an original index)."""
    d = build_dir(req['name'])
    f = sbp_in(d)
    src = Blueprint.load(f)
    actors = src.actors()
    keep = {}
    for p in req.get('pieces', []):
        keep[int(p['i'])] = p
    out = Blueprint()
    for attr in ('header_version', 'object_version', 'build_version', 'extra_header',
                 'object_flags', 'chunk_v2', 'dims', 'cost', 'recipes'):
        setattr(out, attr, getattr(src, attr))
    out.objects = []

    def apply(o, p):
        o['pos'] = [float(v) for v in p['pos']]
        o['rot'] = [float(v) for v in p['rot']]
        if p.get('color') and get_color(o) is not None:
            set_color(o, hex_to_linear(p['color']))
            if get_color(o, 'SecondaryColor') is not None:
                set_color(o, hex_to_linear(p['color']), 'SecondaryColor')

    for i, a in enumerate(actors):
        if i not in keep:
            continue
        a = dict(a)
        apply(a, keep[i])
        out.objects.append(a)
        out.objects.extend(src.components_of(actors[i]))
    for c in req.get('clones', []):
        o = out.add_copy(actors[int(c['from'])], src, c['pos'], c['rot'])
        apply(o, c)
    # cost scales with the amount of building (it was an estimate to begin with)
    ratio = len(out.actors()) / max(1, len(actors))
    out.cost = [(i, max(1, math.ceil(n * ratio))) for i, n in src.cost]
    # grow dims if pieces moved outside the designer volume
    xs = [o['pos'] for o in out.actors()] or [[0, 0, 0]]
    need = [math.ceil(max(abs(p[0]) for p in xs) / 400) + 1,
            math.ceil(max(abs(p[1]) for p in xs) / 400) + 1,
            math.ceil(max(p[2] for p in xs) / 800) + 1]
    out.dims = [max(a, b) for a, b in zip(out.dims, need)]
    hist = d / 'history'
    hist.mkdir(exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')
    shutil.copyfile(f, hist / ('%s %s.sbp' % (f.stem, stamp)))
    out.save(f)
    Blueprint.load(f)  # must parse back
    return model(req['name'])


def make_factory(req):
    """Build a production-line blueprint for a plan and store it as a new build."""
    import factory
    from sbp import write_sbpcfg
    targets = [(calc.find_item(t[0]), float(t[1])) for t in req.get('targets', []) if float(t[1]) > 0]
    if not targets:
        raise ValueError('nothing to build')
    plan = calc.plan(targets, use=req.get('use', []), clock=1.0)   # blueprints can't hold power shards
    items = calc.db()['items']
    title = req.get('name') or ' + '.join('%s %s' % (calc.fmt(r), items[i]['name']) for i, r in targets) + ' Factory'
    title = re.sub(r'[^\w .\-()&,+]', '', title)[:80]
    folder = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    d = CREATIONS / folder
    n = 2
    while d.exists():
        d = CREATIONS / ('%s-%d' % (folder, n)); n += 1
    d.mkdir(parents=True)
    f, rep = factory.build_best(plan, title)
    out = d / (title + '.sbp')
    f.bp.save(out)
    write_sbpcfg(out.with_suffix('.sbpcfg'), '%s\n\nMachines: %s\n\nRaw inputs: %s\n\nPower: %s.\n\nGenerated by claude-satisfactory-builder.' % (
        title, '; '.join(rep['rows']), '; '.join(rep['raw_inputs']), rep.get('power', 'wire it in game')))
    return dict(name=d.name, title=title, **rep)


WORLDS = {}   # save path -> (mtime, World, packed pieces)


def list_saves():
    """The player's game-1.2 saves, newest first (older saves can't be written)."""
    out = []
    for s in worldlib.save_files():
        try:
            with open(s['path'], 'rb') as fh:
                s['ok'] = struct.unpack('<3i', fh.read(12))[1] >= 60
        except OSError:
            continue
        s['session'] = Path(s['path']).parent.name
        out.append(s)
    return out


def known_save(path):
    for s in list_saves():
        if s['path'] == path and s['ok']:
            return Path(path)
    raise ValueError('not one of your game 1.2 saves')


def world_of(path):
    p = known_save(path)
    mt = p.stat().st_mtime
    hit = WORLDS.get(str(p))
    if hit and hit[0] == mt:
        return hit[1], hit[2]
    w = worldlib.World(p)
    packed = pack_world(w)
    WORLDS.clear()                      # one world in memory at a time
    WORLDS[str(p)] = (mt, w, packed)
    return w, packed


def pack_world(w):
    """Meta (types, player, bounds) and a Float32 array, 9 per piece: type, x, y, z, qx, qy, qz, qw, length (cm)."""
    types, idx, vals = [], {}, array('f')

    def put(t, pos, rot, length):
        if t not in idx:
            idx[t] = len(types); types.append(t)
        vals.extend((idx[t], pos[0], pos[1], pos[2], rot[0], rot[1], rot[2], rot[3], length))

    for i in w.lightweight():
        put(short(i.cls), i.pos, i.rot, i.length or 0)
    for a, _ in w.save.buildings():
        t = short(a['cls'])
        pts = spline_points(a, steps=2) or wire_ends(a, in_save=True)
        if not pts:
            put(t, a['pos'], a['rot'], 0)
            continue
        for p, q in zip(pts, pts[1:]):            # belts, pipes, wires, rails: straight segments
            d = [q[k] - p[k] for k in range(3)]
            n = math.sqrt(sum(v * v for v in d))
            if n < 1:
                continue
            yaw, pitch = math.atan2(d[1], d[0]), math.asin(max(-1, min(1, d[2] / n)))
            rot = qmul((0, 0, math.sin(yaw / 2), math.cos(yaw / 2)), (0, math.sin(-pitch / 2), 0, math.cos(-pitch / 2)))
            put(t, p, rot, n)
    player = next((o['pos'] for o in w.save.objects() if o['type'] == 1 and '/Char_Player.' in o['cls']), None)
    xs, ys, zs = vals[1::9], vals[2::9], vals[3::9]
    machines = calc.db()['machines']
    boxes = {t: machines[t]['clearance'] for t in types if machines.get(t, {}).get('clearance')}
    for t in types:          # rough sizes for logistics pieces that aren't lines
        if t in boxes or re.search(r'^ConveyorBelt|^Pipeline(MK2)?$|PipeHyper$|PowerLine|Wire|RailroadTrack', t):
            continue
        if re.search(r'Pole|Support', t):
            boxes[t] = [-30, -30, 0, 30, 30, 500 if 'Power' in t else 150]
        elif re.search(r'Conveyor|Pipe|Valve|Junction', t):
            boxes[t] = [-100, -100, -50, 100, 100, 150]
    meta = dict(name=w.path.stem, session=w.session_name(), path=str(w.path), count=len(vals) // 9,
                lightweight=sum(1 for _ in w.lightweight()), types=types, boxes=boxes, player=player,
                removed=[round(v) for p in w.removed_foliage() for v in p[:2]],   # x, y of cleared trees/bushes
                bounds=[min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)] if xs else None)
    return meta, vals.tobytes()


TERRAIN = None        # folder with tiles.json + heights.bin (tools/terrain extract)
_TERRAIN = {}


def terrain():
    """The ground, read once: meta, raw heights, and a 4 m overview (33 x 33 per 128 x 128 tile)."""
    if 'meta' not in _TERRAIN:
        if not (TERRAIN / 'tiles.json').is_file():
            return None
        meta = json.loads((TERRAIN / 'tiles.json').read_text())
        raw = (TERRAIN / 'heights.bin').read_bytes()
        n = 128
        picks = list(range(0, n - 1, 4)) + [n - 1]
        over = array('H')
        for k in range(len(meta['tiles'])):
            tile = array('H'); tile.frombytes(raw[k * n * n * 2:(k + 1) * n * n * 2])
            for y in picks:
                row = y * n
                over.extend(tile[row + x] for x in picks)
        _TERRAIN.update(meta=dict(tiles=[t[3:8] for t in meta['tiles']], n=n, picks=picks, mid=32768, zscale=1 / 128),
                        raw=raw, over=over.tobytes())
    return _TERRAIN


_OBJECTS = {}
BIG_CM = 30000      # models over 300 m (background mountains, backdrops) are always loaded, not by area
REC = 44            # one copy in objects.bin: uint16 model, uint16 0, 10 float32 (pos, quaternion, scale)


def objects():
    """Trees, boulders and other placed models (tools/terrain objects): meta, model shapes, copies by 500 m area."""
    if 'meta' not in _OBJECTS:
        if not (TERRAIN / 'objects.json').is_file():
            return None
        meta = json.loads((TERRAIN / 'objects.json').read_text())
        raw = (TERRAIN / 'objects.bin').read_bytes()
        n, o = struct.unpack_from('<I', raw, 0)[0], 4
        for _ in range(n):
            nv, ni = struct.unpack_from('<II', raw, o); o += 8 + nv * 12 + ni * 4
        big = {i for i, m in enumerate(meta['models']) if m['size'] >= BIG_CM}
        areas, always = {}, []
        for key, (off, count) in meta['areas'].items():
            keep = []
            for k in range(count):
                rec = raw[off + k * REC:off + (k + 1) * REC]
                (always if struct.unpack_from('<H', rec)[0] in big else keep).append(rec)
            areas[key] = b''.join(keep)
        _OBJECTS.update(meta=dict(models=[{k: m[k] for k in ('name', 'kind', 'tris', 'size')} for m in meta['models']],
                                  areas={k: len(v) // REC for k, v in areas.items()}, area_m=500),
                        shapes=raw[:o], areas=areas, big=b''.join(always))
    return _OBJECTS


def do_place(req):
    """Put a build into a NEW copy of a save: {path, build, pos: [x, y, z] cm, yaw, name?}."""
    src = known_save(req['path'])
    f = sbp_in(build_dir(req['build']))
    w = worldlib.World(src)                       # fresh copy: placing never touches the cached one
    n, skipped = w.add_blueprint(Blueprint.load(f), [float(v) for v in req['pos']], float(req.get('yaw', 0)))
    name = req.get('name') or '%s - %s' % (src.stem, f.stem)
    out = worldlib.next_free_save(src, name)
    w.write(out)
    return dict(ok=True, path=str(out), name=out.stem, added=n, skipped=dict(skipped))


def do_install(req):
    d = build_dir(req['name'])
    f = sbp_in(d)
    session = req['session']
    if session not in sessions():
        raise ValueError('unknown save %r' % session)
    try:
        path = install(f, session, overwrite=bool(req.get('overwrite')))
    except FileExistsError:
        return 409, dict(error='exists', message='%s is already in that save.' % f.name)
    return 200, dict(ok=True, path=str(path), session=session)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write('studio: ' + fmt % args + '\n')

    def send(self, code, body, ctype='application/json'):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path in ('/', '/index.html'):
                return self.send(200, (HERE / 'index.html').read_bytes(), 'text/html; charset=utf-8')
            if u.path in ('/planner', '/planner.html'):
                return self.send(200, (HERE / 'planner.html').read_bytes(), 'text/html; charset=utf-8')
            if u.path in ('/map', '/map.html'):
                return self.send(200, (HERE / 'map.html').read_bytes(), 'text/html; charset=utf-8')
            if u.path == '/pieces.js':
                return self.send(200, (HERE / 'pieces.js').read_bytes(), 'text/javascript; charset=utf-8')
            if u.path == '/api/saves':
                return self.send(200, list_saves())
            if u.path == '/api/world':
                return self.send(200, world_of(q['path'][0])[1][0])
            if u.path == '/api/terrain':
                t = terrain()
                return self.send(200, t['meta'] if t else dict(missing=True))
            if u.path == '/api/terrain.bin':
                return self.send(200, terrain()['over'], 'application/octet-stream')
            if u.path.startswith('/api/objects/'):
                ob = objects()
                if not ob:
                    return self.send(404, dict(error='not extracted'))
                part = u.path.rsplit('/', 1)[-1]
                if part == 'meta':
                    return self.send(200, ob['meta'])
                if part == 'area':
                    return self.send(200, ob['areas'].get(q['k'][0], b''), 'application/octet-stream')
                return self.send(200, ob[{'shapes.bin': 'shapes', 'big.bin': 'big'}[part]], 'application/octet-stream')
            if u.path in ('/api/rocks.bin', '/api/water.json'):
                f = TERRAIN / u.path.split('/')[-1]
                if not f.is_file():
                    return self.send(404, dict(error='not extracted'))
                return self.send(200, f.read_bytes(), 'application/json' if f.suffix == '.json' else 'application/octet-stream')
            if u.path == '/api/terrain/tile':
                t, k, size = terrain(), int(q['i'][0]), 128 * 128 * 2
                return self.send(200, t['raw'][k * size:(k + 1) * size], 'application/octet-stream')
            if u.path == '/api/world.bin':
                return self.send(200, world_of(q['path'][0])[1][1], 'application/octet-stream')
            if u.path == '/api/items':
                items = calc.db()['items']
                return self.send(200, sorted(
                    ([k, v['name'], v['form']] for k, v in items.items() if calc.producible(k) and v['name']),
                    key=lambda x: x[1]))
            if u.path == '/api/recipes':
                item = q['item'][0]
                rs = calc.db()['recipes']
                return self.send(200, [dict(id=k, name=rs[k]['name'], alternate=rs[k]['alternate'],
                                            default=k == calc.default_recipe(item),
                                            machine=calc.db()['machines'][rs[k]['machine']]['name'])
                                       for k in sorted(calc.producers(item), key=lambda k: (rs[k]['alternate'], rs[k]['name']))])
            if u.path == '/api/creations':
                return self.send(200, list_creations())
            if u.path == '/api/creation':
                return self.send(200, model(q['name'][0]))
            if u.path == '/api/sessions':
                return self.send(200, dict(root=str(blueprints_root()), sessions=sessions()))
            return self.send(404, dict(error='not found'))
        except Exception as e:
            return self.send(400, dict(error=str(e)))

    def do_POST(self):
        u = urlparse(self.path)
        try:
            n = int(self.headers.get('Content-Length', 0))
            req = json.loads(self.rfile.read(n) or b'{}')
            if u.path == '/api/save':
                return self.send(200, save(req))
            if u.path == '/api/install':
                code, body = do_install(req)
                return self.send(code, body)
            if u.path == '/api/place':
                return self.send(200, do_place(req))
            if u.path == '/api/factory':
                return self.send(200, make_factory(req))
            if u.path == '/api/plan':
                targets = [(calc.find_item(t[0]), float(t[1])) for t in req.get('targets', []) if float(t[1]) > 0]
                if not targets:
                    return self.send(200, None)
                return self.send(200, calc.plan(targets, use=req.get('use', []),
                                                clock=float(req.get('clock', 100)) / 100,
                                                miner=req.get('miner', 'MinerMk2'),
                                                purity=req.get('purity', 'normal')))
            return self.send(404, dict(error='not found'))
        except Exception as e:
            return self.send(400, dict(error=str(e)))


def main():
    global CREATIONS
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8770)
    ap.add_argument('--creations', default=str(Path.cwd() / '.local' / 'blueprints'))
    ap.add_argument('--terrain', default=None, help='folder with tiles.json + heights.bin (default: <creations>/../terrain/data)')
    a = ap.parse_args()
    CREATIONS = Path(a.creations).resolve()
    global TERRAIN
    TERRAIN = Path(a.terrain).resolve() if a.terrain else CREATIONS.parent / 'terrain' / 'data'
    CREATIONS.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(('127.0.0.1', a.port), Handler)
    print('Blueprint Studio on http://localhost:%d  (builds in %s)' % (a.port, CREATIONS), flush=True)
    srv.serve_forever()


if __name__ == '__main__':
    main()

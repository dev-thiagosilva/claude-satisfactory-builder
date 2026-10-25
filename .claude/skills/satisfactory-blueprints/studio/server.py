"""Blueprint Studio: a local web app to view, tweak and install the blueprints Claude made.

  python -I server.py [--port 8770] [--creations .local/blueprints]

Serves studio/index.html and a small JSON API on 127.0.0.1 only:
  GET  /api/creations                 builds in the creations folder
  GET  /api/creation?name=<folder>    pieces of one build (type, transform, paint)
  POST /api/save                      apply edits (keep/move/recolour/duplicate/delete); old file kept in history/
  GET  /api/sessions                  the game's save folders that hold blueprints
  POST /api/install                   copy a build into a save's blueprint folder
  GET  /planner                       production planner page (machines, resources, power)
  GET  /api/items, /api/recipes?item= items that can be produced; recipes for one item
  POST /api/plan                      {targets: [[item, rate]], use: [recipe], clock, miner, purity}
Each build is a folder: <creations>/<folder>/<Name>.sbp (+ .sbpcfg, build.py, history/).
"""
import argparse, json, math, re, shutil, sys, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
from sbp import (Blueprint, short, get_float, get_color, set_color, paint_key, sessions,
                 blueprints_root, install, size_name)
import calc

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


def spline_of(o):
    """Belt/pipe path as world points (cm), sampled from its spline, or None."""
    import re, struct
    from sbp import qrotate
    d = o['data']
    i = d.find(b'mSplineData\x00')
    if i < 0:
        return None
    d = d[i:]
    vals = [(m.group(1), struct.unpack_from('<3d', d, m.end())) for m in re.finditer(
        rb'(Location|ArriveTangent|LeaveTangent)\x00.*?/Script/CoreUObject\x00\x00\x00\x00\x00\x18\x00\x00\x00\x08', d, re.S)]
    pts = [dict(vals[k:k + 3]) for k in range(0, len(vals) - 2, 3)]
    out = []
    for a, b in zip(pts, pts[1:]):
        p0, p1, t0, t1 = a[b'Location'], b[b'Location'], a[b'LeaveTangent'], b[b'ArriveTangent']
        for s in [k / 8 for k in range(9)]:
            h = (2*s**3 - 3*s**2 + 1, s**3 - 2*s**2 + s, -2*s**3 + 3*s**2, s**3 - s**2)
            loc = [h[0]*p0[j] + h[1]*t0[j] + h[2]*p1[j] + h[3]*t1[j] for j in range(3)]
            w = qrotate(o['rot'], loc)
            out.append([round(o['pos'][j] + w[j], 1) for j in range(3)])
    return out or None


def model(name):
    f = sbp_in(build_dir(name))
    bp = Blueprint.load(f)
    pieces = []
    for i, o in enumerate(bp.actors()):
        custom = get_color(o) is not None
        pieces.append(dict(i=i, type=short(o['cls']), pos=o['pos'], rot=o['rot'], scale=o['scale'],
                           len=get_float(o, 'mLength'), paint=paint_key(o), custom=custom,
                           spline=spline_of(o)))
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
    write_sbpcfg(out.with_suffix('.sbpcfg'), '%s\n\nMachines: %s\n\nRaw inputs: %s\n\nGenerated by claude-satisfactory-builder.' % (
        title, '; '.join(rep['rows']), '; '.join(rep['raw_inputs'])))
    return dict(name=d.name, title=title, **rep)


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
    a = ap.parse_args()
    CREATIONS = Path(a.creations).resolve()
    CREATIONS.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(('127.0.0.1', a.port), Handler)
    print('Blueprint Studio on http://localhost:%d  (builds in %s)' % (a.port, CREATIONS), flush=True)
    srv.serve_forever()


if __name__ == '__main__':
    main()

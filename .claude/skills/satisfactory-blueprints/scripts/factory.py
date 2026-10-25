"""Factory generator: turn a production plan (calc.py) into a ready-to-place production line.

Each recipe step becomes a row of machines set to their recipe and clock speed. Splitter
manifolds feed every machine input (second and later inputs run on raised manifolds so their
feeders pass over the first), merger manifolds collect the outputs, and belt lanes in a corridor
on the west side link the rows. Lanes run overhead in their own column and ramp down only where
they join a row, so lines never cross. Raw resources arrive as open belt ends on the south edge
(connect your miners there); the products and any solid byproducts go into storage containers.
Everything stands on a foundation floor. A collision check runs before saving.

Not yet: pipes for fluids (fluid ports are left open), power lines, and routing byproducts back
into the line.

  python -I factory.py "Reinforced Iron Plate" 5 --out ".local/blueprints/rip-factory/RIP Factory.sbp"
  python -I factory.py "Modular Frame" 2 --use "Stitched Iron Plate" --name "Frames"

Library: build_factory(plan_dict, name) -> (Blueprint, report dict)
"""
import argparse, json, math, re, struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sbp import (Library, SIZES, set_float, short, estimate_cost, write_sbpcfg, out_of_bounds,
                 qrotate, find_prop)
from build_library import prop_spans, _span, _element_tags, _fstr, set_object_prop
import calc

LIB_DIR = Path(__file__).resolve().parent.parent / 'library'
FLOOR_TOP = 100.0            # foundations 0..100 cm; machines stand at z = 100
BELT_Z = FLOOR_TOP + 100.0   # machine belt ports are 1 m above the machine's base
MAX_BELT = 2400.0            # longest single belt piece (cm)
# Lane height classes: (height, lead-in before the ramp, ramp run). Long lanes go well overhead;
# shorter ones use a low pass with gentle ramps; very short hops stay at belt height.
LANE_CLASSES = {'high': (BELT_Z + 600.0, 200.0, 900.0), 'low': (BELT_Z + 300.0, 200.0, 450.0)}   # ramps ~34 deg (belts allow 35)
MANIFOLD_GAP = 400.0         # between parallel input (or output) manifolds of one row
LANE_Z, RAMP_RUN = LANE_CLASSES['high'][0], LANE_CLASSES['high'][2]
COLUMN_GAP = 300.0
SPLITTER = {'Input1': (-100, 0, 0), 'Output1': (100, 0, 0), 'Output2': (0, 100, 0), 'Output3': (0, -100, 0)}
MERGER = {'Input1': (-100, 0, 0), 'Input2': (0, 100, 0), 'Input3': (0, -100, 0), 'Output1': (100, 0, 0)}
BELT_TIERS = [(60, 1), (120, 2), (270, 3), (480, 4), (780, 5), (1200, 6)]


def yaw_q(deg):
    r = math.radians(deg) / 2
    return [0.0, 0.0, math.sin(r), math.cos(r)]


def add(a, b): return [a[i] + b[i] for i in range(3)]
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def mul(a, s): return [v * s for v in a]
def norm(a): return math.sqrt(sum(v * v for v in a))
def unit(a):
    n = norm(a)
    return [v / n for v in a] if n else [1.0, 0.0, 0.0]


class Factory:
    def __init__(self, size='extra-large'):
        self.lib = Library.load()
        self.bp = self.lib.new_blueprint(size=size)
        self.ports = json.loads((LIB_DIR / 'ports.json').read_text())
        self.belts = []          # (actor, [sample points]) for the collision check
        self.machines = []       # (type, pos, yaw) for the collision check and report
        self._tags = None

    # ---------- placing pieces ----------
    def place(self, t, pos, yaw=0.0, custom=False):
        donor = self.lib.donor(t, custom=custom)
        a = self.bp.add_copy(donor, self.lib.bp, pos, yaw_q(yaw))
        comps = {o['path'].rsplit('.', 1)[1]: o for o in self.bp.objects[-40:]
                 if o['type'] == 0 and o.get('outer') == a['path']}
        return dict(type=t, actor=a, comps=comps, pos=list(pos), yaw=yaw)

    def port(self, piece, name):
        if piece['type'].startswith('ConveyorAttachmentSplitter'):
            local = SPLITTER[name]
        elif piece['type'].startswith('ConveyorAttachmentMerger'):
            local = MERGER[name]
        else:
            local = self.ports[piece['type']][name]['pos']
        return add(piece['pos'], qrotate(yaw_q(piece['yaw']), local)), piece['comps'][name]

    # ---------- connections ----------
    @staticmethod
    def connect(comp_a, comp_b):
        """Link two connection components both ways (mConnectedComponent)."""
        for c, other in ((comp_a, comp_b), (comp_b, comp_a)):
            value = _fstr('Persistent_Level') + _fstr(other['path'])
            tag = _fstr('mConnectedComponent') + _fstr('ObjectProperty') + struct.pack('<iiB', 0, len(value), 0)
            blob = c['data']
            sp = _span(blob, 'mConnectedComponent', True) if b'mConnectedComponent' in blob else None
            if sp:
                blob = set_object_prop(blob, 'mConnectedComponent', other['path'], True)
                # keep the level part as Persistent_Level
            else:
                spans, none_at = prop_spans(blob, True)
                if none_at is None:
                    none_at = blob.index(_fstr('None'))
                blob = blob[:none_at] + tag + value + blob[none_at:]
            c['data'] = blob

    # ---------- belts ----------
    def _spline_tags(self, belt):
        if self._tags is None:
            sp = _span(belt['data'], 'mSplineData', True)
            tags, _ = _element_tags(belt['data'], sp['value'] + 4, sp['end'])
            self._tags = {t['name']: belt['data'][t['start']:t['value']] for t in tags}
        return self._tags

    def _set_spline(self, belt, pts):
        """pts: [(location, arrive tangent, leave tangent)] relative to the belt's origin."""
        tags = self._spline_tags(belt)
        elems = b''.join(tags['Location'] + struct.pack('<3d', *p) + tags['ArriveTangent'] + struct.pack('<3d', *a) +
                         tags['LeaveTangent'] + struct.pack('<3d', *l) + _fstr('None') for p, a, l in pts)
        value = struct.pack('<i', len(pts)) + elems
        sp = _span(belt['data'], 'mSplineData', True)
        head = bytearray(belt['data'][:sp['value']])
        struct.pack_into('<i', head, sp['size_at'], len(value))
        belt['data'] = bytes(head) + value + belt['data'][sp['end']:]

    def belt_piece(self, p0, d0, p1, d1, rate, src=None, dst=None):
        """One belt from p0 (heading d0) to p1 (heading d1). src/dst: connection components."""
        tier = next((t for cap, t in BELT_TIERS if rate <= cap + 1e-6), 6)
        b = self.place('ConveyorBeltMk%d' % tier, p0, 0.0)
        span = norm(sub(p1, p0))
        k = span
        self._set_spline(b['actor'], [([0, 0, 0], mul(unit(d0), k), mul(unit(d0), k)),
                                      (sub(p1, p0), mul(unit(d1), k), mul(unit(d1), k))])
        if src is not None:
            self.connect(src, b['comps']['ConveyorAny0'])
        if dst is not None:
            self.connect(b['comps']['ConveyorAny1'], dst)
        # sample the curve for the collision check (cubic Hermite)
        t0, t1 = mul(unit(d0), k), mul(unit(d1), k)
        pts = []
        n = max(2, int(span / 50))
        for i in range(n + 1):
            s = i / n
            h00, h10, h01, h11 = 2*s**3 - 3*s**2 + 1, s**3 - 2*s**2 + s, -2*s**3 + 3*s**2, s**3 - s**2
            pts.append([h00 * p0[j] + h10 * t0[j] + h01 * p1[j] + h11 * t1[j] for j in range(3)])
        self.belts.append((b, pts))
        return b

    def belt_path(self, waypoints, rate, src=None, dst=None, d_start=None, d_end=None):
        """Belts along a polyline (waypoints), rounding corners, splitting long runs, chained
        together; src feeds the first piece, the last piece feeds dst."""
        pts = []
        for w in waypoints:                     # drop repeated points
            if not pts or norm(sub(w, pts[-1])) > 1:
                pts.append(list(w))
        segs = []                     # (p0, d0, p1, d1)
        n = len(pts)
        lens = [norm(sub(pts[i + 1], pts[i])) for i in range(n - 1)]
        # each corner's radius fits within half of the straight runs on both sides
        radius = [0.0] + [min(200.0, lens[i - 1] / 2, lens[i] / 2) for i in range(1, n - 1)] + [0.0]
        cur = pts[0]
        cur_d = unit(d_start) if d_start else unit(sub(pts[1], pts[0]))
        for i in range(1, n):
            a, b = pts[i - 1], pts[i]
            d = unit(sub(b, a))
            R = radius[i]
            if i < n - 1:
                d_next = unit(sub(pts[i + 1], b))
                turn = sum(d[j] * d_next[j] for j in range(3)) < 0.999 and R > 1
            else:
                turn = False
            end = sub(b, mul(d, R)) if turn else b
            # straight run (split if long)
            run = norm(sub(end, cur))
            pieces = max(1, math.ceil(run / MAX_BELT))
            for k in range(pieces):
                q0 = add(cur, mul(sub(end, cur), k / pieces))
                q1 = add(cur, mul(sub(end, cur), (k + 1) / pieces))
                segs.append((q0, cur_d if (k == 0) else d, q1, d))
                cur_d = d
            cur = end
            if turn:
                after = add(b, mul(d_next, R))
                segs.append((cur, d, after, d_next))
                cur, cur_d = after, d_next
        if d_end:
            p0, d0, p1, _ = segs[-1]
            segs[-1] = (p0, d0, p1, unit(d_end))
        prev = None
        for i, (p0, d0, p1, d1) in enumerate(segs):
            s = src if i == 0 else prev['comps']['ConveyorAny1']
            t = dst if i == len(segs) - 1 else None
            b = self.belt_piece(p0, d0, p1, d1, rate, src=s if i == 0 else None, dst=t)
            if i > 0:
                self.connect(prev['comps']['ConveyorAny1'], b['comps']['ConveyorAny0'])
            prev = b
        return prev

    # ---------- machines ----------
    def set_machine(self, piece, recipe_path, clock):
        a = piece['actor']
        a['data'] = set_object_prop(a['data'], 'mCurrentRecipe', recipe_path, True)
        for name in ('mCurrentPotential', 'mPendingPotential'):
            off, t = find_prop(a['data'], name)
            if off is not None:
                set_float(a, name, clock)
            else:
                spans, none_at = prop_spans(a['data'], True)
                tag = _fstr(name) + _fstr('FloatProperty') + struct.pack('<iiBf', 0, 4, 0, clock)
                a['data'] = a['data'][:none_at] + tag + a['data'][none_at:]


# ---------- layout ----------
def machine_info(f, mtype):
    ports = f.ports.get(mtype, {})
    ins = sorted([k for k in ports if k.startswith('Input')])
    outs = sorted([k for k in ports if k.startswith('Output')])
    mean_in = sum(ports[k]['pos'][1] for k in ins) / max(1, len(ins))
    yaw = 180.0 if ins and mean_in > 0 else 0.0
    m = calc.db()['machines'].get(mtype, {})
    box = m.get('clearance') or [-400, -500, 0, 400, 500, 600]
    xs = [box[0], box[3]] + [p['pos'][0] for p in ports.values()]
    width = max(abs(v) for v in xs) * 2
    pitch = math.ceil((max(width, 600) + 200) / 100) * 100
    rot = lambda k: qrotate(yaw_q(yaw), ports[k]['pos'])
    return dict(ins=ins, outs=outs, yaw=yaw, pitch=pitch, rot=rot,
                y_in=min((rot(k)[1] for k in ins), default=-500),
                y_out=max((rot(k)[1] for k in outs), default=500))


def build_factory(plan, name='Factory', seed=0):
    import random
    rnd = random.Random(seed)
    D = calc.db()
    f = Factory()
    items = D['items']
    solid = lambda i: items[i]['form'] == 'solid'
    report = dict(warnings=[], rows=[], raw_inputs=[], outputs=[])
    steps = [l for l in plan['recipes']]
    targets = {i for i, _, _ in plan['targets']}
    k_max = 0
    rows = []
    for l in steps:
        mt = l['machine']
        info = machine_info(f, mt)
        ins = [(i, v) for i, _, v in l['inputs'] if solid(i)]
        outs = [(i, v) for i, _, v in l['outputs'] if solid(i)]
        if any(not solid(i) for i, _, _ in l['inputs'] + l['outputs']):
            report['warnings'].append('%s uses fluids: connect its pipes in game' % l['recipe_name'])
        if len(ins) > len(info['ins']) or len(outs) > len(info['outs']):
            report['warnings'].append('%s: machine ports unknown, belts not connected' % l['recipe_name'])
            ins, outs = ins[:len(info['ins'])], outs[:len(info['outs'])]
        k_max = max(k_max, len(ins) - 1)
        rows.append(dict(step=l, info=info, ins=ins, outs=outs))

    margin = 900 + 600 * k_max                     # room for raised manifold entries to climb
    # lanes: one per (item, consumer row & manifold); raw items come from the south edge
    producers = {}
    for ri, r in enumerate(rows):
        for oi, (i, v) in enumerate(r['outs']):
            producers.setdefault(i, (ri, oi))
    lanes = []
    for ri, r in enumerate(rows):
        for k, (i, v) in enumerate(r['ins']):
            lanes.append(dict(item=i, rate=v, dst=(ri, k), src=producers.get(i)))
    for ri, r in enumerate(rows):                  # product / byproduct exits to storage
        for oi, (i, v) in enumerate(r['outs']):
            if not any(l['src'] == (ri, oi) for l in lanes) or i in targets:
                lanes.append(dict(item=i, rate=v, dst=None, src=(ri, oi), store=True))
    n_cols = len(lanes)
    x_rows = margin + n_cols * COLUMN_GAP + 800     # rows start east of the corridor
    col_x = lambda c: x_rows - margin - 600 - c * COLUMN_GAP

    # rows stacked northwards, in plan (tier) order
    y_cursor = 1600.0                               # south strip for raw inputs
    for r in rows:
        info, n = r['info'], r['step']['machines']
        r['x0'] = x_rows
        y_min = info['y_in'] - 300 - MANIFOLD_GAP * max(0, len(r['ins']) - 1) - 200
        y_max = info['y_out'] + 300 + MANIFOLD_GAP * max(0, len(r['outs']) - 1) + 200
        r['y'] = y_cursor - y_min
        y_cursor += (y_max - y_min) + 400
        r['n'] = n
    y_north = y_cursor + 600

    # Lane columns: lanes too short to go overhead stay at belt height; give them the westmost
    # columns, beyond where any other row's line reaches, so nothing crosses them.
    def lane_ys(L):
        if L['src'] is None:
            y0 = 0.0
        else:
            ri, oi = L['src']
            y0 = rows[ri]['y'] + rows[ri]['info']['y_out'] + 300 + MANIFOLD_GAP * oi
        if L.get('store'):
            y1 = y_north
        else:
            ri, k = L['dst']
            y1 = rows[ri]['y'] + rows[ri]['info']['y_in'] - 300 - MANIFOLD_GAP * k
        return y0, y1
    for L in lanes:
        y0, y1 = lane_ys(L)
        span = abs(y1 - y0)
        L['cls'] = next((c for c, (z, lead, ramp) in LANE_CLASSES.items() if span > 600 + lead + 2 * ramp + 400), 'ground')
        L['ground'] = L['cls'] == 'ground'
    order = {'high': 0, 'low': 1, 'ground': 2}
    for c, L in enumerate(sorted(lanes, key=lambda L: (order[L['cls']], rnd.random() if seed else 0))):
        L['col'] = c

    # place machines and manifolds
    for ri, r in enumerate(rows):
        info, l = r['info'], r['step']
        mt, n, clock = l['machine'], r['n'], l['clock_percent'] / 100.0
        rpath = D['recipes'][l['recipe']]['path']
        r['machines'] = []
        for m in range(n):
            pos = [r['x0'] + m * info['pitch'], r['y'], FLOOR_TOP]
            p = f.place(mt, pos, info['yaw'])
            f.set_machine(p, rpath, clock)
            r['machines'].append(p)
            f.machines.append((mt, pos, info['yaw']))
        # input manifolds
        r['entries'] = []
        for k, (item, rate) in enumerate(r['ins']):
            port = info['ins'][k]
            y_k = r['y'] + info['y_in'] - 300 - MANIFOLD_GAP * k
            z_k = BELT_Z + 300 * k
            splits = []
            for p in r['machines']:
                ppos, pcomp = f.port(p, port)
                s = f.place('ConveyorAttachmentSplitter', [ppos[0], y_k, z_k], 0.0)
                o2, o2c = f.port(s, 'Output2')
                f.belt_path([o2, ppos], rate / n, src=o2c, dst=pcomp, d_start=[0, 1, 0], d_end=[0, 1, 0])
                splits.append(s)
            for a, b in zip(splits, splits[1:]):
                pa, ca = f.port(a, 'Output1'); pb, cb = f.port(b, 'Input1')
                f.belt_path([pa, pb], rate, src=ca, dst=cb)
            p_in, c_in = f.port(splits[0], 'Input1')
            # climb from belt height at the corridor edge to this manifold's height
            edge = [r['x0'] - margin, y_k, BELT_Z]
            r['entries'].append((edge, p_in, c_in, rate))
        # output manifolds (flow west)
        r['exits'] = []
        for oi, (item, rate) in enumerate(r['outs']):
            port = info['outs'][oi]
            y_o = r['y'] + info['y_out'] + 300 + MANIFOLD_GAP * oi
            merges = []
            for p in r['machines']:
                ppos, pcomp = f.port(p, port)
                mg = f.place('ConveyorAttachmentMerger', [ppos[0], y_o, BELT_Z], 180.0)
                i2, i2c = f.port(mg, 'Input2')
                f.belt_path([ppos, i2], rate / n, src=pcomp, dst=i2c, d_start=[0, 1, 0], d_end=[0, 1, 0])
                merges.append(mg)
            for a, b in zip(merges[1:], merges):      # east -> west
                pa, ca = f.port(a, 'Output1'); pb, cb = f.port(b, 'Input1')
                f.belt_path([pa, pb], rate, src=ca, dst=cb)
            p_out, c_out = f.port(merges[0], 'Output1')
            r['exits'].append((p_out, c_out, rate, item))
        report['rows'].append('%d x %s (%s) at %g%%' % (n, l['machine_name'], l['recipe_name'], l['clock_percent']))

    # producer exits run west along their row and split off into each lane's column
    by_src = {}
    for lane in lanes:
        if lane['src'] is not None:
            by_src.setdefault(lane['src'], []).append(lane)
    exit_tail = {}
    for (ri, oi), ls in by_src.items():
        p_out, c_out, rate, item = rows[ri]['exits'][oi]
        ls.sort(key=lambda L: -col_x(L['col']))          # nearest column first
        prev_p, prev_c = p_out, c_out
        for L in ls:
            x = col_x(L['col'])
            s = f.place('ConveyorAttachmentSplitter', [x, p_out[1], BELT_Z], 180.0)
            pi, ci = f.port(s, 'Input1')
            f.belt_path([prev_p, pi], rate, src=prev_c, dst=ci)
            north = L.get('store') or rows[L['dst'][0]]['y'] > rows[ri]['y']
            side = 'Output3' if north else 'Output2'           # yaw 180: Output3 faces north
            L['start'] = f.port(s, side)
            L['start_dir'] = [0, 1 if north else -1, 0]
            prev_p, prev_c = f.port(s, 'Output1')
        exit_tail[(ri, oi)] = (prev_p, prev_c)

    # lanes: up the column, along it overhead, down at the far end
    raw_x = {}
    for L in lanes:
        x = col_x(L['col'])
        if L['src'] is None:                            # raw resource from the south edge
            start_p, start_c, sdir = [x, 0.0, BELT_Z], None, [0, 1, 0]
            report['raw_inputs'].append('%s %s/min: belt end at the south edge' % (
                items[L['item']]['name'], calc.fmt(L['rate'])))
        else:
            (start_p, start_c), sdir = L['start'], L['start_dir']
        if L.get('store'):
            y_end = y_north
            box = f.place('StorageContainerMk2', [x, y_end + 400, FLOOR_TOP], 0.0)
            end_p, end_c = f.port(box, 'Input0')
            dy = 1
            pts = [start_p, [x, start_p[1] + dy * 600, BELT_Z], [x, start_p[1] + dy * (600 + RAMP_RUN), LANE_Z],
                   [x, end_p[1] - 600 - RAMP_RUN, LANE_Z], [x, end_p[1] - 600, BELT_Z], end_p]
            f.belt_path(pts, L['rate'], src=start_c, dst=end_c, d_start=sdir, d_end=[0, 1, 0])
            report['outputs'].append('%s %s/min into a storage container' % (items[L['item']]['name'], calc.fmt(L['rate'])))
            continue
        ri, k = L['dst']
        edge, p_in, c_in, rate = rows[ri]['entries'][k]
        y_t = edge[1]
        dy = 1 if y_t > start_p[1] else -1
        if not L['ground']:                                        # overhead lane
            hz, lead, ramp = LANE_CLASSES[L['cls']]
            out_lead = 600.0          # leave the branching splitter level before climbing
            run = [[x, start_p[1] + dy * out_lead, BELT_Z], [x, start_p[1] + dy * (out_lead + ramp), hz],
                   [x, y_t - dy * (lead + ramp), hz], [x, y_t - dy * lead, BELT_Z]]
        else:                                                      # short hop: stay at belt height
            run = []
        pts = [start_p] + run + [[x, y_t, BELT_Z], edge, [p_in[0] - 600, p_in[1], p_in[2]], p_in]
        f.belt_path(pts, L['rate'], src=start_c, dst=c_in, d_start=sdir, d_end=[1, 0, 0])

    # floor, then a plot that fits the factory (production lines are long and narrow, so they get
    # their own dimensions rather than one of the square building sizes)
    acts = f.bp.actors()
    xs = [o['pos'][0] for o in acts]; ys = [o['pos'][1] for o in acts]
    x_lo, x_hi = min(xs) - 800, max(xs) + 1200
    y_lo, y_hi = min(ys) - 800, max(ys) + 800
    for tx in range(int(x_lo // 800), int(x_hi // 800) + 1):
        for ty in range(int(y_lo // 800), int(y_hi // 800) + 1):
            f.place('Foundation_Concrete_8x1', [tx * 800 + 400, ty * 800 + 400, 50.0], 0.0)
    acts = f.bp.actors()
    cx = (min(o['pos'][0] for o in acts) + max(o['pos'][0] for o in acts)) / 2
    cy = (min(o['pos'][1] for o in acts) + max(o['pos'][1] for o in acts)) / 2
    cx, cy = round(cx / 800) * 800, round(cy / 800) * 800
    for o in acts:
        o['pos'][0] -= cx; o['pos'][1] -= cy
    hx = max(abs(o['pos'][0]) for o in acts) + 400
    hy = max(abs(o['pos'][1]) for o in acts) + 400
    top = max(o['pos'][2] for o in acts) + 1600
    f.bp.dims = [math.ceil(hx / 400), math.ceil(hy / 400), max(2, math.ceil(top / 800))]
    for b, pts in f.belts:
        for p in pts:
            p[0] -= cx; p[1] -= cy
    report['size'] = '%d x %d m (%d x %d foundations)' % (f.bp.dims[0] * 8, f.bp.dims[1] * 8, f.bp.dims[0], f.bp.dims[1])
    report['collisions'] = collisions(f)
    used = sorted({short(o['cls']) for o in f.bp.actors()})
    f.bp.recipes = f.lib.recipes_for([t for t in used if t in f.lib.index['types']])
    f.bp.cost = estimate_cost(f.bp)
    report['pieces'] = len(acts)
    report['machines'] = len(f.machines)
    report['belts'] = len(f.belts)
    return f, report


def build_best(plan, name='Factory', tries=30):
    """build_factory, retrying with shuffled lane columns until no belts collide."""
    best = None
    for seed in range(tries):
        f, rep = build_factory(plan, name, seed)
        if best is None or rep['collisions'] < best[1]['collisions']:
            best = (f, rep)
        if rep['collisions'] == 0:
            break
    best[1]['attempts'] = seed + 1
    return best


def collisions(f, clearance=110.0):
    """Pairs of belts that pass closer than `clearance` cm (ignoring belts that join)."""
    cell = 200.0
    grid = {}
    owner = []
    for bi, (b, pts) in enumerate(f.belts):
        for p in pts:
            key = (int(p[0] // cell), int(p[1] // cell), int(p[2] // cell))
            grid.setdefault(key, []).append((bi, p))
    joined = set()
    paths = {}
    for bi, (b, _) in enumerate(f.belts):
        paths[b['actor']['path']] = bi
    for bi, (b, _) in enumerate(f.belts):
        for c in b['comps'].values():
            for m in re.finditer(rb'PersistentLevel\.(Build_ConveyorBelt\w+?_C_\d+)', c['data']):
                other = paths.get('Persistent_Level:PersistentLevel.' + m.group(1).decode())
                if other is not None:
                    joined.add((min(bi, other), max(bi, other)))
    hits = set()
    for key, pts in grid.items():
        near = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    near += grid.get((key[0] + dx, key[1] + dy, key[2] + dz), [])
        for bi, p in pts:
            for bj, q in near:
                if bj <= bi or (bi, bj) in joined or (bi, bj) in hits:
                    continue
                if norm(sub(p, q)) < clearance:
                    # belts meeting at a splitter/merger are fine: ignore points within 1.5 m of an end
                    ends = [f.belts[bi][1][0], f.belts[bi][1][-1], f.belts[bj][1][0], f.belts[bj][1][-1]]
                    if min(norm(sub(p, e)) for e in ends) < 150 or min(norm(sub(q, e)) for e in ends) < 150:
                        continue
                    hits.add((bi, bj))
    return len(hits)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Build a ready-to-place production line blueprint.')
    ap.add_argument('targets', nargs='+', help='item name, then rate per minute (repeatable)')
    ap.add_argument('--use', action='append', default=[], help='recipe to use (e.g. an alternate)')
    ap.add_argument('--name', default=None, help='blueprint name')
    ap.add_argument('--out', default=None, help='.sbp path (default .local/blueprints/<name>/<name>.sbp)')
    a = ap.parse_args(argv)
    t = a.targets
    targets = [(calc.find_item(t[i]), float(t[i + 1])) for i in range(0, len(t), 2)]
    plan = calc.plan(targets, use=[calc.find_recipe(u) for u in a.use], clock=1.0)
    name = a.name or ' + '.join('%s %s' % (calc.fmt(r), calc.db()['items'][i]['name']) for i, r in targets) + ' Factory'
    f, rep = build_best(plan, name)
    out = Path(a.out) if a.out else Path('.local/blueprints') / re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') / (name + '.sbp')
    out.parent.mkdir(parents=True, exist_ok=True)
    f.bp.save(out)
    write_sbpcfg(out.with_suffix('.sbpcfg'), '%s\n\nMachines: %s\n\nRaw inputs: %s\n\nGenerated by claude-satisfactory-builder.' % (
        name, '; '.join(rep['rows']), '; '.join(rep['raw_inputs'])))
    print(json.dumps(dict(file=str(out), **rep), indent=1))


if __name__ == '__main__':
    main()

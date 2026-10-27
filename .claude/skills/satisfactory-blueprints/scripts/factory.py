"""Factory generator: turn a production plan (calc.py) into a ready-to-place production line.

Each recipe step becomes a row of machines set to their recipe and clock speed. Splitter
manifolds feed every machine input (second and later inputs run on raised manifolds so their
feeders pass over the first), merger manifolds collect the outputs, and belt lanes in a corridor
on the west side link the rows. Lanes run overhead in their own column and ramp down only where
they join a row, so lines never cross. Raw resources arrive as open belt ends on the south edge
(connect your miners there); the products and any solid byproducts go into storage containers.
Every machine gets a power pole wired to it; the poles are chained along each row and from row
to row, and the first row's first pole has a free connection for the player's grid.
Everything stands on a foundation floor.

Belts are built the way the game builds its own: one belt per run with several spline points,
a straight 1 m lead out of every connector, rounded corners, never steeper than 35 degrees and
never zero-length (the game drops a belt it can't build, which cuts the line). Before saving,
the layout is checked for touching belts, lanes that would have to stay low across another, and
belts the game would refuse; it's retried with other lane orders until all of these are zero.

Not yet: pipes for fluids (fluid ports are left open) and routing byproducts back into the line.

  python -I factory.py "Reinforced Iron Plate" 5 --out ".local/blueprints/rip-factory/RIP Factory.sbp"
  python -I factory.py "Modular Frame" 2 --use "Stitched Iron Plate" --name "Frames"

Library: build_factory(plan_dict, name) -> (Blueprint, report dict)
"""
import argparse, json, math, re, struct, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sbp import (Library, SIZES, set_float, short, estimate_cost, write_sbpcfg, out_of_bounds,
                 qrotate, find_prop)
from build_library import prop_spans, _span, _element_tags, _fstr, set_object_prop, add_prop
import calc

LIB_DIR = Path(__file__).resolve().parent.parent / 'library'
FLOOR_TOP = 100.0            # foundations 0..100 cm; machines stand at z = 100
BELT_Z = FLOOR_TOP + 100.0   # machine belt ports are 1 m above the machine's base
MAX_BELT = 5000.0            # longest single belt (cm); the game allows about 56 m
MAX_STRAIGHT = 2400.0        # straight runs get a spline point at least this often
LEAD = 100.0                 # straight lead out of every connector, as the game builds belts
CORNER = 200.0               # corner radius where there's room
MAX_SLOPE = 35.0             # steepest belt the game builds (degrees)
# Lane height classes: (height, lead-in before the ramp, ramp run). Long lanes go well overhead;
# shorter ones use a low pass with gentle ramps; very short hops stay at belt height.
LANE_CLASSES = {'high': (BELT_Z + 600.0, 200.0, 900.0), 'low': (BELT_Z + 300.0, 200.0, 450.0)}   # ramps ~34 deg (belts allow 35)
ROW_GAP = 1200.0             # between one row's outputs and the next row's inputs: room for lanes to climb
MANIFOLD_GAP = 900.0         # between parallel input (or output) manifolds of one row
INPUT_OFFSET = 500.0         # from a machine's input face to its first input manifold
RAISE = 250.0                # each extra input manifold sits this much higher, so its feeders
                             # pass over the lower ones; drops stay under 35 degrees with the gap above
LANE_Z, RAMP_RUN = LANE_CLASSES['high'][0], LANE_CLASSES['high'][2]
COLUMN_GAP = 300.0
SPLITTER = {'Input1': (-100, 0, 0), 'Output1': (100, 0, 0), 'Output2': (0, 100, 0), 'Output3': (0, -100, 0)}
MERGER = {'Input1': (-100, 0, 0), 'Input2': (0, 100, 0), 'Input3': (0, -100, 0), 'Output1': (100, 0, 0)}
BELT_TIERS = [(60, 1), (120, 2), (270, 3), (480, 4), (780, 5), (1200, 6)]
PIPE_TIERS = [(300, 'Pipeline_NoIndicator'), (600, 'PipelineMK2_NoIndicator')]   # m³/min
JUNCTION = {'Connection0': (-100, 0, 0), 'Connection1': (100, 0, 0), 'Connection2': (0, 100, 0), 'Connection3': (0, -100, 0)}
ENDS = {'belt': ('ConveyorAny0', 'ConveyorAny1'), 'pipe': ('PipelineConnection0', 'PipelineConnection1')}
# Splitters, mergers and pipe junctions by role, with their ports named by the side they face.
_J = dict(W='Connection0', E='Connection1', N='Connection2', S='Connection3')
NODES = {
    ('belt', 'feed'): ('ConveyorAttachmentSplitter', 0.0, dict(W='Input1', E='Output1', N='Output2')),
    ('belt', 'collect'): ('ConveyorAttachmentMerger', 180.0, dict(E='Input1', S='Input2', W='Output1')),
    ('belt', 'branch'): ('ConveyorAttachmentSplitter', 180.0, dict(E='Input1', W='Output1', S='Output2', N='Output3')),
    ('belt', 'join'): ('ConveyorAttachmentMerger', 0.0, dict(W='Input1', N='Input2', S='Input3', E='Output1')),
    ('pipe', 'feed'): ('PipelineJunction_Cross', 0.0, _J),
    ('pipe', 'collect'): ('PipelineJunction_Cross', 0.0, _J),
    ('pipe', 'branch'): ('PipelineJunction_Cross', 0.0, _J),
    ('pipe', 'join'): ('PipelineJunction_Cross', 0.0, _J),
}
CAPS = {'belt': 1200.0, 'pipe': 600.0}   # most a single belt / pipe carries per minute
# where factory inputs and products are buffered: (piece, its inlet, its outlet, outlet's local y, half width)
BUFFERS = {'belt': ('StorageContainerMk1', 'Input0', 'Output1', 400.0, 300.0),
           'pipe': ('PipeStorageTank', 'ConnectionAny1', 'ConnectionAny0', 200.0, 300.0)}
STORES = {'belt': ('StorageContainerMk2', 'Input0'), 'pipe': ('PipeStorageTank', 'ConnectionAny1')}
POLE_TIER = 'Mk2'            # Mk.2 poles: 7 connections, so one pole powers 4 machines
POLE_LINKS = {'PowerPoleMk1': 4, 'PowerPoleMk2': 7, 'PowerPoleMk3': 10}
CAP = 1200.0                 # most items a belt carries (Mk.6); bigger flows split into rows/belts
EPS = 0.01
RAW_BOX = 'StorageContainerMk1'   # buffer on every factory input (the supply belt fills it)
RAW_Y0, RAW_STEP, RAW_SLOT = 1400.0, 1000.0, 700.0   # input lines 10 m apart: room to climb over the next
STORE_SLOT = 800.0           # spacing of the product containers
SIGN = 'StandaloneWidgetSign_Small'   # Label Sign, 2 m x 1 m
SUPPORT = 'Beam_Painted'     # vertical beams under anything raised: nothing floats
UP = (0.0, -math.sqrt(0.5), 0.0, math.sqrt(0.5))   # a beam's local +X pointing straight up
SUPPORT_EVERY = 800.0        # post spacing under raised belts (cm)
SPLITTER_BELOW = 100.0       # a splitter/merger body reaches this far below its belt connectors
BELT_BELOW = 40.0            # a belt's underside, below its centre line
# (row gap, manifold gap) to try, tightest first: build_best keeps the smallest clean layout
SPACINGS = [(400.0, 650.0), (800.0, 650.0), (800.0, 900.0), (1200.0, 900.0)]
WIRE_MAX = 9000.0            # the game allows 100 m per power line; keep a margin
WIRE_VEC = re.compile(rb'(Locations|CachedRelativeLocations)\x00.*?/Script/CoreUObject\x00\x00\x00\x00\x00\x18\x00\x00\x00[\x08\x09]', re.S)


def yaw_q(deg):
    r = math.radians(deg) / 2
    return [0.0, 0.0, math.sin(r), math.cos(r)]


def add(a, b): return [a[i] + b[i] for i in range(3)]
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def mul(a, s): return [v * s for v in a]
def norm(a): return math.sqrt(sum(v * v for v in a))
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
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
        self.folds = 0           # belts that double back on themselves (should stay 0)
        self.wire_jobs = []      # (piece, its power connection, piece, its power connection)
        self.wire_lengths = []   # metres, for the report
        self.poles = []
        self.n_signs = 0
        self.supports = []       # (x, y, top) of every support post
        self.sign_jobs = []      # (anchor point, side: -1 south / +1 north, title, label)
        self.blocks = []         # (x0, x1, y0, y1, top) of machines and containers, for supports
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
        elif piece['type'] == 'PipelineJunction_Cross':
            local = JUNCTION[name]
        else:
            local = self.ports[piece['type']][name]['pos']
        return add(piece['pos'], qrotate(yaw_q(piece['yaw']), local)), piece['comps'][name]

    def node(self, kind, role, pos):
        """A splitter / merger / pipe junction for this kind and role (see NODES)."""
        t, yaw, sides = NODES[(kind, role)]
        n = self.place(t, pos, yaw)
        n['sides'] = sides
        return n

    def side(self, n, facing):
        return self.port(n, n['sides'][facing])

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
                blob = add_prop(blob, tag + value)
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

    def belt_path(self, waypoints, rate, src=None, dst=None, d_start=None, d_end=None, kind='belt', net=None):
        """A belt along a polyline (waypoints), shaped the way the game shapes its own belts: one
        belt with several spline points, a straight 1 m lead out of each connector, corners
        rounded into arcs, and the game's tangent sizes (half the length on straights, 4·r·tan(θ/4)
        on arcs). Runs longer than one belt allows are split into belts joined end to end.
        src feeds the first belt, the last belt feeds dst. Never makes a zero-length belt.
        kind='pipe' lays pipes the same way (net: the pipe network id for this fluid)."""
        pts = []
        for w in waypoints:                     # drop repeated points
            if not pts or norm(sub(w, pts[-1])) > 1:
                pts.append(list(w))
        i = 1
        while i < len(pts) - 1:                 # drop points in the middle of a straight line
            if dot(unit(sub(pts[i], pts[i - 1])), unit(sub(pts[i + 1], pts[i]))) > 0.9999:
                pts.pop(i)
            else:
                i += 1
        if len(pts) < 2:
            raise ValueError('belt with no length between %s and its target' % (pts,))
        n = len(pts)
        lens = [norm(sub(pts[i + 1], pts[i])) for i in range(n - 1)]

        def room(j):
            """How much of segment j one corner may use (keeps the 1 m connector leads straight)."""
            if n == 2:
                return 0.0
            if j == 0:
                return max(0.0, lens[j] - (LEAD if src is not None else 0.0))
            if j == n - 2:
                return max(0.0, lens[j] - (LEAD if dst is not None else 0.0))
            return lens[j] / 2

        pieces = []                              # (p0, p1, d0, d1, tangent size)
        cur = pts[0]
        cur_d = unit(d_start) if d_start else unit(sub(pts[1], pts[0]))
        for i in range(1, n):
            d = unit(sub(pts[i], pts[i - 1]))
            turn, R = False, 0.0
            if i < n - 1:
                d_next = unit(sub(pts[i + 1], pts[i]))
                R = min(CORNER, room(i - 1), room(i))
                turn = R >= 1.0
            end = sub(pts[i], mul(d, R)) if turn else pts[i]
            run = norm(sub(end, cur))
            if run >= 1.0:
                k = max(1, math.ceil(run / MAX_STRAIGHT))
                for m in range(k):
                    q0, q1 = add(cur, mul(sub(end, cur), m / k)), add(cur, mul(sub(end, cur), (m + 1) / k))
                    pieces.append((q0, q1, cur_d if m == 0 else d, d, run / k / 2))
                    cur_d = d
            cur = end
            if i < n - 1 and dot(d, d_next) < -0.5:
                self.folds += 1                  # belt doubling back on itself: a layout bug
            if turn:
                theta = math.acos(max(-1.0, min(1.0, dot(d, d_next))))
                r = R / math.tan(theta / 2)
                after = add(pts[i], mul(d_next, R))
                pieces.append((cur, after, d, d_next, 4 * r * math.tan(theta / 4)))
                cur, cur_d = after, d_next
        if d_end:
            p0, p1, d0, _, mag = pieces[-1]
            pieces[-1] = (p0, p1, d0, unit(d_end), mag)
        # pack the pieces into belts no longer than the game allows
        belts, acc = [[]], 0.0
        for pc in pieces:
            ln = norm(sub(pc[1], pc[0]))
            if belts[-1] and acc + ln > MAX_BELT:
                belts.append([])
                acc = 0.0
            belts[-1].append(pc)
            acc += ln
        e0, e1 = ENDS[kind]
        prev = None
        for bi, group in enumerate(belts):
            b = self._belt(group, rate, kind, net)
            if bi == 0 and src is not None:
                self.connect(src, b['comps'][e0])
            if prev is not None:
                self.connect(prev['comps'][e1], b['comps'][e0])
            prev = b
        if dst is not None:
            self.connect(prev['comps'][e1], dst)
        return prev

    def _belt(self, pieces, rate, kind='belt', net=None):
        """One belt (or pipe) through consecutive pieces (p0, p1, d0, d1, tangent size), the
        lowest tier that carries `rate`."""
        if kind == 'pipe':
            t = next((t for cap, t in PIPE_TIERS if rate <= cap + 1e-6), PIPE_TIERS[-1][1])
        else:
            t = 'ConveyorBeltMk%d' % next((t for cap, t in BELT_TIERS if rate <= cap + 1e-6), 6)
        origin = pieces[0][0]
        b = self.place(t, origin, 0.0)
        b['kind'] = kind
        if kind == 'pipe' and net is not None:
            for c in ENDS['pipe']:
                off, _ = find_prop(b['comps'][c]['data'], 'mPipeNetworkID')
                if off is not None:
                    blob = bytearray(b['comps'][c]['data']); struct.pack_into('<i', blob, off, net)
                    b['comps'][c]['data'] = bytes(blob)
        spline = [(sub(origin, origin), mul(pieces[0][2], pieces[0][4]), mul(pieces[0][2], pieces[0][4]))]
        for k, (p0, p1, d0, d1, mag) in enumerate(pieces):
            arrive = mul(d1, mag)
            leave = mul(pieces[k + 1][2], pieces[k + 1][4]) if k + 1 < len(pieces) else arrive
            spline.append((sub(p1, origin), arrive, leave))
        self._set_spline(b['actor'], spline)
        # sample the curve for the collision and slope checks (cubic Hermite)
        pts = []
        for p0, p1, d0, d1, mag in pieces:
            t0, t1 = mul(d0, mag), mul(d1, mag)
            steps = max(2, int(norm(sub(p1, p0)) / 50))
            for i in range(0 if not pts else 1, steps + 1):
                s = i / steps
                h00, h10, h01, h11 = 2*s**3 - 3*s**2 + 1, s**3 - 2*s**2 + s, -2*s**3 + 3*s**2, s**3 - s**2
                pts.append([h00 * p0[j] + h10 * t0[j] + h01 * p1[j] + h11 * t1[j] for j in range(3)])
        self.belts.append((b, pts))
        return b

    # ---------- machines ----------
    def set_machine(self, piece, recipe_path, clock):
        a = piece['actor']
        a['data'] = set_object_prop(a['data'], 'mCurrentRecipe', recipe_path, True)
        for name in ('mCurrentPotential', 'mPendingPotential'):
            off, t = find_prop(a['data'], name)
            if off is not None:
                set_float(a, name, clock)
            else:
                a['data'] = add_prop(a['data'], _fstr(name) + _fstr('FloatProperty') + struct.pack('<iiBf', 0, 4, 0, clock))

    # ---------- signs ----------
    @staticmethod
    def _set_array(blob, name, elements):
        sp = _span(blob, name, True)
        value = struct.pack('<i', len(elements)) + b''.join(elements)
        head = bytearray(blob[:sp['value']])
        struct.pack_into('<i', head, sp['size_at'], len(value))
        return bytes(head) + value + blob[sp['end']:]

    @staticmethod
    def _str_prop(name, text):
        v = _fstr(text)
        return _fstr(name) + _fstr('StrProperty') + struct.pack('<iiB', 0, len(v), 0) + v

    def sign_later(self, anchor, side, title, label):
        """A sign beside the belt at `anchor`, on its south (-1) or north (+1) side, placed once
        every belt exists so it can stand clear of them (see add_supports)."""
        self.sign_jobs.append((list(anchor), side, title, label))

    def sign(self, pos, yaw, title, label):
        """A Label Sign (2 m x 1 m) at pos, its face turned to yaw (0 faces -Y). Two lines of
        text, no icons."""
        s = self.place(SIGN, pos, yaw)
        a = s['actor']
        blob = a['data'].replace(b'BPW_Sign1x1_0', b'BPW_Sign4x1_2')   # the label layout (same length)
        blob = self._set_array(blob, 'mPrefabTextElementSaveData', [
            self._str_prop('ElementName', 'Name') + self._str_prop('Text', title.upper()) + _fstr('None'),
            self._str_prop('ElementName', 'Label') + self._str_prop('Text', label) + _fstr('None')])
        blob = self._set_array(blob, 'mPrefabIconElementSaveData', [])
        blob = self._set_array(blob, 'mGlobalPrefabIconElementSaveData', [])
        a['data'] = blob
        self.n_signs += 1
        return s

    # ---------- smart splitters ----------
    def sort_rules(self, piece, rules):
        """Smart splitter rules: {output name: 'Wildcard' | 'Overflow' | 'None' | item class}.
        Outputs not named get 'None'. Rule index n-1 is the splitter's Output n."""
        rules = dict(rules)
        for o in ('Output1', 'Output2', 'Output3'):
            rules.setdefault(o, 'None')
        elems = []
        for out, what in sorted(rules.items()):
            path = '/Game/FactoryGame/Resource/FilteringRules/Desc_%s.Desc_%s_C' % (what, what)
            v = _fstr('') + _fstr(path)
            elems.append(_fstr('ItemClass') + _fstr('ObjectProperty') + struct.pack('<iiB', 0, len(v), 0) + v +
                         _fstr('OutputIndex') + _fstr('IntProperty') + struct.pack('<iiBi', 0, 4, 0, int(out[-1]) - 1) +
                         _fstr('None'))
        piece['actor']['data'] = self._set_array(piece['actor']['data'], 'mSortRules', elems)

    # ---------- power ----------
    def power_name(self, piece):
        """The piece's power connection component name, if we know where wires attach to it."""
        known = self.ports.get(piece['type'], {})
        return next((n for n in piece['comps'] if re.match(r'Power(Input|Connection)', n) and n in known), None)

    def wire_later(self, a, b):
        """Queue a power line between two placed pieces (wires are drawn once positions are final)."""
        self.wire_jobs.append((a, self.power_name(a), b, self.power_name(b)))

    def _attach(self, piece, name):
        o = piece['actor']
        local = self.ports[piece['type']][name]['pos']
        w = qrotate(o['rot'], local)
        return [o['pos'][k] + w[k] for k in range(3)]

    def make_wires(self):
        """Every queued power line, as the game stores one: the wire actor at its second end, both
        end positions (world and relative), its length, the two connections it joins after its
        properties, and each connection listing its wires in mWires."""
        lists = {}
        ref = lambda path: _fstr('Persistent_Level') + _fstr(path)
        for a, na, b, nb in self.wire_jobs:
            pa, pb = self._attach(a, na), self._attach(b, nb)
            w = self.bp.add_copy(self.lib.donor('PowerLine'), self.lib.bp, pb, [0.0, 0.0, 0.0, 1.0])
            blob = bytearray(w['data'])
            sp = _span(bytes(blob), 'mWireInstances', True)
            offs = [m.end() + (4 if blob[m.end() - 1] & 1 else 0)
                    for m in WIRE_VEC.finditer(bytes(blob), sp['value'], sp['end'])]
            for off, vec in zip(offs, (pa, pb, sub(pa, pb), [0.0, 0.0, 0.0])):
                struct.pack_into('<3d', blob, off, *vec)
            w['data'] = bytes(blob)
            set_float(w, 'mCachedLength', norm(sub(pa, pb)))
            spans, none_at = prop_spans(w['data'], True)
            end = none_at + len(_fstr('None'))
            ca, cb = a['comps'][na], b['comps'][nb]
            w['data'] = w['data'][:end] + bytes(4) + ref(ca['path']) + ref(cb['path'])
            for c in (ca, cb):
                lists.setdefault(id(c), (c, []))[1].append(w['path'])
            self.wire_lengths.append(norm(sub(pa, pb)) / 100)
        for c, paths in lists.values():
            value = struct.pack('<i', len(paths)) + b''.join(ref(p) for p in paths)
            tag = _fstr('mWires') + _fstr('ArrayProperty') + struct.pack('<i', 1) + _fstr('ObjectProperty') + \
                struct.pack('<iiB', 0, len(value), 0)
            c['data'] = add_prop(c['data'], tag + value)


# ---------- layout ----------
def feeder(a, b, over=(), lead=150.0, clear=130.0):
    """Waypoints for a belt from a splitter (a) straight ahead into a machine port (b): level out
    of the splitter, then down in straight ramps passing `clear` cm above each lower manifold it
    crosses (over: [(y, height)] in the order met), level again into the port."""
    d = unit(sub([b[0], b[1], 0], [a[0], a[1], 0]))
    if abs(a[2] - b[2]) < 1:
        return [a, b]
    pts = [a, [a[0] + d[0] * lead, a[1] + d[1] * lead, a[2]]]
    for y, z in over:
        pts.append([a[0], y, min(a[2], max(b[2], z + clear))])
    pts += [[b[0] - d[0] * lead, b[1] - d[1] * lead, b[2]], b]
    return pts


def machine_info(f, mtype):
    """Ports by kind and side: ins/outs are belt ports, pipe_ins/pipe_outs pipe ports. A pipe
    port named neither input nor output belongs to whichever side it sits on. The machine is
    turned so its inputs face south (-Y)."""
    ports = f.ports.get(mtype, {})
    ins = sorted([k for k in ports if k.startswith('Input')])
    outs = sorted([k for k in ports if k.startswith('Output')])
    pipes = [k for k in ports if 'Pipe' in k]
    ref = ins or [k for k in pipes if 'Input' in k]
    in_side = 1 if ref and sum(ports[k]['pos'][1] for k in ref) / len(ref) > 0 else -1
    pipe_ins = sorted(k for k in pipes if 'Input' in k or ('Output' not in k and ports[k]['pos'][1] * in_side > 0))
    pipe_outs = sorted(k for k in pipes if k not in pipe_ins)
    yaw = 180.0 if in_side > 0 else 0.0
    m = calc.db()['machines'].get(mtype, {})
    box = m.get('clearance') or [-400, -500, 0, 400, 500, 600]
    xs = [box[0], box[3]] + [p['pos'][0] for p in ports.values()]
    width = max(abs(v) for v in xs) * 2
    pitch = math.ceil((max(width, 600) + 200) / 100) * 100
    rot = lambda k: qrotate(yaw_q(yaw), ports[k]['pos'])
    return dict(ins=ins, outs=outs, pipe_ins=pipe_ins, pipe_outs=pipe_outs, yaw=yaw, pitch=pitch, rot=rot,
                y_in=min((rot(k)[1] for k in ins + pipe_ins), default=-500),
                y_out=max((rot(k)[1] for k in outs + pipe_outs), default=500))


def build_factory(plan, name='Factory', seed=0, row_gap=None, manifold_gap=None, pole=None):
    """Lay out a production line for a calc.plan(). row_gap / manifold_gap override the spacing
    (build_best searches them for the most compact layout); pole is 'Mk1', 'Mk2' or 'Mk3'."""
    import random
    rnd = random.Random(seed)
    ROW_GAP_ = row_gap or ROW_GAP
    GAP = manifold_gap or MANIFOLD_GAP
    pole_type = 'PowerPole' + (pole or POLE_TIER)
    D = calc.db()
    f = Factory()
    items = D['items']
    iname = lambda i: items[i]['name']
    solid = lambda i: items[i]['form'] == 'solid'
    kind_of = lambda i: 'belt' if solid(i) else 'pipe'
    unit = lambda kd: '/min' if kd == 'belt' else ' m3/min'
    report = dict(warnings=[], rows=[], raw_inputs=[], outputs=[])
    targets = {}
    for i, _, v in plan['targets']:
        targets[i] = targets.get(i, 0.0) + v

    # rows: one per recipe step, split into parallel rows so no belt carries more than CAP
    rows = []
    for l in plan['recipes']:
        info = machine_info(f, l['machine'])
        ins, outs = [], []
        for flows_, belt_ports, pipe_ports, dest in ((l['inputs'], info['ins'], info['pipe_ins'], ins),
                                                     (l['outputs'], info['outs'], info['pipe_outs'], outs)):
            free = {'belt': list(belt_ports), 'pipe': list(pipe_ports)}
            for i, _, v in sorted(flows_, key=lambda x: not solid(x[0])):     # belts first, then pipes
                kd = kind_of(i)
                if free[kd]:
                    dest.append(dict(item=i, rate=v, kind=kd, port=free[kd].pop(0)))
                else:
                    report['warnings'].append('%s: no known %s port for %s; connect it in game' % (
                        l['recipe_name'], kd, iname(i)))
        n = l['machines']
        parts = min(n, max([1] + [math.ceil(e['rate'] / CAPS[e['kind']] - 1e-9) for e in ins + outs]))
        for p in range(parts):
            n_p = n // parts + (1 if p < n % parts else 0)
            share = n_p / n
            rows.append(dict(step=l, info=info, n=n_p,
                             ins=[dict(e, rate=e['rate'] * share) for e in ins],
                             outs=[dict(e, rate=e['rate'] * share) for e in outs]))
        report['rows'].append('%d x %s (%s) at %g%%%s' % (n, l['machine_name'], l['recipe_name'],
                              l['clock_percent'], ' in %d rows' % parts if parts > 1 else ''))
    k_max = max([len(r['ins']) - 1 for r in rows], default=0)
    margin = 900 + 600 * k_max                     # room for raised manifold entries to climb

    # Flows, item by item: producer exits feed consumer manifolds; what's left (targets and
    # surplus) goes to storage in loads of at most CAP. Items nobody makes come in from outside:
    # their consumers are packed into input containers of at most CAP each (one supply belt each).
    flows = {}
    for ri, r in enumerate(rows):
        for oi, e in enumerate(r['outs']):
            flows.setdefault(e['item'], ([], []))[0].append((('row', ri, oi), e['rate']))
        for k, e in enumerate(r['ins']):
            flows.setdefault(e['item'], ([], []))[1].append(((ri, k), e['rate']))
    net = {i: n + 1 for n, i in enumerate(sorted(flows))}      # one pipe network per fluid
    lanes, raw_groups = [], []
    for item, (srcs, dsts) in flows.items():
        kd = kind_of(item)
        CAP = CAPS[kd]
        if not srcs:
            groups = []
            for dst, v in sorted(dsts, key=lambda d: -d[1]):
                g = next((g for g in groups if g['rate'] + v <= CAP + 1e-6), None)
                if g is None:
                    g = dict(item=item, kind=kd, rate=0.0, dsts=[])
                    groups.append(g)
                g['rate'] += v
                g['dsts'].append((dst, v))
            for g in groups:
                j = len(raw_groups)
                raw_groups.append(g)
                for dst, v in g['dsts']:
                    lanes.append(dict(item=item, kind=kd, rate=v, src=('raw', j), dst=dst))
            continue
        sinks = list(dsts)
        left = sum(v for _, v in srcs) - sum(v for _, v in dsts)
        while left > EPS:
            q = min(CAP, left)
            sinks.append((None, q))
            left -= q
        si = di = 0
        s_left, d_left = srcs[0][1], sinks[0][1] if sinks else 0
        while si < len(srcs) and di < len(sinks):
            q = min(s_left, d_left)
            if q > EPS:
                lanes.append(dict(item=item, kind=kd, rate=q, src=srcs[si][0], dst=sinks[di][0], store=sinks[di][0] is None))
            s_left -= q
            d_left -= q
            if s_left <= EPS:
                si += 1
                s_left = srcs[si][1] if si < len(srcs) else 0
            if d_left <= EPS:
                di += 1
                d_left = sinks[di][1] if di < len(sinks) else 0
        if di < len(sinks) and sinks[di][0] is not None and d_left > EPS:
            report['warnings'].append('%s: not enough made inside the line for every consumer' % iname(item))
    n_cols = len(lanes)
    x_rows = margin + n_cols * COLUMN_GAP + 800     # rows start east of the corridor
    col_x = lambda c: x_rows - margin - 600 - c * COLUMN_GAP

    # raw input containers along the south, east of the corridor; each one's exit line runs west
    # at its own height (further east = further north, so no line crosses another container)
    raw_y = [RAW_Y0 + RAW_STEP * j for j in range(len(raw_groups))]
    y_cursor = (raw_y[-1] if raw_y else 0.0) + 1600.0
    for r in rows:
        info = r['info']
        y_min = info['y_in'] - INPUT_OFFSET - GAP * max(0, len(r['ins']) - 1) - 200
        y_max = info['y_out'] + 300 + GAP * max(0, len(r['outs']) - 1) + 200
        r['x0'] = x_rows
        r['y'] = y_cursor - y_min
        r['y_bottom'], r['y_top'] = y_cursor, y_cursor + (y_max - y_min)
        y_cursor += (y_max - y_min) + ROW_GAP_
    y_north = y_cursor + 600

    def src_y(src):
        if src[0] == 'raw':
            return raw_y[src[1]]
        _, ri, oi = src
        return rows[ri]['y'] + rows[ri]['info']['y_out'] + 300 + GAP * oi

    def lane_ys(L):
        if L.get('store'):
            return src_y(L['src']), y_north
        ri, k = L['dst']
        return src_y(L['src']), rows[ri]['y'] + rows[ri]['info']['y_in'] - INPUT_OFFSET - GAP * k

    for L in lanes:
        y0, y1 = lane_ys(L)
        span = abs(y1 - y0)
        classes = [c for c in LANE_CLASSES if L['kind'] == 'belt' or c == 'low']     # pipes stay low (head lift)
        L['cls'] = next((c for c in classes if span > 600 + LANE_CLASSES[c][1] + 2 * LANE_CLASSES[c][2] + 400), 'ground')
        L['ground'] = L['cls'] == 'ground'
    order = {'high': 0, 'low': 1, 'ground': 2}
    for c, L in enumerate(sorted(lanes, key=lambda L: (order[L['cls']], rnd.random() if seed else 0))):
        L['col'] = c
    # Lanes feeding one row from the same side: the one whose manifold is met first must sit
    # west of the ones going further, or its turn into the row crosses them while they come down.
    groups = {}
    for L in lanes:
        if L.get('store'):
            continue
        y0, y1 = lane_ys(L)
        groups.setdefault((L['dst'][0], 1 if y1 > y0 else -1, L['ground']), []).append(L)
    for (ri, dy, ground), ls in groups.items():
        cols = sorted(L['col'] for L in ls)
        ls.sort(key=lambda L: -L['dst'][1] if dy > 0 else L['dst'][1])
        for L, c in zip(ls, cols):
            L['col'] = c
    # A source that also sends to storage sends there last: that lane takes the westmost column
    # of its source's lanes, and the splitters before it give their own lanes priority (overflow).
    by_src = {}
    for L in lanes:
        by_src.setdefault(L['src'], []).append(L)
    for ls in by_src.values():
        out = [L for L in ls if L.get('store')]
        if out and len(ls) > 1:
            west = max(ls, key=lambda L: L['col'])
            out[0]['col'], west['col'] = west['col'], out[0]['col']

    # place machines, manifolds and their signs
    for ri, r in enumerate(rows):
        info, l = r['info'], r['step']
        mt, n, clock = l['machine'], r['n'], l['clock_percent'] / 100.0
        rpath = D['recipes'][l['recipe']]['path']
        r['machines'] = []
        for m in range(n):
            pos = [r['x0'] + m * info['pitch'], r['y'], FLOOR_TOP]
            p = f.place(mt, pos, info['yaw'])
            f.set_machine(p, rpath, clock)
            half = (info['pitch'] - 200) / 2             # the machine body: between its port faces
            f.blocks.append((pos[0] - half, pos[0] + half, pos[1] + info['y_in'] + 20, pos[1] + info['y_out'] - 20, FLOOR_TOP + 600))
            r['machines'].append(p)
            f.machines.append((mt, pos, info['yaw']))
        r['entries'] = []
        for k, e in enumerate(r['ins']):
            item, rate, kd, port = e['item'], e['rate'], e['kind'], e['port']
            y_k = r['y'] + info['y_in'] - INPUT_OFFSET - GAP * k
            over = [(r['y'] + info['y_in'] - INPUT_OFFSET - GAP * j, BELT_Z + RAISE * j) for j in range(k - 1, -1, -1)]
            z_k = max(BELT_Z + RAISE * k, f.port(r['machines'][0], port)[0][2])
            splits = []
            for p in r['machines']:
                ppos, pcomp = f.port(p, port)
                s = f.node(kd, 'feed', [ppos[0], y_k, z_k])
                o2, o2c = f.side(s, 'N')
                f.belt_path(feeder(o2, ppos, over), rate / n, src=o2c, dst=pcomp, d_start=[0, 1, 0], d_end=[0, 1, 0],
                            kind=kd, net=net[item])
                f.sign_later(ppos, -1, iname(item), 'IN %s%s' % (calc.fmt(rate / n), unit(kd)))
                splits.append(s)
            for a, b in zip(splits, splits[1:]):
                pa, ca = f.side(a, 'E'); pb, cb = f.side(b, 'W')
                f.belt_path([pa, pb], rate, src=ca, dst=cb, kind=kd, net=net[item])
            p_in, c_in = f.side(splits[0], 'W')
            r['entries'].append(([r['x0'] - margin, y_k, BELT_Z], p_in, c_in, rate))
        r['exits'] = []
        y_m0 = r['y'] + info['y_out'] + 300
        for oi, e in enumerate(r['outs']):
            item, rate, kd, port = e['item'], e['rate'], e['kind'], e['port']
            y_o = y_m0 + GAP * oi
            merges = []
            for p in r['machines']:
                ppos, pcomp = f.port(p, port)
                mg = f.node(kd, 'collect', [ppos[0], y_o, BELT_Z])
                i2, i2c = f.side(mg, 'S')
                # a second output (a fluid beside a solid) hops over the first output's line
                pts = [ppos, i2] if oi == 0 else [ppos, [ppos[0], y_m0 - 150, BELT_Z + 300],
                                                  [ppos[0], y_m0 + 150, BELT_Z + 300], i2]
                f.belt_path(pts, rate / n, src=pcomp, dst=i2c, d_start=[0, 1, 0], d_end=[0, 1, 0], kind=kd, net=net[item])
                f.sign_later(ppos, 1, iname(item), 'OUT %s%s' % (calc.fmt(rate / n), unit(kd)))
                merges.append(mg)
            for a, b in zip(merges[1:], merges):      # east -> west
                pa, ca = f.side(a, 'W'); pb, cb = f.side(b, 'E')
                f.belt_path([pa, pb], rate, src=ca, dst=cb, kind=kd, net=net[item])
            p_out, c_out = f.side(merges[0], 'W')
            r['exits'].append(([p_out], c_out, rate, item))

    # raw input containers: the player's supply belt fills each one, the line takes from it
    raw_exits = []
    for j, g in enumerate(raw_groups):
        xc = x_rows + RAW_SLOT * j
        piece, inlet, outlet, out_y, half = BUFFERS[g['kind']]
        box = f.place(piece, [xc, raw_y[j] - 400 - out_y, FLOOR_TOP], 0.0)
        f.blocks.append((xc - half, xc + half, raw_y[j] - 400 - 2 * out_y, raw_y[j] - 400, FLOOR_TOP + 500))
        out_p, out_c = f.port(box, outlet)
        in_p, _ = f.port(box, inlet)
        f.sign_later(in_p, -1, iname(g['item']), 'SUPPLY %s%s' % (calc.fmt(g['rate']), unit(g['kind'])))
        raw_exits.append(([out_p, [xc, raw_y[j], BELT_Z]], out_c, g['rate'], g['item']))
        report['raw_inputs'].append('%s %s%s: into the %s on the south side' % (
            iname(g['item']), calc.fmt(g['rate']), unit(g['kind']),
            'input container' if g['kind'] == 'belt' else 'fluid buffer (connect a pipe)'))

    def exit_of(src):
        return raw_exits[src[1]] if src[0] == 'raw' else rows[src[1]]['exits'][src[2]]

    # each source's exit line runs west and splits off into its lanes' columns, nearest first;
    # a lane to storage takes what the others leave (smart splitters send it the overflow)
    for src, ls in by_src.items():
        lead, c_out, rate, item = exit_of(src)
        kd = ls[0]['kind']
        y_exit = lead[-1][1]
        ls.sort(key=lambda L: -col_x(L['col']))
        has_store = kd == 'belt' and any(L.get('store') for L in ls) and len(ls) > 1
        prev_pts, prev_c, left = lead, c_out, rate
        for L in ls:
            x = col_x(L['col'])
            if L.get('store') and L is ls[-1] and has_store:
                L['start'] = (prev_pts[0], prev_c)
                L['prefix'] = prev_pts[1:] + [[x, y_exit, BELT_Z]]
                L['start_dir'] = None
                continue
            smart = has_store
            if smart:
                s = f.place('ConveyorAttachmentSplitterSmart', [x, y_exit, BELT_Z], 180.0)
                s['sides'] = NODES[('belt', 'branch')][2]
            else:
                s = f.node(kd, 'branch', [x, y_exit, BELT_Z])
            pi, ci = f.side(s, 'E')
            f.belt_path(prev_pts + [pi], left, src=prev_c, dst=ci, kind=kd, net=net[item])
            north = L.get('store') or lane_ys(L)[1] > y_exit
            facing = 'N' if north else 'S'
            if smart:
                f.sort_rules(s, {s['sides'][facing]: 'Wildcard', s['sides']['W']: 'Overflow'})
            L['start'] = f.side(s, facing)
            L['start_dir'] = [0, 1 if north else -1, 0]
            L['prefix'] = []
            left -= L['rate']
            prev_pts, prev_c = [f.side(s, 'W')[0]], f.side(s, 'W')[1]

    # entries fed by more than one lane get a merger per lane at the turn into the row
    by_dst = {}
    for L in lanes:
        if not L.get('store'):
            by_dst.setdefault(L['dst'], []).append(L)

    # Level runs at belt height that cross lane columns: turns into rows, exit lines, and the
    # store lanes' turns east. A lane must be up at full height wherever one crosses its column.
    runs = []
    for dst, ls in by_dst.items():
        edge = rows[dst[0]]['entries'][dst[1]][0]
        runs.append((edge[1], min(col_x(L['col']) for L in ls), edge[0], ('entry', dst)))
    for src, ls in by_src.items():
        lead = exit_of(src)[0]
        runs.append((lead[-1][1], min(col_x(L['col']) for L in ls), lead[-1][0], ('exit', src)))

    def crossings(L, x):
        own = {('exit', L['src'])}
        if not L.get('store'):
            own.add(('entry', L['dst']))
        return sorted(y for y, lo, hi, who in runs if who not in own and lo + 1 < x < hi - 1)

    def ramps(L, x, y0, y_t, dy, ramp, lead):
        """Where to climb and descend: (c0, c1, d0, d1) along y, or None if no clear stretch."""
        ahead = [y for y in crossings(L, x) if (y - y0) * dy > 0 and (y_t - y) * dy > 0]
        c0 = y0 + dy * 150.0
        c1 = c0 + dy * ramp
        d1 = y_t - dy * lead
        d0 = d1 - dy * ramp
        if (d0 - c1) * dy < 0:
            return None
        for y in ahead:
            if (y - (c1 + dy * 150)) * dy < 0 or (y - (d0 - dy * 150)) * dy > 0:
                return None
        return c0, c1, d0, d1

    def lane_plan(L, x, y0, y_t, dy):
        for cls in dict.fromkeys([L['cls'], 'low']):
            hz, lead, ramp = LANE_CLASSES[cls]
            r = ramps(L, x, y0, y_t, dy, ramp, lead)
            if r:
                return (hz,) + r
        return None

    def column_run(L, x, y0, y_t, dy):
        plan_ = None if L['ground'] else lane_plan(L, x, y0, y_t, dy)
        if plan_ is None:
            if any((y - y0) * dy > 0 and (y_t - y) * dy > 0 for y in crossings(L, x)):
                report['lane_conflicts'] += 1
            return []
        hz, c0, c1, d0, d1 = plan_
        return [[x, c0, BELT_Z], [x, c1, hz], [x, d0, hz], [x, d1, BELT_Z]]

    report['lane_conflicts'] = 0
    # storage: lanes turn east at their own height into slots east of the corridor (the
    # easternmost lane turns first and goes furthest), product containers in a row facing south
    stores = sorted([L for L in lanes if L.get('store')], key=lambda L: -col_x(L['col']))
    m = len(stores)
    y_box = y_north + 1400 + 300 * m + 600
    for i, L in enumerate(stores):
        L['y_turn'] = y_north + 1400 + 300 * i
        L['slot_x'] = x_rows + STORE_SLOT * (m - 1 - i) + STORE_SLOT / 2
    for L in lanes:
        x = col_x(L['col'])
        start_p, start_c = L['start']
        pre = L['prefix']
        y0 = (pre[-1] if pre else start_p)[1]
        if L.get('store'):
            y_t = L['y_turn']
            piece, inlet = STORES[L['kind']]
            in_y = -f.ports[piece][inlet]['pos'][1]
            box = f.place(piece, [L['slot_x'], y_box + in_y, FLOOR_TOP], 0.0)
            f.blocks.append((L['slot_x'] - 350, L['slot_x'] + 350, y_box, y_box + 2 * in_y, FLOOR_TOP + 600))
            end_p, end_c = f.port(box, inlet)
            pts = [start_p] + pre + column_run(L, x, y0, y_t, 1) + [[x, y_t, BELT_Z], [L['slot_x'], y_t, BELT_Z], end_p]
            f.belt_path(pts, L['rate'], src=start_c, dst=end_c, d_start=L['start_dir'], d_end=[0, 1, 0],
                        kind=L['kind'], net=net[L['item']])
            f.sign_later(end_p, -1, iname(L['item']), 'OUT %s%s' % (calc.fmt(L['rate']), unit(L['kind'])))
            if L['kind'] == 'pipe' and L['item'] not in targets:
                report['warnings'].append('%s %s m3/min is left over and goes into a fluid buffer: when it is full the '
                                          'machines making it stop. Use it elsewhere or pick a recipe that uses it.' % (
                                              iname(L['item']), calc.fmt(L['rate'])))
            report['outputs'].append('%s %s%s into a %s' % (iname(L['item']), calc.fmt(L['rate']), unit(L['kind']),
                                                           'storage container' if L['kind'] == 'belt' else 'fluid buffer'))
            continue
        ri, k = L['dst']
        edge, p_in, c_in, rate = rows[ri]['entries'][k]
        y_t = edge[1]
        dy = 1 if y_t > y0 else -1
        run = column_run(L, x, y0, y_t, dy)
        group = by_dst[L['dst']]
        if len(group) == 1:
            pts = [start_p] + pre + run + [[x, y_t, BELT_Z], edge, [p_in[0] - 600, p_in[1], p_in[2]], p_in]
            f.belt_path(pts, L['rate'], src=start_c, dst=c_in, d_start=L['start_dir'], d_end=[1, 0, 0],
                        kind=L['kind'], net=net[L['item']])
            continue
        node = f.node(L['kind'], 'join', [x, y_t, BELT_Z])                  # W in, N/S in, E out
        sp_, sc_ = f.side(node, 'S' if dy > 0 else 'N')
        f.belt_path([start_p] + pre + run + [sp_], L['rate'], src=start_c, dst=sc_, d_start=L['start_dir'], d_end=[0, dy, 0],
                    kind=L['kind'], net=net[L['item']])
        L['node'] = node
    for dst, group in by_dst.items():
        if len(group) < 2:
            continue
        edge, p_in, c_in, rate = rows[dst[0]]['entries'][dst[1]]
        kd, item = group[0]['kind'], group[0]['item']
        nodes = [L['node'] for L in sorted(group, key=lambda L: col_x(L['col']))]   # west first
        acc = 0.0
        for a, b, L in zip(nodes, nodes[1:], sorted(group, key=lambda L: col_x(L['col']))):
            acc += L['rate']
            pa, ca = f.side(a, 'E'); pb, cb = f.side(b, 'W')
            f.belt_path([pa, pb], acc, src=ca, dst=cb, kind=kd, net=net[item])
        pe, ce = f.side(nodes[-1], 'E')
        f.belt_path([pe, edge, [p_in[0] - 600, p_in[1], p_in[2]], p_in], rate, src=ce, dst=c_in, d_end=[1, 0, 0],
                    kind=kd, net=net[item])

    # power: each pole serves as many machines as its connections allow (keeping two for the
    # poles either side and one for the next row / the player's grid), standing in the gap between
    # the machines it serves; poles chain along each row, first poles chain from row to row.
    per_pole = max(1, POLE_LINKS[pole_type] - 3)
    spine = None
    no_power = set()
    for ri, r in enumerate(rows):
        prev, first = None, None
        ms = r['machines']
        for g0 in range(0, len(ms), per_pole):
            grp = ms[g0:g0 + per_pole]
            h = len(grp) // 2
            x = (grp[h - 1]['pos'][0] + grp[h]['pos'][0]) / 2 if len(grp) > 1 else grp[0]['pos'][0] - r['info']['pitch'] / 2
            pl = f.place(pole_type, [x, r['y'], FLOOR_TOP], 0.0)
            f.poles.append(pl)
            for p in grp:
                if f.power_name(p):
                    f.wire_later(pl, p)
                else:
                    no_power.add(r['step']['machine_name'])
            if prev is not None:
                f.wire_later(prev, pl)
            else:
                first = pl
            prev = pl
        if spine is not None:
            a = spine
            if abs(first['pos'][1] - a['pos'][1]) > WIRE_MAX:
                relay = f.place(pole_type, [first['pos'][0], (rows[ri - 1]['y_top'] + r['y_bottom']) / 2, FLOOR_TOP], 0.0)
                f.poles.append(relay)
                f.wire_later(a, relay)
                a = relay
            f.wire_later(a, first)
        spine = first
    report['power'] = 'connect your power grid to the pole beside the first machines of the first row'
    report['power_poles'] = len(f.poles)
    for nm in sorted(no_power):
        report['warnings'].append('%s: no known power point, wire it in game' % nm)

    report.update(add_supports(f))

    # floor, then a plot that fits the factory exactly (no size presets for production lines)
    acts = f.bp.actors()
    xs = [o['pos'][0] for o in acts]; ys = [o['pos'][1] for o in acts]
    x_lo, x_hi = min(xs) - 600, max(xs) + 600
    y_lo, y_hi = min(ys) - 600, max(ys) + 600
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
    f.make_wires()
    report['size'] = '%d x %d m (%d x %d foundations)' % (f.bp.dims[0] * 8, f.bp.dims[1] * 8, f.bp.dims[0], f.bp.dims[1])
    report['area_m2'] = f.bp.dims[0] * f.bp.dims[1] * 64
    report['collisions'] = collisions(f)
    report['belt_problems'] = belt_problems(f)
    report['pole_clearance_m'] = round(min(
        (math.hypot(q[0] - p['actor']['pos'][0], q[1] - p['actor']['pos'][1])
         for p in f.poles for b, pts in f.belts for q in pts if q[2] < FLOOR_TOP + 900), default=99) / 100, 1)
    report['power_lines'] = len(f.wire_lengths)
    report['longest_power_line_m'] = round(max(f.wire_lengths, default=0), 1)
    report['belt_tiers'] = dict(sorted(Counter(short(b['actor']['cls']).replace('ConveyorBelt', 'Belt ').replace('_NoIndicator', '')
                                               for b, _ in f.belts).items()))
    report['signs'] = f.n_signs
    used = sorted({short(o['cls']) for o in f.bp.actors()})
    f.bp.recipes = f.lib.recipes_for([t for t in used if t in f.lib.index['types']])
    f.bp.cost = estimate_cost(f.bp)
    report['pieces'] = len(acts)
    report['machines'] = len(f.machines)
    report['belts'] = len(f.belts)
    return f, report


def build_best(plan, name='Factory', tries=8, pole=None):
    """The most compact layout with no problems: tries several row and manifold spacings (tight
    first) and lane orders, keeps the smallest plot where nothing collides, no lane has to stay
    low across another and every belt is one the game can build."""
    def score(rep):
        b = rep['belt_problems']
        return rep['collisions'] + rep['lane_conflicts'] + b['too_short'] + b['too_steep'] + b['doubling_back']
    best, attempts = None, 0
    for row_gap, gap in SPACINGS:
        for seed in range(tries):
            attempts += 1
            f, rep = build_factory(plan, name, seed, row_gap, gap, pole)
            key = (score(rep), rep['area_m2'])
            if best is None or key < best[0]:
                best = (key, f, rep)
            if score(rep) == 0 or (seed == 0 and score(rep) > 10):
                break                     # done, or this spacing is far too tight to fix by reordering
        if best[0][0] == 0:
            break                         # spacings are tried tightest first: the first clean one is the smallest
    _, f, rep = best
    rep['warnings'] = list(dict.fromkeys(rep['warnings']))
    rep['attempts'] = attempts
    return f, rep


def add_supports(f):
    """Nothing floats: a vertical beam under every raised splitter/merger, beam posts under raised
    belts about every SUPPORT_EVERY cm, and every sign standing on a post beside its belt. No post
    or sign may pass through a belt, machine, container or another sign; a spot that isn't clear
    is moved along (belts) or to the other side (signs). Returns counts for the report."""
    cell = 200.0
    grid = {}
    for bi, (b, pts) in enumerate(f.belts):
        for p in pts:
            grid.setdefault((int(p[0] // cell), int(p[1] // cell)), []).append((bi, p))
    panels = []                                   # placed signs: (x0, x1, y0, y1, z0, z1)

    def near(x, y, r):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for bi, p in grid.get((int(x // cell) + dx, int(y // cell) + dy), []):
                    if abs(p[0] - x) < r and abs(p[1] - y) < r:
                        yield bi, p

    def column_clear(x, y, top, own=None, r=80.0):
        if any(bi != own and p[2] < top + 30 for bi, p in near(x, y, r)):
            return False
        if any(x0 - 30 < x < x1 + 30 and y0 - 30 < y < y1 + 30 for x0, x1, y0, y1, _ in f.blocks):
            return False
        return not any(x0 - 30 < x < x1 + 30 and y0 - 30 < y < y1 + 30 for x0, x1, y0, y1, z0, z1 in panels)

    def post(x, y, top):
        length = top - FLOOR_TOP
        if length < 50:
            return False
        o = f.bp.add_copy(f.lib.donor(SUPPORT), f.lib.bp, [x, y, FLOOR_TOP], UP)
        set_float(o, 'mLength', round(length, 1))
        f.supports.append((x, y, top))
        return True

    out = dict(supports=0, unsupported=0)
    # raised splitters and mergers
    for o in f.bp.actors():
        if short(o['cls']).startswith(('ConveyorAttachment', 'PipelineJunction')) and o['pos'][2] > BELT_Z + 50:
            x, y, z = o['pos']
            top = z - SPLITTER_BELOW
            if column_clear(x, y, top, r=60.0) and post(x, y, top):
                out['supports'] += 1
            else:
                out['unsupported'] += 1
    # raised belts: a post every SUPPORT_EVERY along the belt, slid along until the spot is clear
    for bi, (b, pts) in enumerate(f.belts):
        run, wanted = 0.0, False
        for p, q in zip(pts, pts[1:]):
            run += norm(sub(q, p))
            if q[2] <= BELT_Z + 150:
                run = 0.0
                continue
            if run >= SUPPORT_EVERY or wanted:
                wanted = True
                top = q[2] - BELT_BELOW
                if column_clear(q[0], q[1], top, own=bi) and post(q[0], q[1], top):
                    out['supports'] += 1
                    run, wanted = 0.0, False
        if wanted:
            out['unsupported'] += 1
    # signs: beside their belt (2 m to one side), 1.5-2.5 m up, on a post
    for anchor, side, title, label in f.sign_jobs:
        y = anchor[1] + side * 150.0
        z0 = FLOOR_TOP + 150.0                    # bottom edge of the 1 m tall sign
        for dx in (200.0, -200.0, 320.0, -320.0, 440.0, -440.0):
            x = anchor[0] + dx
            box = (x - 110, x + 110, y - 60, y + 60, z0 - 30, z0 + 130)
            if any(box[0] < p[0] < box[1] and box[2] < p[1] < box[3] and box[4] < p[2] < box[5] for _, p in near(x, y, 160)):
                continue
            if any(not (box[1] < b[0] or b[1] < box[0] or box[3] < b[2] or b[3] < box[2]) for b in panels):
                continue
            if any(b[0] < x + 110 and x - 110 < b[1] and b[2] < y + 60 and y - 60 < b[3] for b in f.blocks):
                continue
            f.sign([x, y, z0 + 50], 180.0 if side > 0 else 0.0, title, label)
            post(x, y, z0)
            panels.append(box)
            out['supports'] += 1
            break
        else:
            out['signs_not_placed'] = out.get('signs_not_placed', 0) + 1
    return out


def belt_problems(f):
    """Belts the game would refuse or draw wrong: too short, or steeper than it allows."""
    short_, steep = 0, 0
    for b, pts in f.belts:
        length = sum(norm(sub(q, p)) for p, q in zip(pts, pts[1:]))
        if length < 50:
            short_ += 1
        if b.get('kind') == 'pipe':
            continue                              # pipes may climb steeply
        for p, q in zip(pts, pts[1:]):
            h = math.hypot(q[0] - p[0], q[1] - p[1])
            if h > 1e-6 and math.degrees(math.atan2(abs(q[2] - p[2]), h)) > MAX_SLOPE + 0.5:
                steep += 1
                break
            if h <= 1e-6 and abs(q[2] - p[2]) > 1:
                steep += 1
                break
    return dict(too_short=short_, too_steep=steep, doubling_back=f.folds)


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
            for m in re.finditer(rb'PersistentLevel\.(Build_(?:ConveyorBelt|Pipeline)\w*?_C_\d+)', c['data']):
                other = paths.get('Persistent_Level:PersistentLevel.' + m.group(1).decode())
                if other is not None:
                    joined.add((min(bi, other), max(bi, other)))
    hits = set()
    f.clashes = []           # (point on one belt, point on the other) for each clash
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
                    f.clashes.append(([round(v) for v in p], [round(v) for v in q]))
    return len(hits)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Build a ready-to-place production line blueprint.')
    ap.add_argument('targets', nargs='+', help='item name, then rate per minute (repeatable)')
    ap.add_argument('--use', action='append', default=[], help='recipe to use (e.g. an alternate)')
    ap.add_argument('--name', default=None, help='blueprint name')
    ap.add_argument('--out', default=None, help='.sbp path (default .local/blueprints/<name>/<name>.sbp)')
    ap.add_argument('--pole', choices=['Mk1', 'Mk2', 'Mk3'], default=None,
                    help='power pole tier (default %s; Mk.1 for early saves, one pole per machine)' % POLE_TIER)
    a = ap.parse_args(argv)
    t = a.targets
    targets = [(calc.find_item(t[i]), float(t[i + 1])) for i in range(0, len(t), 2)]
    plan = calc.plan(targets, use=[calc.find_recipe(u) for u in a.use], clock=1.0)
    name = a.name or ' + '.join('%s %s' % (calc.fmt(r), calc.db()['items'][i]['name']) for i, r in targets) + ' Factory'
    f, rep = build_best(plan, name, pole=a.pole)
    out = Path(a.out) if a.out else Path('.local/blueprints') / re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') / (name + '.sbp')
    out.parent.mkdir(parents=True, exist_ok=True)
    f.bp.save(out)
    write_sbpcfg(out.with_suffix('.sbpcfg'), '%s\n\nMachines: %s\n\nRaw inputs: %s\n\nPower: %s.\n\nGenerated by claude-satisfactory-builder.' % (
        name, '; '.join(rep['rows']), '; '.join(rep['raw_inputs']), rep.get('power', 'wire it in game')))
    print(json.dumps(dict(file=str(out), **rep), indent=1))


if __name__ == '__main__':
    main()

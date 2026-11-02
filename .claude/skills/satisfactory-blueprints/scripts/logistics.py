"""Trains, trucks/tractors and drones in a save: tracks and roads, stations, truck stations and drone ports,
the carriers serving them, and what each one imports and exports per minute (trucks and drones measured
where the save has it, trains estimated). Trucks and drones: see roads_and_drones().

  python -I logistics.py "here again too"            # summary per station
  python -I logistics.py "<save>.sav" --json out.json

How it's read (game 1.2):
  tracks     Build_RailroadTrack(_Integrated): mSplineData (drawn), TrackConnection components link them
             (mConnectedComponents) into the rail graph used for route lengths.
  stations   Build_TrainStation; its name is on the FGTrainStationIdentifier that points at it
             (mStation, mStationName). Platforms chain to it through PlatformConnection components
             (mConnectedTo): freight platforms (Build_TrainDockingStation, ...Liquid) and empty ones.
  platforms  load mode unless mIsInLoadMode is stored (the default is load; the save only keeps it when
             false). Load = belts feed it, the train takes the items away (export); unload = the train
             leaves items, belts carry them into the factory (import). Their inventory shows what's there.
  trains     BP_Train: name, FirstVehicle, TimeTable. Vehicles are coupled to each other (references after
             their property list); BP_FreightWagon holds 32 stacks, or 32 x 50 m3 of a fluid.
  timetable  FGRailroadTimeTable mStops: station identifier + docking rules with load/unload item filters.

What a train carries: the items its loading stops have for it (load platforms' contents and the stop's
load filter, or what is in its wagons now), dropped at its unloading stops (unload filters respected).
Its capacity per trip is shared evenly between the items it carries; trips take the route length along
the tracks at TRAIN_SPEED plus DOCK_S at every stop. Both are estimates: say so.
"""
import heapq, json, math, re, struct, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sav import Save
from sbp import Reader, find_prop, short, spline_points
from world import _object_prop
import calc
import production

TRAIN_SPEED = 25.0          # m/s on average (top speed 120 km/h = 33 m/s, less for curves and braking)
DOCK_S = 27.0               # a platform's load or unload time (mTimeToCompleteLoad / ...Unload)
WAGON_SLOTS = 32            # Desc_FreightWagon mInventorySize
TRUCK_SPEED = 14.0          # m/s (~50 km/h on average) for vehicles with no measured dockings yet
TRUCK_DOCK_S = 30.0
PLATFORMS = ('Build_TrainDockingStation_C', 'Build_TrainDockingStationLiquid_C',
             'Build_TrainPlatformEmpty_C', 'Build_TrainPlatformEmpty_02_C')


def _refs(d):
    return [m.decode('latin1') for m in re.findall(rb'(Persistent_Level:PersistentLevel\.[\w.]+)\x00', d)]


def _item(path):
    m = re.search(r'Desc_(\w+?)_C$', path or '')
    return m.group(1) if m else None


def text_prop(d, name):
    """A TextProperty's string (station and train names), or ''."""
    off, t = find_prop(d, name)
    if off is None or t != 'TextProperty':
        return ''
    try:
        r = Reader(d, off)
        r.i32()
        hist = d[r.o]; r.o += 1
        if hist == 255:
            if r.i32():
                return r.string()
            return ''
        if hist == 0:
            r.string(); r.string()
            return r.string()
    except Exception:
        pass
    return ''


def _filter(found):
    """A stop's load/unload filter: [] = no filter (anything), ['None'] = nothing. The game's own filter
    items: Desc_None (nothing), Desc_Wildcard / Desc_AnyUndefined (anything)."""
    f = [m.decode() if isinstance(m, bytes) else m for m in found]
    if any(x in ('Wildcard', 'AnyUndefined') for x in f):
        return []
    real = [x for x in f if x != 'None']
    return real or (['None'] if f else [])


def inventory(d):
    """{item: amount} in an inventory component (fluids in m3)."""
    out, items = Counter(), calc.db()['items']
    for m in re.finditer(rb'/Game/[\w/.\-]+?Desc_(\w+?)_C\x00', d):
        j = d.find(b'NumItems\x00', m.end())
        if j < 0:
            continue
        n = struct.unpack_from('<i', d, j + 9 + 4 + 12 + 9)[0]
        it = m.group(1).decode()
        out[it] += n / (1000 if items.get(it, {}).get('form', 'solid') != 'solid' else 1)
    return out


def rail(sav):
    D = calc.db()
    items = D['items']
    save = Save(sav)
    objs = {o['path']: o for o in save.objects()}
    comps = defaultdict(list)
    for o in objs.values():
        if o['type'] == 0:
            comps[o['outer']].append(o)
    nets = production.networks(save)
    # what each belt/pipe network makes more of than it uses: what its load platforms export when
    # nothing is waiting on them (an idle factory)
    surplus = defaultdict(Counter)
    for m in production.machines(save):
        n = nets.get(m['path'], -1)
        if n >= 0 and not (m['kind'] == 'machine' and not m['recipe']):
            for i, v in production.flows(m):
                if i != '_power':
                    surplus[n][i] += v

    # ---- tracks: shapes, lengths, graph
    tracks, shapes, length = {}, [], {}
    for o in objs.values():
        if o['type'] != 1 or 'Build_RailroadTrack' not in o['cls']:
            continue
        pts = spline_points(o, steps=4)
        if pts:
            length[o['path']] = sum(math.dist(a, b) for a, b in zip(pts, pts[1:])) / 100
            shapes.append([round(v / 100, 1) for p in pts for v in p[:2]])
        else:
            length[o['path']] = 16.0
        tracks[o['path']] = o
    graph = defaultdict(set)
    for t in tracks:
        for c in comps[t]:
            if c['path'].rsplit('.', 1)[-1].startswith('TrackConnection'):
                for ref in _refs(c['data']):
                    other = ref.rsplit('.', 1)[0]
                    if other in tracks and other != t:
                        graph[t].add(other); graph[other].add(t)

    def route_m(a, b):
        """Shortest track distance (m) between two tracks; None if not linked."""
        if a == b:
            return 0.0
        best, todo = {a: 0.0}, [(0.0, a)]
        while todo:
            d, t = heapq.heappop(todo)
            if t == b:
                return d
            if d > best.get(t, 1e18):
                continue
            for n in graph[t]:
                nd = d + length.get(n, 16.0)
                if nd < best.get(n, 1e18):
                    best[n] = nd; heapq.heappush(todo, (nd, n))
        return None

    # ---- stations and their platforms
    names = {}
    for o in objs.values():
        if o['cls'].endswith('FGTrainStationIdentifier'):
            st = _object_prop(o['data'], 'mStation')
            if st:
                names[o['path']] = (st, text_prop(o['data'], 'mStationName'))
    link = defaultdict(set)                     # platform-like actor -> neighbours along the platform chain
    for o in objs.values():
        if o['type'] == 0 and o['outer'] in objs and objs[o['outer']]['cls'].split('.')[-1] in PLATFORMS + ('Build_TrainStation_C',):
            to = _object_prop(o['data'], 'mConnectedTo')
            if to:
                b = to.rsplit('.', 1)[0]
                link[o['outer']].add(b); link[b].add(o['outer'])
    station_of = {}                             # platform -> station (nearest along the chain)
    stations = {}
    for ident, (sp, nm) in names.items():
        so = objs.get(sp)
        if not so:
            continue
        stations[sp] = dict(id=len(stations), path=sp, ident=ident, name=nm or 'Station',
                            x=round(so['pos'][0] / 100, 1), y=round(so['pos'][1] / 100, 1),
                            track=_object_prop(so['data'], 'mRailroadTrack'), platforms=[], trains=[])
    frontier = [(0, sp, sp) for sp in stations]
    while frontier:
        k, at, sp = frontier.pop(0)
        for n in link[at]:
            if n in stations or n in station_of:
                continue
            station_of[n] = sp
            frontier.append((k + 1, n, sp))
    for p, sp in station_of.items():
        o = objs[p]
        cl = o['cls'].split('.')[-1]
        if 'DockingStation' not in cl:
            continue
        fluid = 'Liquid' in cl
        d = o['data']
        off, _ = find_prop(d, 'mIsInLoadMode')
        load = off is None or bool(d[off - 1] & 0x10)
        belts_in = belts_out = 0
        for c in comps[p]:
            part = c['path'].rsplit('.', 1)[-1]
            if ('Input' in part or 'Output' in part) and _object_prop(c['data'], 'mConnectedComponent'):
                if 'Input' in part: belts_in += 1
                else: belts_out += 1
        inv = Counter()
        for c in comps[p]:
            if c['path'].endswith('.inventory'):
                inv += inventory(c['data'])
        stations[sp]['platforms'].append(dict(
            fluid=fluid, load=load, belts_in=belts_in, belts_out=belts_out, network=nets.get(p, -1),
            x=round(o['pos'][0] / 100, 1), y=round(o['pos'][1] / 100, 1),
            items={k: round(v, 1) for k, v in inv.items()}))

    # ---- trains
    vehicles = {p: o for p, o in objs.items() if o['type'] == 1 and ('BP_Locomotive' in o['cls'] or 'BP_FreightWagon' in o['cls'])}
    coupled = defaultdict(set)
    for p, o in vehicles.items():
        for ref in _refs(o['data']):
            if ref in vehicles and ref != p:
                coupled[p].add(ref); coupled[ref].add(p)
    by_ident = {s['ident']: s for s in stations.values()}
    trains = []
    for o in objs.values():
        if not o['cls'].endswith('BP_Train_C'):
            continue
        d = o['data']
        first = _object_prop(d, 'FirstVehicle')
        seen, todo = set(), [first] if first in vehicles else []
        while todo:
            v = todo.pop()
            if v in seen:
                continue
            seen.add(v); todo += list(coupled[v])
        locos = sum('Locomotive' in v for v in seen)
        wagons = [v for v in seen if 'FreightWagon' in v]
        carried = Counter()
        fluid_w = solid_w = empty_w = 0
        for w in wagons:
            inv = Counter()
            for c in comps[w]:
                if c['path'].endswith('StorageInventory'):
                    inv += inventory(c['data'])
            carried += inv
            if not inv:
                empty_w += 1
            elif any(items.get(i, {}).get('form', 'solid') != 'solid' for i in inv):
                fluid_w += 1
            else:
                solid_w += 1
        tt = objs.get(_object_prop(d, 'TimeTable') or '')
        stops = []
        if tt:
            td = tt['data']
            marks = [(m.start(), m.group(1).decode('latin1')) for m in
                     re.finditer(rb'(Persistent_Level:PersistentLevel\.FGTrainStationIdentifier_\d+)\x00', td)]
            for k, (at, ident) in enumerate(marks):
                end = marks[k + 1][0] if k + 1 < len(marks) else len(td)
                seg = td[at:end]
                li, ui = seg.find(b'LoadFilterDescriptors\x00'), seg.find(b'UnloadFilterDescriptors\x00')
                lf = _filter(re.findall(rb'Desc_(\w+?)_C\x00', seg[li:ui]) if li >= 0 <= ui else [])
                uf = _filter(re.findall(rb'Desc_(\w+?)_C\x00', seg[ui:]) if ui >= 0 else [])
                if ident in by_ident:
                    stops.append(dict(station=by_ident[ident]['id'], load_filter=lf, unload_filter=uf))
        trains.append(dict(id=len(trains), name=text_prop(d, 'mTrainName') or 'Train', locos=locos,
                           wagons=len(wagons), fluid_wagons=fluid_w, solid_wagons=solid_w, empty_wagons=empty_w,
                           carrying={k: round(v, 1) for k, v in carried.items()}, stops=stops))

    st_list = sorted(stations.values(), key=lambda s: s['id'])
    for t in trains:
        # route length and trip time
        ids = [s['station'] for s in t['stops']]
        path, ok = 0.0, len(ids) >= 2
        for a, b in zip(ids, ids[1:] + ids[:1]):
            m = route_m(st_list[a]['track'], st_list[b]['track']) if ok else None
            if m is None:
                ok = False; break
            path += m
        t['route_m'] = round(path) if ok else None
        t['trip_s'] = round(path / TRAIN_SPEED + DOCK_S * len(ids)) if ok else None
        for a in set(ids):
            st_list[a]['trains'].append(t['id'])
        # what it loads where, and where it drops it
        loads = defaultdict(set)
        for s in t['stops']:
            st = st_list[s['station']]
            have = set()
            for p in st['platforms']:
                if p['load']:
                    got = set(p['items'])
                    if not got and p['network'] >= 0:      # nothing waiting: what its factory has spare
                        got = {i for i, v in surplus[p['network']].items() if v > 0.01 and i != 'Water'
                               and (items.get(i, {}).get('form', 'solid') != 'solid') == p['fluid']}
                    have |= got
            if s['load_filter'] == ['None']:
                have = set()
            elif s['load_filter']:
                have = (have | set(s['load_filter'])) & set(s['load_filter'])
            for it in have:
                loads[it].add(s['station'])
        for it in t['carrying']:
            if it not in loads:
                loads[it] = set()
        moves = []
        for it, frm in loads.items():
            to = [s['station'] for s in t['stops']
                  if any(not p['load'] and p['fluid'] == (items.get(it, {}).get('form', 'solid') != 'solid')
                         for p in st_list[s['station']]['platforms'])
                  and (not s['unload_filter'] or it in s['unload_filter']) and s['station'] not in frm]
            if not frm and not to:
                continue
            moves.append(dict(item=it, frm=sorted(frm), to=sorted(set(to))))
        # capacity per minute, shared evenly by the solids and by the fluids it carries
        solids = [m for m in moves if items.get(m['item'], {}).get('form', 'solid') == 'solid']
        fluids = [m for m in moves if m not in solids]
        sw = t['solid_wagons'] + (t['empty_wagons'] if not fluids else t['empty_wagons'] / 2 if solids else 0)
        fw = t['fluid_wagons'] + (t['empty_wagons'] if not solids else t['empty_wagons'] / 2 if fluids else 0)
        for group, w in ((solids, sw), (fluids, fw)):
            for m in group:
                stack = items.get(m['item'], {}).get('stack', 100)
                per_trip = w * WAGON_SLOTS * stack / len(group)
                m['per_min'] = round(per_trip * 60 / t['trip_s'], 1) if t['trip_s'] else None
        t['moves'] = moves

    # per station: what arrives and leaves, by item, with the trains doing it
    for st in st_list:
        st['imports'], st['exports'] = defaultdict(lambda: [0.0, []]), defaultdict(lambda: [0.0, []])
    for t in trains:
        for m in t['moves']:
            for a in m['to']:
                e = st_list[a]['imports'][m['item']]; e[0] += m['per_min'] or 0; e[1].append(t['id'])
            for a in m['frm']:
                e = st_list[a]['exports'][m['item']]; e[0] += m['per_min'] or 0; e[1].append(t['id'])
    for st in st_list:
        for k in ('imports', 'exports'):
            st[k] = {i: [round(v, 1), sorted(set(ts))] for i, (v, ts) in st[k].items()}
        del st['path'], st['ident'], st['track']
    item_names = {i: [items.get(i, {}).get('name') or i, items.get(i, {}).get('form', 'solid')]
                  for st in st_list for d in (st['imports'], st['exports']) for i in d}
    for t in trains:
        for m in t['moves']:
            item_names.setdefault(m['item'], [items.get(m['item'], {}).get('name') or m['item'],
                                              items.get(m['item'], {}).get('form', 'solid')])
    road = roads_and_drones(objs, comps, nets, surplus)
    for st in road['truck_stations'] + road['drone_ports']:
        for d in (st['imports'], st['exports']):
            for i in d:
                item_names.setdefault(i, [items.get(i, {}).get('name') or i, items.get(i, {}).get('form', 'solid')])
    return dict(tracks=shapes, stations=st_list, trains=trains, items=item_names, **road,
                assumptions=dict(speed_m_s=TRAIN_SPEED, dock_s=DOCK_S, wagon_slots=WAGON_SLOTS))


def _num(d, name, start=0):
    """(value, offset after it) of the next Float/Int property `name` at or after `start`."""
    i = d.find(name.encode() + b'\x00', start)
    if i < 0:
        return None, -1
    r = Reader(d, i + len(name) + 1)
    t = r.string()
    r.o += 9
    v = struct.unpack_from('<f' if t == 'FloatProperty' else '<i', d, r.o)[0]
    return v, r.o + 4


def _str(d, name):
    off, t = find_prop(d, name)
    if off is None:
        return ''
    try:
        return Reader(d, off).string()
    except Exception:
        return ''


def roads_and_drones(objs, comps, nets, surplus):
    """Trucks, tractors and the Explorer on their roads, and drones between their ports.

    Roads (game 1.2): Build_VehiclePath_* segments (mSplinePoints) between path nodes. A vehicle has no
    stored route: it is the set of truck stations it docks at, which every station records in
    mVehicleTracking (OwnerVehicle, AverageTimeBetweenDocks s, AverageItemsTransferredPerDock): measured
    throughput, items per minute = items per dock / time between docks. Truck stations load or unload like
    train platforms (mIsInLoadMode stored only for unload).
    Drones: Build_DroneStation + FGDroneStationInfo (mBuildingTag name, mPairedStation). The port that owns
    the drone records its latest trips (TripDuration s, OutgoingItemCount home -> partner, IncomingItemCount
    partner -> home). What they carry: the sending port's input inventory, else its factory's spare items."""
    items = calc.db()['items']

    def spare(net, fluid=None):
        return {i for i, v in surplus.get(net, {}).items() if v > 0.01 and i != 'Water'
                and (fluid is None or (items.get(i, {}).get('form', 'solid') != 'solid') == fluid)}

    def belts(path, kinds):
        return sum(1 for c in comps[path] if c['path'].rsplit('.', 1)[-1].startswith(kinds)
                   and _object_prop(c['data'], 'mConnectedComponent'))

    def inv(path, suffix):
        out = Counter()
        for c in comps[path]:
            if c['path'].endswith(suffix):
                out += inventory(c['data'])
        return out

    # roads
    roads = []
    for o in objs.values():
        if o['type'] == 1 and '/Build_VehiclePath_' in o['cls']:
            k = o['data'].find(b'mSplinePoints\x00')
            if k >= 0:
                pts = spline_points(dict(o, data=b'mSplineData\x00' + o['data'][k + 14:]), steps=3)
                if pts:
                    roads.append([round(v / 100, 1) for p in pts for v in p[:2]])

    # vehicles and truck stations
    vtype = {p: o['cls'].split('.')[-1].replace('BP_', '').replace('_C', '')
             for p, o in objs.items() if o['type'] == 1 and re.search(r'BP_(Truck|Tractor|Explorer|Golfcart\w*)_C$', o['cls'])}
    vid, vslots = {}, {}
    stations, docks = [], defaultdict(list)          # vehicle -> [(station index, items/min)]
    for p, o in objs.items():
        if not o['cls'].endswith(('Build_TruckStation_C', 'Build_FluidTruckStation_C')):
            continue
        d = o['data']
        off, _ = find_prop(d, 'mIsInLoadMode')
        load = off is None or bool(d[off - 1] & 0x10)
        ident = objs.get(_object_prop(d, 'mStationIdentifier') or '')
        name = (text_prop(ident['data'], 'mStationName') if ident else '') or 'Truck Station'
        k = len(stations)
        st = dict(id=k, kind='truck', name=name, x=round(o['pos'][0] / 100, 1), y=round(o['pos'][1] / 100, 1),
                  load=load, network=nets.get(p, -1), belts_in=belts(p, 'Input'), belts_out=belts(p, 'Output'),
                  items={i: round(v, 1) for i, v in inv(p, '.inventory').items()}, vehicles=[], imports={}, exports={})
        at = 0
        for m in re.finditer(rb'OwnerVehicle\x00', d):
            v = _object_prop(d[m.start() - 4:], 'OwnerVehicle')
            gap, at = _num(d, 'AverageTimeBetweenDocks', m.end())
            per_dock, at = _num(d, 'AverageItemsTransferredPerDock', m.end())
            slots, _ = _num(d, 'VehicleInventorySizeLinear', m.end())
            if v in vtype:
                vid.setdefault(v, len(vid))
                rate = per_dock * 60 / gap if gap and gap > 1 and per_dock else 0.0
                st['vehicles'].append(vid[v])
                docks[v].append((k, rate))
                vslots[v] = slots or vslots.get(v, 0)
        stations.append(st)
    vehicles = [None] * len(vid)
    for v, i in vid.items():
        vehicles[i] = dict(id=i, kind=vtype[v], stops=[k for k, _ in docks[v]], slots=vslots.get(v, 0),
                           per_min={str(k): round(r, 1) for k, r in docks[v]}, measured=any(r for _, r in docks[v]))
    # what each vehicle carries: what sits at its unloading stations (it arrived), else what its loading
    # stations hold or their factory has spare; its measured rate at each station is shared between them
    for v in vehicles:
        frm = [stations[k] for k in v['stops'] if stations[k]['load']]
        to = [stations[k] for k in v['stops'] if not stations[k]['load']]
        carried = set().union(*[set(s['items']) for s in to]) or \
            set().union(*[set(s['items']) or spare(s['network']) for s in frm])
        v['carrying'] = sorted(carried)
        if not v['measured'] and carried and len(v['stops']) >= 2:
            # never docked yet: a full load per round trip, straight distance x 1.3 at TRUCK_SPEED, DOCK_S per stop
            pts = [stations[k] for k in v['stops']]
            dist = sum(math.dist((a['x'], a['y']), (b['x'], b['y'])) for a, b in zip(pts, pts[1:] + pts[:1])) * 1.3
            v['trip_s'] = round(dist / TRUCK_SPEED + TRUCK_DOCK_S * len(pts))
            stack = sum(items.get(i, {}).get('stack', 100) for i in carried) / len(carried)
            rate = (v['slots'] or 48) * stack * 60 / v['trip_s']
            v['per_min'] = {str(k): round(rate, 1) for k in v['stops']}
        for s in frm + to:
            rate = v['per_min'].get(str(s['id']), 0)
            d = s['exports'] if s['load'] else s['imports']
            for i in carried:
                e = d.setdefault(i, [0.0, []])
                e[0] = round(e[0] + rate / max(1, len(carried)), 1)
                e[1].append(v['id'])

    # drone ports
    infos = {p: o for p, o in objs.items() if o['cls'].endswith('FGDroneStationInfo')}
    ports, by_station = [], {}
    for p, o in objs.items():
        if o['cls'].endswith('Build_DroneStation_C'):
            info = infos.get(_object_prop(o['data'], 'mInfo') or '')
            by_station[p] = len(ports)
            ports.append(dict(id=len(ports), kind='drone', name=(_str(info['data'], 'mBuildingTag') if info else '') or 'Drone Port',
                              x=round(o['pos'][0] / 100, 1), y=round(o['pos'][1] / 100, 1), network=nets.get(p, -1),
                              has_drone=bool(_object_prop(o['data'], 'mStationDrone')),
                              items={i: round(v, 1) for i, v in inv(p, 'InputInventory').items()},
                              received={i: round(v, 1) for i, v in inv(p, 'OutputInventory').items()},
                              partner=None, trip_s=None, out_per_min=None, in_per_min=None, imports={}, exports={},
                              _info=info))
    station_of_info = {_object_prop(o['data'], 'mStation'): q for q, o in infos.items()}
    info_station = {q: s for s, q in station_of_info.items()}
    for port in ports:
        info = port.pop('_info')
        if not info:
            continue
        d = info['data']
        partner = info_station.get(_object_prop(d, 'mPairedStation') or '')
        if partner in by_station:
            port['partner'] = by_station[partner]
        trips, at = [], 0
        while True:
            dur, at = _num(d, 'TripDuration', at)
            if dur is None:
                break
            inc, _ = _num(d, 'IncomingItemCount', at)
            out, _ = _num(d, 'OutgoingItemCount', at)
            if dur and dur > 1:
                trips.append((dur, inc or 0, out or 0))
        if trips:
            dur = sum(t[0] for t in trips) / len(trips)
            port['trip_s'] = round(dur)
            port['in_per_min'] = round(sum(t[1] for t in trips) / len(trips) * 60 / dur, 1)
            port['out_per_min'] = round(sum(t[2] for t in trips) / len(trips) * 60 / dur, 1)
    for port in ports:
        if port['partner'] is None or not port['has_drone']:
            continue
        other = ports[port['partner']]
        for frm, to, rate in ((port, other, port['out_per_min']), (other, port, port['in_per_min'])):
            if rate == 0:
                continue                                # measured: nothing goes this way
            what = set(to['received']) or set(frm['items']) or spare(frm['network'])
            for i in what:
                share = (rate or 0) / max(1, len(what))
                for d in (frm['exports'], to['imports']):
                    e = d.setdefault(i, [0.0, []])
                    e[0] = round(e[0] + share, 1)
                    e[1].append(port['id'])
    for port in ports:
        del port['received']
    return dict(roads=roads, truck_stations=stations, vehicles=vehicles, drone_ports=ports)


def main(argv):
    if not argv:
        print(__doc__); return 1
    sys.stdout.reconfigure(encoding='utf-8')
    r = rail(production.find_save(argv[0]))
    if '--json' in argv:
        Path(argv[argv.index('--json') + 1]).write_text(json.dumps(r), encoding='utf-8')
    names = r['items']
    print('%d track pieces, %d stations, %d trains' % (len(r['tracks']), len(r['stations']), len(r['trains'])))
    for st in r['stations']:
        pl = Counter(('fluid ' if p['fluid'] else '') + ('load' if p['load'] else 'unload') for p in st['platforms'])
        print('\n%s  (%d trains; platforms %s)' % (st['name'], len(set(st['trains'])), dict(pl)))
        for k, arrow in (('imports', 'in '), ('exports', 'out')):
            for i, (v, ts) in sorted(st[k].items(), key=lambda kv: -kv[1][0]):
                print('   %s %-28s ~%s/min  (%d trains)' % (arrow, names[i][0], production.fmt(v), len(ts)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

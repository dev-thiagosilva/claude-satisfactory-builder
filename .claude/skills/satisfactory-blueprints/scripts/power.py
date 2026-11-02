"""The power grid in a save: which buildings are wired to a generator, and what's left unconnected.

  python -I power.py "here again too"

How it's read (game 1.2):
  circuits  FGPowerCircuit (under CircuitSubsystem): mComponents = every power connection on it. The game
            builds these itself, so they include links it makes on its own (train stations pass power along
            the rails). A power switch sits in the two circuits it joins; when it's on (mIsSwitchOn) they
            count as one grid here.
  wires     Build_PowerLine: its two ends are the references after its property list (the connections).
  poles     Build_PowerPole*, wall outlets, towers: how many wires each holds (POLE_LINKS = the most it can).

Each producing or powered building (production.machines) is then on:
  main     the grid with the most generator power (the one to connect everything to)
  other    a grid with generators of its own
  island   wired to other buildings, but nothing on that circuit generates power
  loose    no wire at all
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sav import Save
from sbp import find_prop, short
import production

POLE_LINKS = {'PowerPoleMk1': 4, 'PowerPoleMk2': 7, 'PowerPoleMk3': 10, 'PowerPoleWall': 4, 'PowerPoleWall_Mk2': 7,
              'PowerPoleWall_Mk3': 10, 'PowerPoleWallDouble': 4, 'PowerPoleWallDouble_Mk2': 7,
              'PowerPoleWallDouble_Mk3': 10, 'PowerTowerPlatform': 2, 'PowerTower': 2}
WIRE_MAX_M = 100.0          # longest power line the game lets you build


def _refs(d):
    return [m.decode('latin1').strip() for m in re.findall(rb'(Persistent_Level:PersistentLevel\.[^\x00]+)\x00', d)]


def grid(save):
    """{group_of: {actor path: group id}, groups: [...], main: id, lines: [[x1, y1, x2, y2]], poles: [...]}."""
    objs = {o['path']: o for o in save.objects()}
    # circuits -> actors on them
    circuits = {}
    for o in objs.values():
        if o['cls'].endswith('FGPowerCircuit'):
            circuits[o['path']] = {r.rsplit('.', 1)[0] for r in _refs(o['data'])}
    parent = {c: c for c in circuits}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    of_actor = defaultdict(set)
    for c, acts in circuits.items():
        for a in acts:
            of_actor[a].add(c)
    # a switch that's on joins the circuits on its two sides
    for a, cs in of_actor.items():
        o = objs.get(a)
        if o and o['cls'].endswith('Build_PowerSwitch_C') and len(cs) > 1:
            off, _ = find_prop(o['data'], 'mIsSwitchOn')
            if off is not None and o['data'][off - 1] & 0x10:
                cs = list(cs)
                for c in cs[1:]:
                    parent[find(c)] = find(cs[0])
    ids, group_of = {}, {}
    for a, cs in of_actor.items():
        g = find(next(iter(cs)))
        group_of[a] = ids.setdefault(g, len(ids))

    # what each group generates and holds
    groups = [dict(id=i, gen_mw=0.0, generators=0, batteries=0, buildings=0, need_mw=0.0) for i in range(len(ids))]
    for m in production.machines(save):
        g = group_of.get(m['path'])
        if g is None:
            continue
        mw = sum(v for i, v in production.flows(m) if i == '_power')
        if m['kind'] == 'generator':
            groups[g]['gen_mw'] += mw; groups[g]['generators'] += 1
        else:
            groups[g]['buildings'] += 1; groups[g]['need_mw'] -= mw
    for a, g in group_of.items():
        if objs.get(a) and objs[a]['cls'].endswith('Build_PowerStorageMk1_C'):
            groups[g]['batteries'] += 1
    for g in groups:
        g['gen_mw'] = round(g['gen_mw'], 1); g['need_mw'] = round(g['need_mw'], 1)
    main = max(groups, key=lambda g: g['gen_mw'])['id'] if groups else -1

    # wires (drawn) and poles with their free slots
    pos = lambda a: objs[a]['pos'] if a in objs and objs[a]['type'] == 1 else None
    lines, used = [], Counter()
    for o in objs.values():
        if o['type'] == 1 and o['cls'].endswith('Build_PowerLine_C'):
            ends = [r.rsplit('.', 1)[0] for r in _refs(o['data'][o['data'].rfind(b'\x05\x00\x00\x00None\x00'):])][-2:]
            if len(ends) == 2 and pos(ends[0]) and pos(ends[1]):
                a, b = pos(ends[0]), pos(ends[1])
                lines.append([round(a[0] / 100, 1), round(a[1] / 100, 1), round(b[0] / 100, 1), round(b[1] / 100, 1)])
                used[ends[0]] += 1; used[ends[1]] += 1
    poles = []
    for p, o in objs.items():
        k = short(o['cls'])
        if o['type'] == 1 and k in POLE_LINKS:
            poles.append([round(o['pos'][0] / 100, 1), round(o['pos'][1] / 100, 1), group_of.get(p, -1),
                          max(0, POLE_LINKS[k] - used[p])])
    return dict(group_of=group_of, groups=groups, main=main, lines=lines, poles=poles,
                assumptions=dict(wire_max_m=WIRE_MAX_M))


def main(argv):
    if not argv:
        print(__doc__); return 1
    sys.stdout.reconfigure(encoding='utf-8')
    save = Save(production.find_save(argv[0]))
    g = grid(save)
    status = Counter()
    for m in production.machines(save):
        k = g['group_of'].get(m['path'])
        grp = g['groups'][k] if k is not None else None
        s = 'loose' if grp is None else 'main' if k == g['main'] else 'other' if grp['gen_mw'] > 0 else 'island'
        status[(m['kind'], s)] += 1
    print('%d grids; main grid: %s' % (len(g['groups']), g['groups'][g['main']] if g['groups'] else None))
    for gr in sorted(g['groups'], key=lambda x: -x['gen_mw'])[:6]:
        print('  grid %d: %s MW from %d generators, %d buildings need %s MW, %d batteries' % (
            gr['id'], production.fmt(gr['gen_mw']), gr['generators'], gr['buildings'], production.fmt(gr['need_mw']), gr['batteries']))
    for k, n in sorted(status.items()):
        print('  %-10s %-7s %d' % (k[0], k[1], n))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

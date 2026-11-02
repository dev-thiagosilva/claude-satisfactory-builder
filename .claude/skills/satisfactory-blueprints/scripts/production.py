"""What a save produces and uses per minute, item by item, and what's missing.

Reads every machine, extractor and generator in a game-1.2 save: its recipe (or resource node, or
fuel), clock speed, Somersloop boost and the productivity the game measured, then adds up the
game's own recipe rates (library/production.json). Every other building that draws power (pumps,
stations, sinks, lights...: `consumers`) counts toward power. Rates are per minute; fluids in m³/min.

  python -I production.py "here again too"              # a save by name (or a path to a .sav)
  python -I production.py "here again too" --json out.json

Two views of every item:
  now   what the machines did over the game's last productivity measurement (rate x productivity)
  full  what they would do running non-stop at their clock: the demand the factory was built for
Missing = items whose full-speed use is above their full-speed production (the factory can't run
at 100% without more of them), with the extra raw resources that would make up the gap, using the
player's own recipes where they have one. Resource node purity comes from the game files
(.local/terrain/data/nodes.json, `terrain.exe nodes`); without it every node counts as normal.

Not counted: items moved by trains, trucks and drones (they don't change the totals), stock in
storage, what the AWESOME Sinks burn (they take any surplus), and hand crafting.

Library use:
  from production import report, format_report
  r = report('<save.sav>')
"""
import json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sav import Save
from sbp import short, find_prop, get_float
from world import save_files, _object_prop
import calc

NODES = HERE.parents[3] / '.local' / 'terrain' / 'data' / 'nodes.json'
PURITY = {'impure': 0.5, 'normal': 1.0, 'pure': 2.0}
SLOW = 0.9                                     # productivity below this counts as held up


def _item(desc_path):
    """'/Game/.../Desc_OreIron.Desc_OreIron_C' -> 'OreIron'."""
    m = re.search(r'Desc_(\w+?)_C$', desc_path or '')
    return m.group(1) if m else None


def _recipe(path):
    m = re.search(r'Recipe_(\w+?)_C$', path or '')
    return m.group(1) if m else None


def _f(o, name, default):
    v = get_float(o, name)
    return default if v is None else v


def find_save(name_or_path):
    p = Path(name_or_path)
    if p.suffix == '.sav' and p.exists():
        return p
    hits = [s['path'] for s in save_files() if s['name'].lower() == str(name_or_path).lower()]
    if not hits:
        raise FileNotFoundError('no save called %r' % name_or_path)
    return Path(hits[0])


def rules(save):
    """Advanced Game Settings switched on in the save (BP_GameState: mCheatNoPower, mCheatNoFuel,
    mCheatNoCost). A 1.2 bool tag stores its value in the flags byte after the type, child count and
    size: 0x10 = true."""
    gs = next((o for o in save.objects() if o['cls'].endswith('BP_GameState_C')), None)
    on = []
    for name in ('mCheatNoPower', 'mCheatNoFuel', 'mCheatNoCost'):
        i = gs['data'].find(name.encode() + b'\x00') if gs else -1
        if i >= 0 and gs['data'][i + len(name) + 1 + 4 + len('BoolProperty') + 1 + 8] & 0x10:
            on.append(name[6:])
    return on


def machines(save):
    """One dict per producing building: kind, recipe or resource, clock, boost, productivity."""
    D = calc.db()
    nodes = json.loads(NODES.read_text()) if NODES.exists() else {}
    for o in save.objects():
        if o['type'] != 1 or '/Build_' not in o['cls']:
            continue
        t = short(o['cls'])
        d = o['data']
        clock = _f(o, 'mCurrentPotential', 1.0)
        dur = _f(o, 'mLastProductivityMeasurementDuration', 0.0)
        prod = _f(o, 'mLastProductivityMeasurementProduceDuration', 0.0) / dur if dur > 0 else None
        m = dict(type=t, clock=clock, productivity=prod, pos=o['pos'], path=o['path'])
        if t in D['machines']:
            m.update(kind='machine', recipe=_recipe(_object_prop(d, 'mCurrentRecipe')),
                     boost=_f(o, 'mCurrentProductionBoost', 1.0))
        elif t in D['extractors']:
            node = (_object_prop(d, 'mExtractableResource') or '').split('.')[-1]
            info = nodes.get(node)
            if t == 'WaterPump':
                res, purity = 'Water', 'normal'
            elif info:
                res, purity = _item(info[0]) or info[0].replace('Desc_', '').replace('_C', ''), info[1]
            else:
                res, purity = None, 'normal'
            m.update(kind='extractor', node=node, resource=res, purity=purity, known=bool(info) or t == 'WaterPump')
        elif t in D.get('generators', {}):
            m.update(kind='generator', fuel=_item(_object_prop(d, 'mCurrentFuelClass')))
            if t == 'GeneratorGeoThermal':
                node = (_object_prop(d, 'mExtractableResource') or '').split('.')[-1]
                m['purity'] = (nodes.get(node) or [None, 'normal'])[1]
        elif t in D.get('consumers', {}):
            m.update(kind='consumer')                # pumps, stations, sinks, lights...: power only
        else:
            continue
        yield m


def flows(m):
    """[(item, per minute at full speed)]: + made, - used. Power in MW as ('_power', MW)."""
    D = calc.db()
    out = []
    if m['kind'] == 'machine':
        r = D['recipes'].get(m['recipe'] or '')
        if not r:
            return out
        k = 60.0 / r['duration'] * m['clock']
        out += [(i, a * k * m['boost']) for i, a in r['outputs']]
        out += [(i, -a * k) for i, a in r['inputs']]
        mach = D['machines'][m['type']]
        base = (r['power_const'] + r['power_factor'] / 2) if mach['variable'] else mach['power']
        out.append(('_power', -base * m['clock'] ** mach['exponent'] * m['boost'] ** 2))
    elif m['kind'] == 'extractor':
        e = D['extractors'][m['type']]
        mult = 1.0 if m['type'] == 'WaterPump' else PURITY[m['purity']]
        if m['resource']:
            out.append((m['resource'], e['rate'] * mult * m['clock']))
        out.append(('_power', -e['power'] * m['clock'] ** 1.321929))
    elif m['kind'] == 'consumer':
        c = D['consumers'][m['type']]
        out.append(('_power', -c['power'] * m['clock'] ** c['exponent']))
    else:
        g = D['generators'][m['type']]
        mw = g['power'] * m['clock'] * (PURITY[m.get('purity', 'normal')] if m['type'] == 'GeneratorGeoThermal' else 1)
        out.append(('_power', mw))
        fuel = m['fuel'] or (g['fuels'][0][0] if g['fuels'] else None)
        if fuel and D['items'].get(fuel, {}).get('energy'):
            burn = mw * 60 / D['items'][fuel]['energy']
            out.append((fuel, -burn))
            byp = next((b for f, b, n in g['fuels'] if f == fuel and b), None)
            if byp:
                out.append((byp, burn * next(n for f, b, n in g['fuels'] if f == fuel)))
        if g['water_ratio']:
            out.append(('Water', -mw * g['water_ratio'] * 60 / 1000))
    return out


def networks(save):
    """{actor path: network id}: buildings joined by belts, lifts, pipes, pumps, splitters and mergers
    (every connector's mConnectedComponent, both ends). Hypertubes link places, not factories: skipped."""
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for o in save.objects():
        if o['type'] != 0 or b'mConnectedComponent\x00' not in o['data'] or 'PipeHyper' in o['outer']:
            continue
        to = _object_prop(o['data'], 'mConnectedComponent')
        if to and 'PipeHyper' not in to:
            a, b = find(o['outer']), find(to.rsplit('.', 1)[0])
            if a != b:
                parent[a] = b
    ids = {}
    return {a: ids.setdefault(find(a), len(ids)) for a in list(parent)}


def sites(sav):
    """Every producing building for the factory map: position (m), what it is, its recipe, the
    productivity the game measured, its belt network, and its full-speed flows. Items are indexes
    into `items` ([name, form, raw, sink points]) to keep the list small."""
    D = calc.db()
    save = Save(sav)
    net = networks(save)
    names, index = [], {}

    def ix(i):
        if i not in index:
            index[i] = len(names)
            it = D['items'].get(i, {})
            names.append([it.get('name') or i, it.get('form', 'solid'), bool(it.get('raw')), it.get('points', 0)])
        return index[i]
    out = []
    for m in machines(save):
        if m['kind'] == 'machine' and not m['recipe']:
            label = 'no recipe'
        elif m['kind'] == 'machine':
            label = D['recipes'].get(m['recipe'], {}).get('name', m['recipe'])
        elif m['kind'] == 'extractor':
            label = (D['items'].get(m['resource'] or '', {}).get('name') or '?') + \
                    ('' if m['type'] == 'WaterPump' else ' (%s)' % m['purity'])
        elif m['kind'] == 'consumer':
            label = D['consumers'][m['type']]['name']
        else:
            label = D['items'].get(m['fuel'] or '', {}).get('name') or 'fuel'
        fl = [] if label == 'no recipe' else flows(m)
        out.append([round(m['pos'][0] / 100, 1), round(m['pos'][1] / 100, 1), m['kind'][0], m['type'], label,
                    None if m['productivity'] is None else round(m['productivity'], 3), net.get(m['path'], -1),
                    [[ix(i), round(v, 3)] for i, v in fl if i != '_power'],
                    round(sum(v for i, v in fl if i == '_power'), 1)])
    return dict(fields=['x', 'y', 'kind', 'type', 'label', 'productivity', 'network', 'flows', 'power'],
                machines=out, items=names, rules=rules(save))


def close_gaps(net, prefer):
    """Raw resources still needed to cover every shortfall in `net` (item -> full-speed net per minute),
    after using the factory's own surpluses: a short item is taken from surplus first, the rest is made
    with the player's most used recipe for it (or the default one), whose inputs are short in turn and
    whose byproducts join the surplus. Returns ({raw: per minute}, {item no recipe makes: per minute})."""
    D = calc.db()
    rs, items = D['recipes'], D['items']
    pool = {i: v for i, v in net.items() if v > 0}
    todo = [(i, -v) for i, v in net.items() if v < -1e-6]
    raw, unmade = defaultdict(float), defaultdict(float)
    for _ in range(200000):
        if not todo:
            break
        i, need = todo.pop()
        take = min(pool.get(i, 0), need)
        pool[i] = pool.get(i, 0) - take
        need -= take
        if need < 1e-6:
            continue
        k = prefer.get(i) if prefer.get(i) in rs else calc.default_recipe(i)
        if items.get(i, {}).get('raw') or not k:
            (raw if items.get(i, {}).get('raw') else unmade)[i] += need
            continue
        runs = need / calc.per_minute(k, i)
        for j, a in rs[k]['outputs']:
            if j != i:
                pool[j] = pool.get(j, 0) + runs * a * 60 / rs[k]['duration']
        todo += [(j, runs * a * 60 / rs[k]['duration']) for j, a in rs[k]['inputs']]
    return raw, unmade


def report(sav):
    D = calc.db()
    items = D['items']
    save = Save(sav)
    ms = list(machines(save))
    made_full, used_full, made_now, used_now = (defaultdict(float) for _ in range(4))
    power = dict(generated_now=0.0, generators_full=0.0, machines_full=0.0)
    power_by = defaultdict(float)                  # MW at full speed: making, extracting, then each other type
    users = defaultdict(list)                      # item -> [(recipe or kind, productivity)] of its consumers
    counts, idle, unknown_nodes, running = Counter(), Counter(), Counter(), Counter()
    recipe_use = defaultdict(Counter)              # item -> recipes making it, by machine count
    for m in ms:
        counts[m['type']] += m['kind'] != 'consumer'
        if m['kind'] == 'machine' and not m['recipe']:
            idle[m['type']] += 1
            continue
        if m['kind'] == 'extractor' and not m['known']:
            unknown_nodes[m['type']] += 1
        p = m['productivity'] or 0.0
        if m['kind'] != 'consumer':
            running[m['kind']] += p > 0
        for i, v in flows(m):
            if i == '_power':
                if v > 0:
                    power['generators_full'] += v; power['generated_now'] += v * p
                else:
                    power['machines_full'] -= v
                    power_by[{'machine': 'Making items', 'extractor': 'Mining and pumping'}.get(
                        m['kind']) or D['consumers'][m['type']]['name']] -= v
                continue
            (made_full if v > 0 else used_full)[i] += abs(v)
            (made_now if v > 0 else used_now)[i] += abs(v) * p
            if v < 0:
                users[i].append((m.get('recipe') or m['type'], p))
            elif m['kind'] == 'machine':
                recipe_use[i][m['recipe']] += 1

    def name(i):
        return items.get(i, {}).get('name') or i

    table = []
    for i in sorted(set(made_full) | set(used_full), key=name):
        table.append(dict(item=i, name=name(i), form=items.get(i, {}).get('form', 'solid'),
                          raw=items.get(i, {}).get('raw', False),
                          made_now=round(made_now[i], 3), used_now=round(used_now[i], 3),
                          net_now=round(made_now[i] - used_now[i], 3),
                          made_full=round(made_full[i], 3), used_full=round(used_full[i], 3),
                          net_full=round(made_full[i] - used_full[i], 3)))

    # missing: full-speed shortfalls and the machines waiting on them
    missing = []
    for t in sorted(table, key=lambda t: t['net_full']):
        short_by = -t['net_full']
        if short_by <= 1e-3 or t['used_full'] <= 0:
            continue
        slow = Counter(r for r, p in users[t['item']] if p < SLOW)
        missing.append(dict(item=t['item'], name=t['name'], form=t['form'], short_by=round(short_by, 3),
                            made_full=t['made_full'], used_full=t['used_full'],
                            held_up=[[D['recipes'].get(r, {}).get('name', r), n] for r, n in slow.most_common(5)]))
    prefer = {i: rc.most_common(1)[0][0] for i, rc in recipe_use.items() if rc}
    raw_extra, unmade = close_gaps({t['item']: t['net_full'] for t in table}, prefer)

    # unused nodes of each missing raw resource, and what they'd give at the most one extractor can do
    nodes = json.loads(NODES.read_text()) if NODES.exists() else {}
    used = {m.get('node') for m in ms if m['kind'] == 'extractor'}
    free = {}
    for i in raw_extra:
        best = [(n, pur) for n, (res, pur, *_) in nodes.items()
                if _item(res) == i and n not in used and n.startswith('BP_ResourceNode') and 'Geyser' not in n]
        ex = D['extractors']['MinerMk3' if items[i]['form'] == 'solid' else 'OilPump']
        free[i] = dict(nodes=dict(Counter(p for _, p in best)), extractor=ex['name'],
                       max_rate=round(sum(ex['rate'] * 2.5 * PURITY[p] for _, p in best), 1))

    held, per_recipe = Counter(), Counter()
    for m in ms:
        if m['kind'] == 'machine' and m['recipe']:
            per_recipe[m['recipe']] += 1
            held[m['recipe']] += (m['productivity'] or 0) < SLOW
    total = sum(1 for m in ms if m['kind'] != 'consumer') - sum(idle.values())
    power['by'] = sorted(([k, round(v, 1), sum(1 for m in ms if m['kind'] == 'consumer' and
                                                  D['consumers'][m['type']]['name'] == k)]
                          for k, v in power_by.items()), key=lambda r: -r[1])
    return dict(
        save=str(sav), rules=rules(save), machines={t: n for t, n in counts.most_common() if n},
        idle_no_recipe=dict(idle),
        running=dict(any=sum(running.values()), of=total, **running),
        unknown_nodes=dict(unknown_nodes), nodes_file=NODES.exists(),
        power={k: round(v, 1) if isinstance(v, float) else v for k, v in power.items()},
        items=table, missing=missing,
        raw_extra=[[i, name(i), round(v, 2), items.get(i, {}).get('form', 'solid')]
                   for i, v in sorted(raw_extra.items(), key=lambda kv: -kv[1]) if v > .01],
        unmade=[[i, name(i), round(v, 2)] for i, v in unmade.items() if v > .01], free_nodes=free,
        held_up=[[D['recipes'].get(r, {}).get('name', r), n, per_recipe[r]] for r, n in held.most_common(15) if n])


def fmt(v):
    return '{:,.1f}'.format(v).rstrip('0').rstrip('.') if abs(v) < 1e6 else '{:,.0f}'.format(v)


def format_report(r):
    unit = lambda f: ' m³' if f != 'solid' else ''
    run, pw = r['running'], r['power']
    L = ['Save: %s' % Path(r['save']).stem,
         'Machines: ' + ', '.join('%d %s' % (n, t) for t, n in list(r['machines'].items())[:12]) + ' ...',
         'Running: %d of %d made something during the game\'s last measurement (%d machines, %d extractors, '
         '%d generators)' % (run['any'], run['of'], run.get('machine', 0), run.get('extractor', 0), run.get('generator', 0)),
         'Power: generators %s MW now, %s MW at full speed; everything that uses power needs %s MW at full speed%s' % (
             fmt(pw['generated_now']), fmt(pw['generators_full']), fmt(pw['machines_full']),
             ' (SHORT by %s MW)' % fmt(pw['machines_full'] - pw['generators_full'])
             if pw['machines_full'] > pw['generators_full'] and 'NoPower' not in r['rules'] else ''), '']
    if r['rules']:
        L[-1:-1] = ['Game rules on: %s%s' % (', '.join(r['rules']), ' (machines need no power: the power lines '
                                             'are for reference only)' if 'NoPower' in r['rules'] else '')]
    L[-1:-1] = ['  power use at full speed: ' + ', '.join(
        '%s %s MW%s' % (k, fmt(v), ' (%d)' % n if n else '') for k, v, n in pw['by'])]
    if r['idle_no_recipe']:
        L += ['No recipe set: ' + ', '.join('%d %s' % (n, t) for t, n in r['idle_no_recipe'].items()), '']
    if not r['nodes_file']:
        L += ['(node purity unknown: every miner counted on a normal node)', '']
    elif r['unknown_nodes']:
        L += ['(node not found for: %s; counted as normal)' % r['unknown_nodes'], '']
    L.append('%-34s %12s %12s %12s   %12s %12s' % ('Item (per minute)', 'made now', 'used now', 'net now', 'made full', 'net full'))
    for t in sorted(r['items'], key=lambda t: (not t['raw'], -t['made_full'])):
        if t['made_full'] < .01 and t['used_full'] < .01:
            continue
        L.append('%-34s %12s %12s %12s   %12s %12s' % ((t['name'] + unit(t['form']))[:34], fmt(t['made_now']),
                                                       fmt(t['used_now']), fmt(t['net_now']), fmt(t['made_full']),
                                                       fmt(t['net_full'])))
    L += ['', 'Missing (full-speed use above full-speed production):']
    for m in r['missing']:
        L.append('  %-32s short %s/min (makes %s, needs %s)%s' % (
            m['name'], fmt(m['short_by']), fmt(m['made_full']), fmt(m['used_full']),
            ('; waiting: ' + ', '.join('%d on %s' % (n, k) for k, n in m['held_up'])) if m['held_up'] else ''))
    L += ['', 'Raw resources still missing to close every gap (after your surpluses; your recipes):']
    for i, n, v, f in r['raw_extra']:
        fr = r['free_nodes'].get(i)
        L.append('  %-32s %s/min%s' % (n + unit(f), fmt(v), '' if not fr or i == 'Water' else
                 '   unused nodes: %s, up to %s/min with %s at 250%%' % (
                     ', '.join('%d %s' % (c, p) for p, c in sorted(fr['nodes'].items())) or 'none',
                     fmt(fr['max_rate']), fr['extractor'])))
    if not r['raw_extra']:
        L.append('  none')
    if r['unmade']:
        L += ['  no machine makes: ' + ', '.join('%s %s/min' % (n, fmt(v)) for _, n, v in r['unmade'])]
    L += ['', 'Machines held up (productivity under %d%%), by recipe:' % (SLOW * 100)]
    L += ['  %-40s %d of %d' % (k, n, total) for k, n, total in r['held_up']]
    return '\n'.join(L)


def main(argv):
    if not argv:
        print(__doc__); return 1
    sys.stdout.reconfigure(encoding='utf-8')
    r = report(find_save(argv[0]))
    if '--json' in argv:
        Path(argv[argv.index('--json') + 1]).write_text(json.dumps(r, indent=1), encoding='utf-8')
    print(format_report(r))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

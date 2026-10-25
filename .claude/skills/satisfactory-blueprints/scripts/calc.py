"""Production calculator: how many machines, resources and power to make items at a given rate.

Uses the game's own recipe data (library/production.json, from build_assets.py). Rates are per
minute; fluids are in m³/min.

  python -I calc.py "Reinforced Iron Plate" 10
  python -I calc.py "Heavy Modular Frame" 5 "Computer" 2.5 --use "Stitched Iron Plate" --clock 250
  python -I calc.py "Heavy Modular Frame" --total 500 --minutes 60 --miner Mk3 --purity pure
  python -I calc.py --alternates "Reinforced Iron Plate"      # list its recipes
  python -I calc.py ... --json                                 # machine-readable result

Library use:
  from calc import plan, find_item, find_recipe, format_plan
  result = plan([('IronPlateReinforced', 10)], use=['Alternate_ReinforcedIronPlate_2'])
"""
import argparse, json, math, sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'library' / 'production.json'
_DB = None
EPS = 1e-9
PURITY = {'impure': 0.5, 'normal': 1.0, 'pure': 2.0}


def db():
    global _DB
    if _DB is None:
        _DB = json.loads(DATA.read_text(encoding='utf-8'))
    return _DB


# ---------- lookups ----------
def _norm(s):
    return ''.join(ch for ch in s.lower() if ch.isalnum())


def find_item(query):
    """Item id from an id or in-game name ('Reinforced Iron Plate', 'IronPlateReinforced')."""
    items = db()['items']
    if query in items:
        return query
    q = _norm(query)
    exact = [k for k, v in items.items() if _norm(v['name']) == q or _norm(k) == q]
    if exact:
        # prefer something that can actually be produced or mined
        exact.sort(key=lambda k: (not producible(k) and not items[k]['raw'], k))
        return exact[0]
    part = sorted({k for k, v in items.items() if q in _norm(v['name']) and (producible(k) or v['raw'])},
                  key=lambda k: len(items[k]['name']))
    if len(part) == 1:
        return part[0]
    raise LookupError('unknown item %r%s' % (query, (': did you mean ' + ', '.join(
        items[k]['name'] for k in part[:8]) + '?') if part else ''))


def find_recipe(query):
    """Recipe id from an id or name ('Stitched Iron Plate', 'Alternate: Stitched Iron Plate')."""
    recipes = db()['recipes']
    if query in recipes:
        return query
    q = _norm(query.replace('Alternate:', ''))
    hits = [k for k, r in recipes.items() if _norm(r['name'].replace('Alternate:', '')) == q or _norm(k) == q]
    if not hits:
        hits = [k for k, r in recipes.items() if q in _norm(r['name'])]
    if len(hits) == 1:
        return hits[0]
    raise LookupError('unknown or ambiguous recipe %r%s' % (query, (': ' + ', '.join(
        recipes[k]['name'] for k in hits[:8])) if hits else ''))


_PRODUCERS = None


def producers(item):
    """Recipe ids that output this item."""
    global _PRODUCERS
    if _PRODUCERS is None:
        _PRODUCERS = {}
        for k, r in db()['recipes'].items():
            for i, _ in r['outputs']:
                _PRODUCERS.setdefault(i, []).append(k)
    return _PRODUCERS.get(item, [])


def producible(item):
    return bool(producers(item))


def default_recipe(item):
    """The recipe a new player would use: standard (not alternate), the item as its main output,
    not packaging/unpackaging or ore conversion."""
    rs = db()['recipes']
    cands = producers(item)
    if not cands:
        return None

    def score(k):
        r = rs[k]
        return (r['alternate'],
                r['outputs'][0][0] != item,
                r['machine'] in ('Packager', 'Converter'),
                k.startswith(('Unpackage', 'Packaged')),
                len(r['inputs']), k)
    return min(cands, key=score)


def per_minute(recipe, item, side='outputs'):
    r = db()['recipes'][recipe]
    return sum(n for i, n in r[side] if i == item) * 60.0 / r['duration']


# ---------- solving ----------
def plan(targets, use=(), clock=1.0, miner='MinerMk2', purity='normal'):
    """targets: [(item, rate per minute)]. use: recipe ids to prefer (e.g. alternates) for the
    items they output. clock: max clock per machine (1.0 = 100%, up to 2.5 with power shards).
    Returns a dict with recipes (machines, clock, power, flows), raw resources, extractors,
    byproducts and totals."""
    D = db()
    rs, items = D['recipes'], D['items']
    chosen = {}
    for k in use:
        for i, _ in rs[k]['outputs'][:1]:
            chosen[i] = k

    def recipe_for(item):
        if item not in chosen:
            chosen[item] = default_recipe(item)
        return chosen[item]

    raw = {k for k, v in items.items() if v['raw']}
    want = {}
    for item, rate in targets:
        want[item] = want.get(item, 0) + rate
    runs = {}                                  # recipe -> machines at 100%
    for _ in range(5000):
        net = {i: -r for i, r in want.items()}
        for k, n in runs.items():
            r = rs[k]
            for i, a in r['outputs']:
                net[i] = net.get(i, 0) + n * a * 60 / r['duration']
            for i, a in r['inputs']:
                net[i] = net.get(i, 0) - n * a * 60 / r['duration']
        deficits = [(i, -v) for i, v in net.items() if v < -EPS and i not in raw and recipe_for(i)]
        if not deficits:
            break
        for i, d in deficits:
            k = recipe_for(i)
            runs[k] = runs.get(k, 0) + d / per_minute(k, i)
    else:
        raise RuntimeError('did not converge (a recipe loop that consumes more than it makes?)')

    # results
    lines = []
    total_power = 0.0
    for k, n in runs.items():
        if n < EPS:
            continue
        r, m = rs[k], D['machines'][rs[k]['machine']]
        count = math.ceil(n / clock - 1e-6)
        clk = n / count
        base = (r['power_const'] + r['power_factor'] / 2) if m['variable'] else m['power']
        power = count * base * clk ** m['exponent']
        total_power += power
        lines.append(dict(
            recipe=k, recipe_name=r['name'], alternate=r['alternate'],
            machine=r['machine'], machine_name=m['name'],
            machines_exact=round(n, 4), machines=count, clock_percent=round(clk * 100, 4),
            power_mw=round(power, 2),
            inputs=[[i, items[i]['name'], round(n * a * 60 / r['duration'], 4)] for i, a in r['inputs']],
            outputs=[[i, items[i]['name'], round(n * a * 60 / r['duration'], 4)] for i, a in r['outputs']]))
    depth = {}

    def item_depth(i, seen=()):
        if i in depth:
            return depth[i]
        k = chosen.get(i)
        if not k or i in raw or i in seen:
            return 0
        depth[i] = 1 + max([item_depth(j, seen + (i,)) for j, _ in rs[k]['inputs']] or [0])
        return depth[i]
    for l in lines:
        l['tier'] = max(item_depth(i) for i, _, _ in l['outputs'])
    lines.sort(key=lambda l: (l['tier'], l['recipe_name']))

    net = {i: -r for i, r in want.items()}
    for l in lines:
        for i, _, v in l['outputs']:
            net[i] = net.get(i, 0) + v
        for i, _, v in l['inputs']:
            net[i] = net.get(i, 0) - v
    raw_use = {i: round(-v, 4) for i, v in net.items() if v < -EPS}
    byproducts = {i: round(v, 4) for i, v in net.items() if v > 1e-6}

    extractors = {}
    for i, rate in raw_use.items():
        form = items[i]['form']
        if form == 'solid':
            ex = D['extractors'].get(miner) or D['extractors']['MinerMk2']
            per = ex['rate'] * PURITY[purity] * clock
            extractors[i] = dict(extractor=ex['name'], each=round(per, 2), count=math.ceil(rate / per - 1e-6),
                                 note='%s nodes at %d%% clock' % (purity, clock * 100))
        else:
            ex = next((e for e in D['extractors'].values() if i in e['allowed'] and e['name'] != 'Resource Well Extractor'),
                      None) or next((e for e in D['extractors'].values() if i in e['allowed']), None)
            if ex:
                per = ex['rate'] * (PURITY[purity] if ex['name'] != 'Water Extractor' else 1) * clock
                extractors[i] = dict(extractor=ex['name'], each=round(per, 2), count=math.ceil(rate / per - 1e-6),
                                     note='%s at %d%% clock' % ('any water' if ex['name'] == 'Water Extractor'
                                                                else purity + ' nodes', clock * 100))
    ex_power = sum(
        e['count'] * next(x['power'] for x in D['extractors'].values() if x['name'] == e['extractor'])
        * clock ** 1.321929 for e in extractors.values())

    def transport(item, rate):
        tiers = D['belts'] if items[item]['form'] == 'solid' else D['pipes']
        for name, cap in tiers:
            if rate <= cap + EPS:
                return name
        name, cap = tiers[-1]
        return '%d x %s' % (math.ceil(rate / cap), name)

    flows = {}
    for l in lines:
        for i, n, v in l['outputs'] + l['inputs']:
            flows[i] = max(flows.get(i, 0), v)
    return dict(
        targets=[[i, items[i]['name'], r] for i, r in want.items()],
        settings=dict(max_clock_percent=clock * 100, miner=miner, purity=purity,
                      recipes_used={i: rs[k]['name'] for i, k in chosen.items() if k}),
        recipes=lines,
        raw=[[i, items[i]['name'], v, items[i]['form']] for i, v in sorted(raw_use.items(), key=lambda kv: -kv[1])],
        extractors=extractors,
        byproducts=[[i, items[i]['name'], v] for i, v in byproducts.items() if i not in want],
        transport={items[i]['name']: [round(v, 2), transport(i, v)] for i, v in flows.items()},
        power_mw=round(total_power, 1), extractor_power_mw=round(ex_power, 1),
        machines_total=sum(l['machines'] for l in lines))


# ---------- output ----------
def unit(item):
    return 'm³/min' if db()['items'][item]['form'] != 'solid' else '/min'


def fmt(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


def format_plan(p):
    out = ['Target: ' + ', '.join('%s %s %s' % (fmt(r), n, unit(i)) for i, n, r in p['targets']),
           'Max clock %d%% | %s on %s nodes' % (p['settings']['max_clock_percent'],
                                              db()['extractors'].get(p['settings']['miner'], {}).get('name', ''),
                                              p['settings']['purity']), '']
    out.append('%-34s %-22s %8s %7s %9s' % ('Recipe', 'Machine', 'Count', 'Clock', 'Power'))
    for l in p['recipes']:
        out.append('%-34s %-22s %8s %6s%% %7s MW' % (
            (l['recipe_name'] + (' *' if l['alternate'] else ''))[:34], l['machine_name'],
            '%d (%s)' % (l['machines'], fmt(l['machines_exact'])), fmt(l['clock_percent']), fmt(l['power_mw'])))
        out.append('    in:  ' + ', '.join('%s %s' % (fmt(v), n) for _, n, v in l['inputs']))
        out.append('    out: ' + ', '.join('%s %s' % (fmt(v), n) for _, n, v in l['outputs']))
    out += ['', 'Raw resources:']
    for i, n, v, form in p['raw']:
        e = p['extractors'].get(i)
        out.append('  %-18s %10s %-7s %s' % (n, fmt(v), unit(i),
                   ('-> %d x %s (%s each, %s)' % (e['count'], e['extractor'], fmt(e['each']), e['note'])) if e else ''))
    if p['byproducts']:
        out += ['', 'Byproducts / surplus:'] + ['  %-18s %10s %s' % (n, fmt(v), unit(i)) for i, n, v in p['byproducts']]
    out += ['', 'Machines: %d | Power: %s MW production + %s MW extraction = %s MW' % (
        p['machines_total'], fmt(p['power_mw']), fmt(p['extractor_power_mw']),
        fmt(p['power_mw'] + p['extractor_power_mw'])), '* = alternate recipe']
    return '\n'.join(out)


def list_alternates(item):
    rs = db()['recipes']
    out = ['Recipes for %s:' % db()['items'][item]['name']]
    for k in sorted(producers(item), key=lambda k: (rs[k]['alternate'], k)):
        r = rs[k]
        rate = per_minute(k, item)
        out.append('  %-40s %-14s %s/min  <- %s' % (
            r['name'] + ('' if k != default_recipe(item) else '  (default)'), db()['machines'][r['machine']]['name'],
            fmt(rate), ', '.join('%s %s' % (fmt(a * 60 / r['duration']), db()['items'][i]['name']) for i, a in r['inputs'])))
    return '\n'.join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Satisfactory production calculator (game data).')
    ap.add_argument('targets', nargs='*', help='item name, then rate per minute (repeatable): "Computer" 2.5')
    ap.add_argument('--total', type=float, help='total amount of the (single) target item instead of a rate')
    ap.add_argument('--minutes', type=float, default=60, help='time to make --total in (default 60)')
    ap.add_argument('--use', action='append', default=[], help='recipe to use, e.g. an alternate (repeatable)')
    ap.add_argument('--clock', type=float, default=100, help='max clock speed %% (100, up to 250 with shards)')
    ap.add_argument('--miner', default='Mk2', help='Mk1, Mk2 or Mk3')
    ap.add_argument('--purity', default='normal', choices=list(PURITY))
    ap.add_argument('--alternates', metavar='ITEM', help='list the recipes that make ITEM')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    if a.alternates:
        print(list_alternates(find_item(a.alternates)))
        return
    t = a.targets
    if a.total is not None:
        if len(t) != 1:
            ap.error('--total needs exactly one item')
        targets = [(find_item(t[0]), a.total / a.minutes)]
    else:
        if not t or len(t) % 2:
            ap.error('give item/rate pairs, e.g. "Reinforced Iron Plate" 10')
        targets = [(find_item(t[i]), float(t[i + 1])) for i in range(0, len(t), 2)]
    p = plan(targets, use=[find_recipe(u) for u in a.use], clock=a.clock / 100,
             miner='Miner' + a.miner.replace('Miner', '').capitalize(), purity=a.purity)
    print(json.dumps(p, indent=1, ensure_ascii=False) if a.json else format_plan(p))


if __name__ == '__main__':
    main()

"""Generate a Satisfactory blueprint of the Heydar Aliyev Center (Zaha Hadid, Baku).

The white shell is a lofted surface of painted beams laid side by side (0.5 m apart), the glass
facade is thin 8x4 window walls, the first-floor slab and plaza are concrete foundations.
Design units are metres, x along the facade, y from front (-16) to back (+16), z up from the plaza.

All pieces come from the skill's donor library, so this runs on any PC.

  python -I heydar_aliyev_center.py --out ".local/blueprints/heydar-aliyev-center/Heydar Aliyev Center.sbp"
  python -I heydar_aliyev_center.py --out ... --install "<save session name>"   # also copy into the game
"""
import argparse, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from sbp import Blueprint, Library, short, set_float, get_color, set_color, item, install, write_sbpcfg

ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
ap.add_argument('--out', default='Heydar Aliyev Center.sbp', help='.sbp to write (a .sbpcfg goes next to it)')
ap.add_argument('--install', metavar='SESSION', help='also copy the result into this save session\'s blueprint folder')
args = ap.parse_args()
OUT = args.out

WHITE = (0.86, 0.86, 0.86, 1.0)
FRAME = (0.03, 0.035, 0.04, 1.0)
DEPTH_FRONT, DEPTH_BACK = -16.0, 16.0
LINE_SPACING = 0.5      # beams are 0.5 m wide, so this gives a closed surface
SEGMENT = 2.0           # target beam length along the flow
PLAZA_TOP = 1.0         # foundations occupy z 0..1
SLAB_Z = 5.0            # first-floor slab z 5..6 above plaza top
APRON_DEPTH = 14.0      # how far back the front-left roof slopes down to the plaza

# Silhouette traced from the photo (back/main profile), left curl -> peak -> right lobe -> slab.
BACK = [(-22.5, 0), (-24.8, 7.3), (-24.3, 14.7), (-21.8, 17.0), (-15.7, 17.2), (-9.8, 18.0),
        (-5.7, 20.5), (-1.5, 24.6), (2.6, 29.8), (6.7, 35.1), (10.5, 38.4), (14.3, 40.2),
        (17.7, 40.4), (21.2, 39.2), (23.6, 36.2), (24.8, 30.7), (25.1, 23.8), (24.9, 16.9),
        (23.9, 12.8), (21.8, 9.8), (19.8, 7.3), (17.0, 6.0)]
# Front edge: same as BACK on the right, but the left part dips to the plaza (the grooved face).
FRONT = [(-22.5, 0), (-24.8, 7.3), (-24.3, 12.5), (-21.5, 14.0), (-17.5, 6.0), (-13.5, 0.6),
         (-9.0, 4.0), (-5.0, 10.0), (0.0, 19.0), (5.0, 29.0), (10.0, 36.5)] + BACK[11:]
assert len(FRONT) == len(BACK)


# ---------- geometry ----------
def catmull(points, samples=24):
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(samples):
            t = k / samples
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    out.append(points[-1])
    return out


def resample(poly, step):
    d = [0.0]
    for a, b in zip(poly, poly[1:]):
        d.append(d[-1] + math.dist(a, b))
    n = max(1, round(d[-1] / step))
    out, j = [], 0
    for i in range(n + 1):
        s = d[-1] * i / n
        while j < len(d) - 2 and d[j + 1] < s:
            j += 1
        t = (s - d[j]) / max(d[j + 1] - d[j], 1e-9)
        out.append(tuple(poly[j][k] + (poly[j + 1][k] - poly[j][k]) * t for k in range(2)))
    return out


def smoothstep(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def profile_at(y):
    """Control points of the shell cross-section at depth y (blend front edge -> main profile)."""
    w = smoothstep((y - DEPTH_FRONT) / APRON_DEPTH)
    return [(f[0] + (b[0] - f[0]) * w, f[1] + (b[1] - f[1]) * w) for f, b in zip(FRONT, BACK)]


def offset_inward(poly, dist):
    out = []
    for i, p in enumerate(poly):
        a, b = poly[max(i - 1, 0)], poly[min(i + 1, len(poly) - 1)]
        tx, tz = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, tz) or 1
        out.append((p[0] + tz / n * dist, p[1] - tx / n * dist))  # right-hand normal = interior
    return out


def quat_from_dir(d):
    """Rotation taking the beam's local +X onto unit vector d (no roll)."""
    x, y, z = d
    q = (0.0, -z, y, 1.0 + x)
    if q[3] < 1e-6:                       # pointing straight back along -X
        return (0.0, 0.0, 1.0, 0.0)
    n = math.sqrt(sum(c * c for c in q))
    return tuple(c / n for c in q)


def yaw(deg):
    r = math.radians(deg) / 2
    return (0.0, 0.0, math.sin(r), math.cos(r))


# ---------- donors (from the shipped library) ----------
PIECES = ['Beam_Painted', 'Wall_Window_Thin_8x4_01', 'Foundation_Concrete_8x1']
lib = Library.load(needs=PIECES, custom_paint=True)
beam_donor = lib.donor('Beam_Painted', custom=True)
glass_donor = lib.donor('Wall_Window_Thin_8x4_01', custom=True)
found_donor = lib.donor('Foundation_Concrete_8x1', custom=False)
for o, col in ((beam_donor, WHITE), (glass_donor, FRAME)):   # paint once; every copy inherits it
    set_color(o, col, 'PrimaryColor')
    if get_color(o, 'SecondaryColor'):
        set_color(o, col, 'SecondaryColor')

bp = lib.new_blueprint(dims=[8, 6, 6])


def add(donor, pos_m, rot, length_m=None):
    # design (x, y, z) metres -> Unreal cm; plaza top is z = PLAZA_TOP. Unreal is left-handed:
    # facing the front (-Y side), +X is on your left, so x is negated to match the photo.
    o = bp.add_copy(donor, lib.bp, [-pos_m[0] * 100, pos_m[1] * 100, (pos_m[2] + PLAZA_TOP) * 100], rot)
    if length_m is not None:
        set_float(o, 'mLength', round(length_m * 100, 1))
    return o


beam_len = 0.0


def beam_between(a, b, overlap=0.15):
    """Painted beam from 3D point a to b (metres), stretched slightly so joints don't gap."""
    global beam_len
    d = [b[i] - a[i] for i in range(3)]
    L = math.sqrt(sum(c * c for c in d))
    if L < 0.05:
        return
    u = [c / L for c in d]
    start = [a[i] - u[i] * overlap for i in range(3)]
    # add() negates x of the position, so mirror the direction too
    add(beam_donor, start, quat_from_dir((-u[0], u[1], u[2])), L + 2 * overlap)
    beam_len += L + 2 * overlap


# ---------- shell ----------
n_lines = int(round((DEPTH_BACK - DEPTH_FRONT) / LINE_SPACING)) + 1
for j in range(n_lines):
    y = DEPTH_FRONT + j * LINE_SPACING
    pts = resample(catmull(profile_at(y)), SEGMENT)
    for p, q in zip(pts, pts[1:]):
        beam_between((p[0], y, p[1]), (q[0], y, q[1]))

# Rim: a 1.5 m white band on the front and back edges, like the panelled edge in the photo.
for y, ctrl in ((DEPTH_FRONT, FRONT), (DEPTH_BACK, BACK)):
    edge = resample(catmull(ctrl), SEGMENT)
    for k in (1, 2, 3):
        band = offset_inward(edge, 0.5 * k)
        for p, q in zip(band, band[1:]):
            beam_between((p[0], y, p[1]), (q[0], y, q[1]))

# ---------- first-floor slab ----------
for x in (-4, 4, 12, 17):
    for y in (-12, -4, 4, 12):
        add(found_donor, (x, y, SLAB_Z + 0.5), (0, 0, 0, 1))
for z in (SLAB_Z + 0.25, SLAB_Z + 0.75):     # white fascia on the slab's front and back edge
    for y in (DEPTH_FRONT - 0.25, DEPTH_BACK + 0.25):
        x = -8.0
        while x < 21.0:
            nx = min(x + 8.0, 21.0)
            beam_between((x, y, z), (nx, y, z), overlap=0.0)
            x = nx


# ---------- glass ----------
def glass_polygon(y):
    """Outline of the upper glass at depth y: under the shell's inner edge there, above the slab."""
    inner = offset_inward(resample(catmull(profile_at(y)), 0.5), 1.5)
    poly = [p for p in inner if p[1] >= SLAB_Z + 1.0 and p[0] >= -8.0]
    return poly + [(poly[-1][0], SLAB_Z + 1.0), (-8.0, SLAB_Z + 1.0)]


def span_at(poly, z):
    xs = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] - z) * (b[1] - z) < 0:
            xs.append(a[0] + (z - a[1]) / (b[1] - a[1]) * (b[0] - a[0]))
    return (min(xs), max(xs)) if len(xs) >= 2 else None


def glass_row(x0, x1, z, y, back=False):
    w = x1 - x0
    if w < 3.0:
        return 0
    n = max(1, math.ceil(w / 8.0))
    centers = [x0 + 4.0] if n == 1 else [x0 + 4.0 + i * (w - 8.0) / (n - 1) for i in range(n)]
    for i, c in enumerate(centers):
        # walls stretch along their local Y; yaw 90 lays them along the facade (x)
        add(glass_donor, (c, y + (0.02 if i % 2 else 0.0), z), yaw(270 if back else 90))
    return n


panes = 0
for y, back in ((DEPTH_FRONT + 1.0, False), (DEPTH_BACK - 1.0, True)):
    poly = glass_polygon(y)
    z = SLAB_Z + 1.0
    while z < 40:
        lo, hi = span_at(poly, z + 0.2), span_at(poly, z + 3.8)
        if lo or hi:
            # Rising side (left): take the row's widest extent; the sloped roof in front hides
            # the overshoot. Lobe side (right): allow at most 1.5 m past the row top (rim band).
            xl = min(s[0] for s in (lo, hi) if s)
            xr = max(s[1] for s in (lo, hi) if s)
            if hi:
                xr = min(xr, hi[1] + 1.5)
            panes += glass_row(xl, xr, z, y, back)
        z += 4.0
for y, back in ((DEPTH_FRONT + 3.0, False), (DEPTH_BACK - 3.0, True)):   # ground floor, set back
    panes += glass_row(-8.0, 20.0, 0.0, y, back)

# ---------- plaza ----------
for x in range(-28, 29, 8):
    for y in range(-20, 21, 8):
        add(found_donor, (x, y, -0.5), (0, 0, 0, 1))

# ---------- header ----------
n_found = sum(1 for o in bp.objects if short(o['cls']) == 'Foundation_Concrete_8x1')
bp.cost = [(item('Desc_SteelPlate'), math.ceil(beam_len / 4 + 6 * panes)),   # estimate
           (item('Desc_Silica'), 2 * panes),
           (item('Desc_Cement'), 5 * n_found)]
bp.recipes = lib.recipes_for(PIECES)
Path(OUT).parent.mkdir(parents=True, exist_ok=True)
bp.save(OUT)
write_sbpcfg(Path(OUT).with_suffix('.sbpcfg'),
             "Heydar Aliyev Center (Zaha Hadid, Baku). A white lofted shell made of painted beams, "
             "steel-framed glass curtain walls, a first-floor slab and a concrete plaza.\n\n"
             "**AWESOME Shop Requirements**\n* Structural Beam Pack (painted beams)\n"
             "* Steel-Framed Windows\n* Concrete Foundation Material\n\n"
             "Custom 8x6x6 size (64 x 48 x 48 m): place it from the blueprint menu; it can't be "
             "reopened in a vanilla designer.\n\n*Generated from a photo with Claude.*",
             color=(0.86, 0.86, 0.86, 1.0))

if args.install:
    print('installed', install(OUT, args.install))

check = Blueprint.load(OUT)
xs = [o['pos'] for o in check.actors()]
print('pieces', len(check.actors()), '| beams m', round(beam_len), '| panes', panes, '| foundations', n_found)
print('bounds m', [(round(min(p[i] for p in xs) / 100, 1), round(max(p[i] for p in xs) / 100, 1)) for i in range(3)])
print('cost', [(short(i), n) for i, n in check.cost])

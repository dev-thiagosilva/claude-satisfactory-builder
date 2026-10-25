---
name: satisfactory-blueprints
description: Read, visualize in 3D, edit and create Satisfactory blueprint files (.sbp / .sbpcfg) directly on disk, without opening the game, using a shipped library of building pieces. Use this whenever the user mentions Satisfactory blueprints, .sbp files, the blueprint designer, their blueprints folder, or wants to see, inspect, count pieces of, cost out, modify, duplicate, mirror, stack, or generate a building/factory layout as a blueprint, even if they don't say ".sbp".
---

# Satisfactory blueprints

Work with blueprint files as data: parse them, render them, change them, and write new ones
the game can load. Everything goes through `scripts/sbp.py`. It reads and writes every format
from Update 8 to 1.2 and round-trips all of the user's blueprints byte-for-byte.

## Where the files are

`%LOCALAPPDATA%\FactoryGame\Saved\SaveGames\blueprints\<session name>\`, for example
`C:\Users\<user>\AppData\Local\FactoryGame\Saved\SaveGames\blueprints\<save name>\`.
`sessions()` in `sbp.py` lists them; `install(sbp, session)` copies a finished blueprint in.
Each blueprint is `<name>.sbp` (the buildings) plus `<name>.sbpcfg` (description, icon, colour).
List the folder when the user names a blueprint loosely, since names contain brackets and spaces.

## Look at a blueprint

```bash
python -I scripts/sbp.py info   "<file.sbp>"              # size, piece counts, cost, recipes
python -I scripts/sbp.py render "<file.sbp>" out.html     # interactive 3D viewer
python -I scripts/sbp.py dump   "<file.sbp>" out.json     # every piece: type, pos, rot, length, paint
python -I scripts/sbp.py catalog "<blueprints root>"      # every usable piece type + donor files
```

Show the render to the user in the app's Browser pane. A static server lets the page load
three.js: add a `.claude/launch.json` entry running `python -m http.server <port>` in the
output folder, call `preview_start`, then navigate to the file. Check it with a screenshot before
saying it works. The viewer has a toggle per piece type, a cut-height slider for seeing inside,
Front/Side/3-4/Top buttons, and the cost line. For scripted screenshots, run
`setView('front')` or `setCamera([x, y, z], [tx, ty, tz])` (three.js metres, Y up) through the
browser's JavaScript tool. Custom paint renders in its real colour.

Tell the user what the render approximates. Positions, rotations and beam lengths are exact.
Shapes are boxes and arcs, not the game meshes. Paint shows the slot number only, because the
file doesn't store the user's actual colours. Belts and pipes have spline data that the viewer
doesn't draw yet; they show up as small markers.

## Edit or create a blueprint

Use the library. Keep the user's original file untouched: write to a new name, and only
overwrite if they ask for that.

```python
import sys; sys.path.insert(0, r'<skill dir>/scripts')
from sbp import Blueprint, Library, get_float, set_float, get_color, set_color, short, estimate_cost

bp = Blueprint.load(src)
beam = next(o for o in bp.actors() if short(o['cls']) == 'Beam_Painted')
copy = bp.clone(beam, pos=[x, y, z], rot=[0, 0, 0, 1])   # structural piece
set_float(copy, 'mLength', 1200.0)                        # beams: length in cm
m = bp.clone_with_components(machine, pos=[...])          # machines bring their connectors
bp.remove(some_actor)                                     # also drops its components
bp.save(dst)
```

Why build from clones: each building's data blob holds properties, paint and component links
that are hard to write from scratch. Copying a real piece of the same type and changing its
transform gives the game exactly what it expects. To use a piece type that isn't in the file
yet, take it from another blueprint in the folder: `bp.objects.append(...)` after a
`clone` from the other `Blueprint`, and add its recipe to `bp.recipes`.

## Build something new (e.g. from a photo or an idea)

1. **Pick pieces from `library/ASSETS.md`**, the list of every buildable piece in the game. It's
   grouped by design purpose and has a quick picker ("I want X → use Y") plus use/tips/go-to
   pieces per category, then name, size, real build cost and unlock. ✅ = sample from a real
   build, 🧪 = sample made from a similar piece (not yet confirmed in game), 🎨 = takes any
   colour; unmarked pieces can't be placed yet.
   `python -I scripts/sbp.py library` prints the ready ones. The library is game-1.2 format
   only (`donors-v60.sbp`), so every build comes out in the format the player's game writes.
   Train platforms come with their built-in track: `add_copy` brings companions along. `Library.load(needs=[...],
   custom_paint=True)` checks they're all available. Mixing pieces across versions isn't
   verified, so don't. To use a piece that only exists in the user's own blueprints, run
   `sbp.py catalog "<blueprints root>"` and clone from their file, with their OK.
2. **Start the blueprint from the library**: `bp = lib.new_blueprint(size='medium')` copies the
   right header for that version and sets the plot size. Sizes, in foundations per side, cubed:
   `small` 6, `medium` 10 (default), `large` 20, `extra-large` 40 (`SIZES`, `DEFAULT_SIZE`).
   `size_limits_m(size)` gives the half-width and height in metres to design within, and
   `out_of_bounds(bp)` must be empty before saving. Add pieces with
   `bp.add_copy(lib.donor(type, custom=True), lib.bp, pos_cm, quat)`.
3. **Generate geometry in code.** Painted beams are the most flexible piece: any length via
   `mLength`, any angle via the quaternion, 0.5 × 0.5 m section. Laying beam lines 0.5 m apart
   along curves gives closed, smooth surfaces. Thin window walls (8 × 4 m) give framed glass.
   Foundations give floors. `examples/heydar_aliyev_center.py` is a full worked example: a curve
   traced from a photo, a lofted shell, a rim band, glass fill clipped to the shell, slab and
   plaza, cost and recipes, ~4,100 pieces.
4. **Paint.** A donor with a Custom swatch stores `PrimaryColor`/`SecondaryColor`.
   `set_color(obj, (r, g, b, a))` with linear values (white ≈ 0.86) recolours it. Swatch-slot
   donors only reference the user's palette slot, so their colour is whatever that slot is in game.
5. **Mind handedness.** Unreal is left-handed: when you face a blueprint from its -Y side, +X is on
   your **left**. Mirror x (positions and directions) when you design in a normal right-handed
   frame, or the build comes out flipped. The viewer reproduces this, so check it with
   `setView('front')`.
6. **Header.** Set `bp.recipes = lib.recipes_for([...])` for every piece type used, and set
   `bp.cost = estimate_cost(bp)`, which uses the game's own build recipes from `assets.json`.
7. **Install.** `write_sbpcfg(path, description)` writes the companion file. Then
   `install(sbp, session)` copies both into the save's blueprint folder, and refuses to overwrite.

Before saving a new or edited blueprint:
- **Grid and bounds.** Foundations snap to 800 cm and walls to 400 cm heights. Keep pieces
  inside the designer volume for `bp.dims` (see `references/format.md` §6), or change `dims` to
  match.
- **Rotations** are quaternions `(x, y, z, w)` about Unreal's Z-up axes. Yaw θ is
  `(0, 0, sin θ/2, cos θ/2)`, so 90° is `(0, 0, 0.7071, 0.7071)`.
- **Recipes.** `bp.recipes` must list every building recipe used, or the game may treat the
  blueprint as locked.
- **Cost.** `bp.cost` is what the blueprint menu shows. Recompute it with `estimate_cost(bp)`
  after adding or removing pieces.
- **Belt and pipe connections** live in component data. Moving a machine doesn't move the belt
  splines attached to it, so call out reconnecting in game when the layout changes.
- **.sbpcfg.** Copy the original's `.sbpcfg` to the new name, then edit the description if wanted.

After saving, reload the file with `Blueprint.load` to make sure it parses, and render it so the
user can check the change visually before loading it in game. The game picks up new blueprint
files when the save is reloaded.

## Blueprint Studio

`studio/server.py` serves a local editor on `http://localhost:8770` for every build in a
creations folder (`--creations`, default `./.local/blueprints`; one folder per build with its
`.sbp`). The player can view a build, select, move, rotate, duplicate, delete and recolour
pieces, undo, save (a backup goes to `history/`), and install it into a save with
**Use in game**. Prefer the studio over a static render whenever the player should see or change
a build.

## Production planning

`scripts/calc.py` answers "how many machines / resources / how much power" from the game's own
recipes (`library/production.json`, written by `build_assets.py`). For each step it gives the
machine count and an even clock, plus raw resources with miner/extractor counts, byproducts
(fed back in before anything extra is built), power on the game's clock curve, and the belt or
pipe tier.

```bash
python -I scripts/calc.py "Heavy Modular Frame" 5 "Computer" 2.5     # item/rate pairs, per minute
python -I scripts/calc.py "Reinforced Iron Plate" 10 --use "Stitched Iron Plate" --clock 250
python -I scripts/calc.py "Heavy Modular Frame" --total 500 --minutes 60 --miner Mk3 --purity pure
python -I scripts/calc.py --alternates "Reinforced Iron Plate"         # list recipes for an item
```

In code, use `from calc import plan, find_item, find_recipe, format_plan`, or add `--json`. The
studio also serves a visual **Production planner** at `/planner`, like satisfactory-calculator.com:
add items, switch each step's recipe, and set max clock, miner tier and node purity.

## Production lines

`scripts/factory.py` turns a plan into a ready-to-place production line: rows of machines set to
their recipe and clock, splitter/merger manifolds, overhead belt lanes linking the rows, raw
inputs as open belt ends, products into storage, and a foundation floor. Belts are real splines
with both ends connected; a collision check and layout retries keep belts from touching.

```bash
python -I scripts/factory.py "Reinforced Iron Plate" 5 [--use "Stitched Iron Plate"] [--name "RIP Line"] [--out file.sbp]
```

In code: `factory.build_best(calc.plan(...), name)` returns `(Factory, report)`, and you save
`factory.bp`. Machine ports come from `library/ports.json`. Not yet included: pipes for fluids,
power, and byproducts fed back in. The studio planner's **Build this factory** button does the
same.

## Formats and details

Read `references/format.md` for the byte layout (header, chunk variants, object headers,
property encoding, piece origins and sizes, .sbpcfg) before doing anything the helpers above
don't already cover, such as editing spline points, reading recipes or clock speeds, or
writing a property type you haven't seen yet.

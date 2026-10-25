# claude-satisfactory-builder

Claude designs Satisfactory buildings for players and saves them as blueprints the game can place.
A photo, a famous building or an idea goes in. A previewed `.sbp` + `.sbpcfg` in the player's
blueprint folder comes out.

**Who you're working with:** usually a player who doesn't program. They bring the idea and make
the choices; you do everything technical. They arrive here through the `satisfactory-builder`
skill (see `install/`), which put this repo on their PC and moved you into it.

## Talking with the player

- Use game words, not code words: "pieces", "beams", "foundations", "glass walls", "your save",
  "the blueprint menu". Don't show code, file formats or terminal output unless they ask.
- Never ask them to run a command, edit a file or find a folder. Do it, then say what happened in
  a sentence.
- Ask only what changes the build, a few questions at a time, with a suggested default for each:
  what to build (photo/idea), which **size** (below; default **medium**), colours/materials, and
  which save to put it in. List their saves with `sessions()` from `sbp.py` and offer the most
  recent.

## Build sizes

Every build uses one of four sizes. **Ask the player which size before building**, and offer
**medium** as the default. Then build only that size. Don't generate the other sizes unless
they ask. If they later want it bigger or smaller, regenerate at the new size.

| Size | Footprint (foundations) | In metres | Max height |
|---|---|---|---|
| `small` | 6 × 6 | 48 × 48 m | 48 m |
| `medium` *(default)* | 10 × 10 | 80 × 80 m | 80 m |
| `large` | 20 × 20 | 160 × 160 m | 160 m |
| `extra-large` | 40 × 40 | 320 × 320 m | 320 m |

- The size is the blueprint's plot: `lib.new_blueprint(size=...)` sets `dims`, and every piece
  must stay inside it (`size_limits_m(size)` gives half-width and height; `out_of_bounds(bp)`
  must be empty before saving). Scale the design to fill the plot sensibly.
- Pieces don't scale: beams stay 0.5 m wide, glass panes 8 × 4 m, foundations 8 m. Bigger sizes
  mean more pieces and more cost. Mention it for large and extra-large. For example, the Heydar
  example is ~3,800 pieces small, ~6,400 medium, ~13,000 large and ~29,000 extra-large.
- Only small (6 × 6 × 6) matches an in-game designer (Mk3), so it's the only size the player can
  reopen in a designer. Every size can be placed from the blueprint menu.
- Show before you install, in the **Blueprint Studio** (see below). Point them at it, describe
  what they're looking at, and say plainly what's approximate. Iterate: take their feedback in
  chat and regenerate, or let them tweak it in the studio themselves.
- Install only when they say they want it, either through the studio's **Use in game** button or
  by you calling `install(...)`. Then tell them how to use it: reload the save, open the build
  menu's **Blueprints** tab, and which AWESOME Shop unlocks the pieces need. Give the estimated
  cost.
- Be honest about limits. The preview uses simple shapes, the cost is an estimate, and placement
  is only proven once they've tried it in game. Ask them to tell you how it went.

## Layout

| Path | What it is |
|---|---|
| `install/satisfactory-builder/SKILL.md` | The skill players install. Fetches/updates this repo and hands over to this file |
| `.claude/skills/satisfactory-blueprints/` | Project skill with all the tooling. **Load it before any blueprint work** |
| `  scripts/sbp.py` | Read/write/edit/render `.sbp`; `Library`, `install`, `sessions`, `write_sbpcfg` |
| `  library/ASSETS.md` | **Every buildable piece in the game** (546), grouped by design purpose, with a **quick picker** ("I want X → use Y") and per-category use/tips/go-to pieces; name, size, real cost, unlock, and whether it's **ready**. Start here when choosing pieces |
| `  library/assets.json` | The same data for code (`assets()`, `estimate_cost(bp)` in `sbp.py`) |
| `  library/donors-v60.sbp` | Sample pieces in game-1.2 format that builds copy from (`index.json` lists them). The project targets **game 1.2 only** |
| `  scripts/sav.py` | Read-only reader for 1.2 save files (used to take building samples from a world) |
| `  studio/` | **Blueprint Studio**: local three.js app (`server.py` + `index.html`) to view, edit and install builds |
| `  examples/heydar_aliyev_center.py` | Worked example: a famous building traced from a photo |
| `  references/format.md` | Byte-level format, piece sizes and origins, designer limits |
| `  scripts/build_library.py` | Maintainer tool that regenerates `library/` from 1.1/1.2 blueprints and save files |
| `.local/blueprints/<name>/` | The player's builds: `build.py`, the `.sbp`/`.sbpcfg`, reference images. **Gitignored** |
| `out/` | Scratch output (previews, test saves). Gitignored |

The project skill is self-contained (scripts, library, viewer) so it can also be installed on its
own. Keep anything it needs inside its folder.

## Building a blueprint

1. **Choose pieces from `library/ASSETS.md`.** Start with its quick picker, then read the
   category's **Use for / Tips / Go-to pieces**. Pieces marked ✅ (sampled from real builds) or
   🧪 (made from a similar piece, not yet confirmed in game) can be placed. Prefer ✅ where there's
   a choice. For pieces with no mark, say they aren't in the library yet and suggest the closest
   ready one. ⛔ legacy pieces can't be built in the current game. Painted beams make curves and
   surfaces at any angle and length. Thin window walls make framed glass. Foundations make floors
   and plazas. Walls, roofs, ramps and quarter pipes make conventional buildings. Prefer pieces
   marked "any colour" when colour matters.
2. **Write a generator** at `.local/blueprints/<kebab-name>/build.py`, modelled on
   `examples/heydar_aliyev_center.py`:
   `lib = Library.load(needs=[...], custom_paint=...)`, `bp = lib.new_blueprint(size='medium')`,
   `bp.add_copy(lib.donor(type), lib.bp, pos_cm, quat)`, `set_float(o, 'mLength', cm)`,
   `set_color(o, rgba)`, then `bp.recipes = lib.recipes_for(...)`, `bp.cost = estimate_cost(bp)`,
   `bp.save(...)`, `write_sbpcfg(...)`. Everything in one blueprint comes from one library version,
   which `Library.load` guarantees.
3. **Check it yourself first.** Open it in the studio (next section), and use
   `setView('front')` / `setCamera(pos, target)` from the browser's JavaScript tool to screenshot
   it against the reference. Fix what's off before showing the player.
4. **Show the player the studio** at `http://localhost:8770/?build=<folder>`.
5. **Install** when they ask: the studio's **Use in game** button, or `install(sbp, session)`.
   Both refuse to overwrite. On a name clash pick a new name, or ask before replacing an earlier
   version of the same build.

## Production planning

When a player asks how many machines, resources or how much power something needs, use
`scripts/calc.py`. It works from the game's own recipes (`library/production.json`, written by
`build_assets.py`): machines with clock speeds, raw resources with miner/extractor counts,
byproducts, power, and belt/pipe tiers.
`python -I .claude/skills/satisfactory-blueprints/scripts/calc.py "Heavy Modular Frame" 5 [--use "Stitched Iron Plate"] [--clock 250] [--miner Mk3 --purity pure]`,
`--total 500 --minutes 60` for an amount, `--alternates ITEM` to list recipes. For the visual
version, point them to the studio's **Production planner** at `http://localhost:8770/planner`
(add items, switch alternate recipes per row, set clock/miner/purity).

## Production lines (factories)

When a player wants a factory for some items ("build me a line for 5 motors a minute"), plan it
with `calc.py`, then build it with `scripts/factory.py`. Or they press **Build this factory as a
blueprint** in the planner. Either way the result is a ready production line in
`.local/blueprints/<name>/`:
- one row per recipe step, each machine set to its recipe and clock (≤ 100%, because blueprints
  can't hold power shards);
- splitter manifolds feeding every input (extra inputs on raised manifolds), merger manifolds
  collecting outputs;
- overhead belt lanes in a corridor on the west side linking the rows (each lane in its own
  column; short hops use a low pass or stay at belt height);
- raw resources arrive as open belt ends on the south edge (the player connects miners there);
  products and solid byproducts go into storage containers;
- a foundation floor, and a plot sized to fit (production lines are long; they don't use the
  four building sizes).

`python -I .claude/skills/satisfactory-blueprints/scripts/factory.py "Motor" 2 [--use "..."] [--name "..."]`
prints a report: rows, raw inputs, outputs, size, warnings and belt collisions. The generator
retries lane layouts until no belts touch. A remaining collision is cosmetic (belts clip, items
still flow); say where it is.

Tell the player plainly what isn't done yet: **pipes for fluids** (fluid ports are left open;
the report lists which steps), **power** (no poles or wires; they connect it), and **byproducts
fed back into the line** (they go to storage). Machine ports come from `library/ports.json`,
learned from belts and pipes plugged into machines in a real 1.2 save (`build_library.py
--save`). Ports never seen plugged in are mirrored from a sibling and marked `inferred`. The
first in-game test of a generated line should be a small one (e.g. 30 Iron Plate).

## Blueprint Studio

A local web app for the player's builds in `.local/blueprints/`. It lists their builds and shows
each in 3D, with piece-type toggles, a cut-height slider and Front/Side/3-4/Top views. Players
can click to select pieces (Shift adds), select all of a type, move in 0.5/1/4/8 m steps,
rotate 15°/90°, duplicate, delete, recolour pieces that take any colour, undo/redo, **Save**
(the previous file goes to the build's `history/`), and **Use in game**, which installs into the
chosen save.

- Start it: `preview_start` with the `studio` config in `.claude/launch.json` (port 8770). If
  that starts the wrong server, run
  `python -I .claude/skills/satisfactory-blueprints/studio/server.py --port 8770 --creations .local/blueprints`
  in the background and call `preview_start` with `url: http://localhost:8770`. The player can
  also open that address in their own browser.
- It listens on this PC only (127.0.0.1) and only writes inside `.local/blueprints/<build>/` and
  the game's blueprint folders.
- After the player edits and saves in the studio, re-read the `.sbp` before regenerating, so
  you don't overwrite their manual changes. Ask whether to keep them if a regenerate would lose
  them.
- Edits that the studio can't do (reshaping curves, new parts, a different size) are yours: change
  `build.py` and regenerate.

Rules that bite:
- **Unreal is left-handed.** Seen from the blueprint's front (-Y side), +X is on the left. Mirror
  x when designing in a normal frame, then check with the front view.
- **Units are centimetres**, rotations are quaternions (x, y, z, w), Z is up. Yaw θ =
  `(0, 0, sin θ/2, cos θ/2)`. Beams extend along local +X from their origin, 0.5 × 0.5 m section.
- **`dims`** (8 m units) comes from the size preset and must cover the pieces: x and y in
  ±dims·400 cm, z in 0…dims_z·800 cm.
- **Header**: recipes for every piece type, and the cost from `estimate_cost(bp)`, which uses the
  game's own build recipes. Length-based pieces may round slightly differently in game.
- **Machines and logistics** come with empty ports and no power, as if freshly placed. The player
  connects belts, pipes and power in game. Power lines aren't in the library, because a wire
  needs two ends.

## The player's game files

`%LOCALAPPDATA%\FactoryGame\Saved\SaveGames\blueprints\<save session>\`. Never modify or delete
a player's existing blueprints. Read them only if the player asks, e.g. to look at or remix one of
their own designs (`sbp.py info/render/dump`, `catalog` for the pieces they contain).

## Maintaining this repo

- **Game 1.2 only.** The library and every build are in game-1.2 format (object version 60).
  The reader still opens older blueprints (Update 8 onwards) so players can look at old designs.
- After changing `sbp.py`, round-trip a large set of real blueprints and confirm every file is
  byte-identical (`roundtrip` command; the maintainer's set is 443 files).
- To grow the library: run `scripts/build_assets.py` first (so `assets.json` exists), then
  `scripts/build_library.py "<blueprints root>" --save "<world>.sav"` over 1.1/1.2 blueprints and
  saves that contain the new pieces. Check `ASSETS.md` (its ready column refreshes), run
  `examples/piece_test.py`, and commit `library/`. It:
  - takes one sample per piece type, clean if possible. Pieces only ever seen wired up get their
    links to other buildings removed (empty ports, no power);
  - samples train platforms together with their built-in track (they don't work without it);
  - makes every lightweight structure (foundations, ramps, walls, roofs, beams, pillars,
    walkways…) from a real 1.2 structure sample by swapping class and recipe, since in 1.2 they
    share one property set. Part-less pieces like doors and signs come from their own kind;
    machine models (MinerMk1/2/3) from each other. Pieces made this way are marked 🧪;
  - adds a custom-RGB paint variant by copying a real 1.2 customization block;
  - skips anything carrying a player's account data, takes no signs from saves (player text),
    drops the `BuiltBy` player handle, and records no file names;
  - empties every inventory (machines, storage, stations) and resets clock and production boost
    to 100%, so no items, power shards or Somersloops travel with the samples;
  - with `--save`, learns machine port positions into `ports.json` for the factory generator.
  New object ids keep the original digit count, because references also sit inside longer
  strings whose stored sizes must not change. `sav.py` documents the save layout.
- Confirm 🧪 pieces in game with `examples/piece_test.py`, which writes four test blueprints
  with one of every ready piece. Place them in a sandbox save and record broken pieces. A
  confirmed piece can be promoted by building it in game and re-running `build_library.py` on
  the blueprint.
- After a game update, regenerate the full piece list from the game's modding data:
  `scripts/build_assets.py "<game>/CommunityResources/Docs/en-US.json"`. It writes
  `assets.json` and `ASSETS.md` with names and numbers only, no description text.
- Still missing from the library (see ASSETS.md): power lines (need two ends), some hypertube
  pieces, and pieces not in the maintainer's world yet: Biomass Burner, Nuclear Power Plant, Power Tower, Priority
  Merger/Power Switch, Pipeline T-Junction, Street Light, Flood Light Tower, Buffer Stop, Fluid
  Truck Station, landing/jump pads, and unique buildings (HUB, Space Elevator, MAM, designers).
  Building one of each in a 1.2 world and re-running `build_library.py --save` adds them.
- Not yet supported: drawing belt/pipe splines in the preview, exact game meshes in the preview.

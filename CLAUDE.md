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
| `  scripts/sav.py` | Reader for 1.2 save files (building samples; offsets for the writer) |
| `  scripts/world.py` | Builds straight into a **new copy** of a 1.2 save: `World(sav).add_blueprint(bp, pos, yaw)`, `write()` |
| `  studio/` | **Blueprint Studio**: local three.js app (`server.py` + `index.html`) to view, edit and install builds; `map.html` is the **World map**, `pieces.js` the shapes both share |
| `  tools/terrain/` | C# tool (CUE4Parse) that reads the ground heights from the player's game install into `.local/terrain/data` for the World map |
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
  can't hold power shards); a step whose belts would carry more than 1200/min (or pipes more
  than 600 m³/min) is split into parallel rows;
- solids on belts, fluids on pipes, built the same way: splitter / pipe-junction manifolds
  feeding every input (extra inputs on raised manifolds), merger / junction manifolds collecting
  outputs (a fluid output beside a solid one hops over its line); every belt and pipe is the
  lowest tier that carries its flow (belts Mk.1–6, pipes Mk.1 300 / Mk.2 600 m³/min);
- flows balanced item by item: producer rows feed consumer rows (a consumer fed by two sources
  gets a merger per lane), what's left goes to storage, and a source that feeds both gives its
  consumers priority through smart splitters (overflow to storage);
- overhead belt and pipe lanes in a corridor on the west side linking the rows (each lane in its
  own column; short hops use a low pass or stay at belt height; pipes only use the low pass, to
  keep the head lift small);
- raw resources arrive in **input buffers** on the south side, each with a label sign: storage
  containers for solids (≤ 1200/min, one supply belt) and fluid buffers for fluids (≤ 600 m³/min,
  one supply pipe); products go into storage containers / fluid buffers on the north side. A
  fluid byproduct nobody uses (e.g. Heavy Oil Residue from Plastic) goes to a fluid buffer with a
  warning: the line stops when it's full, so tell the player to use it or pick a recipe that does;
- power: Mk.2 poles by default (`--pole Mk1|Mk3`), each powering as many machines as its
  connections allow, chained along each row and from row to row; the player connects their
  grid to the first pole of the first row;
- a Label Sign (2 × 1 m) beside every machine input and output, every input container and
  every product container, standing on a beam post: item name and rate ("IRON ORE" /
  "IN 22.5/min");
- supports (`add_supports`): a vertical painted beam under every raised splitter/merger and
  under raised belts about every 8 m, never through a belt, machine, container or sign;
- a foundation floor, and the most compact plot: `build_best` tries tight row and manifold
  spacings first and keeps the smallest layout with zero problems (production lines don't use
  the four building sizes).

`python -I .claude/skills/satisfactory-blueprints/scripts/factory.py "Motor" 2 [--use "..."] [--name "..."]`
prints a report: rows, raw inputs, outputs, size, power, warnings, `collisions` (belts passing
too close), `lane_conflicts` (a lane forced to stay low across another's turn-in) and
`belt_problems` (too short, too steep, doubling back). The generator retries lane layouts until
all of these are zero; anything left over, say where it is.

Belts must be built the way the game builds its own, or placement goes wrong. A zero-length or
folded belt can't be built: the game drops it, which cuts the line, and its broken collision
pushes the player into the air. So `belt_path` makes one belt per run with several spline
points, a straight 1 m lead out of every connector, corners rounded into arcs, tangents sized as
the game does (half the segment on straights, 4·r·tan(θ/4) on arcs), at most 35° and ~50 m per
belt. Drops from raised manifolds into machines go level, ramp, level (`feeder`).

**Factory rules: the player's standing requirements for every line** (also in the project
skill's "Factory rules"):
1. **Exact output, default recipes.** Build exactly the rate asked for (500 Circuit Boards/min
   means 500 out), with each item's default recipe unless the player names an alternate.
2. **Belts sized to the flow.** Each belt is the lowest tier that carries its rate (Mk.1 60,
   Mk.2 120, Mk.3 270, Mk.4 480, Mk.5 780, Mk.6 1200 /min). Nothing runs above 1200/min: larger
   flows split into parallel belts and rows.
3. **Inputs as full Mk.6 belts.** Plan each raw input as belts of up to 1200/min, one item per
   belt, split into the machines in an orderly, even way.
4. **A buffer on every input, followed by a label sign.** Each factory input enters a buffer:
   a storage container for belts, a fluid buffer for pipes (crude oil, water...). The player's
   supply belt or pipe feeds it, it feeds the line, and a label sign at its inlet names the item
   and the rate to supply. Fluids are inputs too: never leave a machine's pipe port unconnected.
5. **Few poles.** One pole powers several machines (up to its connection limit), chained
   efficiently, with one free connection for the player's grid.
6. **Smallest footprint.** Factories don't use the size presets; the plot fits the most compact
   layout that has zero belt problems.
7. **Labelled workflow.** A Label Sign (2 m × 1 m) beside every belt connection that matters:
   each factory input (item and the rate to supply), each machine input and output, and each
   product output, reading e.g. "IRON ORE 450/min".
8. **Nothing floats.** Every piece above the floor stands on something: raised splitters and
   mergers on a vertical beam to the floor, overhead belts on beam posts about every 8 m, signs
   on a beam post beside their belt. Posts never pass through a belt below. Buildings too: no
   hanging pieces without a visible support.

Tell the player plainly what isn't done yet: **byproducts fed back into the line** (leftovers go
to storage), **pumps** (pipe lanes stay low, but long fluid runs may need a pump in game), and
**packaging** of leftover fluids.
Machine ports and power points come from `library/ports.json`, learned from belts, pipes and
power lines plugged into machines in a real 1.2 save (`build_library.py --save`). Ports never
seen plugged in are mirrored from a sibling and marked `inferred`; machines with no known power
point (Particle Accelerator, Quantum Encoder) are listed in the warnings. The first in-game test
of a generated line should be a small one (e.g. 30 Iron Plate).

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
- It listens on this PC only (127.0.0.1) and only writes inside `.local/blueprints/<build>/`,
  the game's blueprint folders, and new save files next to the player's saves (World map).
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
- **Machines and logistics** come with empty ports and no power, as if freshly placed, unless the
  build links them (the factory generator does; so can a building's own lights). Links are
  data on both sides: belts and pipes in `mConnectedComponent` on both connectors; a power line
  carries its two connections after its properties, and each connection lists its wires in
  `mWires`. Anything added to a piece goes **before** the `None` that ends its property list
  (`add_prop` in `build_library.py`); the game stops reading there, so a link written after it
  is silently lost. The power line in the library is a template with both ends blank:
  `factory.Factory.make_wires` shows how to fill one in.

## Building straight into a save (World map)

For builds too big for a blueprint (designer limits, or the game freezing while it places a big
hologram), put them into a copy of the player's save instead. Open
`http://localhost:8770/map`: it lists their game-1.2 saves, draws everything in the chosen one
(the player in cyan), and lets them pick a build, drop it, move it by compass steps, turn it,
see how many existing pieces it overlaps, and **Put in a copy of my save**. Or call
`world.World(sav).add_blueprint(...)` + `write(next_free_save(...))` yourself.
- Only **structural pieces** go in (everything `lightweight` in `assets.json`). They are added
  to the game's own compact list, as if built by hand. Machines, belts, doors, lights and
  other separate objects are skipped and listed: say so.
- **The ground** comes from the game's own files, not the save: `tools/terrain` reads every
  landscape tile (2,289 tiles of 128 × 128 points, 1 m apart) into `.local/terrain/data`
  (`heights.bin` + `tiles.json`; game data, never committed). The map shows it at 4 m and swaps
  in 1 m detail near the view. **Cliffs and rocks** come from the game's own simplified
  far-view models (`WPHLOD_Landscape` layer, 518 areas of 256 m, ~1.1 M triangles, `rocks.bin`):
  complete but blocky, so edges can be a few metres off. **Water** is the top faces of the 270
  `FGWaterVolume`s (lakes, rivers, ocean; `water.json`), exact heights (lake at your base:
  −16.75 m, matching the water extractors). A dropped build lands on ground, rock or water under
  the mouse, and the overlap line also warns when cliffs or rocks reach into its space.
  **Trees, boulders, plants and other placed models** (`objects.bin/json`): every model 3 m or
  bigger (grass, flowers, waterfalls, fog and flat water/field planes skipped), 275 models,
  ~763,000 copies, each model at its most detailed level within ~600 (trees) / 400 triangles
  (levels of ≤ 12 triangles are flat cards and skipped). Copies load per 500 m area within
  ~800 m of the view; models over 300 m (background mountains, canyon backdrops) always show.
  Switches: Trees, Boulders, Other objects on; Bushes & plants off (70 % of copies). Trees the
  player cleared are hidden using the save's `FGFoliageRemovalSubsystem` (`World.removed_foliage`).
  Satisfactory's own foliage component `FGFoliageInstancedSMC` must be registered as a
  `UFoliageInstancedStaticMeshComponent` in CUE4Parse, or none of its ~3 M copies are read.
- Extracting the ground (once per game update; ~40 s). It needs the .NET 10 SDK in
  `.local/dotnet` (Microsoft's zip from builds.dotnet.microsoft.com, SHA-512 checked against the
  release metadata, unzipped; ask the player before downloading, ~300 MB) and the CUE4Parse
  NuGet package (ask too). Oodle is decoded by the managed `OodleSharp` that comes with it, so
  no Oodle DLL is needed. Satisfactory 1.2 runs on **Unreal 5.6**, and the shipped
  `FactoryGame.usmap` doesn't parse with CUE4Parse but isn't needed (the packages are versioned):
  ```
  set DOTNET_ROOT=.local\dotnet
  .local\dotnet\dotnet build -c Release .claude/skills/satisfactory-blueprints/tools/terrain
  set TERRAIN_USMAP=0
  .local\terrain\bin\Release\net10.0\terrain.exe extract "<game dir>" managed .local/terrain/data
  .local\terrain\bin\Release\net10.0\terrain.exe hlod    "<game dir>" managed .local/terrain/data
  .local\terrain\bin\Release\net10.0\terrain.exe water   "<game dir>" managed .local/terrain/data
  .local\terrain\bin\Release\net10.0\terrain.exe objects "<game dir>" managed .local/terrain/data
  ```
  Each tile's world position comes from its own section (`RootComponent` + (SectionBase −
  LandscapeSectionOffset) × scale), not the parent Landscape actor. **A cell can hold two
  sections, and texture names (`Heightmap_0`…) repeat in each**: match a tile's height texture
  by full path and take the transform from the tile's own section (`comp.Outer`), or tiles get
  another section's heights (it showed as dark strips on the map). Check after extracting:
  every neighbouring tile edge should match (4,463 of 4,465 do). Height 0 marks a hole in the
  ground (sinkholes, cave mouths, filled by cliff models in game); the map draws it as a dark floor. Heights: world z = base +
  (h − 32768) / 128 × scale z. Restart the studio afterwards.
- Then they load the new save from the game's **Load Game** menu (same session). Their
  original save is never changed. Saves from before game 1.2 must be loaded and saved once in
  1.2 first.
- After changing `world.py`, run `world.py roundtrip` on every 1.2 save: each must come back
  byte-identical (19 saves on the maintainer's PC).

## The player's game files

`%LOCALAPPDATA%\FactoryGame\Saved\SaveGames\blueprints\<save session>\`. Never modify or delete
a player's existing blueprints or saves (world.py only writes new save files next to them and
refuses to overwrite). Read them only if the player asks, e.g. to look at or remix one of
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
  - keeps power lines as a template with both ends blank (a wire needs two ends to be placed);
  - with `--save`, learns machine port positions and power-line attach points into
    `ports.json` for the factory generator.
  New object ids keep the original digit count, because references also sit inside longer
  strings whose stored sizes must not change. `sav.py` documents the save layout.
- Confirm 🧪 pieces in game with `examples/piece_test.py`, which writes four test blueprints
  with one of every ready piece. Place them in a sandbox save and record broken pieces. A
  confirmed piece can be promoted by building it in game and re-running `build_library.py` on
  the blueprint.
- After a game update, regenerate the full piece list from the game's modding data:
  `scripts/build_assets.py "<game>/CommunityResources/Docs/en-US.json"`. It writes
  `assets.json` and `ASSETS.md` with names and numbers only, no description text.
- Still missing from the library (see ASSETS.md): some hypertube
  pieces, and pieces not in the maintainer's world yet: Biomass Burner, Nuclear Power Plant, Power Tower, Priority
  Merger/Power Switch, Pipeline T-Junction, Street Light, Flood Light Tower, Buffer Stop, Fluid
  Truck Station, landing/jump pads, and unique buildings (HUB, Space Elevator, MAM, designers).
  Building one of each in a 1.2 world and re-running `build_library.py --save` adds them.
- Not yet supported: drawing belt/pipe splines in the studio preview, exact game meshes (the
  World map uses the game's simplified models), objects inside blueprint actors whose model is
  set only in the blueprint's construction script, and writing
  machines/belts/doors (non-lightweight pieces) into a save.

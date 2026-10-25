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
  what to build (photo/idea), roughly how big, colours/materials, and which save to put it in.
  List their saves with `sessions()` from `sbp.py` and offer the most recent.
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
| `  library/` | **Building-piece library**: `donors-v<NN>.sbp` sample pieces per game version, `index.json`, `items.json` (cost items) |
| `  library/CATALOG.md` | Every piece you can build with: category, versions, whether it takes any colour |
| `  studio/` | **Blueprint Studio**: local three.js app (`server.py` + `index.html`) to view, edit and install builds |
| `  examples/heydar_aliyev_center.py` | Worked example: a famous building traced from a photo |
| `  references/format.md` | Byte-level format, piece sizes and origins, designer limits |
| `  scripts/build_library.py` | Maintainer tool that regenerates `library/` from a folder of blueprints |
| `.local/blueprints/<name>/` | The player's builds: `build.py`, the `.sbp`/`.sbpcfg`, reference images. **Gitignored** |
| `out/` | Scratch output (previews, test saves). Gitignored |

The project skill is self-contained (scripts, library, viewer) so it can also be installed on its
own. Keep anything it needs inside its folder.

## Building a blueprint

1. **Choose pieces from the library** (`library/CATALOG.md`). Painted beams make curves and
   surfaces at any angle and length. Thin window walls make framed glass. Foundations make floors
   and plazas. Walls, roofs, ramps and quarter pipes make conventional buildings. Prefer pieces
   marked "any colour" when colour matters.
2. **Write a generator** at `.local/blueprints/<kebab-name>/build.py`, modelled on
   `examples/heydar_aliyev_center.py`:
   `lib = Library.load(needs=[...], custom_paint=...)`, `bp = lib.new_blueprint(dims)`,
   `bp.add_copy(lib.donor(type), lib.bp, pos_cm, quat)`, `set_float(o, 'mLength', cm)`,
   `set_color(o, rgba)`, then `bp.recipes = lib.recipes_for(...)`, `bp.cost = [(item(...), n)]`,
   `bp.save(...)`, `write_sbpcfg(...)`. Everything in one blueprint comes from one library version,
   which `Library.load` guarantees.
3. **Check it yourself first.** Open it in the studio (next section), and use
   `setView('front')` / `setCamera(pos, target)` from the browser's JavaScript tool to screenshot
   it against the reference. Fix what's off before showing the player.
4. **Show the player the studio** at `http://localhost:8770/?build=<folder>`.
5. **Install** when they ask: the studio's **Use in game** button, or `install(sbp, session)`.
   Both refuse to overwrite. On a name clash pick a new name, or ask before replacing an earlier
   version of the same build.

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
- **`dims`** (8 m units) must cover the pieces: x and y in ±dims·400 cm, z in 0…dims_z·800 cm.
  Vanilla designers are Mk1 4×4×4, Mk2 5×5×5, Mk3 6×6×6. Bigger works for placing, but can't be
  reopened in a designer: tell the player.
- **Header**: recipes for every piece type, and an estimated cost (painted beam ≈ 1 Steel Beam
  per 4 m; thin window wall 2 Silica + ~6 Steel Beam; 1 m concrete foundation ≈ 5 Concrete).
- **Machines and logistics**: the library only holds samples that link to nothing else, so
  machines come without belts or power, and most belts, pipes and power lines are missing (the
  catalogue shows the few unconnected ones). The player wires things up in game.

## The player's game files

`%LOCALAPPDATA%\FactoryGame\Saved\SaveGames\blueprints\<save session>\`. Never modify or delete
a player's existing blueprints. Read them only if the player asks, e.g. to look at or remix one of
their own designs (`sbp.py info/render/dump`, `catalog` for the pieces they contain).

## Maintaining this repo

- After changing `sbp.py`, round-trip a large set of real blueprints and confirm every file is
  byte-identical (`roundtrip` command; the maintainer's set is 442 files, object versions 36–60).
- To grow the library, run `scripts/build_library.py "<folder of blueprints>"` over blueprints
  that contain the new pieces, check `CATALOG.md`, and commit `library/`. It keeps only samples
  that link to nothing outside themselves, and it records no file names.
- Not yet supported: belts/pipes/power lines in the library, drawing splines in the preview,
  exact game meshes in the preview.

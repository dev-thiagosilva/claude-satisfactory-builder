# Claude Satisfactory Builder

Turn a photo, a sketch or an idea into a **Satisfactory blueprint** you can place in your game.
You chat with Claude; Claude designs the building, shows it to you in 3D, lets you tweak it, and
puts it in your save. No programming needed.

> Example: from a single photo of the Heydar Aliyev Center in Baku, Claude produced a
> 4,127-piece blueprint (white curved shell, glass façade, plaza) ready to place in game.

## What you need

- **Satisfactory** (1.0 or newer) on a Windows PC.
- **Claude running on your computer**: the [Claude desktop app](https://claude.ai/download)'s
  **Code** tab, or Claude Code. Claude needs to work on your PC to save blueprints into your game.
- Claude sets up anything else it needs, like Python, and asks you first.

## Install (one time)

1. Download [`install/satisfactory-builder/SKILL.md`](install/satisfactory-builder/SKILL.md).
2. Add it to Claude as a skill:
   - **Claude desktop app / claude.ai:** Settings → Capabilities → Skills → upload the file,
     zipped in a folder named `satisfactory-builder`, if it asks for a zip.
   - **Claude Code:** put it at `%USERPROFILE%\.claude\skills\satisfactory-builder\SKILL.md`.
3. That's it. The first time you ask for a building, Claude downloads this project to
   `%USERPROFILE%\claude-satisfactory-builder` and keeps it up to date.

## Use it

Just ask, for example:

- *"Build this in Satisfactory"* + drop a photo
- *"Make me a glass dome greenhouse, about 40 m wide, white frame"*
- *"A train station roof like this sketch"* + a drawing

Pick a size, or let Claude use **medium**:

| Size | Plot (foundations) | About |
|---|---|---|
| Small | 6 × 6 | 48 m across, up to 48 m tall |
| **Medium** (default) | 10 × 10 | 80 m across, up to 80 m tall |
| Large | 20 × 20 | 160 m across, up to 160 m tall |
| Extra-large | 40 × 40 | 320 m across, up to 320 m tall |

Bigger builds use many more pieces and cost much more to build in game.

Claude will:

1. Ask a few quick questions (size, colours, which save it's for).
2. Design it from the game's real building pieces: beams, foundations, walls, glass and more
   (see the [piece catalogue](.claude/skills/satisfactory-blueprints/library/CATALOG.md)).
3. Open the **Blueprint Studio** in your browser at `http://localhost:8770`, where you can
   orbit around your building and change it: click pieces to select them, then move, rotate,
   duplicate, delete or recolour them. Undo works, and every save keeps the previous version.
4. When you're happy, press **Use in game** (or ask Claude) to put it in your save.

Then in Satisfactory: **reload your save**, open the build menu, and find it in the
**Blueprints** tab. Claude tells you which AWESOME Shop unlocks it needs and roughly what it costs.

## Good to know

- The 3D preview uses simple shapes, not the game's exact models, and the cost is an estimate.
- Only **small** matches an in-game blueprint designer (Mk3). Medium and bigger can be placed
  normally, but can't be reopened in a designer.
- Your own blueprints are never changed or overwritten. Claude's builds live in
  `claude-satisfactory-builder\.local\blueprints` until you install them.
- Machines come without belts, pipes or power attached. Hook those up in game.

## For contributors

See [`CLAUDE.md`](CLAUDE.md) for how the project works. The tooling lives in
[`.claude/skills/satisfactory-blueprints`](.claude/skills/satisfactory-blueprints/SKILL.md):

- a reader/writer for `.sbp` (tested byte-for-byte on 442 real blueprints, game versions
  Update 8 to 1.2)
- the piece library
- the Blueprint Studio
- a worked example

Licensed under the terms in [LICENSE](LICENSE). Satisfactory is a trademark of Coffee Stain
Studios; this is a fan project and isn't affiliated with them.

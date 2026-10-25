---
name: satisfactory-builder
description: Design and build Satisfactory buildings for the user as ready-to-place blueprints, from a photo, a famous building, a sketch or just an idea, with a 3D preview before anything touches the game. Use this whenever the user wants to make, design, recreate or build something in Satisfactory, mentions Satisfactory blueprints or the blueprint designer, or shares a picture and asks for it "in Satisfactory", even if they don't say "blueprint". The user does not need to know anything about programming.
---

# Satisfactory builder (installer)

This skill is a small launcher. The real tools, building-piece library and instructions live in
the **claude-satisfactory-builder** repository. Get it onto this computer, move into it, and
follow its `CLAUDE.md`. Do all of that yourself: the user may never have used a terminal, so
don't ask them to run commands, and keep any setup talk to one short line.

## 1. Get or update the workspace

Workspace folder: `claude-satisfactory-builder` in the user's home folder
(`%USERPROFILE%\claude-satisfactory-builder` on Windows, `~/claude-satisfactory-builder` elsewhere).

- **Folder exists and is a git checkout:** run `git -C <folder> pull --ff-only` to get updates.
  If that fails because of local changes, leave it as is and carry on: their `.local/` work is
  never tracked, so this is rare. Mention it only if it matters.
- **Folder missing, git available:**
  `git clone https://github.com/dev-thiagosilva/claude-satisfactory-builder.git <folder>`
- **Folder missing, no git:** download
  `https://github.com/dev-thiagosilva/claude-satisfactory-builder/archive/refs/heads/master.zip`
  and extract it to `<folder>`. On Windows:
  `Invoke-WebRequest <url> -OutFile $env:TEMP\csb.zip; Expand-Archive $env:TEMP\csb.zip $env:TEMP\csb -Force; Move-Item $env:TEMP\csb\claude-satisfactory-builder-master <folder>`.
  Without git there are no automatic updates. Download again later to update, keeping `.local/`.

## 2. Check what's needed

- **Python 3.9+** (`python --version`, or `py -3 --version` on Windows). If it's missing, tell the
  user in one sentence that a free tool called Python is needed, and with their OK install it
  (`winget install -e --id Python.Python.3.12` on Windows, the package manager elsewhere). Nothing
  else needs installing.
- **The game's blueprint folder**
  (`%LOCALAPPDATA%\FactoryGame\Saved\SaveGames\blueprints\` on Windows). If it doesn't exist,
  the game hasn't been run on this PC, or it saves elsewhere. You can still build and preview,
  and install later.

## 3. Hand over

Move the session into the workspace folder (in the Claude app use its change-directory tool;
in a terminal, work from that folder), then read `<folder>/CLAUDE.md` and follow it from there.
It covers how to talk with the user, the building workflow, the project skill
`satisfactory-blueprints`, and the piece library.

This needs Claude running on the user's own computer (the Claude desktop app's Code tab or
Claude Code), because it reads and writes files in the game's folder. In a chat with no access
to their computer, say so plainly and point them to the README in the repository.

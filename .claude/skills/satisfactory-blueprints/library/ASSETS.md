# Every buildable piece in Satisfactory

Generated from the game's own modding data (`CommunityResources/Docs/en-US.json`) by
`scripts/build_assets.py`; machine-readable copy in `assets.json`.

**546 pieces** in the game. **479 are ready** (152 from real builds, 327 made from similar pieces):
the donor library has a sample, so Claude can place them in a blueprint today.

- **Ready**: ✅ = sample taken from a real build; 🧪 = sample made from a similar piece of the
  same kind (should work, not yet confirmed in game); 🎨 = also takes any colour;
  ⛔ legacy = no build recipe in the current game (old or event pieces).
  Versions are blueprint object versions (36 = Update 8, 42–46 = 1.0, 52–60 = 1.1/1.2).
- **Class**: the name used in code (`Build_<Class>_C` in the game).
- **Cost**: what the build gun charges. Beams and similar pieces cost per length.
- **Unlock**: the milestone, AWESOME Shop pack or MAM research that unlocks the piece.

## Quick picker

| I want… | Use |
|---|---|
| A flat floor, plaza or platform | Foundation_Concrete_8x1, Foundation_ConcretePolished_8x1 |
| A glass floor or skylight | FoundationGlass_01 |
| A slope, ramp or tiered seating | Ramp_Concrete_8x1 / 8x2 / 8x4, RampDouble_* |
| A rounded 90° edge | QuarterPipeMiddle_* (curves up), DownQuarterPipe_* (curves down), *InCorner/*OutCorner |
| Free-form curves, organic shapes, outlines, lattices | Beam_Painted (any length/angle/colour), laid side by side |
| A solid wall | Wall_Concrete_8x4, SteelWall_8x4, Wall_8x4_01 (Ficsit orange) |
| A triangle (gable) or diagonal wall | *_Tris_*, *_FlipTris_*, *_Angular_* |
| A glass wall / curtain wall | Wall_Window_Thin_8x4_01 (any colour) |
| A wall with windows | Wall_Concrete_8x4_Window_01…04, SteelWall_8x4_Window_* |
| A pitched roof | Roof_Metal_01…03 + In/OutCorner; glass: Roof_Window_* |
| A flat roof | Roof_A_01, or foundations |
| Columns | PillarMiddle_Concrete, Pillar_Small_* |
| A door or garage door | Wall_Door_8x4_01, Gate_Automated_8x4, BigGarageDoor_16x8 |
| Walkways and stairs | CatwalkStraight/Stairs, WalkwayStraight, Stairs_Left_01 |
| Railings, fences, road barriers | Railing_01, Fence_01, Barrier_Low_01 |
| Lights | CeilingLight, StreetLight, FloodlightWall |
| A label or sign | StandaloneWidgetSign_* |
| A factory floor | Production machines + Belts, lifts & sorting (player connects them in game) |

Combine materials from one family for a consistent look (e.g. concrete walls + polished
concrete floors + concrete pillars). Use painted beams wherever a shape doesn't fit the 8 m
grid.

## Contents

**Building design**

- [Floors & foundations](#floors--foundations): 19 pieces, 19 ready
- [Ramps, slopes & rounded edges](#ramps-slopes--rounded-edges): 182 pieces, 179 ready
- [Glass & windows](#glass--windows): 27 pieces, 27 ready
- [Doors & gates](#doors--gates): 13 pieces, 13 ready
- [Roofs](#roofs): 30 pieces, 30 ready
- [Walls & facades](#walls--facades): 51 pieces, 24 ready
- [Beams, pillars & structure](#beams-pillars--structure): 20 pieces, 19 ready
- [Walkways, stairs, railings & fences](#walkways-stairs-railings--fences): 42 pieces, 37 ready
- [Lights, signs & decoration](#lights-signs--decoration): 24 pieces, 18 ready

**Factory & logistics**

- [Production machines](#production-machines): 11 pieces, 11 ready
- [Extraction](#extraction): 7 pieces, 7 ready
- [Power](#power): 21 pieces, 14 ready
- [Belts, lifts & sorting](#belts-lifts--sorting): 34 pieces, 33 ready
- [Pipes & fluids](#pipes--fluids): 16 pieces, 15 ready
- [Hypertubes](#hypertubes): 9 pieces, 5 ready
- [Trains, vehicles & drones](#trains-vehicles--drones): 18 pieces, 15 ready
- [Storage](#storage): 6 pieces, 5 ready
- [Special & unique buildings](#special--unique-buildings): 16 pieces, 8 ready

## Floors & foundations

**Use for:** Ground, floors, plazas, platforms and slabs between storeys.

**Tips:** 8 × 8 m grid, 1/2/4 m thick. Materials: concrete, polished concrete (light, smooth), asphalt (dark, roads), metal/grip, Ficsit (orange). Glass foundations make glass floors and skylights; frame foundations are see-through.

**Go-to pieces:** Foundation (1 m) (`Foundation_Concrete_8x1`), Foundation (1 m) (`Foundation_ConcretePolished_8x1`), Glass Frame Foundation (`FoundationGlass_01`), Frame Foundation (`Foundation_Frame_01`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅🎨 60 | Conveyor Lift Floor Hole | `FoundationPassthrough_Lift` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Conveyor Lift Floor Hole |
| 🧪🎨 60 | Foundation (1 m) | `Foundation_8x1_01` | 8 × 8 × 1 m | 5 Concrete | Tier 1: Base Building |
| ✅🎨 60 | Foundation (1 m) | `Foundation_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| ✅🎨 60 | Foundation (1 m) | `Foundation_ConcretePolished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| ✅🎨 60 | Foundation (1 m) | `Foundation_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| ✅🎨 60 | Foundation (1 m) | `Foundation_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation (2 m) | `Foundation_8x2_01` | 8 × 8 × 2 m | 5 Concrete | Tier 1: Base Building |
| 🧪🎨 60 | Foundation (2 m) | `Foundation_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| ✅ 60 | Foundation (2 m) | `Foundation_ConcretePolished_8x2_2` | 8 × 8 × 2 m |  |  |
| ✅🎨 60 | Foundation (2 m) | `Foundation_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| ✅🎨 60 | Foundation (2 m) | `Foundation_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation (4 m) | `Foundation_8x4_01` | 8 × 8 × 4 m | 5 Concrete | Tier 1: Base Building |
| ✅🎨 60 | Foundation (4 m) | `Foundation_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| ✅🎨 60 | Foundation (4 m) | `Foundation_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| ✅🎨 60 | Foundation (4 m) | `Foundation_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation (4 m) | `Foundation_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| ✅🎨 60 | Frame Floor | `Flat_Frame_01` | 8 × 8 × 0.4 m | 2 Steel Beam | AWESOME Shop: Structural Frame Set |
| ✅🎨 60 | Frame Foundation | `Foundation_Frame_01` | 8 × 8 × 4 m | 5 Steel Beam | AWESOME Shop: Structural Frame Set |
| ✅🎨 60 | Glass Frame Foundation | `FoundationGlass_01` | 8 × 8 × 1 m | 2 Steel Beam, 5 Concrete | AWESOME Shop: Structural Frame Set |

## Ramps, slopes & rounded edges

**Use for:** Slopes, sloped roofs and tiers, and rounded 90° edges between a floor and a wall (quarter pipes).

**Tips:** Ramp 8x1/8x2/8x4 rise 1/2/4 m over 8 m; double ramps rise 2× over 16 m; inverted ramps slope the underside. Quarter pipes curve up (QuarterPipe) or down (DownQuarterPipe); In/OutCorner pieces round the corners.

**Go-to pieces:** Ramp (2 m) (`Ramp_Concrete_8x2`), Half Foundation (4 m) (`QuarterPipeMiddle_Concrete_8x4`), Inverted Quarter Pipe (`DownQuarterPipe_Concrete_8x4`), Inverted Ramp (2 m) (`InvertedRamp_Concrete_8x2`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| 🧪🎨 60 | Double Ramp (2 m) | `RampDouble_8x1` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Double Ramp Set |
| 🧪🎨 60 | Double Ramp (2 m) | `RampDouble_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (2 m) | `RampDouble_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (2 m) | `RampDouble_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (2 m) | `RampDouble_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (4 m) | `RampDouble` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Double Ramp Set |
| 🧪🎨 60 | Double Ramp (4 m) | `RampDouble_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (4 m) | `RampDouble_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (4 m) | `RampDouble_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (4 m) | `RampDouble_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (8 m) | `RampDouble_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (8 m) | `RampDouble_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (8 m) | `RampDouble_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (8 m) | `RampDouble_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Double Ramp (8 m) | `Ramp_8x8x8` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Double Ramp Set |
| 🧪🎨 60 | Down Corner Ramp (1 m) | `Ramp_Diagonal_8x1_01` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
| 🧪🎨 60 | Down Corner Ramp (1 m) | `Ramp_DownCorner_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Down Corner Ramp (1 m) | `Ramp_DownCorner_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Down Corner Ramp (1 m) | `Ramp_DownCorner_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Down Corner Ramp (1 m) | `Ramp_DownCorner_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Down Corner Ramp (2 m) | `Ramp_Diagonal_8x2_01` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
| 🧪🎨 60 | Down Corner Ramp (2 m) | `Ramp_DownCorner_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Down Corner Ramp (2 m) | `Ramp_DownCorner_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Down Corner Ramp (2 m) | `Ramp_DownCorner_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Down Corner Ramp (2 m) | `Ramp_DownCorner_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Down Corner Ramp (4 m) | `Ramp_Diagonal_8x4_01` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
| 🧪🎨 60 | Down Corner Ramp (4 m) | `Ramp_DownCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Down Corner Ramp (4 m) | `Ramp_DownCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Down Corner Ramp (4 m) | `Ramp_DownCorner_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Down Corner Ramp (4 m) | `Ramp_DownCorner_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Frame Ramp | `Ramp_Frame_01` | 8 × 8 × 4 m | 5 Steel Beam | AWESOME Shop: Structural Frame Set |
| 🧪🎨 60 | Half Foundation (1 m) | `QuarterPipeMiddle_Asphalt_8x1` | 8 × 4 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Half Foundation (1 m) | `QuarterPipeMiddle_Concrete_8x1` | 8 × 4 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Half Foundation (1 m) | `QuarterPipeMiddle_Grip_8x1` | 8 × 4 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Half Foundation (1 m) | `QuarterPipeMiddle_PolishedConcrete_8x1` | 8 × 4 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Half Foundation (2 m) | `QuarterPipeMiddle_Asphalt_8x2` | 8 × 4 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Half Foundation (2 m) | `QuarterPipeMiddle_Concrete_8x2` | 8 × 4 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Half Foundation (2 m) | `QuarterPipeMiddle_Grip_8x2` | 8 × 4 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Half Foundation (2 m) | `QuarterPipeMiddle_PolishedConcrete_8x2` | 8 × 4 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Half Foundation (4 m) | `QuarterPipeMiddle_Asphalt_8x4` | 8 × 4 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Half Foundation (4 m) | `QuarterPipeMiddle_Concrete_8x4` | 8 × 4 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Half Foundation (4 m) | `QuarterPipeMiddle_Grip_8x4` | 8 × 4 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Half Foundation (4 m) | `QuarterPipeMiddle_PolishedConcrete_8x4` | 8 × 4 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (1 m) | `QuarterPipeMiddleInCorner_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (1 m) | `QuarterPipeMiddleInCorner_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (1 m) | `QuarterPipeMiddleInCorner_Ficsit_8x1` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
| 🧪🎨 60 | Inner Corner Extension (1 m) | `QuarterPipeMiddleInCorner_Grip_8x1` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (1 m) | `QuarterPipeMiddleInCorner_PolishedConcrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (2 m) | `QuarterPipeMiddleInCorner_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (2 m) | `QuarterPipeMiddleInCorner_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (2 m) | `QuarterPipeMiddleInCorner_Ficsit_8x2` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
| 🧪🎨 60 | Inner Corner Extension (2 m) | `QuarterPipeMiddleInCorner_Grip_8x2` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (2 m) | `QuarterPipeMiddleInCorner_PolishedConcrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (4 m) | `QuarterPipeMiddleInCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (4 m) | `QuarterPipeMiddleInCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (4 m) | `QuarterPipeMiddleInCorner_Ficsit_8x4` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
| 🧪🎨 60 | Inner Corner Extension (4 m) | `QuarterPipeMiddleInCorner_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Extension (4 m) | `QuarterPipeMiddleInCorner_PolishedConcrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Quarter Pipe | `QuarterPipeCorner_01` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipes Pack |
| 🧪🎨 60 | Inner Corner Quarter Pipe | `QuarterPipeInCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Quarter Pipe | `QuarterPipeInCorner_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Quarter Pipe | `QuarterPipeInCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inner Corner Quarter Pipe | `QuarterPipeInCorner_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (1 m) | `InvertedRamp_DCorner_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (1 m) | `InvertedRamp_DCorner_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (1 m) | `InvertedRamp_DCorner_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (1 m) | `InvertedRamp_DCorner_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (1 m) | `RampInverted_8x1_Corner_02` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Inverted Corner Ramp Pack |
| 🧪🎨 60 | Inverted Down Corner (2 m) | `InvertedRamp_DCorner_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (2 m) | `InvertedRamp_DCorner_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (2 m) | `InvertedRamp_DCorner_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (2 m) | `InvertedRamp_DCorner_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (2 m) | `RampInverted_8x2_Corner_02` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Inverted Corner Ramp Pack |
| 🧪🎨 60 | Inverted Down Corner (4 m) | `InvertedRamp_DCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (4 m) | `InvertedRamp_DCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (4 m) | `InvertedRamp_DCorner_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (4 m) | `InvertedRamp_DCorner_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Down Corner (4 m) | `RampInverted_8x4_Corner_02` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Inverted Corner Ramp Pack |
| ✅🎨 60 | Inverted Frame Ramp | `Ramp_Frame_Inverted_01` | 8 × 8 × 4 m | 5 Steel Beam | AWESOME Shop: Structural Frame Set |
| 🧪🎨 60 | Inverted Inner Corner Quarter Pipe | `DownQuarterPipeInCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Inner Corner Quarter Pipe | `DownQuarterPipeInCorner_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Inner Corner Quarter Pipe | `DownQuarterPipeInCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Inner Corner Quarter Pipe | `DownQuarterPipeInCorner_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Inner Corner Quarter Pipe | `QuarterPipeCorner_02` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipes Pack |
| 🧪🎨 60 | Inverted Outer Corner Quarter Pipe | `DownQuarterPipeOutCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Outer Corner Quarter Pipe | `DownQuarterPipeOutCorner_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Outer Corner Quarter Pipe | `DownQuarterPipeOutCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Outer Corner Quarter Pipe | `DownQuarterPipeOutCorner_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Outer Corner Quarter Pipe | `QuarterPipeCorner_04` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipes Pack |
| 🧪🎨 60 | Inverted Quarter Pipe | `DownQuarterPipe_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Quarter Pipe | `DownQuarterPipe_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Quarter Pipe | `DownQuarterPipe_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Quarter Pipe | `DownQuarterPipe_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Quarter Pipe | `QuarterPipe_02` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipes Pack |
| 🧪🎨 60 | Inverted Ramp (1 m) | `InvertedRamp_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (1 m) | `InvertedRamp_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (1 m) | `InvertedRamp_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (1 m) | `InvertedRamp_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (1 m) | `RampInverted_8x1` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Inverted Ramp Set |
| 🧪🎨 60 | Inverted Ramp (2 m) | `InvertedRamp_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (2 m) | `InvertedRamp_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (2 m) | `InvertedRamp_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (2 m) | `InvertedRamp_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (2 m) | `RampInverted_8x2_01` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Inverted Ramp Set |
| 🧪🎨 60 | Inverted Ramp (4 m) | `InvertedRamp_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (4 m) | `InvertedRamp_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (4 m) | `InvertedRamp_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (4 m) | `InvertedRamp_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp (4 m) | `Ramp_8x4_Inverted_01` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Inverted Ramp Set |
| 🧪🎨 60 | Inverted Up Corner (1 m) | `InvertedRamp_UCorner_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (1 m) | `InvertedRamp_UCorner_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (1 m) | `InvertedRamp_UCorner_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (1 m) | `InvertedRamp_UCorner_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (1 m) | `RampInverted_8x1_Corner_01` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Inverted Corner Ramp Pack |
| 🧪🎨 60 | Inverted Up Corner (2 m) | `InvertedRamp_UCorner_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (2 m) | `InvertedRamp_UCorner_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (2 m) | `InvertedRamp_UCorner_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (2 m) | `InvertedRamp_UCorner_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (2 m) | `RampInverted_8x2_Corner_01` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Inverted Corner Ramp Pack |
| 🧪🎨 60 | Inverted Up Corner (4 m) | `InvertedRamp_UCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (4 m) | `InvertedRamp_UCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (4 m) | `InvertedRamp_UCorner_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (4 m) | `InvertedRamp_UCorner_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Inverted Up Corner (4 m) | `RampInverted_8x4_Corner_01` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Inverted Corner Ramp Pack |
| 🧪🎨 60 | Outer Corner Extension (1 m) | `QuarterPipeMiddleOutCorner_Asphalt_4x1` | 4 × 4 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Extension (1 m) | `QuarterPipeMiddleOutCorner_Concrete_4x1` | 4 × 4 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Extension (1 m) | `QuarterPipeMiddleOutCorner_Ficsit_4x1` | 4 × 4 × 1 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
| 🧪🎨 60 | Outer Corner Extension (1 m) | `QuarterPipeMiddleOutCorner_Grip_4x1` | 4 × 4 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Extension (1 m) | `QuarterPipeMiddleOutCorner_PolishedConcrete_4x1` | 4 × 4 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Extension (2 m) | `QuarterPipeMiddleOutCorner_Asphalt_4x2` | 4 × 4 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Extension (2 m) | `QuarterPipeMiddleOutCorner_Concrete_4x2` | 4 × 4 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Extension (2 m) | `QuarterPipeMiddleOutCorner_Ficsit_4x2` | 4 × 4 × 2 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
| 🧪🎨 60 | Outer Corner Extension (2 m) | `QuarterPipeMiddleOutCorner_Grip_4x2` | 4 × 4 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Extension (2 m) | `QuarterPipeMiddleOutCorner_PolishedConcrete_4x2` | 4 × 4 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Extension (4 m) | `QuarterPipeMiddleOutCorner_Asphalt_4x4` | 4 × 4 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Extension (4 m) | `QuarterPipeMiddleOutCorner_Concrete_4x4` | 4 × 4 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Extension (4 m) | `QuarterPipeMiddleOutCorner_Ficsit_4x4` | 4 × 4 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
| 🧪🎨 60 | Outer Corner Extension (4 m) | `QuarterPipeMiddleOutCorner_Grip_4x4` | 4 × 4 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Extension (4 m) | `QuarterPipeMiddleOutCorner_PolishedConcrete_4x4` | 4 × 4 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Quarter Pipe | `QuarterPipeCorner_03` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipes Pack |
| 🧪🎨 60 | Outer Corner Quarter Pipe | `QuarterPipeOutCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Quarter Pipe | `QuarterPipeOutCorner_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Quarter Pipe | `QuarterPipeOutCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Outer Corner Quarter Pipe | `QuarterPipeOutCorner_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Quarter Pipe | `QuarterPipe` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipes Pack |
| 🧪🎨 60 | Quarter Pipe | `QuarterPipe_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Quarter Pipe | `QuarterPipe_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Quarter Pipe | `QuarterPipe_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Quarter Pipe | `QuarterPipe_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Ramp (1 m) | `Ramp_8x1_01` | 8 × 8 × 1 m | 5 Concrete | Tier 1: Base Building |
| 🧪🎨 60 | Ramp (1 m) | `Ramp_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Ramp (1 m) | `Ramp_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Ramp (1 m) | `Ramp_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Ramp (1 m) | `Ramp_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Ramp (2 m) | `Ramp_8x2_01` | 8 × 8 × 2 m | 5 Concrete | Tier 1: Base Building |
| 🧪🎨 60 | Ramp (2 m) | `Ramp_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Ramp (2 m) | `Ramp_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Ramp (2 m) | `Ramp_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Ramp (2 m) | `Ramp_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Ramp (4 m) | `Ramp_8x4_01` | 8 × 8 × 4 m | 5 Concrete | Tier 1: Base Building |
| 🧪🎨 60 | Ramp (4 m) | `Ramp_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| ✅🎨 60 | Ramp (4 m) | `Ramp_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Ramp (4 m) | `Ramp_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Ramp (4 m) | `Ramp_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Up Corner Ramp (1 m) | `Ramp_Diagonal_8x1_02` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
| 🧪🎨 60 | Up Corner Ramp (1 m) | `Ramp_UpCorner_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Up Corner Ramp (1 m) | `Ramp_UpCorner_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Up Corner Ramp (1 m) | `Ramp_UpCorner_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Up Corner Ramp (1 m) | `Ramp_UpCorner_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Up Corner Ramp (2 m) | `Ramp_Diagonal_8x2_02` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
| 🧪🎨 60 | Up Corner Ramp (2 m) | `Ramp_UpCorner_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Up Corner Ramp (2 m) | `Ramp_UpCorner_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Up Corner Ramp (2 m) | `Ramp_UpCorner_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Up Corner Ramp (2 m) | `Ramp_UpCorner_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Up Corner Ramp (4 m) | `Ramp_Diagonal_8x4_02` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
| 🧪🎨 60 | Up Corner Ramp (4 m) | `Ramp_UpCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| ✅🎨 60 | Up Corner Ramp (4 m) | `Ramp_UpCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Up Corner Ramp (4 m) | `Ramp_UpCorner_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Up Corner Ramp (4 m) | `Ramp_UpCorner_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| ⛔ legacy | Half Foundation (1 m) | `QuarterPipeMiddle_Ficsit_8x1` | 8 × 4 × 1 m |  |  |
| ⛔ legacy | Half Foundation (2 m) | `QuarterPipeMiddle_Ficsit_8x2` | 8 × 4 × 2 m |  |  |
| ⛔ legacy | Half Foundation (4 m) | `QuarterPipeMiddle_Ficsit_8x4` | 8 × 4 × 4 m |  |  |

## Glass & windows

**Use for:** Curtain walls, shop fronts, greenhouses, glass roofs.

**Tips:** Full Frame Window (Wall_Window_Thin_8x4_01) is the cleanest glass wall: a fine mullion grid that takes any colour. Wall_*_Window_0X are solid walls with window openings. Roof_Window_* are glass roofs.

**Go-to pieces:** Full Frame Window (`Wall_Window_Thin_8x4_01`), Panel Window (`Wall_Window_8x4_03`), Single Window (`Wall_Concrete_8x4_Window_01`), Flat Roof (`Roof_Window_01`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| 🧪🎨 60 | Angled Frame Window | `Wall_Window_8x4_05` |  | 2 Silica, 2 Steel Beam | AWESOME Shop: Steel-Framed Windows |
| ✅🎨 60 | Flat Roof | `Roof_Window_01` | 8 × 8 × 0 m | 3 Concrete | Start |
| 🧪🎨 60 | Frame Window | `SteelWall_8x4_Window_03` |  | 2 Silica | Start |
| 🧪🎨 60 | Frame Window | `Wall_Concrete_8x4_Window_02` |  | 2 Silica | Start |
| 🧪🎨 60 | Frame Window | `Wall_Window_8x4_02` |  | 2 Silica | AWESOME Shop: Windowed Walls |
| ✅🎨 60 | Full Frame Window | `Wall_Window_Thin_8x4_01` |  | 2 Silica, 2 Steel Beam | AWESOME Shop: Steel-Framed Windows |
| ✅🎨 60 | Hex Frame Window | `Wall_Window_Thin_8x4_02` |  | 2 Silica, 2 Steel Beam | AWESOME Shop: Steel-Framed Windows |
| 🧪🎨 60 | Honeycomb Frame Window | `Wall_Window_8x4_06` |  | 2 Silica, 2 Steel Beam | AWESOME Shop: Steel-Framed Windows |
| 🧪🎨 60 | Inner Corner Roof (1 m) | `Roof_Window_InCorner_01` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Inner Corner Roof (2 m) | `Roof_Window_InCorner_02` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Inner Corner Roof (4 m) | `Roof_Window_InCorner_03` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Outer Corner Roof (1 m) | `Roof_Window_OutCorner_01` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Outer Corner Roof (2 m) | `Roof_Window_OutCorner_02` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Outer Corner Roof (4 m) | `Roof_Window_OutCorner_03` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Panel Window | `SteelWall_8x4_Window_04` |  | 2 Silica | Start |
| 🧪🎨 60 | Panel Window | `Wall_Concrete_8x4_Window_03` |  | 2 Silica | Start |
| 🧪🎨 60 | Panel Window | `Wall_Window_8x4_03` |  | 2 Silica | AWESOME Shop: Windowed Walls |
| 🧪🎨 60 | Reinforced Window | `SteelWall_8x4_Window_02` |  | 2 Silica | Start |
| 🧪🎨 60 | Reinforced Window | `Wall_Concrete_8x4_Window_04` |  | 2 Silica | Start |
| 🧪🎨 60 | Reinforced Window | `Wall_Window_8x4_04` |  | 2 Silica | AWESOME Shop: Windowed Walls |
| 🧪🎨 60 | Roof (1 m) | `Roof_Window_02` | 8 × 8 × 1 m | 3 Concrete | Start |
| 🧪🎨 60 | Roof (2 m) | `Roof_Window_03` | 8 × 8 × 2 m | 3 Concrete | Start |
| 🧪🎨 60 | Roof (4 m) | `Roof_Window_04` | 8 × 8 × 4 m | 3 Concrete | Start |
| 🧪🎨 60 | Single Window | `SteelWall_8x4_Window_01` |  | 2 Silica | Start |
| 🧪🎨 60 | Single Window | `Wall_Concrete_8x4_Window_01` |  | 2 Silica | Start |
| 🧪🎨 60 | Single Window | `Wall_Window_8x4_01` |  | 2 Silica | AWESOME Shop: Windowed Walls |
| 🧪🎨 60 | Triple Frame Window | `Wall_Window_8x4_07` |  | 2 Silica, 2 Steel Beam | AWESOME Shop: Steel-Framed Windows |

## Doors & gates

**Use for:** Entrances: personnel doors, automatic gates, big garage doors for vehicles.

**Tips:** Doors fill a standard 8 × 4 m wall slot; garage doors are 16 × 8 m.

**Go-to pieces:** Center Door Wall (`Wall_Door_8x4_01`), Automated Gate (`Gate_Automated_8x4`), Roll-Up Gate (`BigGarageDoor_16x8`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅🎨 60 | Automated Gate | `Gate_Automated_8x4` |  | 6 Iron Plate | AWESOME Shop: Gates |
| 🧪🎨 60 | Center Door Wall | `Wall_Concrete_CDoor_8x4` |  | 2 Concrete | Start |
| ✅🎨 60 | Center Door Wall | `Wall_Door_8x4_01` |  | 2 Concrete | AWESOME Shop: Door Walls |
| 🧪🎨 60 | Center Door Wall | `Wall_Door_8x4_01_Steel` |  | 2 Concrete | Start |
| 🧪🎨 60 | Gate Hole Wall | `SteelWall_8x4_Gate_01` |  | 2 Concrete | Start |
| 🧪🎨 60 | Gate Hole Wall | `Wall_Concrete_Gate_8x4` |  | 2 Concrete | Start |
| 🧪🎨 60 | Gate Hole Wall | `Wall_Gate_8x4_01` |  | 2 Concrete | AWESOME Shop: Gates |
| ✅🎨 60 | Roll-Up Gate | `BigGarageDoor_16x8` |  | 4 Concrete, 4 Iron Plate | AWESOME Shop: Gates |
| 🧪🎨 60 | Roll-Up Gate | `BigGarageDoor_16x8_Concrete` |  | 8 Concrete | Start |
| 🧪🎨 60 | Roll-Up Gate | `BigGarageDoor_16x8_Steel` |  | 4 Concrete, 4 Steel Beam | Start |
| 🧪🎨 60 | Side Door Wall | `Wall_Concrete_SDoor_8x4` |  | 2 Concrete | Start |
| ✅🎨 60 | Side Door Wall | `Wall_Door_8x4_03` |  | 2 Concrete | AWESOME Shop: Door Walls |
| 🧪🎨 60 | Side Door Wall | `Wall_Door_8x4_03_Steel` |  | 2 Concrete | Start |

## Roofs

**Use for:** Pitched and flat roofs.

**Tips:** _01/_02/_03 are three pitches; In/OutCorner pieces turn corners. Materials: metal, orange (Ficsit), tar, glass (Roof_Window).

**Go-to pieces:** Flat Roof (`Roof_A_01`), Flat Roof (`Roof_Window_01`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅🎨 60 | Flat Roof | `Roof_A_01` | 8 × 8 × 0 m | 3 Concrete | Start |
| 🧪🎨 60 | Flat Roof | `Roof_Orange_01` | 8 × 8 × 0 m | 3 Concrete | AWESOME Shop: FICSIT Roofs |
| 🧪🎨 60 | Flat Roof | `Roof_Tar_01` | 8 × 8 × 0 m | 3 Concrete | Start |
| 🧪🎨 60 | Inner Corner Roof (1 m) | `Roof_Metal_InCorner_01` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Inner Corner Roof (1 m) | `Roof_Orange_InCorner_01` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
| 🧪🎨 60 | Inner Corner Roof (1 m) | `Roof_Tar_InCorner_01` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Inner Corner Roof (2 m) | `Roof_Metal_InCorner_02` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Inner Corner Roof (2 m) | `Roof_Orange_InCorner_02` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
| 🧪🎨 60 | Inner Corner Roof (2 m) | `Roof_Tar_InCorner_02` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Inner Corner Roof (4 m) | `Roof_Metal_InCorner_03` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Inner Corner Roof (4 m) | `Roof_Orange_InCorner_03` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
| 🧪🎨 60 | Inner Corner Roof (4 m) | `Roof_Tar_InCorner_03` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Outer Corner Roof (1 m) | `Roof_Metal_OutCorner_01` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Outer Corner Roof (1 m) | `Roof_Orange_OutCorner_01` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
| 🧪🎨 60 | Outer Corner Roof (1 m) | `Roof_Tar_OutCorner_01` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Outer Corner Roof (2 m) | `Roof_Metal_OutCorner_02` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Outer Corner Roof (2 m) | `Roof_Orange_OutCorner_02` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
| 🧪🎨 60 | Outer Corner Roof (2 m) | `Roof_Tar_OutCorner_02` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Outer Corner Roof (4 m) | `Roof_Metal_OutCorner_03` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Outer Corner Roof (4 m) | `Roof_Orange_OutCorner_03` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
| 🧪🎨 60 | Outer Corner Roof (4 m) | `Roof_Tar_OutCorner_03` | 8 m | 3 Concrete | Start |
| 🧪🎨 60 | Roof (1 m) | `Roof_A_02` | 8 × 8 × 1 m | 3 Concrete | Start |
| 🧪🎨 60 | Roof (1 m) | `Roof_Orange_02` | 8 × 8 × 1 m | 3 Concrete | AWESOME Shop: FICSIT Roofs |
| 🧪🎨 60 | Roof (1 m) | `Roof_Tar_02` | 8 × 8 × 1 m | 3 Concrete | Start |
| 🧪🎨 60 | Roof (2 m) | `Roof_A_03` | 8 × 8 × 2 m | 3 Concrete | Start |
| 🧪🎨 60 | Roof (2 m) | `Roof_Orange_03` | 8 × 8 × 2 m | 3 Concrete | AWESOME Shop: FICSIT Roofs |
| 🧪🎨 60 | Roof (2 m) | `Roof_Tar_03` | 8 × 8 × 2 m | 3 Concrete | Start |
| 🧪🎨 60 | Roof (4 m) | `Roof_A_04` | 8 × 8 × 4 m | 3 Concrete | Start |
| 🧪🎨 60 | Roof (4 m) | `Roof_Orange_04` | 8 × 8 × 4 m | 3 Concrete | AWESOME Shop: FICSIT Roofs |
| 🧪🎨 60 | Roof (4 m) | `Roof_Tar_04` | 8 × 8 × 4 m | 3 Concrete | Start |

## Walls & facades

**Use for:** Building envelopes and facades.

**Tips:** 8 × 4 m (or 8 × 1 m strips). Tris/FlipTris are triangles for gables, Angular are diagonals, Corner pieces turn 90°. Materials: concrete, steel, orange (Ficsit, Wall_8x4_01).

**Go-to pieces:** Basic Wall (4 m) (`Wall_Concrete_8x4`), Tilted Wall (4 m) (`SteelWall_8x4`) – not ready yet, Basic Wall (4 m) (`Wall_8x4_01`), Ramp Wall (4 m) (`Wall_Concrete_Tris_8x4`) – not ready yet

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅🎨 60 | Basic Wall (1 m) | `SteelWall_8x1` |  | 2 Concrete | Start |
| ✅🎨 60 | Basic Wall (1 m) | `Wall_Concrete_8x1` |  | 2 Concrete | Start |
| ✅🎨 60 | Basic Wall (1 m) | `Wall_Orange_8x1` |  | 2 Concrete | Tier 1: Base Building |
| ✅🎨 60 | Basic Wall (4 m) | `Wall_8x4_01` |  | 2 Concrete | Tier 1: Base Building |
| ✅🎨 60 | Basic Wall (4 m) | `Wall_8x4_02` |  | 2 Concrete | Start |
| ✅🎨 60 | Basic Wall (4 m) | `Wall_Concrete_8x4` |  | 2 Concrete | Start |
| ✅🎨 60 | Frame Wall | `Wall_Frame_01` |  | 2 Steel Beam | AWESOME Shop: Structural Frame Set |
| 🧪🎨 60 | Inverted Ramp Wall (1 m) | `SteelWall_FlipTris_8x1` |  | 2 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp Wall (2 m) | `SteelWall_FlipTris_8x2` |  | 2 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp Wall (4 m) | `SteelWall_FlipTris_8x4` |  | 2 Concrete | Start |
| 🧪🎨 60 | Inverted Ramp Wall (8 m) | `SteelWall_FlipTris_8x8` |  | 2 Concrete | Start |
| 🧪🎨 60 | Ramp Wall (1 m) | `SteelWall_Tris_8x1` |  | 2 Concrete | Start |
| 🧪🎨 60 | Ramp Wall (2 m) | `SteelWall_Tris_8x2` |  | 2 Concrete | Start |
| 🧪🎨 60 | Ramp Wall (4 m) | `SteelWall_Tris_8x4` |  | 2 Concrete | Start |
| 🧪🎨 60 | Ramp Wall (8 m) | `SteelWall_Tris_8x8` |  | 2 Concrete | Start |
| 🧪🎨 60 | Tilted Corner Wall (4 m) | `Wall_Orange_8x4_Corner_01` | 8 m | 2 Concrete | AWESOME Shop: Tilted Walls |
| 🧪🎨 60 | Tilted Corner Wall (8 m) | `Wall_Orange_8x8_Corner_01` | 8 m | 2 Concrete | AWESOME Shop: Tilted Walls |
| 🧪🎨 60 | Tilted Wall (4 m) | `WallSet_Steel_Angular_8x4` |  | 2 Concrete | Start |
| 🧪🎨 60 | Tilted Wall (4 m) | `Wall_Concrete_Angular_8x4` |  | 2 Concrete | Start |
| 🧪🎨 60 | Tilted Wall (4 m) | `Wall_Orange_Angular_8x4` |  | 2 Concrete | AWESOME Shop: Tilted Walls |
| 🧪🎨 60 | Tilted Wall (8 m) | `WallSet_Steel_Angular_8x8` |  | 2 Concrete | Start |
| 🧪🎨 60 | Tilted Wall (8 m) | `Wall_Concrete_Angular_8x8` |  | 2 Concrete | Start |
| 🧪🎨 60 | Tilted Wall (8 m) | `Wall_Orange_Angular_8x8` |  | 2 Concrete | AWESOME Shop: Tilted Walls |
| ✅ 60 | Wall-Mounted Flood Light | `FloodlightWall` |  | 25 Quickwire, 4 Copper Sheet, 2 Encased Industrial Beam | AWESOME Shop: Flood Lights |
| ⛔ legacy | Inverted Ramp Wall (1 m) | `Wall_Concrete_FlipTris_8x1` |  |  |  |
| ⛔ legacy | Inverted Ramp Wall (1 m) | `Wall_Orange_FlipTris_8x1` |  |  |  |
| ⛔ legacy | Inverted Ramp Wall (2 m) | `Wall_Concrete_FlipTris_8x2` |  |  |  |
| ⛔ legacy | Inverted Ramp Wall (2 m) | `Wall_Orange_FlipTris_8x2` |  |  |  |
| ⛔ legacy | Inverted Ramp Wall (4 m) | `Wall_Concrete_FlipTris_8x4` |  |  |  |
| ⛔ legacy | Inverted Ramp Wall (4 m) | `Wall_Orange_FlipTris_8x4` |  |  |  |
| ⛔ legacy | Inverted Ramp Wall (8 m) | `Wall_Concrete_FlipTris_8x8` |  |  |  |
| ⛔ legacy | Inverted Ramp Wall (8 m) | `Wall_Orange_FlipTris_8x8` |  |  |  |
| ⛔ legacy | Ramp Wall (1 m) | `Wall_Concrete_Tris_8x1` |  |  |  |
| ⛔ legacy | Ramp Wall (1 m) | `Wall_Orange_Tris_8x1` |  |  |  |
| ⛔ legacy | Ramp Wall (2 m) | `Wall_Concrete_Tris_8x2` |  |  |  |
| ⛔ legacy | Ramp Wall (2 m) | `Wall_Orange_Tris_8x2` |  |  |  |
| ⛔ legacy | Ramp Wall (4 m) | `Wall_Concrete_Tris_8x4` |  |  |  |
| ⛔ legacy | Ramp Wall (4 m) | `Wall_Orange_Tris_8x4` |  |  |  |
| ⛔ legacy | Ramp Wall (8 m) | `Wall_Concrete_Tris_8x8` |  |  |  |
| ⛔ legacy | Ramp Wall (8 m) | `Wall_Orange_Tris_8x8` |  |  |  |
|  | Tilted Concave Wall (4 m) | `Wall_Concrete_8x4_Corner_2` | 8 m | 2 Concrete | Start |
|  | Tilted Concave Wall (4 m) | `Wall_Orange_8x4_Corner_02` | 8 m | 2 Concrete | AWESOME Shop: Tilted Walls |
|  | Tilted Concave Wall (4 m) | `Wall_Steel_8x4_Corner_2` | 8 m | 2 Concrete | Start |
|  | Tilted Concave Wall (8 m) | `Wall_Concrete_8x8_Corner_2` | 8 m | 2 Concrete | Start |
|  | Tilted Concave Wall (8 m) | `Wall_Orange_8x8_Corner_02` | 8 m | 2 Concrete | AWESOME Shop: Tilted Walls |
|  | Tilted Concave Wall (8 m) | `Wall_Steel_8x8_Corner_2` | 8 m | 2 Concrete | Start |
|  | Tilted Corner Wall (4 m) | `Wall_Concrete_8x4_Corner_01` | 8 m | 2 Concrete | Start |
|  | Tilted Corner Wall (4 m) | `Wall_Steel_8x4_Corner_01` | 8 m | 2 Concrete | Start |
|  | Tilted Corner Wall (8 m) | `Wall_Concrete_8x8_Corner_01` | 8 m | 2 Concrete | Start |
|  | Tilted Corner Wall (8 m) | `Wall_Steel_8x8_Corner_01` | 8 m | 2 Concrete | Start |
| ⛔ legacy | Tilted Wall (4 m) | `SteelWall_8x4` |  |  |  |

## Beams, pillars & structure

**Use for:** Frames, columns, trusses, outlines, and free-form curves.

**Tips:** Painted Beam is the most flexible piece in the game: any length (up to 40 m), any angle, any colour. Lay beams side by side to make smooth curved surfaces (see the Heydar example). Pillars make columns; connectors and supports join beams.

**Go-to pieces:** Painted Beam (`Beam_Painted`), Metal Beam (`Beam`), Big Concrete Pillar (`PillarMiddle_Concrete`), Small Concrete Pillar (`Pillar_Small_Concrete`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅🎨 60 | Beam Connector | `Beam_Connector` |  | 2 Concrete | AWESOME Shop: Structural Cable Pack |
| ✅🎨 60 | Beam Support | `Beam_Support` |  | 2 Concrete | AWESOME Shop: Structural Cable Pack |
| ✅🎨 60 | Big Concrete Pillar | `PillarMiddle_Concrete` |  | 5 Concrete | AWESOME Shop: Concrete Pillar Set |
| 🧪🎨 60 | Big Frame Pillar | `PillarMiddle_Frame` |  | 5 Steel Beam | AWESOME Shop: Frame Pillar Set |
| 🧪🎨 60 | Big Metal Pillar | `PillarMiddle` |  | 2 Iron Plate, 3 Concrete | AWESOME Shop: Metal Pillar Set |
| ✅🎨 60 | Big Pillar Support | `PillarBase` |  | 5 Concrete | AWESOME Shop: Metal Pillar Set |
| 🧪🎨 60 | Braided Cable | `Beam_Cable` | length 1–40 m | 1 Steel Beam per 4 m | AWESOME Shop: Structural Cable Pack |
| 🧪🎨 60 | Braided Cable Cluster | `Beam_Cable_Cluster` | length 1–40 m | 1 Steel Beam per 4 m | AWESOME Shop: Structural Cable Pack |
| 🧪🎨 60 | Cross Beam | `Beam_Cross` | length 1–40 m | 1 Steel Beam per 4 m | AWESOME Shop: Beam Expansion Pack |
| ✅🎨 60 | Double Beam Connector | `Beam_Connector_Double` |  | 2 Concrete | AWESOME Shop: Structural Cable Pack |
| 🧪🎨 60 | H-Beam | `Beam_H` | length 1–40 m | 1 Steel Beam per 4 m | AWESOME Shop: Beam Expansion Pack |
| 🧪🎨 60 | Metal Beam | `Beam` | length 4–40 m | 1 Steel Beam per 4 m | AWESOME Shop: Structural Beam Pack |
| 🧪🎨 60 | Painted Beam | `Beam_Painted` | length 4–40 m | 1 Steel Beam per 4 m | AWESOME Shop: Structural Beam Pack |
| 🧪🎨 60 | Round Concrete Beam | `Beam_Concrete` | length 1–40 m | 1 Concrete per 4 m | AWESOME Shop: Beam Expansion Pack |
| 🧪🎨 60 | Shelf Beam | `Beam_Shelf` | length 1–40 m | 1 Steel Beam per 4 m | AWESOME Shop: Beam Expansion Pack |
| ✅🎨 60 | Small Concrete Pillar | `Pillar_Small_Concrete` |  | 3 Concrete | AWESOME Shop: Concrete Pillar Set |
| 🧪🎨 60 | Small Frame Pillar | `Pillar_Small_Frame` |  | 3 Steel Beam | AWESOME Shop: Frame Pillar Set |
| ✅🎨 60 | Small Metal Pillar | `Pillar_Small_Metal` |  | 1 Iron Plate, 2 Concrete | AWESOME Shop: Metal Pillar Set |
| 🧪🎨 60 | Small Pillar Support | `PillarBase_Small` |  | 3 Concrete | AWESOME Shop: Metal Pillar Set |
| ⛔ legacy | Pillar Top | `PillarTop` |  |  |  |

## Walkways, stairs, railings & fences

**Use for:** Getting around and edging: walkways, catwalks, stairs, ladders, elevators, railings, fences, barriers.

**Tips:** Catwalks are 4 m wide with railings; walkways are open. Stair_* are foundation-sized stairs (8 × 8 m, rising 1/2/4 m) that match the foundation materials. Barriers and fences line roads and plazas.

**Go-to pieces:** Straight Catwalk (`CatwalkStraight`), Straight Walkway (`WalkwayStraight`), Stairs Left (`Stairs_Left_01`), Modern Railing (`Railing_01`), Low Barrier (`Barrier_Low_01`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| 🧪🎨 60 | Catwalk Intersection | `CatwalkCross` | 4 m | 2 Iron Rod, 1 Iron Plate | AWESOME Shop: Modern Catwalks |
| 🧪🎨 60 | Catwalk Ramp | `CatwalkRamp` | 4 m | 2 Iron Rod, 1 Iron Plate | AWESOME Shop: Modern Catwalks |
| 🧪🎨 60 | Catwalk Stairs | `CatwalkStairs` | 4 m | 2 Iron Rod, 1 Iron Plate | AWESOME Shop: Modern Catwalks |
| 🧪🎨 60 | Catwalk T-Junction | `CatwalkT` | 4 m | 2 Iron Rod, 1 Iron Plate | AWESOME Shop: Modern Catwalks |
| 🧪🎨 60 | Construction Fence | `ChainLinkFence` |  | 2 Iron Rod | AWESOME Shop: Construction Fences |
| 🧪🎨 60 | Corner Road Barrier | `Barrier_Corner` |  | 1 Concrete | AWESOME Shop: Road Barriers |
| ✅ 60 | Elevator Floor Stop | `ElevatorFloorStop` |  | 2 Modular Frame, 1 Motor, 5 Steel Beam | AWESOME Shop: Personnel Elevator |
| 🧪🎨 60 | Foundation Stairs (1 m) | `Stair_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation Stairs (1 m) | `Stair_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation Stairs (1 m) | `Stair_FicsitSet_8x1_01` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Foundation Stairs Set |
| 🧪🎨 60 | Foundation Stairs (1 m) | `Stair_GripMetal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation Stairs (1 m) | `Stair_PolishedConcrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation Stairs (2 m) | `Stair_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation Stairs (2 m) | `Stair_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation Stairs (2 m) | `Stair_FicsitSet_8x2_01` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Foundation Stairs Set |
| 🧪🎨 60 | Foundation Stairs (2 m) | `Stair_GripMetal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation Stairs (2 m) | `Stair_PolishedConcrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation Stairs (4 m) | `Stair_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation Stairs (4 m) | `Stair_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation Stairs (4 m) | `Stair_FicsitSet_8x4_01` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Foundation Stairs Set |
| 🧪🎨 60 | Foundation Stairs (4 m) | `Stair_GripMetal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | Foundation Stairs (4 m) | `Stair_PolishedConcrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| 🧪🎨 60 | High Barrier | `Barrier_Tall_01` |  | 1 Concrete, 1 Iron Plate | AWESOME Shop: Metal Barriers |
| 🧪🎨 60 | Industrial Railing | `Fence_01` |  | 4 Iron Rod | Start |
| ✅🎨 60 | Ladder | `Ladder` |  | 2 Iron Rod | AWESOME Shop: Factory Ladder |
| 🧪🎨 60 | Low Barrier | `Barrier_Low_01` |  | 1 Concrete, 1 Iron Plate | AWESOME Shop: Metal Barriers |
| 🧪🎨 60 | Modern Railing | `Railing_01` |  | 2 Iron Rod | AWESOME Shop: Modern Railing |
| ✅ 60 | Personnel Elevator | `Elevator` |  | 1 Steel Beam, 1 Silica | AWESOME Shop: Personnel Elevator |
| 🧪🎨 60 | Road Barrier | `Concrete_Barrier_01` |  | 2 Concrete | AWESOME Shop: Road Barriers |
| 🧪🎨 60 | Stairs Left | `Stairs_Left_01` | 8 m | 3 Concrete, 3 Iron Plate | Start |
| 🧪🎨 60 | Stairs Right | `Stairs_Right_01` | 8 m | 3 Concrete, 3 Iron Plate | Start |
| 🧪🎨 60 | Straight Catwalk | `CatwalkStraight` | 4 m | 2 Iron Rod, 1 Iron Plate | AWESOME Shop: Modern Catwalks |
| 🧪🎨 60 | Straight Walkway | `WalkwayStraight` | 4 m | 2 Iron Rod, 1 Iron Plate | Start |
| 🧪🎨 60 | Tarp Construction Fence | `TarpFence` |  | 2 Iron Rod | AWESOME Shop: Construction Fences |
| 🧪🎨 60 | Walkway Intersection | `WalkwayCross` | 4 m | 2 Iron Rod, 1 Iron Plate | Start |
| 🧪🎨 60 | Walkway Ramp | `WalkwayRamp` | 4 m | 2 Iron Rod, 1 Iron Plate | Start |
| 🧪🎨 60 | Walkway T-Junction | `WalkwayT` | 4 m | 2 Iron Rod, 1 Iron Plate | Start |
| ⛔ legacy | Catwalk Corner | `CatwalkCorner` | 4 m |  |  |
|  | Jump Pad | `JumpPadAdjustable` |  | 2 Rotor, 15 Iron Plate, 10 Cable | Tier 2: Jump Pads |
| ⛔ legacy | Old Jump Pad | `JumpPad` |  |  |  |
| ⛔ legacy | Old Tilted Jump Pad | `JumpPadTilted` |  |  |  |
| ⛔ legacy | Walkway Corner | `WalkwayTrun` | 4 m |  |  |

## Lights, signs & decoration

**Use for:** Lighting, labels and decoration.

**Tips:** Signs show "Set Text Here" until the player edits them in game. Lights need power.

**Go-to pieces:** Ceiling Light (`CeilingLight`), Street Light (`StreetLight`) – not ready yet, Wall-Mounted Flood Light (`FloodlightWall`), Display Sign (`StandaloneWidgetSign_Medium`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 60 | Ceiling Light | `CeilingLight` |  | 50 Quickwire, 16 Wire, 6 Steel Beam | AWESOME Shop: Indoor Lighting |
| 🧪🎨 60 | Display Sign | `StandaloneWidgetSign_Medium` |  | 2 Reinforced Iron Plate, 5 Quartz Crystal | AWESOME Shop: Display Sign Bundle |
| 🧪🎨 60 | FICSMAS Candy Cane | `CandyCaneDecor` |  | 10 Candy Cane, 1 FICSMAS Bow | MAM: Candy Cane Decor |
| 🧪🎨 60 | FICSMAS Decoration | `WreathDecor` |  | 1 FICSMAS Wreath, 1 FICSMAS Bow | MAM: FICSMAS Decoration |
| 🧪🎨 60 | FICSMAS Snowman | `Snowman` |  | 50 FICSMAS Actual Snow, 3 Candy Cane, 1 FICSMAS Bow, 3 Red FICSMAS Ornament, 2 Blue FICSMAS Ornament | MAM: A Friend |
| 🧪🎨 60 | Label Sign (2 m) | `StandaloneWidgetSign_Small` |  | 2 Iron Plate, 2 Quartz Crystal | AWESOME Shop: Label Sign Bundle |
| 🧪🎨 60 | Label Sign (3 m) | `StandaloneWidgetSign_SmallWide` |  | 3 Iron Plate, 3 Quartz Crystal | AWESOME Shop: Label Sign Bundle |
| 🧪🎨 60 | Label Sign (4 m) | `StandaloneWidgetSign_SmallVeryWide` |  | 4 Iron Plate, 4 Quartz Crystal | AWESOME Shop: Label Sign Bundle |
| ✅🎨 60 | Large Billboard | `StandaloneWidgetSign_Huge` |  | 12 Encased Industrial Beam, 20 Copper Sheet, 5 Crystal Oscillator | AWESOME Shop: Billboard Set |
| ✅🎨 60 | Large Fan | `LargeFan` |  | 1 Iron Plate, 1 Copper Sheet | AWESOME Shop: Ventilation Bundle |
| 🧪🎨 60 | Large Vent | `LargeVent` |  | 1 Iron Plate, 1 Copper Sheet | AWESOME Shop: Ventilation Bundle |
| ✅ 60 | Light Control Panel | `LightsControlPanel` |  | 10 Cable, 5 Reinforced Iron Plate, 3 AI Limiter | AWESOME Shop: Light Control Panel |
| ✅ 60 | Lookout Tower | `LookoutTower` |  | 5 Iron Plate, 5 Iron Rod | Tier 1: Base Building |
| 🧪🎨 60 | Portrait Sign | `StandaloneWidgetSign_Portrait` |  | 4 Reinforced Iron Plate, 10 Quartz Crystal | AWESOME Shop: Display Sign Bundle |
| ✅🎨 60 | Small Billboard | `StandaloneWidgetSign_Large` |  | 3 Encased Industrial Beam, 4 Copper Sheet, 1 Crystal Oscillator | AWESOME Shop: Billboard Set |
| 🧪🎨 60 | Square Sign (0.5 m) | `StandaloneWidgetSign_Square_Tiny` |  | 1 Iron Plate, 1 Quartz Crystal | AWESOME Shop: Label Sign Bundle |
| ✅🎨 60 | Square Sign (1 m) | `StandaloneWidgetSign_Square_Small` |  | 1 Reinforced Iron Plate, 5 Quartz Crystal | AWESOME Shop: Display Sign Bundle |
| ✅🎨 60 | Square Sign (2 m) | `StandaloneWidgetSign_Square` |  | 3 Reinforced Iron Plate, 10 Quartz Crystal | AWESOME Shop: Display Sign Bundle |
|  | FICSMAS Gift Tree | `TreeGiftProducer` |  | 50 FICSMAS Gift, 100 FICSMAS Tree Branch, 30 Red FICSMAS Ornament, 30 Blue FICSMAS Ornament | MAM: FICSMAS Gift Tree |
|  | FICSMAS Snow Cannon | `SnowCannon` |  | 10 FICSMAS Bow, 100 FICSMAS Actual Snow, 20 Copper FICSMAS Ornament | MAM: It's Snowing! |
|  | FICSMAS Snow Dispenser | `SnowDispenser` |  | 10 Candy Cane, 100 FICSMAS Actual Snow, 20 Iron FICSMAS Ornament | MAM: It's Snowing! |
|  | Flood Light Tower | `FloodlightPole` |  | 25 Quickwire, 4 Copper Sheet, 8 Encased Industrial Beam | AWESOME Shop: Flood Lights |
| ⛔ legacy | Giant FICSMAS Tree | `XmassTree` |  |  |  |
|  | Street Light | `StreetLight` |  | 10 Quickwire, 4 Wire, 4 Iron Rod | AWESOME Shop: Street Light |

## Production machines

**Use for:** Factories: turning resources into parts.

**Tips:** Samples come with empty belt/pipe ports and no power. The player connects them in game. Leave clearance for belts on the input/output sides.

**Go-to pieces:** Constructor (`ConstructorMk1`), Assembler (`AssemblerMk1`), Smelter (`SmelterMk1`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅🎨 60 | Assembler | `AssemblerMk1` |  | 8 Reinforced Iron Plate, 4 Rotor, 10 Cable | Tier 2: Part Assembly |
| ✅ 60 | Blender | `Blender` |  | 10 Computer, 10 Heavy Modular Frame, 20 Motor, 50 Aluminum Casing | Tier 7: Control System Development |
| ✅ 60 | Constructor | `ConstructorMk1` |  | 2 Reinforced Iron Plate, 8 Cable | Onboarding: HUB Upgrade 3 |
| ✅🎨 60 | Converter | `Converter` |  | 10 Fused Modular Frame, 25 Cooling System, 50 Radio Control Unit, 100 SAM Fluctuator | Tier 9: Matter Conversion |
| ✅ 60 | Foundry | `FoundryMk1` |  | 10 Modular Frame, 10 Rotor, 20 Concrete | Tier 3: Basic Steel Production |
| ✅🎨 60 | Manufacturer | `ManufacturerMk1` |  | 10 Motor, 20 Modular Frame, 50 Plastic, 50 Cable | Tier 6: Industrial Manufacturing |
| ✅ 60 | Packager | `Packager` |  | 20 Steel Beam, 10 Rubber, 10 Plastic | Tier 5: Fluid Packaging |
| ✅ 60 | Particle Accelerator | `HadronCollider` |  | 10 Turbo Motor, 10 Supercomputer, 25 Fused Modular Frame, 50 Cooling System, 500 Quickwire | Tier 8: Particle Enrichment |
| ✅ 60 | Quantum Encoder | `QuantumEncoder` |  | 20 Turbo Motor, 20 Supercomputer, 50 Cooling System, 50 Time Crystal, 100 Ficsite Trigon | Tier 9: Quantum Encoding |
| ✅ 60 | Refinery | `OilRefinery` |  | 10 Motor, 10 Encased Industrial Beam, 30 Steel Pipe, 20 Copper Sheet | Tier 5: Oil Processing |
| ✅ 60 | Smelter | `SmelterMk1` |  | 5 Iron Rod, 8 Wire | Onboarding: HUB Upgrade 2 |

## Extraction

**Use for:** Mining and pumping resources.

**Tips:** Must sit on a resource node in game, so they rarely suit a free-standing blueprint.

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| 🧪🎨 60 | Miner Mk.1 | `MinerMk1` |  | 1 BP_ItemDescriptorPortableMiner, 10 Iron Plate, 10 Concrete | Onboarding: HUB Upgrade 5 |
| 🧪🎨 60 | Miner Mk.2 | `MinerMk2` |  | 2 BP_ItemDescriptorPortableMiner, 10 Encased Industrial Beam, 20 Steel Pipe, 10 Modular Frame | Tier 4: Advanced Steel Production |
| ✅ 60 | Miner Mk.3 | `MinerMk3` |  | 3 BP_ItemDescriptorPortableMiner, 50 Steel Pipe, 5 Supercomputer, 10 Fused Modular Frame, 3 Turbo Motor | Tier 8: Leading-Edge Production |
| ✅ 60 | Oil Extractor | `OilPump` |  | 15 Motor, 20 Encased Industrial Beam, 60 Cable | Tier 5: Oil Processing |
| ✅ 60 | Resource Well Extractor | `FrackingExtractor` |  | 10 Steel Beam, 10 Aluminum Casing | Tier 8: Advanced Aluminum Production |
| ✅ 60 | Resource Well Pressurizer | `FrackingSmasher` |  | 10 Radio Control Unit, 25 Heavy Modular Frame, 50 Motor, 50 Alclad Aluminum Sheet, 100 Rubber | Tier 8: Advanced Aluminum Production |
| ✅ 60 | Water Extractor | `WaterPump` |  | 20 Copper Sheet, 10 Reinforced Iron Plate, 10 Rotor | Tier 3: Coal Power |

## Power

**Use for:** Generating and distributing electricity.

**Tips:** Power lines need two ends, so the player draws them in game. Wall poles mount on walls; Mk2/Mk3 poles allow more connections.

**Go-to pieces:** Power Pole Mk.1 (`PowerPoleMk1`), Wall Outlet Mk.1 (`PowerPoleWall`), Power Storage (`PowerStorageMk1`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 60 | Coal-Powered Generator | `GeneratorCoal` |  | 20 Reinforced Iron Plate, 10 Rotor, 30 Cable | Tier 3: Coal Power |
| ✅ 60 | Double Wall Outlet Mk.1 | `PowerPoleWallDouble` |  | 8 Wire, 2 Iron Rod | AWESOME Shop: Wall Power Outlets Mk.1 |
| ✅ 60 | Double Wall Outlet Mk.3 | `PowerPoleWallDouble_Mk3` |  |  |  |
| ✅ 60 | Fuel-Powered Generator | `GeneratorFuel` |  | 15 Motor, 15 Encased Industrial Beam, 30 Copper Sheet, 50 Rubber, 50 Quickwire | Tier 5: Petroleum Power |
| ✅ 60 | Geothermal Generator | `GeneratorGeoThermal` |  | 10 Motor, 25 Modular Frame, 25 High-Speed Connector, 50 Copper Sheet, 250 Wire | MAM: Geothermal Generator |
| ✅ 60 | Power Pole Mk.1 | `PowerPoleMk1` |  | 3 Wire, 1 Iron Rod, 1 Concrete | Onboarding: HUB Upgrade 3 |
| ✅ 60 | Power Pole Mk.2 | `PowerPoleMk2` |  | 6 Quickwire, 2 Iron Rod, 2 Concrete | MAM: Power Poles Mk.2 |
| ✅ 60 | Power Pole Mk.3 | `PowerPoleMk3` |  | 2 High-Speed Connector, 2 Steel Pipe, 3 Rubber | MAM: Power Poles Mk.3 |
| ✅ 60 | Power Storage | `PowerStorageMk1` |  | 5 Encased Industrial Beam, 10 Modular Frame, 100 Wire | Tier 4: Expanded Power Infrastructure |
| ✅ 60 | Power Switch | `PowerSwitch` |  | 20 Quickwire, 4 Steel Beam, 1 AI Limiter | MAM: Power Switch |
| ✅ 60 | Power Tower Platform | `PowerTowerPlatform` |  | 10 Concrete, 20 Wire, 20 Steel Beam | Tier 4: Expanded Power Infrastructure |
| ✅ 60 | Wall Outlet Mk.1 | `PowerPoleWall` |  | 4 Wire, 1 Iron Rod | AWESOME Shop: Wall Power Outlets Mk.1 |
| ✅ 60 | Wall Outlet Mk.2 | `PowerPoleWall_Mk2` |  |  |  |
| ✅ 60 | Wall Outlet Mk.3 | `PowerPoleWall_Mk3` |  |  |  |
|  | Biomass Burner | `GeneratorBiomass_Automated` |  | 15 Iron Plate, 15 Iron Rod, 25 Wire | Onboarding: HUB Upgrade 6 |
| ⛔ legacy | Double Wall Outlet Mk.2 | `PowerPoleWallDouble_Mk2` |  |  |  |
| ⛔ legacy | FICSMAS Power Light | `XmassLightsLine` |  |  |  |
|  | Nuclear Power Plant | `GeneratorNuclear` |  | 10 Supercomputer, 25 Heavy Modular Frame, 100 Alclad Aluminum Sheet, 200 Cable, 250 Concrete | Tier 8: Nuclear Power |
|  | Power Line | `PowerLine` |  | 1 Cable per 25 m | Onboarding: HUB Upgrade 2 |
|  | Power Tower | `PowerTower` |  | 10 Concrete, 20 Wire, 20 Steel Beam | Tier 4: Expanded Power Infrastructure |
|  | Priority Power Switch | `PriorityPowerSwitch` |  | 2 High-Speed Connector, 6 Steel Beam, 50 Quickwire | MAM: Priority Power Switch |

## Belts, lifts & sorting

**Use for:** Moving items: belts, lifts, splitters/mergers, belt supports and wall/floor pass-throughs.

**Tips:** Belt and lift samples are short pieces with cut ends. Long runs are easier to draw in game. Mk number = speed tier.

**Go-to pieces:** Conveyor Splitter (`ConveyorAttachmentSplitter`), Conveyor Merger (`ConveyorAttachmentMerger`), Conveyor Pole (`ConveyorPole`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅🎨 60 | Conveyor Belt Mk.1 | `ConveyorBeltMk1` |  | 1 Iron Plate | Onboarding: HUB Upgrade 4 |
| ✅ 60 | Conveyor Belt Mk.2 | `ConveyorBeltMk2` |  | 1 Reinforced Iron Plate | Tier 2: Logistics Mk.2 |
| ✅🎨 60 | Conveyor Belt Mk.3 | `ConveyorBeltMk3` |  | 1 Steel Beam | Tier 4: Logistics Mk.3 |
| ✅ 60 | Conveyor Belt Mk.4 | `ConveyorBeltMk4` |  | 1 Encased Industrial Beam | Tier 5: Logistics Mk.4 |
| ✅ 60 | Conveyor Belt Mk.5 | `ConveyorBeltMk5` |  | 1 Alclad Aluminum Sheet | Tier 7: Logistics Mk.5 |
| ✅🎨 60 | Conveyor Belt Mk.6 | `ConveyorBeltMk6` |  | 1 Ficsite Trigon, 1 Time Crystal | Tier 9: Peak Efficiency |
| ✅ 60 | Conveyor Ceiling Mount | `ConveyorCeilingAttachment` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Conveyor Ceiling Mount |
| ✅🎨 60 | Conveyor Lift Mk.1 | `ConveyorLiftMk1` |  | 2 Iron Plate | Tier 1: Logistics |
| ✅ 60 | Conveyor Lift Mk.2 | `ConveyorLiftMk2` |  | 2 Reinforced Iron Plate | Tier 2: Logistics Mk.2 |
| ✅🎨 60 | Conveyor Lift Mk.3 | `ConveyorLiftMk3` |  | 2 Steel Beam | Tier 4: Logistics Mk.3 |
| ✅ 60 | Conveyor Lift Mk.4 | `ConveyorLiftMk4` |  | 2 Encased Industrial Beam | Tier 5: Logistics Mk.4 |
| ✅ 60 | Conveyor Lift Mk.5 | `ConveyorLiftMk5` |  | 2 Alclad Aluminum Sheet | Tier 7: Logistics Mk.5 |
| ✅🎨 60 | Conveyor Lift Mk.6 | `ConveyorLiftMk6` |  | 2 Ficsite Trigon, 2 Time Crystal | Tier 9: Peak Efficiency |
| ✅🎨 60 | Conveyor Merger | `ConveyorAttachmentMerger` |  | 2 Iron Plate, 2 Iron Rod | Tier 1: Logistics |
| ✅ 60 | Conveyor Pole | `ConveyorPole` |  | 1 Iron Rod, 1 Iron Plate, 1 Concrete | Onboarding: HUB Upgrade 4 |
| ✅🎨 60 | Conveyor Splitter | `ConveyorAttachmentSplitter` |  | 2 Iron Plate, 2 Cable | Tier 1: Logistics |
| ✅🎨 60 | Conveyor Throughput Monitor | `ConveyorMonitor` |  | 4 Reinforced Iron Plate, 10 Quartz Crystal, 1 Crystal Oscillator | AWESOME Shop: Conveyor Throughput Monitor |
| ✅ 60 | Conveyor Wall Hole | `ConveyorWallHole` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Conveyor Wall Hole |
| ✅ 60 | Conveyor Wall Mount | `ConveyorPoleWall` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Conveyor Wall Mount |
| ✅ 60 | Conveyor Wall x 1 | `Wall_Concrete_8x4_ConveyorHole_01` |  | 2 Concrete | Start |
| ✅ 60 | Conveyor Wall x 1 | `Wall_Conveyor_8x4_03` |  | 2 Concrete | AWESOME Shop: Conveyor Walls |
| ✅🎨 60 | Conveyor Wall x 1 | `Wall_Conveyor_8x4_03_Steel` |  | 2 Concrete | Start |
| ✅ 60 | Conveyor Wall x 2 | `Wall_Concrete_8x4_ConveyorHole_02` |  | 2 Concrete | Start |
| ✅ 60 | Conveyor Wall x 2 | `Wall_Conveyor_8x4_02` |  | 2 Concrete | AWESOME Shop: Conveyor Walls |
| ✅ 60 | Conveyor Wall x 2 | `Wall_Conveyor_8x4_02_Steel` |  | 2 Concrete | Start |
| ✅ 60 | Conveyor Wall x 3 | `Wall_Concrete_8x4_ConveyorHole_03` |  | 2 Concrete | Start |
| ✅ 60 | Conveyor Wall x 3 | `Wall_Conveyor_8x4_01` |  | 2 Concrete | AWESOME Shop: Conveyor Walls |
| ✅ 60 | Conveyor Wall x 3 | `Wall_Conveyor_8x4_01_Steel` |  | 2 Concrete | Start |
| 🧪🎨 60 | Perpendicular Wall Conveyor | `Wall_Conveyor_8x4_04` |  | 3 Iron Plate, 3 Concrete | Start |
| 🧪🎨 60 | Perpendicular Wall Conveyor | `Wall_Conveyor_8x4_04_Steel` |  | 3 Iron Plate, 3 Concrete | Start |
| ✅ 60 | Programmable Splitter | `ConveyorAttachmentSplitterProgrammable` |  | 1 Heavy Modular Frame, 2 Computer, 5 AI Limiter | MAM: Programmable Splitter |
| ✅ 60 | Smart Splitter | `ConveyorAttachmentSplitterSmart` |  | 2 Reinforced Iron Plate, 2 Rotor, 1 AI Limiter | MAM: Smart Splitter |
| ✅🎨 60 | Stackable Conveyor Pole | `ConveyorPoleStackable` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | Tier 2: Logistics Mk.2 |
|  | Priority Merger | `ConveyorAttachmentMergerPriority` |  | 2 Reinforced Iron Plate, 1 Modular Frame, 1 Crystal Oscillator | MAM: Material Resonance Screening |

## Pipes & fluids

**Use for:** Moving and storing liquids and gases.

**Tips:** Mk2 pipes carry twice as much. Pumps add head lift for vertical runs.

**Go-to pieces:** Pipeline Support (`PipelineSupport`), Fluid Buffer (`PipeStorageTank`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅🎨 60 | Clean Pipeline Mk.1 | `Pipeline_NoIndicator` |  | 1 Copper Sheet | AWESOME Shop: Clean Pipeline Mk.1 |
| ✅ 60 | Clean Pipeline Mk.2 | `PipelineMK2_NoIndicator` |  | 2 Copper Sheet, 1 Plastic | AWESOME Shop: Clean Pipeline Mk.2 |
| ✅ 60 | Fluid Buffer | `PipeStorageTank` |  | 10 Copper Sheet, 5 Modular Frame | Tier 3: Coal Power |
| ✅🎨 60 | Industrial Fluid Buffer | `IndustrialTank` |  | 5 Encased Industrial Beam, 10 Copper Sheet, 25 Plastic | Tier 5: Petroleum Power |
| ✅🎨 60 | Pipeline Floor Hole | `FoundationPassthrough_Pipe` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Pipeline Floor Hole |
| ✅🎨 60 | Pipeline Junction | `PipelineJunction_Cross` |  | 5 Copper Sheet | Tier 3: Coal Power |
| ✅🎨 60 | Pipeline Mk.1 | `Pipeline` |  | 1 Copper Sheet | Tier 3: Coal Power |
| ✅🎨 60 | Pipeline Mk.2 | `PipelineMK2` |  | 2 Copper Sheet, 1 Plastic | Tier 6: Pipeline Engineering Mk.2 |
| ✅ 60 | Pipeline Pump Mk.1 | `PipelinePump` |  | 2 Copper Sheet, 2 Rotor | Tier 3: Coal Power |
| ✅🎨 60 | Pipeline Pump Mk.2 | `PipelinePumpMk2` |  | 1 Heavy Modular Frame, 2 Motor, 10 Plastic | Tier 6: Pipeline Engineering Mk.2 |
| ✅🎨 60 | Pipeline Support | `PipelineSupport` |  | 2 Iron Plate, 2 Concrete | Tier 3: Coal Power |
| ✅🎨 60 | Pipeline Wall Hole | `PipelineSupportWallHole` |  | 2 Iron Rod, 1 Iron Plate, 2 Concrete | AWESOME Shop: Pipeline Wall Attachments |
| ✅🎨 60 | Pipeline Wall Support | `PipelineSupportWall` |  | 2 Iron Rod, 1 Iron Plate, 2 Concrete | AWESOME Shop: Pipeline Wall Attachments |
| ✅🎨 60 | Stackable Pipeline Support | `PipeSupportStackable` |  | 4 Iron Plate, 2 Iron Rod, 2 Concrete | Tier 4: Logistics Mk.3 |
| ✅ 60 | Valve | `Valve` |  | 4 Rubber, 4 Steel Beam | Tier 5: Oil Processing |
|  | Pipeline T-Junction | `PipelineJunction_T` |  | 5 Copper Sheet | Tier 3: Coal Power |

## Hypertubes

**Use for:** Player transport tubes.

**Tips:** Entrances need power in game.

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 60 | Hypertube | `PipeHyper` |  | 1 Copper Sheet, 1 Steel Pipe | Tier 4: Hypertubes |
| ✅ 60 | Hypertube Entrance | `PipeHyperStart` |  | 4 Encased Industrial Beam, 4 Rotor, 10 Steel Pipe | Tier 4: Hypertubes |
| ✅ 60 | Hypertube Support | `PipeHyperSupport` |  | 2 Iron Plate, 2 Concrete | Tier 4: Hypertubes |
| 🧪🎨 60 | Hypertube Wall Hole | `HyperTubeWallHole` |  | 2 Iron Plate, 2 Concrete | AWESOME Shop: Hypertube Wall Attachments |
| 🧪🎨 60 | Hypertube Wall Support | `HyperTubeWallSupport` |  | 2 Iron Plate, 2 Concrete | AWESOME Shop: Hypertube Wall Attachments |
|  | Hypertube Branch | `HypertubeTJunction` |  | 2 Encased Industrial Beam, 2 Steel Pipe, 5 Copper Sheet | Tier 4: Hypertubes |
|  | Hypertube Floor Hole | `FoundationPassthrough_Hypertube` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Hypertube Floor Hole |
|  | Hypertube Junction | `HyperTubeJunction` |  | 2 Encased Industrial Beam, 2 Steel Beam, 5 Copper Sheet | Tier 4: Hypertubes |
|  | Stackable Hypertube Support | `HyperPoleStackable` |  | 4 Iron Plate, 2 Iron Rod, 2 Concrete | Tier 4: Hypertubes |

## Trains, vehicles & drones

**Use for:** Rail, truck and drone logistics.

**Tips:** Stations depend on their built-in track and are best placed in game. Railway samples work as decorative track.

**Go-to pieces:** Railway (`RailroadTrack`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅🎨 60 | Block Signal | `RailroadBlockSignal` |  | 2 Steel Pipe, 1 Computer | Tier 6: Railway Signalling |
| ✅ 60 | Drone Port | `DroneStation` |  | 20 Heavy Modular Frame, 20 High-Speed Connector, 50 Alclad Aluminum Sheet, 50 Aluminum Casing, 10 Radio Control Unit | Tier 8: Aeronautical Engineering |
| ✅🎨 60 | Empty Platform | `TrainPlatformEmpty` |  | 10 Encased Industrial Beam, 50 Concrete | Tier 6: Monorail Train Technology |
| ✅ 60 | Empty Platform With Catwalk | `TrainPlatformEmpty_02` |  | 10 Encased Industrial Beam, 50 Concrete | Tier 6: Monorail Train Technology |
| 🧪🎨 60 | Explorer Vehicle Path | `VehiclePath_Explorer` |  |  | MAM: The Explorer |
| 🧪🎨 60 | Factory Cart Vehicle Path | `VehiclePath_FactoryCart` |  |  | AWESOME Shop: FICSIT Factory Cart™ |
| ✅🎨 60 | Fluid Freight Platform | `TrainDockingStationLiquid` |  | 5 Motor, 10 Encased Industrial Beam, 25 Plastic, 50 Concrete, 100 Wire | Tier 6: Monorail Train Technology |
| ✅🎨 60 | Freight Platform | `TrainDockingStation` |  | 5 Motor, 10 Encased Industrial Beam, 25 Plastic, 50 Concrete, 100 Wire | Tier 6: Monorail Train Technology |
| ✅🎨 60 | Path Signal | `RailroadPathSignal` |  | 2 Steel Pipe, 1 Computer | Tier 6: Railway Signalling |
| ✅🎨 60 | Railway | `RailroadTrack` |  | 1 Steel Pipe, 1 Steel Beam | Tier 6: Monorail Train Technology |
| ✅🎨 60 | Tractor Vehicle Path | `VehiclePath_Tractor` |  |  | Tier 3: Vehicular Transport |
| ✅🎨 60 | Train Station | `TrainStation` |  | 10 Encased Industrial Beam, 50 Plastic, 50 Concrete, 200 Wire | Tier 6: Monorail Train Technology |
| ✅ 60 | Truck Station | `TruckStation` |  | 15 Modular Frame, 20 Rotor, 50 Cable | Tier 3: Vehicular Transport |
| ✅🎨 60 | Truck Vehicle Path | `VehiclePath_Truck` |  |  | Tier 5: Logistics Mk.4 |
| ✅🎨 60 | Universal Vehicle Path | `VehiclePath_Universal` |  |  | Tier 3: Vehicular Transport |
|  | Buffer Stop | `RailroadEndStop` |  | 2 Steel Pipe, 5 Encased Industrial Beam, 20 Concrete | Tier 6: Monorail Train Technology |
|  | Fluid Truck Station | `FluidTruckStation` |  | 15 Modular Frame, 20 Stator, 20 Rubber, 50 Plastic | Tier 5: Logistics Mk.4 |
|  | U-Jelly Landing Pad | `LandingPad` |  | 2 Rotor, 20 Cable, 200 Biomass | Tier 2: Jump Pads |

## Storage

**Use for:** Item storage: containers, lockers.

**Tips:** Mk2 containers hold twice as much in the same 2 m footprint.

**Go-to pieces:** Storage Container (`StorageContainerMk1`), Industrial Storage Container (`StorageContainerMk2`)

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| 🧪🎨 60 | Basic Shelf Unit | `StackableShelf` |  | 1 Iron Plate, 1 Iron Rod | AWESOME Shop: Basic Shelf Unit |
| ✅ 60 | Hazard Storage Box | `StorageHazard` |  | 6 Iron Plate, 6 Iron Rod | AWESOME Shop: Hazard Box - Personal Storage Skin |
| ✅ 60 | Industrial Storage Container | `StorageContainerMk2` |  | 20 Steel Beam, 20 Steel Pipe | Tier 4: Logistics Mk.3 |
| ✅ 60 | Personal Storage Box | `StoragePlayer` |  | 6 Iron Plate, 6 Iron Rod | Tier 1: Field Research |
| ✅ 60 | Storage Container | `StorageContainerMk1` |  | 10 Iron Plate, 10 Iron Rod | Onboarding: HUB Upgrade 5 |
|  | Medical Storage Box | `StorageMedkit` |  | 6 Iron Plate, 6 Iron Rod | AWESOME Shop: Medical Box - Personal Storage Skin |

## Special & unique buildings

**Use for:** Game-progression buildings. Rarely part of a design.

**Tips:** The HUB and Space Elevator are one per world, and blueprint designers can't go inside a blueprint. Leave these out unless the player asks.

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 60 | AWESOME Sink | `ResourceSink` |  | 15 Reinforced Iron Plate, 30 Cable, 45 Concrete | Tier 2: Resource Sink Bonus Program |
| 🧪🎨 60 | Crafting Bench | `WorkBench` |  | 3 Iron Plate, 3 Iron Rod | Start |
| ✅ 60 | Dimensional Depot Uploader | `CentralStorage` |  | 1 Mercer Sphere, 10 SAM Fluctuator, 10 Modular Frame, 100 Wire | MAM: Dimensional Depot |
| 🧪🎨 60 | Equipment Workshop | `Workshop` |  | 6 Iron Plate, 4 Iron Rod | Onboarding: HUB Upgrade 1 |
| ✅ 60 | Main Portal | `Portal` |  | 5 Turbo Motor, 10 Radio Control Unit, 15 Superposition Oscillator, 25 SAM Fluctuator, 50 Ficsite Trigon | Tier 9: Spatial Energy Regulation |
| ✅ 60 | Radar Tower | `RadarTower` |  | 10 Computer, 20 Heavy Modular Frame, 25 Crystal Oscillator, 100 Cable | MAM: Radar Technology |
| 🧪🎨 60 | SPWN | `PortalPotty` |  | 20 Steel Pipe, 5 Modular Frame, 100 Biomass, 20 Reanimated SAM | MAM: SPWN |
| ✅ 60 | Space Elevator | `SpaceElevator` |  | 500 Concrete, 250 Iron Plate, 400 Iron Rod, 1500 Wire | Onboarding: HUB Upgrade 6 |
|  | AWESOME Shop | `ResourceSinkShop` |  | 200 Screws, 10 Iron Plate, 10 Cable | Tier 2: Resource Sink Bonus Program |
|  | Alien Power Augmenter | `AlienPowerBuilding` |  | 10 Somersloop, 50 SAM Fluctuator, 100 Cable, 50 Encased Industrial Beam, 25 Motor, 10 Computer | MAM: Power Augmenter |
|  | Blueprint Designer Mk.1 | `BlueprintDesigner` |  | 15 Modular Frame, 25 Cable, 100 Concrete, 100 Steel Beam | Tier 4: FICSIT Blueprints |
|  | Blueprint Designer Mk.2 | `BlueprintDesigner_MK2` |  | 10 Heavy Modular Frame, 20 Computer, 100 Rubber, 100 Concrete | Tier 6: FICSIT Blueprints Mk.2 |
| ⛔ legacy | Blueprint Designer Mk.3 | `BlueprintDesigner_Mk3` |  |  |  |
|  | MAM | `Mam` |  | 5 Reinforced Iron Plate, 15 Cable, 45 Wire | Tier 1: Field Research |
|  | Satellite Portal | `PortalSatellite` |  | 5 Radio Control Unit, 10 Superposition Oscillator, 25 SAM Fluctuator, 25 Ficsite Trigon | Tier 9: Spatial Energy Regulation |
|  | The HUB | `TradingPost` |  | 20 Iron Ore | Start |

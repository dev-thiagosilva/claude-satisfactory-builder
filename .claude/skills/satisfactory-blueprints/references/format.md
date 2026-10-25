# Satisfactory blueprint file format (.sbp / .sbpcfg)

Reverse-engineered from real files and verified by byte-identical round-trips of 441 blueprints
(object versions 36, 42, 46, 52, 58, 59, 60 — game Update 8 through 1.2). All integers are
little-endian. Units are Unreal centimetres, Z is up, rotations are quaternions (x, y, z, w).

## Contents
1. Strings
2. .sbp header
3. Compressed chunks
4. Body: object headers
5. Body: object data and properties
6. Building conventions (origins, sizes, grid)
7. .sbpcfg (description / icon / colour)
8. Where files live

## 1. Strings (FString)
`int32 len` then bytes. `len > 0`: latin-1 including a trailing `\0`. `len < 0`: UTF-16LE,
`-len` code units including the terminator. `len == 0`: empty string (no bytes).

## 2. .sbp header (uncompressed)
```
int32  header_version        (2)
int32  object_version        (36 … 60; tells you the game version)
int32  build_version         (engine changelist)
int32  dims_x, dims_y, dims_z  blueprint designer size in 8 m units (e.g. 4,4,4 = Mk1)
int32  cost_count
  repeat: FString level(empty)  FString item_class_path  int32 amount
int32  recipe_count
  repeat: FString level(empty)  FString recipe_class_path
bytes  extra header            object_version >= ~58: engine/custom-version block
                               ("++FactoryGame+rel-main-1.2.0", GUID+int list). Copy verbatim.
```
The cost list is what the game shows in the blueprint menu. When adding pieces, update it
(`estimate_cost(bp)` sums each piece's build recipe), or the in-game preview will understate the price.
The recipe list must include every building recipe used, or the blueprint may show as locked.

## 3. Compressed chunks
Everything after the header is a sequence of zlib chunks, each holding at most 131072
uncompressed bytes of the body.
```
1.0+ (object_version >= 42):          pre-1.0 (object_version 36):
uint32 0x9E2A83C1  tag                 uint32 0x9E2A83C1
uint32 0x22222222  archive header      uint32 0
int64  131072      max chunk size      int64  131072
uint8  3           compressor = zlib   (no compressor byte)
int64 csize, int64 usize, int64 csize, int64 usize
bytes  zlib stream (csize bytes)
```
Python's default `zlib.compress` reproduces the game's output exactly.

## 4. Body: object headers
```
int32 body_size            (= len(body) - 4)
int32 header_block_size    (bytes from the next field to the end of the last header)
int32 object_count
repeat object_count:
  int32   type             1 = actor (a building), 0 = component (connector, inventory, …)
  FString class_path       '/Game/FactoryGame/Buildable/…/Build_X.Build_X_C'
  FString level            'Persistent_Level'
  FString path             'Persistent_Level:PersistentLevel.Build_X_C_2147448562'
  int32   flags            ONLY in object_version >= 52 (value 8 seen)
  actor:     int32 need_transform, float rot[4], float pos[3], float scale[3], int32 placed
  component: FString outer_path  (path of the owning actor)
```
Positions are relative to the blueprint's origin (designer floor centre). Paths must be
unique; the number suffix is arbitrary (the game renames on placement).

## 5. Body: object data and properties
```
int32 data_block_size
int32 object_count         (same as above, same order)
repeat: int32 size, bytes[size]
```
An actor's data begins with its parent object reference (level + path, usually
`…PersistentLevel.BuildableSubsystem`), then component references, then a tagged property
list terminated by `None`:
```
FString name   FString type   int64 size   [type-specific prefix]   value
```
For Float/Int/Double properties the prefix is one byte (has-GUID flag, 0). Examples:
- `mLength` (FloatProperty) — beams, pillars of variable length: length in cm along local X.
- `mColorSlot` (ByteProperty), `mCustomizationData` (StructProperty) — paint; the swatch is
  an object path like `…/Swatches/SwatchDesc_Slot1.SwatchDesc_Slot1_C`.
- Conveyor belts, pipes, hypertubes, railways store `mSplineData` (array of location +
  tangent points) instead of a length.
- Machines store `mCurrentRecipe`, `mCurrentPotential` (clock), and reference components:
  `FactoryConnection` (belt in/out), `PipeConnection`, `PowerConnection`, `InventoryComponent`.

## 6. Building conventions
| Piece | Local size (cm) | Origin |
|---|---|---|
| Foundation 8x1 / 8x2 / 8x4 | 800 × 800 × 100/200/400 | centre of the box |
| Wall 8x4 (incl. windows) | thin (≈20) along X, 800 along Y, 400 tall | bottom centre |
| Beam | 50 × 50 cross-section, `mLength` along +X | start of the beam |
| Small pillar | ≈70 × 70, stacks every 100–400 | bottom centre |
| Quarter pipe middle WxH | W along Y, H radius | centre of the bounding box |
| Machines | varies (Constructor ≈ 790 × 1000 × 800) | floor centre |

The build grid is 800 cm for foundations and 100 cm for fine placement.

`dims` are in 8 m units on all three axes. The usable volume is centred on (0, 0)
horizontally and starts at z = 0: x and y in ±dims·400 cm, z in 0 … dims_z·800 cm.
Vanilla designers: Mk1 4×4×4 (±1600, 0–3200), Mk2 5×5×5 (±2000, 0–4000),
Mk3 6×6×6 (±2400, 0–4800). Larger values (e.g. 4×4×16, 12×12×6, 22×22×12) appear in
blueprints made with external tools or mods; the game still loads them, but they can't be
reopened in a vanilla designer. Some files contain pieces outside these limits.

## 7. .sbpcfg
Small companion file, same base name.
```
int32   config_version (0 seen)
int32   description byte length, then the bytes: NOT null-terminated, unlike FString
        (CRLF line breaks; markdown-ish text, ** bold ** and * bullets render in game)
int32   icon_id
float   colour[4]           linear RGBA
… newer files may append an icon-library reference; copy an existing file and only
  rewrite the description to stay safe (keep everything after the description verbatim).
```

## 8. Where files live
`%LOCALAPPDATA%\FactoryGame\Saved\SaveGames\blueprints\<session name>\`
The game reads the folder at load; a new or changed file shows up after reloading the save.

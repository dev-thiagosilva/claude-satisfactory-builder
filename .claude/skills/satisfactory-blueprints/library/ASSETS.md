# Every buildable piece in Satisfactory

Generated from the game's own modding data (`CommunityResources/Docs/en-US.json`) by
`scripts/build_assets.py`; machine-readable copy in `assets.json`.

**546 pieces** in the game. **157 are ready**: the donor library has a sample, so Claude can
place them in a blueprint today. The rest need a sample first (see `CLAUDE.md`).

- **Ready**: ✅ = sample in the library, 🎨 = also takes any colour.
  Versions are blueprint object versions (36 = Update 8, 42–46 = 1.0, 52–60 = 1.1/1.2).
- **Class**: the name used in code (`Build_<Class>_C` in the game).
- **Cost**: what the build gun charges. Beams and similar pieces cost per length.
- **Unlock**: the milestone, AWESOME Shop pack or MAM research that unlocks the piece.

## Contents

- [Production](#production): 14 pieces, 0 ready
- [Extraction](#extraction): 7 pieces, 0 ready
- [Power](#power): 22 pieces, 2 ready
- [Belts & lifts](#belts--lifts): 35 pieces, 16 ready
- [Pipes & pumps](#pipes--pumps): 16 pieces, 6 ready
- [Hypertubes](#hypertubes): 8 pieces, 3 ready
- [Trains, vehicles & drones](#trains-vehicles--drones): 17 pieces, 3 ready
- [Storage](#storage): 8 pieces, 3 ready
- [Glass & windows](#glass--windows): 28 pieces, 16 ready
- [Roofs](#roofs): 30 pieces, 3 ready
- [Foundations, floors & ramps](#foundations-floors--ramps): 219 pieces, 34 ready
- [Walls, doors & gates](#walls-doors--gates): 71 pieces, 33 ready
- [Beams & pillars](#beams--pillars): 19 pieces, 13 ready
- [Walkways, stairs & catwalks](#walkways-stairs--catwalks): 15 pieces, 10 ready
- [Lights & signs](#lights--signs): 14 pieces, 11 ready
- [Special & other](#special--other): 23 pieces, 4 ready

## Production

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
|  | Assembler | `AssemblerMk1` |  | 8 Reinforced Iron Plate, 4 Rotor, 10 Cable | Tier 2: Part Assembly |
|  | Blender | `Blender` |  | 10 Computer, 10 Heavy Modular Frame, 20 Motor, 50 Aluminum Casing | Tier 7: Control System Development |
|  | Constructor | `ConstructorMk1` |  | 2 Reinforced Iron Plate, 8 Cable | Onboarding: HUB Upgrade 3 |
|  | Converter | `Converter` |  | 10 Fused Modular Frame, 25 Cooling System, 50 Radio Control Unit, 100 SAM Fluctuator | Tier 9: Matter Conversion |
|  | Foundry | `FoundryMk1` |  | 10 Modular Frame, 10 Rotor, 20 Concrete | Tier 3: Basic Steel Production |
|  | Manufacturer | `ManufacturerMk1` |  | 10 Motor, 20 Modular Frame, 50 Plastic, 50 Cable | Tier 6: Industrial Manufacturing |
|  | Old Jump Pad | `JumpPad` |  |  |  |
|  | Old Tilted Jump Pad | `JumpPadTilted` |  |  |  |
|  | Packager | `Packager` |  | 20 Steel Beam, 10 Rubber, 10 Plastic | Tier 5: Fluid Packaging |
|  | Particle Accelerator | `HadronCollider` |  | 10 Turbo Motor, 10 Supercomputer, 25 Fused Modular Frame, 50 Cooling System, 500 Quickwire | Tier 8: Particle Enrichment |
|  | Quantum Encoder | `QuantumEncoder` |  | 20 Turbo Motor, 20 Supercomputer, 50 Cooling System, 50 Time Crystal, 100 Ficsite Trigon | Tier 9: Quantum Encoding |
|  | Refinery | `OilRefinery` |  | 10 Motor, 10 Encased Industrial Beam, 30 Steel Pipe, 20 Copper Sheet | Tier 5: Oil Processing |
|  | Smelter | `SmelterMk1` |  | 5 Iron Rod, 8 Wire | Onboarding: HUB Upgrade 2 |
|  | U-Jelly Landing Pad | `LandingPad` |  | 2 Rotor, 20 Cable, 200 Biomass | Tier 2: Jump Pads |

## Extraction

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
|  | Miner Mk.1 | `MinerMk1` |  | 1 BP_ItemDescriptorPortableMiner, 10 Iron Plate, 10 Concrete | Onboarding: HUB Upgrade 5 |
|  | Miner Mk.2 | `MinerMk2` |  | 2 BP_ItemDescriptorPortableMiner, 10 Encased Industrial Beam, 20 Steel Pipe, 10 Modular Frame | Tier 4: Advanced Steel Production |
|  | Miner Mk.3 | `MinerMk3` |  | 3 BP_ItemDescriptorPortableMiner, 50 Steel Pipe, 5 Supercomputer, 10 Fused Modular Frame, 3 Turbo Motor | Tier 8: Leading-Edge Production |
|  | Oil Extractor | `OilPump` |  | 15 Motor, 20 Encased Industrial Beam, 60 Cable | Tier 5: Oil Processing |
|  | Resource Well Extractor | `FrackingExtractor` |  | 10 Steel Beam, 10 Aluminum Casing | Tier 8: Advanced Aluminum Production |
|  | Resource Well Pressurizer | `FrackingSmasher` |  | 10 Radio Control Unit, 25 Heavy Modular Frame, 50 Motor, 50 Alclad Aluminum Sheet, 100 Rubber | Tier 8: Advanced Aluminum Production |
|  | Water Extractor | `WaterPump` |  | 20 Copper Sheet, 10 Reinforced Iron Plate, 10 Rotor | Tier 3: Coal Power |

## Power

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 46 | Double Wall Outlet Mk.1 | `PowerPoleWallDouble` |  | 8 Wire, 2 Iron Rod | AWESOME Shop: Wall Power Outlets Mk.1 |
| ✅🎨 42,46 | Power Pole Mk.1 | `PowerPoleMk1` |  | 3 Wire, 1 Iron Rod, 1 Concrete | Onboarding: HUB Upgrade 3 |
|  | Alien Power Augmenter | `AlienPowerBuilding` |  | 10 Somersloop, 50 SAM Fluctuator, 100 Cable, 50 Encased Industrial Beam, 25 Motor, 10 Computer | MAM: Power Augmenter |
|  | Biomass Burner | `GeneratorBiomass_Automated` |  | 15 Iron Plate, 15 Iron Rod, 25 Wire | Onboarding: HUB Upgrade 6 |
|  | Coal-Powered Generator | `GeneratorCoal` |  | 20 Reinforced Iron Plate, 10 Rotor, 30 Cable | Tier 3: Coal Power |
|  | Double Wall Outlet Mk.2 | `PowerPoleWallDouble_Mk2` |  |  |  |
|  | Double Wall Outlet Mk.3 | `PowerPoleWallDouble_Mk3` |  |  |  |
|  | FICSMAS Power Light | `XmassLightsLine` |  |  |  |
|  | Fuel-Powered Generator | `GeneratorFuel` |  | 15 Motor, 15 Encased Industrial Beam, 30 Copper Sheet, 50 Rubber, 50 Quickwire | Tier 5: Petroleum Power |
|  | Geothermal Generator | `GeneratorGeoThermal` |  | 10 Motor, 25 Modular Frame, 25 High-Speed Connector, 50 Copper Sheet, 250 Wire | MAM: Geothermal Generator |
|  | Nuclear Power Plant | `GeneratorNuclear` |  | 10 Supercomputer, 25 Heavy Modular Frame, 100 Alclad Aluminum Sheet, 200 Cable, 250 Concrete | Tier 8: Nuclear Power |
|  | Power Line | `PowerLine` |  | 1 Cable per 25 m | Onboarding: HUB Upgrade 2 |
|  | Power Pole Mk.2 | `PowerPoleMk2` |  | 6 Quickwire, 2 Iron Rod, 2 Concrete | MAM: Power Poles Mk.2 |
|  | Power Pole Mk.3 | `PowerPoleMk3` |  | 2 High-Speed Connector, 2 Steel Pipe, 3 Rubber | MAM: Power Poles Mk.3 |
|  | Power Storage | `PowerStorageMk1` |  | 5 Encased Industrial Beam, 10 Modular Frame, 100 Wire | Tier 4: Expanded Power Infrastructure |
|  | Power Switch | `PowerSwitch` |  | 20 Quickwire, 4 Steel Beam, 1 AI Limiter | MAM: Power Switch |
|  | Power Tower | `PowerTower` |  | 10 Concrete, 20 Wire, 20 Steel Beam | Tier 4: Expanded Power Infrastructure |
|  | Power Tower Platform | `PowerTowerPlatform` |  | 10 Concrete, 20 Wire, 20 Steel Beam | Tier 4: Expanded Power Infrastructure |
|  | Priority Power Switch | `PriorityPowerSwitch` |  | 2 High-Speed Connector, 6 Steel Beam, 50 Quickwire | MAM: Priority Power Switch |
|  | Wall Outlet Mk.1 | `PowerPoleWall` |  | 4 Wire, 1 Iron Rod | AWESOME Shop: Wall Power Outlets Mk.1 |
|  | Wall Outlet Mk.2 | `PowerPoleWall_Mk2` |  |  |  |
|  | Wall Outlet Mk.3 | `PowerPoleWall_Mk3` |  |  |  |

## Belts & lifts

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 46 | Conveyor Belt Mk.3 | `ConveyorBeltMk3` |  | 1 Steel Beam | Tier 4: Logistics Mk.3 |
| ✅ 46 | Conveyor Belt Mk.4 | `ConveyorBeltMk4` |  | 1 Encased Industrial Beam | Tier 5: Logistics Mk.4 |
| ✅ 46 | Conveyor Belt Mk.5 | `ConveyorBeltMk5` |  | 1 Alclad Aluminum Sheet | Tier 7: Logistics Mk.5 |
| ✅ 46,52 | Conveyor Belt Mk.6 | `ConveyorBeltMk6` |  | 1 Ficsite Trigon, 1 Time Crystal | Tier 9: Peak Efficiency |
| ✅ 36,46,52 | Conveyor Ceiling Mount | `ConveyorCeilingAttachment` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Conveyor Ceiling Mount |
| ✅ 36,46,52,58,60 | Conveyor Pole | `ConveyorPole` |  | 1 Iron Rod, 1 Iron Plate, 1 Concrete | Onboarding: HUB Upgrade 4 |
| ✅ 36 | Conveyor Splitter | `ConveyorAttachmentSplitter` |  | 2 Iron Plate, 2 Cable | Tier 1: Logistics |
| ✅ 58 | Conveyor Wall Hole | `ConveyorWallHole` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Conveyor Wall Hole |
| ✅ 46,52 | Conveyor Wall Mount | `ConveyorPoleWall` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Conveyor Wall Mount |
| ✅ 46,52,58,60 | Conveyor Wall x 1 | `Wall_Concrete_8x4_ConveyorHole_01` |  | 2 Concrete |  |
| ✅ 46 | Conveyor Wall x 1 | `Wall_Conveyor_8x4_03` |  | 2 Concrete |  |
| ✅ 52,58 | Conveyor Wall x 1 | `Wall_Conveyor_8x4_03_Steel` |  | 2 Concrete |  |
| ✅ 36,46,52,58,60 | Conveyor Wall x 2 | `Wall_Concrete_8x4_ConveyorHole_02` |  | 2 Concrete |  |
| ✅ 46 | Conveyor Wall x 2 | `Wall_Conveyor_8x4_02` |  | 2 Concrete |  |
| ✅ 52,58 | Conveyor Wall x 2 | `Wall_Conveyor_8x4_02_Steel` |  | 2 Concrete |  |
| ✅ 46 | Stackable Conveyor Pole | `ConveyorPoleStackable` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | Tier 2: Logistics Mk.2 |
|  | Buffer Stop | `RailroadEndStop` |  | 2 Steel Pipe, 5 Encased Industrial Beam, 20 Concrete | Tier 6: Monorail Train Technology |
|  | Conveyor Belt Mk.1 | `ConveyorBeltMk1` |  | 1 Iron Plate | Onboarding: HUB Upgrade 4 |
|  | Conveyor Belt Mk.2 | `ConveyorBeltMk2` |  | 1 Reinforced Iron Plate | Tier 2: Logistics Mk.2 |
|  | Conveyor Lift Mk.1 | `ConveyorLiftMk1` |  | 2 Iron Plate | Tier 1: Logistics |
|  | Conveyor Lift Mk.2 | `ConveyorLiftMk2` |  | 2 Reinforced Iron Plate | Tier 2: Logistics Mk.2 |
|  | Conveyor Lift Mk.3 | `ConveyorLiftMk3` |  | 2 Steel Beam | Tier 4: Logistics Mk.3 |
|  | Conveyor Lift Mk.4 | `ConveyorLiftMk4` |  | 2 Encased Industrial Beam | Tier 5: Logistics Mk.4 |
|  | Conveyor Lift Mk.5 | `ConveyorLiftMk5` |  | 2 Alclad Aluminum Sheet | Tier 7: Logistics Mk.5 |
|  | Conveyor Lift Mk.6 | `ConveyorLiftMk6` |  | 2 Ficsite Trigon, 2 Time Crystal | Tier 9: Peak Efficiency |
|  | Conveyor Merger | `ConveyorAttachmentMerger` |  | 2 Iron Plate, 2 Iron Rod | Tier 1: Logistics |
|  | Conveyor Throughput Monitor | `ConveyorMonitor` |  | 4 Reinforced Iron Plate, 10 Quartz Crystal, 1 Crystal Oscillator | AWESOME Shop: Conveyor Throughput Monitor |
|  | Conveyor Wall x 3 | `Wall_Concrete_8x4_ConveyorHole_03` |  | 2 Concrete |  |
|  | Conveyor Wall x 3 | `Wall_Conveyor_8x4_01` |  | 2 Concrete |  |
|  | Conveyor Wall x 3 | `Wall_Conveyor_8x4_01_Steel` |  | 2 Concrete |  |
|  | Perpendicular Wall Conveyor | `Wall_Conveyor_8x4_04` |  | 3 Iron Plate, 3 Concrete |  |
|  | Perpendicular Wall Conveyor | `Wall_Conveyor_8x4_04_Steel` |  | 3 Iron Plate, 3 Concrete |  |
|  | Priority Merger | `ConveyorAttachmentMergerPriority` |  | 2 Reinforced Iron Plate, 1 Modular Frame, 1 Crystal Oscillator | MAM: Material Resonance Screening |
|  | Programmable Splitter | `ConveyorAttachmentSplitterProgrammable` |  | 1 Heavy Modular Frame, 2 Computer, 5 AI Limiter | MAM: Programmable Splitter |
|  | Smart Splitter | `ConveyorAttachmentSplitterSmart` |  | 2 Reinforced Iron Plate, 2 Rotor, 1 AI Limiter | MAM: Smart Splitter |

## Pipes & pumps

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 46,60 | Hypertube Support | `PipeHyperSupport` |  | 2 Iron Plate, 2 Concrete | Tier 4: Hypertubes |
| ✅🎨 58 | Pipeline Mk.2 | `PipelineMK2` |  | 2 Copper Sheet, 1 Plastic | Tier 6: Pipeline Engineering Mk.2 |
| ✅🎨 46,52,58 | Pipeline Support | `PipelineSupport` |  | 2 Iron Plate, 2 Concrete | Tier 3: Coal Power |
| ✅🎨 36 | Pipeline Wall Hole | `PipelineSupportWallHole` |  | 2 Iron Rod, 1 Iron Plate, 2 Concrete | AWESOME Shop: Pipeline Wall Attachments |
| ✅🎨 36,52,58 | Pipeline Wall Support | `PipelineSupportWall` |  | 2 Iron Rod, 1 Iron Plate, 2 Concrete | AWESOME Shop: Pipeline Wall Attachments |
| ✅🎨 46,58 | Stackable Pipeline Support | `PipeSupportStackable` |  | 4 Iron Plate, 2 Iron Rod, 2 Concrete | Tier 4: Logistics Mk.3 |
|  | Clean Pipeline Mk.1 | `Pipeline_NoIndicator` |  | 1 Copper Sheet | AWESOME Shop: Clean Pipeline Mk.1 |
|  | Clean Pipeline Mk.2 | `PipelineMK2_NoIndicator` |  | 2 Copper Sheet, 1 Plastic | AWESOME Shop: Clean Pipeline Mk.2 |
|  | Fluid Buffer | `PipeStorageTank` |  | 10 Copper Sheet, 5 Modular Frame | Tier 3: Coal Power |
|  | Industrial Fluid Buffer | `IndustrialTank` |  | 5 Encased Industrial Beam, 10 Copper Sheet, 25 Plastic | Tier 5: Petroleum Power |
|  | Pipeline Junction | `PipelineJunction_Cross` |  | 5 Copper Sheet |  |
|  | Pipeline Mk.1 | `Pipeline` |  | 1 Copper Sheet | Tier 3: Coal Power |
|  | Pipeline Pump Mk.1 | `PipelinePump` |  | 2 Copper Sheet, 2 Rotor | Tier 3: Coal Power |
|  | Pipeline Pump Mk.2 | `PipelinePumpMk2` |  | 1 Heavy Modular Frame, 2 Motor, 10 Plastic | Tier 6: Pipeline Engineering Mk.2 |
|  | Pipeline T-Junction | `PipelineJunction_T` |  | 5 Copper Sheet | Tier 3: Coal Power |
|  | Valve | `Valve` |  | 4 Rubber, 4 Steel Beam | Tier 5: Oil Processing |

## Hypertubes

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 46 | Hypertube | `PipeHyper` |  | 1 Copper Sheet, 1 Steel Pipe | Tier 4: Hypertubes |
| ✅ 46 | Hypertube Wall Hole | `HyperTubeWallHole` |  | 2 Iron Plate, 2 Concrete | AWESOME Shop: Hypertube Wall Attachments |
| ✅ 46 | Stackable Hypertube Support | `HyperPoleStackable` |  | 4 Iron Plate, 2 Iron Rod, 2 Concrete | Tier 4: Hypertubes |
|  | Hypertube Branch | `HypertubeTJunction` |  | 2 Encased Industrial Beam, 2 Steel Pipe, 5 Copper Sheet | Tier 4: Hypertubes |
|  | Hypertube Entrance | `PipeHyperStart` |  | 4 Encased Industrial Beam, 4 Rotor, 10 Steel Pipe | Tier 4: Hypertubes |
|  | Hypertube Floor Hole | `FoundationPassthrough_Hypertube` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Hypertube Floor Hole |
|  | Hypertube Junction | `HyperTubeJunction` |  | 2 Encased Industrial Beam, 2 Steel Beam, 5 Copper Sheet | Tier 4: Hypertubes |
|  | Hypertube Wall Support | `HyperTubeWallSupport` |  | 2 Iron Plate, 2 Concrete | AWESOME Shop: Hypertube Wall Attachments |

## Trains, vehicles & drones

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 46 | Drone Port | `DroneStation` |  | 20 Heavy Modular Frame, 20 High-Speed Connector, 50 Alclad Aluminum Sheet, 50 Aluminum Casing, 10 Radio Control Unit | Tier 8: Aeronautical Engineering |
| ✅🎨 36,42,46,52 | Modern Railing | `Railing_01` |  | 2 Iron Rod | AWESOME Shop: Modern Railing |
| ✅ 46 | Railway | `RailroadTrack` |  | 1 Steel Pipe, 1 Steel Beam | Tier 6: Monorail Train Technology |
|  | Block Signal | `RailroadBlockSignal` |  | 2 Steel Pipe, 1 Computer | Tier 6: Railway Signalling |
|  | Empty Platform | `TrainPlatformEmpty` |  | 10 Encased Industrial Beam, 50 Concrete | Tier 6: Monorail Train Technology |
|  | Empty Platform With Catwalk | `TrainPlatformEmpty_02` |  | 10 Encased Industrial Beam, 50 Concrete | Tier 6: Monorail Train Technology |
|  | Explorer Vehicle Path | `VehiclePath_Explorer` |  |  | MAM: The Explorer |
|  | Factory Cart Vehicle Path | `VehiclePath_FactoryCart` |  |  | AWESOME Shop: FICSIT Factory Cart™ |
|  | Fluid Freight Platform | `TrainDockingStationLiquid` |  | 5 Motor, 10 Encased Industrial Beam, 25 Plastic, 50 Concrete, 100 Wire | Tier 6: Monorail Train Technology |
|  | Fluid Truck Station | `FluidTruckStation` |  | 15 Modular Frame, 20 Stator, 20 Rubber, 50 Plastic | Tier 5: Logistics Mk.4 |
|  | Freight Platform | `TrainDockingStation` |  | 5 Motor, 10 Encased Industrial Beam, 25 Plastic, 50 Concrete, 100 Wire | Tier 6: Monorail Train Technology |
|  | Path Signal | `RailroadPathSignal` |  | 2 Steel Pipe, 1 Computer | Tier 6: Railway Signalling |
|  | Tractor Vehicle Path | `VehiclePath_Tractor` |  |  | Tier 3: Vehicular Transport |
|  | Train Station | `TrainStation` |  | 10 Encased Industrial Beam, 50 Plastic, 50 Concrete, 200 Wire | Tier 6: Monorail Train Technology |
|  | Truck Station | `TruckStation` |  | 15 Modular Frame, 20 Rotor, 50 Cable | Tier 3: Vehicular Transport |
|  | Truck Vehicle Path | `VehiclePath_Truck` |  |  | Tier 5: Logistics Mk.4 |
|  | Universal Vehicle Path | `VehiclePath_Universal` |  |  | Tier 3: Vehicular Transport |

## Storage

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 36 | Hazard Storage Box | `StorageHazard` |  | 6 Iron Plate, 6 Iron Rod | AWESOME Shop: Hazard Box - Personal Storage Skin |
| ✅ 36 | Medical Storage Box | `StorageMedkit` |  | 6 Iron Plate, 6 Iron Rod | AWESOME Shop: Medical Box - Personal Storage Skin |
| ✅ 36 | Personal Storage Box | `StoragePlayer` |  | 6 Iron Plate, 6 Iron Rod | Tier 1: Field Research |
|  | Basic Shelf Unit | `StackableShelf` |  | 1 Iron Plate, 1 Iron Rod | AWESOME Shop: Basic Shelf Unit |
|  | Dimensional Depot Uploader | `CentralStorage` |  | 1 Mercer Sphere, 10 SAM Fluctuator, 10 Modular Frame, 100 Wire | MAM: Dimensional Depot |
|  | Industrial Storage Container | `StorageContainerMk2` |  | 20 Steel Beam, 20 Steel Pipe | Tier 4: Logistics Mk.3 |
|  | Shelf Beam | `Beam_Shelf` | length 1–40 m | 1 Steel Beam per 4 m | AWESOME Shop: Beam Expansion Pack |
|  | Storage Container | `StorageContainerMk1` |  | 10 Iron Plate, 10 Iron Rod | Onboarding: HUB Upgrade 5 |

## Glass & windows

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 36,42,60 | Flat Roof | `Roof_Window_01` | 8 × 8 × 0 m | 3 Concrete | Start |
| ✅ 42,46 | Frame Window | `Wall_Concrete_8x4_Window_02` |  | 2 Silica |  |
| ✅🎨 36,42,46 | Frame Window | `Wall_Window_8x4_02` |  | 2 Silica | AWESOME Shop: Windowed Walls |
| ✅🎨 36,42,46,52,58,60 | Full Frame Window | `Wall_Window_Thin_8x4_01` |  | 2 Silica, 2 Steel Beam | AWESOME Shop: Steel-Framed Windows |
| ✅ 36,42,46,52,58,60 | Glass Frame Foundation | `FoundationGlass_01` | 8 × 8 × 1 m | 2 Steel Beam, 5 Concrete | AWESOME Shop: Structural Frame Set |
| ✅ 36,46,52,58 | Hex Frame Window | `Wall_Window_Thin_8x4_02` |  | 2 Silica, 2 Steel Beam | AWESOME Shop: Steel-Framed Windows |
| ✅ 46 | Honeycomb Frame Window | `Wall_Window_8x4_06` |  | 2 Silica, 2 Steel Beam | AWESOME Shop: Steel-Framed Windows |
| ✅ 36 | Inner Corner Roof (2 m) | `Roof_Window_InCorner_02` | 8 m | 3 Concrete | Start |
| ✅ 36 | Outer Corner Roof (2 m) | `Roof_Window_OutCorner_02` | 8 m | 3 Concrete | Start |
| ✅ 36 | Panel Window | `Wall_Concrete_8x4_Window_03` |  | 2 Silica |  |
| ✅🎨 36,42 | Panel Window | `Wall_Window_8x4_03` |  | 2 Silica | AWESOME Shop: Windowed Walls |
| ✅ 36 | Reinforced Window | `Wall_Concrete_8x4_Window_04` |  | 2 Silica |  |
| ✅ 46 | Reinforced Window | `Wall_Window_8x4_04` |  | 2 Silica | AWESOME Shop: Windowed Walls |
| ✅ 36 | Roof (2 m) | `Roof_Window_03` | 8 × 8 × 2 m | 3 Concrete | Start |
| ✅ 36,46 | Single Window | `Wall_Concrete_8x4_Window_01` |  | 2 Silica |  |
| ✅ 46 | Triple Frame Window | `Wall_Window_8x4_07` |  | 2 Silica, 2 Steel Beam | AWESOME Shop: Steel-Framed Windows |
|  | Angled Frame Window | `Wall_Window_8x4_05` |  | 2 Silica, 2 Steel Beam | AWESOME Shop: Steel-Framed Windows |
|  | Frame Window | `SteelWall_8x4_Window_03` |  | 2 Silica | Start |
|  | Inner Corner Roof (1 m) | `Roof_Window_InCorner_01` | 8 m | 3 Concrete | Start |
|  | Inner Corner Roof (4 m) | `Roof_Window_InCorner_03` | 8 m | 3 Concrete | Start |
|  | Outer Corner Roof (1 m) | `Roof_Window_OutCorner_01` | 8 m | 3 Concrete | Start |
|  | Outer Corner Roof (4 m) | `Roof_Window_OutCorner_03` | 8 m | 3 Concrete | Start |
|  | Panel Window | `SteelWall_8x4_Window_04` |  | 2 Silica | Start |
|  | Reinforced Window | `SteelWall_8x4_Window_02` |  | 2 Silica | Start |
|  | Roof (1 m) | `Roof_Window_02` | 8 × 8 × 1 m | 3 Concrete | Start |
|  | Roof (4 m) | `Roof_Window_04` | 8 × 8 × 4 m | 3 Concrete | Start |
|  | Single Window | `SteelWall_8x4_Window_01` |  | 2 Silica | Start |
|  | Single Window | `Wall_Window_8x4_01` |  | 2 Silica | AWESOME Shop: Windowed Walls |

## Roofs

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 52,58 | Flat Roof | `Roof_A_01` | 8 × 8 × 0 m | 3 Concrete | Start |
| ✅ 46 | Flat Roof | `Roof_Orange_01` | 8 × 8 × 0 m | 3 Concrete | AWESOME Shop: FICSIT Roofs |
| ✅ 36 | Flat Roof | `Roof_Tar_01` | 8 × 8 × 0 m | 3 Concrete | Start |
|  | Inner Corner Roof (1 m) | `Roof_Metal_InCorner_01` | 8 m | 3 Concrete | Start |
|  | Inner Corner Roof (1 m) | `Roof_Orange_InCorner_01` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
|  | Inner Corner Roof (1 m) | `Roof_Tar_InCorner_01` | 8 m | 3 Concrete | Start |
|  | Inner Corner Roof (2 m) | `Roof_Metal_InCorner_02` | 8 m | 3 Concrete | Start |
|  | Inner Corner Roof (2 m) | `Roof_Orange_InCorner_02` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
|  | Inner Corner Roof (2 m) | `Roof_Tar_InCorner_02` | 8 m | 3 Concrete | Start |
|  | Inner Corner Roof (4 m) | `Roof_Metal_InCorner_03` | 8 m | 3 Concrete | Start |
|  | Inner Corner Roof (4 m) | `Roof_Orange_InCorner_03` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
|  | Inner Corner Roof (4 m) | `Roof_Tar_InCorner_03` | 8 m | 3 Concrete | Start |
|  | Outer Corner Roof (1 m) | `Roof_Metal_OutCorner_01` | 8 m | 3 Concrete | Start |
|  | Outer Corner Roof (1 m) | `Roof_Orange_OutCorner_01` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
|  | Outer Corner Roof (1 m) | `Roof_Tar_OutCorner_01` | 8 m | 3 Concrete | Start |
|  | Outer Corner Roof (2 m) | `Roof_Metal_OutCorner_02` | 8 m | 3 Concrete | Start |
|  | Outer Corner Roof (2 m) | `Roof_Orange_OutCorner_02` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
|  | Outer Corner Roof (2 m) | `Roof_Tar_OutCorner_02` | 8 m | 3 Concrete | Start |
|  | Outer Corner Roof (4 m) | `Roof_Metal_OutCorner_03` | 8 m | 3 Concrete | Start |
|  | Outer Corner Roof (4 m) | `Roof_Orange_OutCorner_03` | 8 m | 3 Concrete | AWESOME Shop: FICSIT Roof Corners |
|  | Outer Corner Roof (4 m) | `Roof_Tar_OutCorner_03` | 8 m | 3 Concrete | Start |
|  | Roof (1 m) | `Roof_A_02` | 8 × 8 × 1 m | 3 Concrete | Start |
|  | Roof (1 m) | `Roof_Orange_02` | 8 × 8 × 1 m | 3 Concrete | AWESOME Shop: FICSIT Roofs |
|  | Roof (1 m) | `Roof_Tar_02` | 8 × 8 × 1 m | 3 Concrete | Start |
|  | Roof (2 m) | `Roof_A_03` | 8 × 8 × 2 m | 3 Concrete | Start |
|  | Roof (2 m) | `Roof_Orange_03` | 8 × 8 × 2 m | 3 Concrete | AWESOME Shop: FICSIT Roofs |
|  | Roof (2 m) | `Roof_Tar_03` | 8 × 8 × 2 m | 3 Concrete | Start |
|  | Roof (4 m) | `Roof_A_04` | 8 × 8 × 4 m | 3 Concrete | Start |
|  | Roof (4 m) | `Roof_Orange_04` | 8 × 8 × 4 m | 3 Concrete | AWESOME Shop: FICSIT Roofs |
|  | Roof (4 m) | `Roof_Tar_04` | 8 × 8 × 4 m | 3 Concrete | Start |

## Foundations, floors & ramps

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 36 | Conveyor Lift Floor Hole | `FoundationPassthrough_Lift` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Conveyor Lift Floor Hole |
| ✅ 46 | Foundation (1 m) | `Foundation_8x1_01` | 8 × 8 × 1 m | 5 Concrete | Tier 1: Base Building |
| ✅ 36,46,58 | Foundation (1 m) | `Foundation_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| ✅🎨 42,46,52,58,60 | Foundation (1 m) | `Foundation_ConcretePolished_8x1` | 8 × 8 × 1 m | 5 Concrete |  |
| ✅🎨 36,42,46,52,58,60 | Foundation (1 m) | `Foundation_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete |  |
| ✅ 52,58,59,60 | Foundation (1 m) | `Foundation_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| ✅ 36 | Foundation (2 m) | `Foundation_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| ✅ 60 | Foundation (2 m) | `Foundation_ConcretePolished_8x2_2` | 8 × 8 × 2 m |  |  |
| ✅🎨 36,46,60 | Foundation (2 m) | `Foundation_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete |  |
| ✅ 58 | Foundation (2 m) | `Foundation_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| ✅ 46 | Foundation (4 m) | `Foundation_8x4_01` | 8 × 8 × 4 m | 5 Concrete | Tier 1: Base Building |
| ✅ 46,58 | Foundation (4 m) | `Foundation_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
| ✅ 60 | Foundation (4 m) | `Foundation_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
| ✅ 58 | Foundation (4 m) | `Foundation_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
| ✅ 46,52,58 | Frame Floor | `Flat_Frame_01` | 8 × 8 × 0.4 m | 2 Steel Beam | AWESOME Shop: Structural Frame Set |
| ✅ 46,52,58,60 | Frame Foundation | `Foundation_Frame_01` | 8 × 8 × 4 m | 5 Steel Beam | AWESOME Shop: Structural Frame Set |
| ✅ 36,42,46 | Half Foundation (1 m) | `QuarterPipeMiddle_Asphalt_8x1` | 8 × 4 × 1 m | 5 Concrete | Start |
| ✅🎨 36,42,46,52 | Half Foundation (1 m) | `QuarterPipeMiddle_Concrete_8x1` | 8 × 4 × 1 m | 5 Concrete |  |
| ✅ 42,52 | Half Foundation (1 m) | `QuarterPipeMiddle_Grip_8x1` | 8 × 4 × 1 m | 5 Concrete | Start |
| ✅🎨 42,46 | Half Foundation (1 m) | `QuarterPipeMiddle_PolishedConcrete_8x1` | 8 × 4 × 1 m | 5 Concrete | Start |
| ✅ 36,46 | Half Foundation (2 m) | `QuarterPipeMiddle_Concrete_8x2` | 8 × 4 × 2 m | 5 Concrete |  |
| ✅ 42 | Half Foundation (4 m) | `QuarterPipeMiddle_Asphalt_8x4` | 8 × 4 × 4 m | 5 Concrete | Start |
| ✅ 42,52 | Half Foundation (4 m) | `QuarterPipeMiddle_Concrete_8x4` | 8 × 4 × 4 m | 5 Concrete |  |
| ✅ 42 | Half Foundation (4 m) | `QuarterPipeMiddle_PolishedConcrete_8x4` | 8 × 4 × 4 m | 5 Concrete | Start |
| ✅ 36 | Inner Corner Extension (2 m) | `QuarterPipeMiddleInCorner_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
| ✅ 60 | Inverted Frame Ramp | `Ramp_Frame_Inverted_01` | 8 × 8 × 4 m | 5 Steel Beam | AWESOME Shop: Structural Frame Set |
| ✅ 36 | Inverted Up Corner (1 m) | `InvertedRamp_UCorner_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete |  |
| ✅ 36 | Outer Corner Extension (2 m) | `QuarterPipeMiddleOutCorner_Asphalt_4x2` | 4 × 4 × 2 m | 5 Concrete | Start |
| ✅ 36 | Outer Corner Extension (4 m) | `QuarterPipeMiddleOutCorner_Asphalt_4x4` | 4 × 4 × 4 m | 5 Concrete | Start |
| ✅ 36 | Ramp (1 m) | `Ramp_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| ✅ 36,42,58 | Ramp (4 m) | `Ramp_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
| ✅ 36 | Up Corner Ramp (1 m) | `Ramp_UpCorner_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
| ✅ 58 | Up Corner Ramp (4 m) | `Ramp_UpCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
| ✅ 42 | Walkway Ramp | `WalkwayRamp` | 4 m | 2 Iron Rod, 1 Iron Plate | Start |
|  | Catwalk Ramp | `CatwalkRamp` | 4 m | 2 Iron Rod, 1 Iron Plate | AWESOME Shop: Modern Catwalks |
|  | Double Ramp (2 m) | `RampDouble_8x1` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Double Ramp Set |
|  | Double Ramp (2 m) | `RampDouble_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Double Ramp (2 m) | `RampDouble_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete |  |
|  | Double Ramp (2 m) | `RampDouble_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Double Ramp (2 m) | `RampDouble_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Double Ramp (4 m) | `RampDouble` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Double Ramp (4 m) | `RampDouble_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Double Ramp (4 m) | `RampDouble_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete |  |
|  | Double Ramp (4 m) | `RampDouble_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Double Ramp (4 m) | `RampDouble_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Double Ramp (8 m) | `RampDouble_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Double Ramp (8 m) | `RampDouble_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Double Ramp (8 m) | `RampDouble_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Double Ramp (8 m) | `RampDouble_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Double Ramp (8 m) | `Ramp_8x8x8` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Double Ramp Set |
|  | Down Corner Ramp (1 m) | `Ramp_Diagonal_8x1_01` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
|  | Down Corner Ramp (1 m) | `Ramp_DownCorner_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Down Corner Ramp (1 m) | `Ramp_DownCorner_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete |  |
|  | Down Corner Ramp (1 m) | `Ramp_DownCorner_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Down Corner Ramp (1 m) | `Ramp_DownCorner_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Down Corner Ramp (2 m) | `Ramp_Diagonal_8x2_01` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
|  | Down Corner Ramp (2 m) | `Ramp_DownCorner_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Down Corner Ramp (2 m) | `Ramp_DownCorner_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete |  |
|  | Down Corner Ramp (2 m) | `Ramp_DownCorner_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Down Corner Ramp (2 m) | `Ramp_DownCorner_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Down Corner Ramp (4 m) | `Ramp_Diagonal_8x4_01` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
|  | Down Corner Ramp (4 m) | `Ramp_DownCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Down Corner Ramp (4 m) | `Ramp_DownCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Down Corner Ramp (4 m) | `Ramp_DownCorner_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Down Corner Ramp (4 m) | `Ramp_DownCorner_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Elevator Floor Stop | `ElevatorFloorStop` |  | 2 Modular Frame, 1 Motor, 5 Steel Beam | AWESOME Shop: Personnel Elevator |
|  | Foundation (2 m) | `Foundation_8x2_01` | 8 × 8 × 2 m | 5 Concrete | Tier 1: Base Building |
|  | Foundation (4 m) | `Foundation_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Foundation Stairs (1 m) | `Stair_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Foundation Stairs (1 m) | `Stair_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete |  |
|  | Foundation Stairs (1 m) | `Stair_FicsitSet_8x1_01` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Foundation Stairs Set |
|  | Foundation Stairs (1 m) | `Stair_GripMetal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Foundation Stairs (1 m) | `Stair_PolishedConcrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Foundation Stairs (2 m) | `Stair_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Foundation Stairs (2 m) | `Stair_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete |  |
|  | Foundation Stairs (2 m) | `Stair_FicsitSet_8x2_01` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Foundation Stairs Set |
|  | Foundation Stairs (2 m) | `Stair_GripMetal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Foundation Stairs (2 m) | `Stair_PolishedConcrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Foundation Stairs (4 m) | `Stair_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Foundation Stairs (4 m) | `Stair_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Foundation Stairs (4 m) | `Stair_FicsitSet_8x4_01` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Foundation Stairs Set |
|  | Foundation Stairs (4 m) | `Stair_GripMetal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Foundation Stairs (4 m) | `Stair_PolishedConcrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Frame Ramp | `Ramp_Frame_01` | 8 × 8 × 4 m | 5 Steel Beam | AWESOME Shop: Structural Frame Set |
|  | Half Foundation (1 m) | `QuarterPipeMiddle_Ficsit_8x1` | 8 × 4 × 1 m |  |  |
|  | Half Foundation (2 m) | `QuarterPipeMiddle_Asphalt_8x2` | 8 × 4 × 2 m | 5 Concrete | Start |
|  | Half Foundation (2 m) | `QuarterPipeMiddle_Ficsit_8x2` | 8 × 4 × 2 m |  |  |
|  | Half Foundation (2 m) | `QuarterPipeMiddle_Grip_8x2` | 8 × 4 × 2 m | 5 Concrete | Start |
|  | Half Foundation (2 m) | `QuarterPipeMiddle_PolishedConcrete_8x2` | 8 × 4 × 2 m | 5 Concrete | Start |
|  | Half Foundation (4 m) | `QuarterPipeMiddle_Ficsit_8x4` | 8 × 4 × 4 m |  |  |
|  | Half Foundation (4 m) | `QuarterPipeMiddle_Grip_8x4` | 8 × 4 × 4 m | 5 Concrete | Start |
|  | Inner Corner Extension (1 m) | `QuarterPipeMiddleInCorner_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Inner Corner Extension (1 m) | `QuarterPipeMiddleInCorner_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete |  |
|  | Inner Corner Extension (1 m) | `QuarterPipeMiddleInCorner_Ficsit_8x1` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
|  | Inner Corner Extension (1 m) | `QuarterPipeMiddleInCorner_Grip_8x1` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inner Corner Extension (1 m) | `QuarterPipeMiddleInCorner_PolishedConcrete_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Inner Corner Extension (2 m) | `QuarterPipeMiddleInCorner_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete |  |
|  | Inner Corner Extension (2 m) | `QuarterPipeMiddleInCorner_Ficsit_8x2` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
|  | Inner Corner Extension (2 m) | `QuarterPipeMiddleInCorner_Grip_8x2` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inner Corner Extension (2 m) | `QuarterPipeMiddleInCorner_PolishedConcrete_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Inner Corner Extension (4 m) | `QuarterPipeMiddleInCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inner Corner Extension (4 m) | `QuarterPipeMiddleInCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inner Corner Extension (4 m) | `QuarterPipeMiddleInCorner_Ficsit_8x4` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
|  | Inner Corner Extension (4 m) | `QuarterPipeMiddleInCorner_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inner Corner Extension (4 m) | `QuarterPipeMiddleInCorner_PolishedConcrete_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inner Corner Quarter Pipe | `QuarterPipeCorner_01` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipes Pack |
|  | Inner Corner Quarter Pipe | `QuarterPipeInCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inner Corner Quarter Pipe | `QuarterPipeInCorner_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inner Corner Quarter Pipe | `QuarterPipeInCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inner Corner Quarter Pipe | `QuarterPipeInCorner_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Down Corner (1 m) | `InvertedRamp_DCorner_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Inverted Down Corner (1 m) | `InvertedRamp_DCorner_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete |  |
|  | Inverted Down Corner (1 m) | `InvertedRamp_DCorner_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Inverted Down Corner (1 m) | `InvertedRamp_DCorner_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Inverted Down Corner (1 m) | `RampInverted_8x1_Corner_02` | 8 × 8 × 1 m | 5 Concrete |  |
|  | Inverted Down Corner (2 m) | `InvertedRamp_DCorner_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Inverted Down Corner (2 m) | `InvertedRamp_DCorner_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete |  |
|  | Inverted Down Corner (2 m) | `InvertedRamp_DCorner_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Inverted Down Corner (2 m) | `InvertedRamp_DCorner_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Inverted Down Corner (2 m) | `RampInverted_8x2_Corner_02` | 8 × 8 × 2 m | 5 Concrete |  |
|  | Inverted Down Corner (4 m) | `InvertedRamp_DCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Down Corner (4 m) | `InvertedRamp_DCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inverted Down Corner (4 m) | `InvertedRamp_DCorner_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Down Corner (4 m) | `InvertedRamp_DCorner_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Down Corner (4 m) | `RampInverted_8x4_Corner_02` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inverted Inner Corner Quarter Pipe | `DownQuarterPipeInCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Inner Corner Quarter Pipe | `DownQuarterPipeInCorner_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inverted Inner Corner Quarter Pipe | `DownQuarterPipeInCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inverted Inner Corner Quarter Pipe | `DownQuarterPipeInCorner_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Inner Corner Quarter Pipe | `QuarterPipeCorner_02` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipes Pack |
|  | Inverted Outer Corner Quarter Pipe | `DownQuarterPipeOutCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Outer Corner Quarter Pipe | `DownQuarterPipeOutCorner_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inverted Outer Corner Quarter Pipe | `DownQuarterPipeOutCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inverted Outer Corner Quarter Pipe | `DownQuarterPipeOutCorner_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Outer Corner Quarter Pipe | `QuarterPipeCorner_04` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipes Pack |
|  | Inverted Quarter Pipe | `DownQuarterPipe_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Quarter Pipe | `DownQuarterPipe_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inverted Quarter Pipe | `DownQuarterPipe_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inverted Quarter Pipe | `DownQuarterPipe_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Quarter Pipe | `QuarterPipe_02` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipes Pack |
|  | Inverted Ramp (1 m) | `InvertedRamp_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Inverted Ramp (1 m) | `InvertedRamp_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete |  |
|  | Inverted Ramp (1 m) | `InvertedRamp_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Inverted Ramp (1 m) | `InvertedRamp_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Inverted Ramp (1 m) | `RampInverted_8x1` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Inverted Corner Ramp Pack |
|  | Inverted Ramp (2 m) | `InvertedRamp_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Inverted Ramp (2 m) | `InvertedRamp_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete |  |
|  | Inverted Ramp (2 m) | `InvertedRamp_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Inverted Ramp (2 m) | `InvertedRamp_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Inverted Ramp (2 m) | `RampInverted_8x2_01` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Inverted Ramp Set |
|  | Inverted Ramp (4 m) | `InvertedRamp_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Ramp (4 m) | `InvertedRamp_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inverted Ramp (4 m) | `InvertedRamp_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Ramp (4 m) | `InvertedRamp_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Ramp (4 m) | `Ramp_8x4_Inverted_01` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Inverted Ramp Set |
|  | Inverted Up Corner (1 m) | `InvertedRamp_UCorner_Asphalt_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Inverted Up Corner (1 m) | `InvertedRamp_UCorner_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Inverted Up Corner (1 m) | `InvertedRamp_UCorner_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Inverted Up Corner (1 m) | `RampInverted_8x1_Corner_01` | 8 × 8 × 1 m | 5 Concrete |  |
|  | Inverted Up Corner (2 m) | `InvertedRamp_UCorner_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Inverted Up Corner (2 m) | `InvertedRamp_UCorner_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete |  |
|  | Inverted Up Corner (2 m) | `InvertedRamp_UCorner_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Inverted Up Corner (2 m) | `InvertedRamp_UCorner_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Inverted Up Corner (2 m) | `RampInverted_8x2_Corner_01` | 8 × 8 × 2 m | 5 Concrete |  |
|  | Inverted Up Corner (4 m) | `InvertedRamp_UCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Up Corner (4 m) | `InvertedRamp_UCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Inverted Up Corner (4 m) | `InvertedRamp_UCorner_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Up Corner (4 m) | `InvertedRamp_UCorner_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Inverted Up Corner (4 m) | `RampInverted_8x4_Corner_01` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Outer Corner Extension (1 m) | `QuarterPipeMiddleOutCorner_Asphalt_4x1` | 4 × 4 × 1 m | 5 Concrete | Start |
|  | Outer Corner Extension (1 m) | `QuarterPipeMiddleOutCorner_Concrete_4x1` | 4 × 4 × 1 m | 5 Concrete |  |
|  | Outer Corner Extension (1 m) | `QuarterPipeMiddleOutCorner_Ficsit_4x1` | 4 × 4 × 1 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
|  | Outer Corner Extension (1 m) | `QuarterPipeMiddleOutCorner_Grip_4x1` | 4 × 4 × 1 m | 5 Concrete | Start |
|  | Outer Corner Extension (1 m) | `QuarterPipeMiddleOutCorner_PolishedConcrete_4x1` | 4 × 4 × 1 m | 5 Concrete | Start |
|  | Outer Corner Extension (2 m) | `QuarterPipeMiddleOutCorner_Concrete_4x2` | 4 × 4 × 2 m | 5 Concrete |  |
|  | Outer Corner Extension (2 m) | `QuarterPipeMiddleOutCorner_Ficsit_4x2` | 4 × 4 × 2 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
|  | Outer Corner Extension (2 m) | `QuarterPipeMiddleOutCorner_Grip_4x2` | 4 × 4 × 2 m | 5 Concrete | Start |
|  | Outer Corner Extension (2 m) | `QuarterPipeMiddleOutCorner_PolishedConcrete_4x2` | 4 × 4 × 2 m | 5 Concrete | Start |
|  | Outer Corner Extension (4 m) | `QuarterPipeMiddleOutCorner_Concrete_4x4` | 4 × 4 × 4 m | 5 Concrete |  |
|  | Outer Corner Extension (4 m) | `QuarterPipeMiddleOutCorner_Ficsit_4x4` | 4 × 4 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipe Extensions Pack |
|  | Outer Corner Extension (4 m) | `QuarterPipeMiddleOutCorner_Grip_4x4` | 4 × 4 × 4 m | 5 Concrete | Start |
|  | Outer Corner Extension (4 m) | `QuarterPipeMiddleOutCorner_PolishedConcrete_4x4` | 4 × 4 × 4 m | 5 Concrete | Start |
|  | Outer Corner Quarter Pipe | `QuarterPipeCorner_03` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Quarter Pipes Pack |
|  | Outer Corner Quarter Pipe | `QuarterPipeOutCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Outer Corner Quarter Pipe | `QuarterPipeOutCorner_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Outer Corner Quarter Pipe | `QuarterPipeOutCorner_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Outer Corner Quarter Pipe | `QuarterPipeOutCorner_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Pipeline Floor Hole | `FoundationPassthrough_Pipe` |  | 2 Iron Rod, 2 Iron Plate, 2 Concrete | AWESOME Shop: Pipeline Floor Hole |
|  | Quarter Pipe | `QuarterPipe` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Quarter Pipe | `QuarterPipe_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Quarter Pipe | `QuarterPipe_ConcretePolished_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Quarter Pipe | `QuarterPipe_Concrete_8x4` | 8 × 8 × 4 m | 5 Concrete |  |
|  | Quarter Pipe | `QuarterPipe_Grip_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Ramp (1 m) | `Ramp_8x1_01` | 8 × 8 × 1 m | 5 Concrete | Tier 1: Base Building |
|  | Ramp (1 m) | `Ramp_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete |  |
|  | Ramp (1 m) | `Ramp_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Ramp (1 m) | `Ramp_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Ramp (2 m) | `Ramp_8x2_01` | 8 × 8 × 2 m | 5 Concrete | Tier 1: Base Building |
|  | Ramp (2 m) | `Ramp_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Ramp (2 m) | `Ramp_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete |  |
|  | Ramp (2 m) | `Ramp_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Ramp (2 m) | `Ramp_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Ramp (4 m) | `Ramp_8x4_01` | 8 × 8 × 4 m | 5 Concrete | Tier 1: Base Building |
|  | Ramp (4 m) | `Ramp_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Ramp (4 m) | `Ramp_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Ramp (4 m) | `Ramp_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Up Corner Ramp (1 m) | `Ramp_Diagonal_8x1_02` | 8 × 8 × 1 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
|  | Up Corner Ramp (1 m) | `Ramp_UpCorner_Concrete_8x1` | 8 × 8 × 1 m | 5 Concrete |  |
|  | Up Corner Ramp (1 m) | `Ramp_UpCorner_Metal_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Up Corner Ramp (1 m) | `Ramp_UpCorner_Polished_8x1` | 8 × 8 × 1 m | 5 Concrete | Start |
|  | Up Corner Ramp (2 m) | `Ramp_Diagonal_8x2_02` | 8 × 8 × 2 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
|  | Up Corner Ramp (2 m) | `Ramp_UpCorner_Asphalt_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Up Corner Ramp (2 m) | `Ramp_UpCorner_Concrete_8x2` | 8 × 8 × 2 m | 5 Concrete |  |
|  | Up Corner Ramp (2 m) | `Ramp_UpCorner_Metal_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Up Corner Ramp (2 m) | `Ramp_UpCorner_Polished_8x2` | 8 × 8 × 2 m | 5 Concrete | Start |
|  | Up Corner Ramp (4 m) | `Ramp_Diagonal_8x4_02` | 8 × 8 × 4 m | 5 Concrete | AWESOME Shop: Corner Ramp Pack |
|  | Up Corner Ramp (4 m) | `Ramp_UpCorner_Asphalt_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Up Corner Ramp (4 m) | `Ramp_UpCorner_Metal_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |
|  | Up Corner Ramp (4 m) | `Ramp_UpCorner_Polished_8x4` | 8 × 8 × 4 m | 5 Concrete | Start |

## Walls, doors & gates

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 36,42,46,52 | Automated Gate | `Gate_Automated_8x4` |  | 6 Iron Plate | AWESOME Shop: Gates |
| ✅ 36,52,58,60 | Basic Wall (1 m) | `SteelWall_8x1` |  | 2 Concrete | Start |
| ✅🎨 36,42,46,52,60 | Basic Wall (1 m) | `Wall_Concrete_8x1` |  | 2 Concrete |  |
| ✅🎨 36,42,46,60 | Basic Wall (1 m) | `Wall_Orange_8x1` |  | 2 Concrete | Tier 1: Base Building |
| ✅🎨 36,42,46,60 | Basic Wall (4 m) | `Wall_8x4_01` |  | 2 Concrete | Tier 1: Base Building |
| ✅ 36,52,58,60 | Basic Wall (4 m) | `Wall_8x4_02` |  | 2 Concrete | Start |
| ✅🎨 36,42,46,52,58,60 | Basic Wall (4 m) | `Wall_Concrete_8x4` |  | 2 Concrete |  |
| ✅ 36 | Center Door Wall | `Wall_Concrete_CDoor_8x4` |  | 2 Concrete |  |
| ✅🎨 42,46 | Center Door Wall | `Wall_Door_8x4_01` |  | 2 Concrete | AWESOME Shop: Door Walls |
| ✅ 52,58 | Frame Wall | `Wall_Frame_01` |  | 2 Steel Beam | AWESOME Shop: Structural Frame Set |
| ✅ 36 | Gate Hole Wall | `Wall_Concrete_Gate_8x4` |  | 2 Concrete |  |
| ✅🎨 42,46 | Gate Hole Wall | `Wall_Gate_8x4_01` |  | 2 Concrete | AWESOME Shop: Gates |
| ✅ 46 | High Barrier | `Barrier_Tall_01` |  | 1 Concrete, 1 Iron Plate | AWESOME Shop: Metal Barriers |
| ✅🎨 42,46 | Industrial Railing | `Fence_01` |  | 4 Iron Rod | Start |
| ✅ 46 | Inverted Ramp Wall (1 m) | `Wall_Concrete_FlipTris_8x1` |  |  |  |
| ✅ 42 | Inverted Ramp Wall (1 m) | `Wall_Orange_FlipTris_8x1` |  |  |  |
| ✅ 36,46 | Inverted Ramp Wall (2 m) | `Wall_Concrete_FlipTris_8x2` |  |  |  |
| ✅ 36 | Inverted Ramp Wall (4 m) | `Wall_Concrete_FlipTris_8x4` |  |  |  |
| ✅ 36,46 | Inverted Ramp Wall (8 m) | `Wall_Concrete_FlipTris_8x8` |  |  |  |
| ✅ 36 | Ramp Wall (1 m) | `Wall_Concrete_Tris_8x1` |  |  |  |
| ✅🎨 42 | Ramp Wall (1 m) | `Wall_Orange_Tris_8x1` |  |  |  |
| ✅ 36 | Ramp Wall (2 m) | `Wall_Concrete_Tris_8x2` |  |  |  |
| ✅ 36 | Ramp Wall (4 m) | `Wall_Concrete_Tris_8x4` |  |  |  |
| ✅ 42 | Ramp Wall (4 m) | `Wall_Orange_Tris_8x4` |  |  |  |
| ✅ 36 | Ramp Wall (8 m) | `Wall_Concrete_Tris_8x8` |  |  |  |
| ✅ 36,46 | Road Barrier | `Concrete_Barrier_01` |  | 2 Concrete | AWESOME Shop: Road Barriers |
| ✅🎨 58 | Roll-Up Gate | `BigGarageDoor_16x8` |  | 4 Concrete, 4 Iron Plate | Start |
| ✅🎨 42,46 | Side Door Wall | `Wall_Door_8x4_03` |  | 2 Concrete | AWESOME Shop: Door Walls |
| ✅ 36 | Side Door Wall | `Wall_Door_8x4_03_Steel` |  | 2 Concrete | Start |
| ✅ 36 | Tilted Corner Wall (8 m) | `Wall_Concrete_8x8_Corner_01` | 8 m | 2 Concrete |  |
| ✅ 36 | Tilted Wall (4 m) | `Wall_Concrete_Angular_8x4` |  | 2 Concrete |  |
| ✅ 36 | Tilted Wall (8 m) | `Wall_Concrete_Angular_8x8` |  | 2 Concrete |  |
| ✅ 46 | Tilted Wall (8 m) | `Wall_Orange_Angular_8x8` |  | 2 Concrete | AWESOME Shop: Tilted Walls |
|  | Center Door Wall | `Wall_Door_8x4_01_Steel` |  | 2 Concrete | Start |
|  | Construction Fence | `ChainLinkFence` |  | 2 Iron Rod | AWESOME Shop: Construction Fences |
|  | Corner Road Barrier | `Barrier_Corner` |  | 1 Concrete |  |
|  | Gate Hole Wall | `SteelWall_8x4_Gate_01` |  | 2 Concrete | Start |
|  | Inverted Ramp Wall (1 m) | `SteelWall_FlipTris_8x1` |  | 2 Concrete | Start |
|  | Inverted Ramp Wall (2 m) | `SteelWall_FlipTris_8x2` |  | 2 Concrete | Start |
|  | Inverted Ramp Wall (2 m) | `Wall_Orange_FlipTris_8x2` |  |  |  |
|  | Inverted Ramp Wall (4 m) | `SteelWall_FlipTris_8x4` |  | 2 Concrete | Start |
|  | Inverted Ramp Wall (4 m) | `Wall_Orange_FlipTris_8x4` |  |  |  |
|  | Inverted Ramp Wall (8 m) | `SteelWall_FlipTris_8x8` |  | 2 Concrete | Start |
|  | Inverted Ramp Wall (8 m) | `Wall_Orange_FlipTris_8x8` |  |  |  |
|  | Low Barrier | `Barrier_Low_01` |  | 1 Concrete, 1 Iron Plate | AWESOME Shop: Metal Barriers |
|  | Ramp Wall (1 m) | `SteelWall_Tris_8x1` |  | 2 Concrete | Start |
|  | Ramp Wall (2 m) | `SteelWall_Tris_8x2` |  | 2 Concrete | Start |
|  | Ramp Wall (2 m) | `Wall_Orange_Tris_8x2` |  |  |  |
|  | Ramp Wall (4 m) | `SteelWall_Tris_8x4` |  | 2 Concrete | Start |
|  | Ramp Wall (8 m) | `SteelWall_Tris_8x8` |  | 2 Concrete | Start |
|  | Ramp Wall (8 m) | `Wall_Orange_Tris_8x8` |  |  |  |
|  | Roll-Up Gate | `BigGarageDoor_16x8_Concrete` |  | 8 Concrete |  |
|  | Roll-Up Gate | `BigGarageDoor_16x8_Steel` |  | 4 Concrete, 4 Steel Beam | Start |
|  | Side Door Wall | `Wall_Concrete_SDoor_8x4` |  | 2 Concrete |  |
|  | Tarp Construction Fence | `TarpFence` |  | 2 Iron Rod | AWESOME Shop: Construction Fences |
|  | Tilted Concave Wall (4 m) | `Wall_Concrete_8x4_Corner_2` | 8 m | 2 Concrete |  |
|  | Tilted Concave Wall (4 m) | `Wall_Orange_8x4_Corner_02` | 8 m | 2 Concrete |  |
|  | Tilted Concave Wall (4 m) | `Wall_Steel_8x4_Corner_2` | 8 m | 2 Concrete |  |
|  | Tilted Concave Wall (8 m) | `Wall_Concrete_8x8_Corner_2` | 8 m | 2 Concrete |  |
|  | Tilted Concave Wall (8 m) | `Wall_Orange_8x8_Corner_02` | 8 m | 2 Concrete |  |
|  | Tilted Concave Wall (8 m) | `Wall_Steel_8x8_Corner_2` | 8 m | 2 Concrete |  |
|  | Tilted Corner Wall (4 m) | `Wall_Concrete_8x4_Corner_01` | 8 m | 2 Concrete |  |
|  | Tilted Corner Wall (4 m) | `Wall_Orange_8x4_Corner_01` | 8 m | 2 Concrete |  |
|  | Tilted Corner Wall (4 m) | `Wall_Steel_8x4_Corner_01` | 8 m | 2 Concrete |  |
|  | Tilted Corner Wall (8 m) | `Wall_Orange_8x8_Corner_01` | 8 m | 2 Concrete |  |
|  | Tilted Corner Wall (8 m) | `Wall_Steel_8x8_Corner_01` | 8 m | 2 Concrete |  |
|  | Tilted Wall (4 m) | `SteelWall_8x4` |  |  |  |
|  | Tilted Wall (4 m) | `WallSet_Steel_Angular_8x4` |  | 2 Concrete | Start |
|  | Tilted Wall (4 m) | `Wall_Orange_Angular_8x4` |  | 2 Concrete | AWESOME Shop: Tilted Walls |
|  | Tilted Wall (8 m) | `WallSet_Steel_Angular_8x8` |  | 2 Concrete | Start |
|  | Wall-Mounted Flood Light | `FloodlightWall` |  | 25 Quickwire, 4 Copper Sheet, 2 Encased Industrial Beam | AWESOME Shop: Flood Lights |

## Beams & pillars

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅🎨 36,42,46,52 | Beam Connector | `Beam_Connector` |  | 2 Concrete |  |
| ✅🎨 36,42,46 | Beam Support | `Beam_Support` |  | 2 Concrete | AWESOME Shop: Structural Cable Pack |
| ✅🎨 42,46,60 | Big Concrete Pillar | `PillarMiddle_Concrete` |  | 5 Concrete |  |
| ✅🎨 46,52 | Big Frame Pillar | `PillarMiddle_Frame` |  | 5 Steel Beam | AWESOME Shop: Frame Pillar Set |
| ✅ 46 | Big Metal Pillar | `PillarMiddle` |  | 2 Iron Plate, 3 Concrete | AWESOME Shop: Metal Pillar Set |
| ✅🎨 36,46,60 | Big Pillar Support | `PillarBase` |  | 5 Concrete | AWESOME Shop: Metal Pillar Set |
| ✅ 36,46 | Double Beam Connector | `Beam_Connector_Double` |  | 2 Concrete |  |
| ✅ 36,42,46 | Metal Beam | `Beam` | length 4–40 m | 1 Steel Beam per 4 m | AWESOME Shop: Structural Cable Pack |
| ✅🎨 36,42,46,52 | Painted Beam | `Beam_Painted` | length 4–40 m | 1 Steel Beam per 4 m | AWESOME Shop: Structural Beam Pack |
| ✅🎨 36,42,46,58,60 | Small Concrete Pillar | `Pillar_Small_Concrete` |  | 3 Concrete |  |
| ✅ 36,46 | Small Frame Pillar | `Pillar_Small_Frame` |  | 3 Steel Beam | AWESOME Shop: Frame Pillar Set |
| ✅ 42,46,52,58 | Small Metal Pillar | `Pillar_Small_Metal` |  | 1 Iron Plate, 2 Concrete | AWESOME Shop: Metal Pillar Set |
| ✅🎨 36,46,52 | Small Pillar Support | `PillarBase_Small` |  | 3 Concrete | AWESOME Shop: Metal Pillar Set |
|  | Braided Cable | `Beam_Cable` | length 1–40 m | 1 Steel Beam per 4 m |  |
|  | Braided Cable Cluster | `Beam_Cable_Cluster` | length 1–40 m | 1 Steel Beam per 4 m |  |
|  | Cross Beam | `Beam_Cross` | length 1–40 m | 1 Steel Beam per 4 m |  |
|  | H-Beam | `Beam_H` | length 1–40 m | 1 Steel Beam per 4 m | AWESOME Shop: Beam Expansion Pack |
|  | Pillar Top | `PillarTop` |  |  |  |
|  | Round Concrete Beam | `Beam_Concrete` | length 1–40 m | 1 Concrete per 4 m |  |

## Walkways, stairs & catwalks

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅🎨 36,42 | Catwalk Corner | `CatwalkCorner` | 4 m |  |  |
| ✅ 36 | Catwalk Intersection | `CatwalkCross` | 4 m | 2 Iron Rod, 1 Iron Plate |  |
| ✅🎨 36 | Catwalk Stairs | `CatwalkStairs` | 4 m | 2 Iron Rod, 1 Iron Plate | AWESOME Shop: Modern Catwalks |
| ✅🎨 36,42 | Catwalk T-Junction | `CatwalkT` | 4 m | 2 Iron Rod, 1 Iron Plate | AWESOME Shop: Modern Catwalks |
| ✅🎨 36,46,52 | Ladder | `Ladder` |  | 2 Iron Rod | AWESOME Shop: Factory Ladder |
| ✅ 36,46 | Straight Catwalk | `CatwalkStraight` | 4 m | 2 Iron Rod, 1 Iron Plate | AWESOME Shop: Modern Catwalks |
| ✅ 42 | Straight Walkway | `WalkwayStraight` | 4 m | 2 Iron Rod, 1 Iron Plate | Start |
| ✅ 42 | Walkway Corner | `WalkwayTrun` | 4 m |  |  |
| ✅ 42 | Walkway Intersection | `WalkwayCross` | 4 m | 2 Iron Rod, 1 Iron Plate |  |
| ✅ 42 | Walkway T-Junction | `WalkwayT` | 4 m | 2 Iron Rod, 1 Iron Plate | Start |
|  | Jump Pad | `JumpPadAdjustable` |  | 2 Rotor, 15 Iron Plate, 10 Cable | Tier 2: Jump Pads |
|  | Personnel Elevator | `Elevator` |  | 1 Steel Beam, 1 Silica | AWESOME Shop: Personnel Elevator |
|  | Space Elevator | `SpaceElevator` |  | 500 Concrete, 250 Iron Plate, 400 Iron Rod, 1500 Wire | Onboarding: HUB Upgrade 6 |
|  | Stairs Left | `Stairs_Left_01` | 8 m | 3 Concrete, 3 Iron Plate | Start |
|  | Stairs Right | `Stairs_Right_01` | 8 m | 3 Concrete, 3 Iron Plate | Start |

## Lights & signs

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 36,42 | Display Sign | `StandaloneWidgetSign_Medium` |  | 2 Reinforced Iron Plate, 5 Quartz Crystal | AWESOME Shop: Display Sign Bundle |
| ✅ 36,42,46 | Label Sign (2 m) | `StandaloneWidgetSign_Small` |  | 2 Iron Plate, 2 Quartz Crystal | AWESOME Shop: Label Sign Bundle |
| ✅ 36,42,46 | Label Sign (3 m) | `StandaloneWidgetSign_SmallWide` |  | 3 Iron Plate, 3 Quartz Crystal | AWESOME Shop: Label Sign Bundle |
| ✅ 36,42,46 | Label Sign (4 m) | `StandaloneWidgetSign_SmallVeryWide` |  | 4 Iron Plate, 4 Quartz Crystal | AWESOME Shop: Label Sign Bundle |
| ✅ 46,60 | Large Billboard | `StandaloneWidgetSign_Huge` |  | 12 Encased Industrial Beam, 20 Copper Sheet, 5 Crystal Oscillator | AWESOME Shop: Billboard Set |
| ✅ 58 | Light Control Panel | `LightsControlPanel` |  | 10 Cable, 5 Reinforced Iron Plate, 3 AI Limiter | AWESOME Shop: Light Control Panel |
| ✅ 36,42 | Portrait Sign | `StandaloneWidgetSign_Portrait` |  | 4 Reinforced Iron Plate, 10 Quartz Crystal | AWESOME Shop: Display Sign Bundle |
| ✅ 42,46,60 | Small Billboard | `StandaloneWidgetSign_Large` |  | 3 Encased Industrial Beam, 4 Copper Sheet, 1 Crystal Oscillator | AWESOME Shop: Billboard Set |
| ✅ 36,42,46 | Square Sign (0.5 m) | `StandaloneWidgetSign_Square_Tiny` |  | 1 Iron Plate, 1 Quartz Crystal | AWESOME Shop: Label Sign Bundle |
| ✅ 36,42,58 | Square Sign (1 m) | `StandaloneWidgetSign_Square_Small` |  | 1 Reinforced Iron Plate, 5 Quartz Crystal | AWESOME Shop: Display Sign Bundle |
| ✅ 36,42,46,52,58 | Square Sign (2 m) | `StandaloneWidgetSign_Square` |  | 3 Reinforced Iron Plate, 10 Quartz Crystal | AWESOME Shop: Display Sign Bundle |
|  | Ceiling Light | `CeilingLight` |  | 50 Quickwire, 16 Wire, 6 Steel Beam | AWESOME Shop: Indoor Lighting |
|  | Flood Light Tower | `FloodlightPole` |  | 25 Quickwire, 4 Copper Sheet, 8 Encased Industrial Beam | AWESOME Shop: Flood Lights |
|  | Street Light | `StreetLight` |  | 10 Quickwire, 4 Wire, 4 Iron Rod | AWESOME Shop: Street Light |

## Special & other

| Ready | Piece | Class | Size | Cost | Unlock |
|---|---|---|---|---|---|
| ✅ 46 | AWESOME Sink | `ResourceSink` |  | 15 Reinforced Iron Plate, 30 Cable, 45 Concrete | Tier 2: Resource Sink Bonus Program |
| ✅ 36 | Crafting Bench | `WorkBench` |  | 3 Iron Plate, 3 Iron Rod | Start |
| ✅ 36 | Equipment Workshop | `Workshop` |  | 6 Iron Plate, 4 Iron Rod | Onboarding: HUB Upgrade 1 |
| ✅ 52,60 | Large Fan | `LargeFan` |  | 1 Iron Plate, 1 Copper Sheet | AWESOME Shop: Ventilation Bundle |
|  | AWESOME Shop | `ResourceSinkShop` |  | 200 Screws, 10 Iron Plate, 10 Cable | Tier 2: Resource Sink Bonus Program |
|  | Blueprint Designer Mk.1 | `BlueprintDesigner` |  | 15 Modular Frame, 25 Cable, 100 Concrete, 100 Steel Beam | Tier 4: FICSIT Blueprints |
|  | Blueprint Designer Mk.2 | `BlueprintDesigner_MK2` |  | 10 Heavy Modular Frame, 20 Computer, 100 Rubber, 100 Concrete | Tier 6: FICSIT Blueprints Mk.2 |
|  | Blueprint Designer Mk.3 | `BlueprintDesigner_Mk3` |  |  |  |
|  | FICSMAS Candy Cane | `CandyCaneDecor` |  | 10 Candy Cane, 1 FICSMAS Bow | MAM: Candy Cane Decor |
|  | FICSMAS Decoration | `WreathDecor` |  | 1 FICSMAS Wreath, 1 FICSMAS Bow | MAM: FICSMAS Decoration |
|  | FICSMAS Gift Tree | `TreeGiftProducer` |  | 50 FICSMAS Gift, 100 FICSMAS Tree Branch, 30 Red FICSMAS Ornament, 30 Blue FICSMAS Ornament | MAM: FICSMAS Gift Tree |
|  | FICSMAS Snow Cannon | `SnowCannon` |  | 10 FICSMAS Bow, 100 FICSMAS Actual Snow, 20 Copper FICSMAS Ornament | MAM: It's Snowing! |
|  | FICSMAS Snow Dispenser | `SnowDispenser` |  | 10 Candy Cane, 100 FICSMAS Actual Snow, 20 Iron FICSMAS Ornament | MAM: It's Snowing! |
|  | FICSMAS Snowman | `Snowman` |  | 50 FICSMAS Actual Snow, 3 Candy Cane, 1 FICSMAS Bow, 3 Red FICSMAS Ornament, 2 Blue FICSMAS Ornament | MAM: A Friend |
|  | Giant FICSMAS Tree | `XmassTree` |  |  |  |
|  | Large Vent | `LargeVent` |  | 1 Iron Plate, 1 Copper Sheet | AWESOME Shop: Ventilation Bundle |
|  | Lookout Tower | `LookoutTower` |  | 5 Iron Plate, 5 Iron Rod | Tier 1: Base Building |
|  | MAM | `Mam` |  | 5 Reinforced Iron Plate, 15 Cable, 45 Wire | Tier 1: Field Research |
|  | Main Portal | `Portal` |  | 5 Turbo Motor, 10 Radio Control Unit, 15 Superposition Oscillator, 25 SAM Fluctuator, 50 Ficsite Trigon | Tier 9: Spatial Energy Regulation |
|  | Radar Tower | `RadarTower` |  | 10 Computer, 20 Heavy Modular Frame, 25 Crystal Oscillator, 100 Cable | MAM: Radar Technology |
|  | SPWN | `PortalPotty` |  | 20 Steel Pipe, 5 Modular Frame, 100 Biomass, 20 Reanimated SAM | MAM: SPWN |
|  | Satellite Portal | `PortalSatellite` |  | 5 Radio Control Unit, 10 Superposition Oscillator, 25 SAM Fluctuator, 25 Ficsite Trigon | Tier 9: Spatial Energy Regulation |
|  | The HUB | `TradingPost` |  | 20 Iron Ore | Start |

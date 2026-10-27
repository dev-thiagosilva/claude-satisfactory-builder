using CUE4Parse.Compression;
using CUE4Parse.Encryption.Aes;
using CUE4Parse.FileProvider;
using CUE4Parse.MappingsProvider;
using CUE4Parse.MappingsProvider.Usmap;
using CUE4Parse.UE4.Objects.Core.Misc;
using CUE4Parse.UE4.Versions;
using CUE4Parse.UE4.Assets.Exports.Component.Landscape;
using System.Text.RegularExpressions;
using Serilog;

// terrain <mode> <game dir> <oodle dll | managed> [arg]
//   extract <out dir>  ground heights of every landscape tile (heights.bin, tiles.json)
//   hlod <out dir>     cliffs and rocks: the game's simplified far-view models, world space (rocks.bin, rocks.json)
//   water <out dir>    top faces of every water volume (water.json)
//   probe <filter>     list game files whose path contains filter
//   cells [n]          classes of exports in the world-partition cells (first n with landscape shown)
//   classes|meshes|dump <package> [type]   look inside one package; reflect <name> lists library types
Log.Logger = new LoggerConfiguration().MinimumLevel.Warning().WriteTo.Console().CreateLogger();
var mode = args[0];
var game = args[1];
if (args[2] != "managed") OodleHelper.Initialize(args[2]);
var provider = new DefaultFileProvider(Path.Combine(game, "FactoryGame", "Content", "Paks"), SearchOption.TopDirectoryOnly,
    new VersionContainer(EGame.GAME_UE5_6), StringComparer.OrdinalIgnoreCase);
if (Environment.GetEnvironmentVariable("TERRAIN_USMAP") != "0")
    provider.MappingsContainer = new FileUsmapTypeMappingsProvider(Path.Combine(game, "CommunityResources", "FactoryGame.usmap"));
provider.Initialize();
provider.Mount();
provider.SubmitKey(new FGuid(), new FAesKey(new byte[32]));
provider.PostMount();
var arg = args.Length > 3 ? args[3] : "";
// Satisfactory's own foliage component is a plain foliage component underneath: register it so its
// per-instance transforms (the trees, bushes and boulders) are read instead of skipped
CUE4Parse.UE4.Assets.ObjectTypeRegistry.RegisterClass("FGFoliageInstancedSMC",
    typeof(CUE4Parse.UE4.Assets.Exports.Component.StaticMesh.UFoliageInstancedStaticMeshComponent));

if (mode == "probe")
{
    Console.WriteLine($"files {provider.Files.Count}");
    foreach (var f in provider.Files.Keys.Where(k => k.Contains(arg, StringComparison.OrdinalIgnoreCase)).Take(40))
        Console.WriteLine(f);
}
else if (mode == "extract")
{
    // extract <out dir>: every landscape tile's full-detail heights.
    //   heights.bin: per tile 128 x 128 uint16 (row-major, y then x), raw landscape height values
    //   tiles.json:  per tile, in heights.bin order: [sectionBaseX, sectionBaseY, size, world x, world y of
    //                vertex (0,0) in cm, world z base, xy scale, z scale]; world z = base + (h - 32768) / 128 * z scale
    var outDir = arg;
    Directory.CreateDirectory(outDir);
    var persistent = provider.LoadPackage("FactoryGame/Content/FactoryGame/Map/GameLevel01/Persistent_Level.umap");
    var land = persistent.GetExports().First(e => e.ExportType == "Landscape");
    var root = land.GetOrDefault<CUE4Parse.UE4.Objects.UObject.FPackageIndex>("RootComponent").Load();
    var loc = root.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FVector>("RelativeLocation");
    var scale = root.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FVector>("RelativeScale3D", new CUE4Parse.UE4.Objects.Core.Math.FVector(1, 1, 1));
    var rot = root.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FRotator>("RelativeRotation");
    Console.WriteLine($"landscape at {loc} scale {scale} rot {rot}");

    var cells = provider.Files.Keys.Where(k => k.Contains("GameLevel01/Persistent_Level/_Generated_/") && k.EndsWith(".umap")).ToList();
    using var bin = File.Create(Path.Combine(outDir, "heights.bin"));
    var tiles = new List<int[]>();
    int done = 0, failed = 0;
    foreach (var c in cells)
    {
        CUE4Parse.UE4.Assets.IPackage pkg;
        List<CUE4Parse.UE4.Assets.Exports.UObject> exports;
        try { pkg = provider.LoadPackage(c); exports = pkg.GetExports().ToList(); }
        catch (Exception e) { Console.WriteLine($"! {c}: {e.Message}"); continue; }
        if (!exports.Any(e => e.ExportType == "LandscapeStreamingProxy")) continue;
        // A cell can hold several sections, and texture names (Heightmap_0...) repeat in each one:
        // match textures by their full path, and take every tile's transform from its own section.
        var factories = exports.OfType<ULandscapeTextureStorageProviderFactory>().ToList();
        foreach (var comp in exports.Where(e => e.ExportType == "LandscapeComponent"))
        {
            try
            {
                // each section has its own world transform: tile (0,0) = root + (SectionBase - SectionOffset) * scale
                var proxy = exports.First(e => e.ExportType == "LandscapeStreamingProxy" && e.Name == comp.Outer?.Name);
                var proot = exports.First(e => e.ExportType == "SceneComponent" && e.Outer?.Name == proxy.Name);
                var ploc = proot.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FVector>("RelativeLocation");
                var pscale = proot.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FVector>("RelativeScale3D", new CUE4Parse.UE4.Objects.Core.Math.FVector(1, 1, 1));
                var poff = proxy.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FIntPoint>("LandscapeSectionOffset");
                int sx = comp.GetOrDefault<int>("SectionBaseX"), sy = comp.GetOrDefault<int>("SectionBaseY");
                int quads = comp.GetOrDefault<int>("ComponentSizeQuads");
                var tex = comp.GetOrDefault<CUE4Parse.UE4.Objects.UObject.FPackageIndex>("HeightmapTexture");
                var bias = comp.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FVector4>("HeightmapScaleBias");
                var texPath = tex.ResolvedObject?.GetPathName();
                var f = factories.Single(x => x.Texture.ResolvedObject?.GetPathName() == texPath);
                var mip = f.Mips[0];
                var src = mip.BulkData.Data;
                var dst = new byte[mip.SizeX * mip.SizeY * 4];
                if (mip.bCompressed) f.DecompressMip(src, src.Length, dst, dst.Length, 0);
                else Array.Copy(src, dst, Math.Min(src.Length, dst.Length));
                int ox = (int)Math.Round(bias.Z * mip.SizeX), oy = (int)Math.Round(bias.W * mip.SizeY), n = quads + 1;
                var buf = new byte[n * n * 2];
                for (int y = 0; y < n; y++)
                    for (int x = 0; x < n; x++)
                    {
                        int p = ((oy + y) * mip.SizeX + ox + x) * 4;          // FColor is B, G, R, A
                        ushort h = (ushort)((dst[p + 2] << 8) | dst[p + 1]);
                        buf[(y * n + x) * 2] = (byte)(h & 0xFF); buf[(y * n + x) * 2 + 1] = (byte)(h >> 8);
                    }
                bin.Write(buf);
                tiles.Add(new[] { sx, sy, n, (int)Math.Round(ploc.X + (sx - poff.X) * pscale.X), (int)Math.Round(ploc.Y + (sy - poff.Y) * pscale.Y),
                                  (int)Math.Round(ploc.Z), (int)Math.Round(pscale.X), (int)Math.Round(pscale.Z) });
                done++;
            }
            catch (Exception e) { if (failed++ < 5) Console.WriteLine($"! {c} {comp.Name}: {e.Message}"); }
        }
    }
    File.WriteAllText(Path.Combine(outDir, "tiles.json"), Newtonsoft.Json.JsonConvert.SerializeObject(new
    {
        location = new[] { loc.X, loc.Y, loc.Z }, scale = new[] { scale.X, scale.Y, scale.Z },
        yaw = rot.Yaw, zscale = 1.0 / 128, mid = 32768, tiles
    }));
    Console.WriteLine($"tiles {done}, failed {failed}");
}
else if (mode == "tile")
{
    // tile <sx,sy>: where one landscape tile's heights come from (debugging)
    var want = arg.Split(',').Select(int.Parse).ToArray();
    foreach (var c in provider.Files.Keys.Where(k => k.Contains("GameLevel01/Persistent_Level/_Generated_/") && k.EndsWith(".umap")))
    {
        List<CUE4Parse.UE4.Assets.Exports.UObject> exports;
        try { exports = provider.LoadPackage(c).GetExports().ToList(); } catch { continue; }
        foreach (var comp in exports.Where(e => e.ExportType == "LandscapeComponent"))
        {
            if (comp.GetOrDefault<int>("SectionBaseX") != want[0] || comp.GetOrDefault<int>("SectionBaseY") != want[1]) continue;
            var tex = comp.GetOrDefault<CUE4Parse.UE4.Objects.UObject.FPackageIndex>("HeightmapTexture");
            Console.WriteLine($"{c}\n  comp {comp.Name} outer {comp.Outer?.Name}\n  tex {tex} import={tex.IsImport} resolved={tex.ResolvedObject?.GetPathName()}");
            Console.WriteLine($"  bias {comp.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FVector4>("HeightmapScaleBias")}");
            foreach (var f in exports.OfType<ULandscapeTextureStorageProviderFactory>())
                Console.WriteLine($"  factory {f.Name} tex {f.Texture} {f.Texture.ResolvedObject?.GetPathName()} mip0 {f.Mips[0].SizeX}");
            foreach (var p in exports.Where(e => e.ExportType == "LandscapeStreamingProxy")) Console.WriteLine($"  proxy {p.Name}");
        }
    }
}
else if (mode == "reflect")
{
    foreach (var t in typeof(DefaultFileProvider).Assembly.GetTypes().Where(t => t.Name.Contains(arg)))
    {
        Console.WriteLine($"{t.FullName} : {t.BaseType?.Name}");
        foreach (var m in t.GetMembers(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic |
                                       System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.DeclaredOnly))
            Console.WriteLine($"   {m.MemberType} {m}");
    }
}
else if (mode == "classes")
{
    // classes <package path>: export types in one package (e.g. the persistent level)
    foreach (var g in provider.LoadPackage(arg).GetExports().GroupBy(e => e.ExportType).OrderByDescending(g => g.Count()))
        Console.WriteLine($"  {g.Key} {g.Count()}");
}
else if (mode == "hlod")
{
    // hlod <out dir> [label filter]: the game's simplified far-view models (cliffs, rocks...) in world space.
    //   rocks.bin: per mesh uint32 vertex count, uint32 index count, float32 xyz (cm) per vertex, uint32 indices
    //   rocks.json: [label, LOD level] per mesh, in rocks.bin order
    var outDir = arg; var want = args.Length > 4 ? args[4] : "WPHLOD_Landscape/";
    Directory.CreateDirectory(outDir);
    var pkg = provider.LoadPackage("FactoryGame/Content/FactoryGame/Map/GameLevel01/Persistent_Level.umap");
    using var bin = new BinaryWriter(File.Create(Path.Combine(outDir, "rocks.bin")));
    var list = new List<object[]>(); long tris = 0;
    foreach (var h in pkg.GetExports().Where(e => e.ExportType == "WorldPartitionHLOD"))
    {
        var label = Newtonsoft.Json.Linq.JObject.FromObject(h)["ActorLabel"]?.ToString() ?? "";
        if (!label.StartsWith(want) || !label.Contains("_L0_")) continue;
        var comp = h.GetOrDefault<CUE4Parse.UE4.Objects.UObject.FPackageIndex>("RootComponent")?.Load();
        var meshRef = comp?.GetOrDefault<CUE4Parse.UE4.Objects.UObject.FPackageIndex>("StaticMesh");
        if (meshRef == null || !meshRef.TryLoad(out CUE4Parse.UE4.Assets.Exports.StaticMesh.UStaticMesh mesh)) continue;
        var lod = mesh.RenderData?.LODs?.FirstOrDefault(l => l.IndexBuffer != null && l.IndexBuffer.Length > 0);
        if (lod == null) continue;
        var loc = comp.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FVector>("RelativeLocation");
        var rot = comp.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FRotator>("RelativeRotation").Quaternion();
        var scl = comp.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FVector>("RelativeScale3D", new CUE4Parse.UE4.Objects.Core.Math.FVector(1, 1, 1));
        var verts = lod.PositionVertexBuffer.Verts; var idx = lod.IndexBuffer.Buffer;
        bin.Write((uint)verts.Length); bin.Write((uint)idx.Length);
        foreach (var v in verts)
        {
            var w = rot.RotateVector(new CUE4Parse.UE4.Objects.Core.Math.FVector(v.X * scl.X, v.Y * scl.Y, v.Z * scl.Z)) + loc;
            bin.Write(w.X); bin.Write(w.Y); bin.Write(w.Z);
        }
        foreach (var i in idx) bin.Write(i);
        list.Add(new object[] { label, h.GetOrDefault<int>("LODLevel") });
        tris += idx.Length / 3;
    }
    File.WriteAllText(Path.Combine(outDir, "rocks.json"), Newtonsoft.Json.JsonConvert.SerializeObject(list));
    Console.WriteLine($"meshes {list.Count}, triangles {tris}");
}
else if (mode == "water")
{
    // water <out dir>: top faces of every FGWaterVolume (lakes, rivers, ocean) in world cm.
    //   water.json: [[name, [x, y, z, x, y, z, ...] (triangles)], ...]
    var outDir = arg;
    Directory.CreateDirectory(outDir);
    var packages = new List<string> { "FactoryGame/Content/FactoryGame/Map/GameLevel01/Persistent_Level.umap" };
    packages.AddRange(provider.Files.Keys.Where(k => k.Contains("GameLevel01/Persistent_Level/_Generated_/") && k.EndsWith(".umap")));
    var result = new List<object[]>(); int volumes = 0;
    foreach (var p in packages)
    {
        List<CUE4Parse.UE4.Assets.Exports.UObject> exports;
        try { exports = provider.LoadPackage(p).GetExports().ToList(); } catch { continue; }
        foreach (var vol in exports.Where(e => e.ExportType == "FGWaterVolume"))
        {
            var bc = vol.GetOrDefault<CUE4Parse.UE4.Objects.UObject.FPackageIndex>("BrushComponent")?.Load();
            var bs = bc?.GetOrDefault<CUE4Parse.UE4.Objects.UObject.FPackageIndex>("BrushBodySetup")?.Load();
            if (bs == null) continue;
            var loc = bc.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FVector>("RelativeLocation");
            var rot = bc.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FRotator>("RelativeRotation").Quaternion();
            var scl = bc.GetOrDefault<CUE4Parse.UE4.Objects.Core.Math.FVector>("RelativeScale3D", new CUE4Parse.UE4.Objects.Core.Math.FVector(1, 1, 1));
            var elems = Newtonsoft.Json.Linq.JObject.FromObject(bs)["Properties"]?["AggGeom"]?["ConvexElems"];
            if (elems == null) continue;
            var tris = new List<double>();
            foreach (var el in elems)
            {
                var vs = el["VertexData"].Select(v => rot.RotateVector(new CUE4Parse.UE4.Objects.Core.Math.FVector(
                    (float)v["X"] * scl.X, (float)v["Y"] * scl.Y, (float)v["Z"] * scl.Z)) + loc).ToList();
                var ix = el["IndexData"]?.Select(i => (int)i).ToList() ?? new List<int>();
                if (vs.Count == 0) continue;
                double zmin = vs.Min(v => v.Z), zmax = vs.Max(v => v.Z);
                for (int t = 0; t + 2 < ix.Count; t += 3)
                {
                    var a = vs[ix[t]]; var b = vs[ix[t + 1]]; var c = vs[ix[t + 2]];
                    double ux = b.X - a.X, uy = b.Y - a.Y, uz = b.Z - a.Z, wx = c.X - a.X, wy = c.Y - a.Y, wz = c.Z - a.Z;
                    double nx = uy * wz - uz * wy, ny = uz * wx - ux * wz, nz = ux * wy - uy * wx, len = Math.Sqrt(nx * nx + ny * ny + nz * nz);
                    if (len == 0 || Math.Abs(nz) / len < 0.7 || (a.Z + b.Z + c.Z) / 3 < (zmin + zmax) / 2) continue;   // top faces only
                    foreach (var v in new[] { a, b, c }) { tris.Add(Math.Round(v.X)); tris.Add(Math.Round(v.Y)); tris.Add(Math.Round(v.Z)); }
                }
            }
            if (tris.Count > 0) { result.Add(new object[] { vol.Name, tris }); volumes++; }
        }
    }
    File.WriteAllText(Path.Combine(outDir, "water.json"), Newtonsoft.Json.JsonConvert.SerializeObject(result));
    Console.WriteLine($"water volumes {volumes}");
}
else if (mode == "objects")
{
    // objects <out dir> [min size cm]: trees, boulders, plants, wrecks and other placed models of at least
    // min size (default 300 cm), skipping grass and the game's far-view duplicates.
    //   objects.bin:  uint32 model count; per model uint32 vertex count, uint32 index count, float32 xyz (cm, model
    //                 space) per vertex, uint32 indices (its simplest detail level); then the copies, grouped by area:
    //                 per copy uint16 model, uint16 0, float32 x y z (cm), float32 quaternion x y z w, float32 scale x y z
    //   objects.json: models [{name, kind, tris, size}], areas {"ax,ay": [byte offset, count]} (500 m areas)
    var outDir = arg; var minSize = args.Length > 4 ? float.Parse(args[4]) : 300f;
    Directory.CreateDirectory(outDir);
    var packages = new List<string> { "FactoryGame/Content/FactoryGame/Map/GameLevel01/Persistent_Level.umap" };
    packages.AddRange(provider.Files.Keys.Where(k => k.Contains("GameLevel01/Persistent_Level/_Generated_/") && k.EndsWith(".umap")));
    var models = new List<(string path, CUE4Parse.UE4.Assets.Exports.StaticMesh.FStaticMeshLODResources lod, float size)>();
    var modelIndex = new Dictionary<string, int>();          // -1 = too small / unusable
    var copies = new Dictionary<(int, int), List<byte[]>>();
    int unresolved = 0, kept = 0;
    T Prop<T>(CUE4Parse.UE4.Assets.Exports.UObject o, string name, T def)
    {
        for (int depth = 0; o != null && depth < 4; depth++)
        {
            if (o.Properties.Any(p => p.Name.Text == name)) return o.GetOrDefault<T>(name, def);
            o = o.Template?.Load();
        }
        return def;
    }
    (CUE4Parse.UE4.Objects.Core.Math.FVector loc, CUE4Parse.UE4.Objects.Core.Math.FQuat rot, CUE4Parse.UE4.Objects.Core.Math.FVector scl) World(CUE4Parse.UE4.Assets.Exports.UObject c, int depth = 0)
    {
        var loc = Prop(c, "RelativeLocation", new CUE4Parse.UE4.Objects.Core.Math.FVector(0, 0, 0));
        var rot = Prop(c, "RelativeRotation", new CUE4Parse.UE4.Objects.Core.Math.FRotator(0, 0, 0)).Quaternion();
        var scl = Prop(c, "RelativeScale3D", new CUE4Parse.UE4.Objects.Core.Math.FVector(1, 1, 1));
        var parent = Prop<CUE4Parse.UE4.Objects.UObject.FPackageIndex>(c, "AttachParent", null);
        if (parent == null || parent.IsNull || depth > 8) return (loc, rot, scl);
        CUE4Parse.UE4.Assets.Exports.UObject po;
        try { po = parent.Load(); } catch { return (loc, rot, scl); }
        if (po == null) return (loc, rot, scl);
        var (pl, pr, ps) = World(po, depth + 1);
        var p = pr.RotateVector(new CUE4Parse.UE4.Objects.Core.Math.FVector(loc.X * ps.X, loc.Y * ps.Y, loc.Z * ps.Z)) + pl;
        return (p, pr * rot, new CUE4Parse.UE4.Objects.Core.Math.FVector(scl.X * ps.X, scl.Y * ps.Y, scl.Z * ps.Z));
    }
    int ModelOf(CUE4Parse.UE4.Objects.UObject.FPackageIndex mesh)
    {
        var path = mesh?.ResolvedObject?.GetPathName();
        if (path == null) return -1;
        if (modelIndex.TryGetValue(path, out var id)) return id;
        id = -1;
        if (!Regex.IsMatch(path, "Waterfall|RiverPlane|WaterPlane|Grassfields|/Grass/|Fog", RegexOptions.IgnoreCase) &&
            mesh.TryLoad(out CUE4Parse.UE4.Assets.Exports.StaticMesh.UStaticMesh sm) && sm.RenderData?.LODs != null)
        {
            var b = sm.RenderData.Bounds.BoxExtent; var size = 2 * Math.Max(b.X, Math.Max(b.Y, b.Z));
            // the most detailed level within a triangle budget (trees keep their crown and trunk), else the simplest
            var usable = sm.RenderData.LODs.Where(l => l.IndexBuffer != null && l.IndexBuffer.Length > 0 && l.PositionVertexBuffer?.Verts != null).ToList();
            var budget = Regex.IsMatch(path, "/Trees?/|Tree|Palm|Kapok|Bamboo", RegexOptions.IgnoreCase) ? 600 : 400;
            // levels of a dozen triangles or fewer are flat cards (impostors): use the simplest real model, up to 3,000
            var solid = usable.Where(l => l.IndexBuffer.Length / 3 > 12).ToList();
            var lod = solid.FirstOrDefault(l => l.IndexBuffer.Length / 3 <= budget)
                      ?? solid.LastOrDefault(l => l.IndexBuffer.Length / 3 <= 3000) ?? usable.LastOrDefault();
            if (size >= minSize && lod != null) { id = models.Count; models.Add((path, lod, size)); }
        }
        modelIndex[path] = id;
        return id;
    }
    void Add(int model, CUE4Parse.UE4.Objects.Core.Math.FVector p, CUE4Parse.UE4.Objects.Core.Math.FQuat q, CUE4Parse.UE4.Objects.Core.Math.FVector s)
    {
        var rec = new byte[44];
        BitConverter.TryWriteBytes(rec.AsSpan(0), (ushort)model);
        var f = new[] { p.X, p.Y, p.Z, q.X, q.Y, q.Z, q.W, s.X, s.Y, s.Z };
        for (int i = 0; i < 10; i++) BitConverter.TryWriteBytes(rec.AsSpan(4 + i * 4), (float)f[i]);
        var key = ((int)Math.Floor(p.X / 50000), (int)Math.Floor(p.Y / 50000));
        if (!copies.TryGetValue(key, out var list)) copies[key] = list = new List<byte[]>();
        list.Add(rec); kept++;
    }
    foreach (var pk in packages)
    {
        List<CUE4Parse.UE4.Assets.Exports.UObject> exports;
        try { exports = provider.LoadPackage(pk).GetExports().ToList(); } catch { continue; }
        foreach (var e in exports.OfType<CUE4Parse.UE4.Assets.Exports.Component.StaticMesh.UStaticMeshComponent>())
        {
            if (e is CUE4Parse.UE4.Assets.Exports.Component.UHLODInstancedStaticMeshComponent) continue;
            var outerName = e.Outer?.Name.Text ?? "";
            if (outerName.StartsWith("WPHLOD") || outerName.Contains("WorldPartitionHLOD")) continue;
            int model;
            try { model = ModelOf(Prop<CUE4Parse.UE4.Objects.UObject.FPackageIndex>(e, "StaticMesh", null)); }
            catch { unresolved++; continue; }
            if (model < 0) continue;
            var (cl, cr, cs) = World(e);
            if (e is CUE4Parse.UE4.Assets.Exports.Component.StaticMesh.UInstancedStaticMeshComponent ism)
            {
                foreach (var inst in ism.PerInstanceSMData ?? Array.Empty<CUE4Parse.UE4.Assets.Exports.Component.StaticMesh.FInstancedStaticMeshInstanceData>())
                {
                    var t = inst.TransformData;
                    var p = cr.RotateVector(new CUE4Parse.UE4.Objects.Core.Math.FVector(t.Translation.X * cs.X, t.Translation.Y * cs.Y, t.Translation.Z * cs.Z)) + cl;
                    Add(model, p, cr * t.Rotation, new CUE4Parse.UE4.Objects.Core.Math.FVector(t.Scale3D.X * cs.X, t.Scale3D.Y * cs.Y, t.Scale3D.Z * cs.Z));
                }
            }
            else Add(model, cl, cr, cs);
        }
    }
    using (var bin = new BinaryWriter(File.Create(Path.Combine(outDir, "objects.bin"))))
    {
        bin.Write((uint)models.Count);
        foreach (var (_, lod, _) in models)
        {
            var v = lod.PositionVertexBuffer.Verts; var ix = lod.IndexBuffer.Buffer;
            bin.Write((uint)v.Length); bin.Write((uint)ix.Length);
            foreach (var p in v) { bin.Write(p.X); bin.Write(p.Y); bin.Write(p.Z); }
            foreach (var i in ix) bin.Write(i);
        }
        var areas = new Dictionary<string, long[]>();
        foreach (var kv in copies)
        {
            areas[$"{kv.Key.Item1},{kv.Key.Item2}"] = new long[] { bin.BaseStream.Position, kv.Value.Count };
            foreach (var r in kv.Value) bin.Write(r);
        }
        string Kind(string p) => Regex.IsMatch(p, "/Trees?/|Tree|Palm|Kapok|Bamboo", RegexOptions.IgnoreCase) ? "tree"
            : Regex.IsMatch(p, "/Rock/|Boulder|Cliff|Rubble", RegexOptions.IgnoreCase) ? "rock"
            : Regex.IsMatch(p, "/Foliage/|Bush|Plant|Fung|Shroom|Coral", RegexOptions.IgnoreCase) ? "plant" : "object";
        File.WriteAllText(Path.Combine(outDir, "objects.json"), Newtonsoft.Json.JsonConvert.SerializeObject(new
        {
            models = models.Select(m => new { name = m.path.Split('.').Last(), path = m.path, kind = Kind(m.path), tris = m.lod.IndexBuffer.Length / 3, size = Math.Round(m.size) }),
            areas
        }));
    }
    Console.WriteLine($"models {models.Count}, copies {kept}, areas {copies.Count}, unresolved {unresolved}");
    foreach (var g in models.GroupBy(m => m.path.Contains("Tree") ? "tree-ish" : "other")) Console.WriteLine($"  {g.Key} models {g.Count()}");
}
else if (mode == "survey")
{
    // survey [n cells]: models placed in the world cells: copies per model (instanced and single), model sizes
    var cells = provider.Files.Keys.Where(k => k.Contains("GameLevel01/Persistent_Level/_Generated_/") && k.EndsWith(".umap")).ToList();
    if (arg != "") cells = cells.Take(int.Parse(arg)).ToList();
    var count = new Dictionary<string, (long inst, long single)>(); var types = new Dictionary<string, int>();
    foreach (var c in cells)
    {
        List<CUE4Parse.UE4.Assets.Exports.UObject> exports;
        try { exports = provider.LoadPackage(c).GetExports().ToList(); } catch { continue; }
        foreach (var e in exports.Where(e => e.ExportType.Contains("StaticMeshComponent") || e.ExportType.Contains("InstancedSMC")))
        {
            var mesh = e.GetOrDefault<CUE4Parse.UE4.Objects.UObject.FPackageIndex>("StaticMesh");
            var path = mesh?.ResolvedObject?.GetPathName() ?? "?";
            var key = $"{e.ExportType}|{e.GetType().Name}";
            types[key] = types.GetValueOrDefault(key) + 1;
            var cur = count.GetValueOrDefault(path);
            if (e is CUE4Parse.UE4.Assets.Exports.Component.StaticMesh.UInstancedStaticMeshComponent ism)
                cur.inst += ism.PerInstanceSMData?.Length ?? 0;
            else cur.single++;
            count[path] = cur;
        }
    }
    foreach (var kv in types.OrderByDescending(k => k.Value)) Console.WriteLine($"type {kv.Key} {kv.Value}");
    Console.WriteLine($"models {count.Count}, instanced copies {count.Values.Sum(v => v.inst)}, single {count.Values.Sum(v => v.single)}");
    foreach (var kv in count.OrderByDescending(k => k.Value.inst + k.Value.single).Take(int.Parse(Environment.GetEnvironmentVariable("TERRAIN_TOP") ?? "50")))
        Console.WriteLine($"  {kv.Value.inst,8} {kv.Value.single,6}  {kv.Key}");
}
else if (mode == "meshes")
{
    // meshes <package path>: static meshes in a package with their size and triangle counts per LOD
    foreach (var m in provider.LoadPackage(arg).GetExports().OfType<CUE4Parse.UE4.Assets.Exports.StaticMesh.UStaticMesh>().Take(60))
    {
        var rd = m.RenderData;
        var b = rd?.Bounds;
        var lods = rd?.LODs?.Select(l => $"{l.IndexBuffer?.Length / 3}t") ?? Array.Empty<string>();
        Console.WriteLine($"{m.Name}  box {b?.BoxExtent}  at {b?.Origin}  nanite {rd?.NaniteResources != null}  lods {string.Join(" ", lods)}");
    }
}
else if (mode == "dump")
{
    // dump <package path> [type filter]: matching exports of one package as JSON
    var pkg = provider.LoadPackage(arg);
    var only = args.Length > 4 ? args[4] : null;
    foreach (var e in pkg.GetExports().Where(e => only == null || e.ExportType.Contains(only)).Take(only == null ? int.MaxValue : (Environment.GetEnvironmentVariable("TERRAIN_ALL") == "1" ? int.MaxValue : 6)))
    {
        if (only == null && !e.ExportType.Contains("Landscape") && e.ExportType != "Texture2D" && e.ExportType != "SceneComponent") continue;
        if (e is CUE4Parse.UE4.Assets.Exports.StaticMesh.UStaticMesh) { Console.WriteLine($"=== {e.ExportType} {e.Name} (mesh)"); continue; }
        var j = Newtonsoft.Json.JsonConvert.SerializeObject(e, Newtonsoft.Json.Formatting.Indented);
        Console.WriteLine($"=== {e.ExportType} {e.Name}\n{(j.Length > 3000 ? j[..3000] + "..." : j)}");
    }
}
else if (mode == "cells")
{
    var cells = provider.Files.Keys.Where(k => k.Contains("GameLevel01/Persistent_Level/_Generated_/") && k.EndsWith(".umap")).ToList();
    Console.WriteLine($"cells {cells.Count}");
    int shown = 0, limit = arg == "" ? 5 : int.Parse(arg);
    var classes = new Dictionary<string, int>();
    foreach (var c in cells)
    {
        List<string> names;
        try { names = provider.LoadPackage(c).GetExports().Select(e => e.ExportType).ToList(); }
        catch (Exception e) { Console.WriteLine($"! {c}: {e.Message}"); continue; }
        foreach (var n in names) classes[n] = classes.GetValueOrDefault(n) + 1;
        if (names.Any(n => n.Contains("Landscape")) && shown++ < limit)
            Console.WriteLine($"{c}: {string.Join(", ", names.GroupBy(n => n).Select(g => $"{g.Key}x{g.Count()}"))}");
    }
    foreach (var kv in classes.OrderByDescending(kv => kv.Value).Take(400))
        Console.WriteLine($"  {kv.Key} {kv.Value}");
}

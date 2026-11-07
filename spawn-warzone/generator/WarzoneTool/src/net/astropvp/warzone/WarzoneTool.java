package net.astropvp.warzone;

import com.boydti.fawe.util.EditSessionBuilder;
import com.sk89q.worldedit.EditSession;
import com.sk89q.worldedit.Vector;
import com.sk89q.worldedit.bukkit.BukkitWorld;
import com.sk89q.worldedit.extent.clipboard.Clipboard;
import com.sk89q.worldedit.extent.clipboard.io.ClipboardFormat;
import com.sk89q.worldedit.function.operation.Operation;
import com.sk89q.worldedit.function.operation.Operations;
import com.sk89q.worldedit.session.ClipboardHolder;
import com.sk89q.worldedit.world.World;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.command.ConsoleCommandSender;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.*;

/**
 * TEST-SERVER console tool for the spawn warzone rebuild (2026-11-06). Never install on live.
 *
 *   wz paste <file> x y z [air]                 paste FAWE schematics/<file>.schematic, min corner at x y z (air pasted only with "air")
 *   wz count x1 y1 z1 x2 y2 z2                  non-air blocks by type in a cuboid
 *   wz block x y z                              type:data + light (block/sky) at a block
 *   wz walk sx sy sz x1 z1 x2 z2                walk test (BFS) from a standing spot, inside the column box; remembers the result
 *   wz path x y z                               is that standing spot reachable in the last walk?
 *   wz stuck x1 z1 x2 z2 ymin ymax              standable spots in the box NOT reachable in the last walk (stuck spots), clustered
 *   wz light x1 z1 x2 z2 ymin ymax              standable spots with light <= 7 (hostile mobs can spawn), clustered
 *   wz report <file>                            writes the last walk/stuck/light lists to plugins/WarzoneTool/<file>.txt
 */
public class WarzoneTool extends JavaPlugin {

    private org.bukkit.World world() { return Bukkit.getWorlds().get(0); }

    private final Set<Long> reach = new HashSet<>();
    private final List<String> lastLines = new ArrayList<>();

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] a) {
        if (!(sender instanceof ConsoleCommandSender)) { sender.sendMessage("console only"); return true; }
        if (a.length == 0) return false;
        try {
            switch (a[0]) {
                case "paste": {
                    World w = new BukkitWorld(world());
                    Clipboard clipboard;
                    File f = new File(getDataFolder().getParentFile(), "FastAsyncWorldEdit/schematics/" + a[1] + ".schematic");
                    try (FileInputStream in = new FileInputStream(f)) {
                        clipboard = ClipboardFormat.SCHEMATIC.getReader(in).read(w.getWorldData());
                    }
                    clipboard.setOrigin(clipboard.getMinimumPoint());
                    boolean air = a.length > 5 && a[5].equals("air");
                    EditSession es = new EditSessionBuilder(w).fastmode(false).checkMemory(false).limitUnlimited()
                            .allowedRegionsEverywhere().changeSetNull().autoQueue(false).build();
                    Operation op = new ClipboardHolder(clipboard, w.getWorldData()).createPaste(es, w.getWorldData())
                            .to(new Vector(i(a[2]), i(a[3]), i(a[4]))).ignoreAirBlocks(!air).build();
                    Operations.completeLegacy(op);
                    es.flushQueue();
                    msg(sender, "pasted " + a[1] + " " + clipboard.getDimensions() + " at " + a[2] + "," + a[3] + "," + a[4]
                            + " air=" + air + " changed=" + es.getBlockChangeCount());
                    return true;
                }
                case "count": {
                    int x1 = i(a[1]), y1 = i(a[2]), z1 = i(a[3]), x2 = i(a[4]), y2 = i(a[5]), z2 = i(a[6]);
                    Map<String, Integer> types = new TreeMap<>(); long n = 0;
                    for (int x = Math.min(x1, x2); x <= Math.max(x1, x2); x++)
                        for (int z = Math.min(z1, z2); z <= Math.max(z1, z2); z++)
                            for (int y = Math.min(y1, y2); y <= Math.max(y1, y2); y++) {
                                Block b = world().getBlockAt(x, y, z);
                                if (b.getType() == Material.AIR) continue;
                                n++; types.merge(b.getType().name() + ":" + b.getData(), 1, Integer::sum);
                            }
                    msg(sender, "non-air " + n + " " + types);
                    return true;
                }
                case "block": {
                    Block b = world().getBlockAt(i(a[1]), i(a[2]), i(a[3]));
                    msg(sender, "block " + a[1] + "," + a[2] + "," + a[3] + " = " + b.getType() + ":" + b.getData()
                            + " light=" + b.getLightLevel() + " blockLight=" + b.getLightFromBlocks() + " sky=" + b.getLightFromSky()
                            + " powered=" + b.isBlockPowered());
                    return true;
                }
                case "walk": {
                    int sx = i(a[1]), sy = i(a[2]), sz = i(a[3]);
                    int x1 = i(a[4]), z1 = i(a[5]), x2 = i(a[6]), z2 = i(a[7]);
                    reach.clear();
                    if (!standable(sx, sy, sz)) { msg(sender, "start " + sx + "," + sy + "," + sz + " is not a standing spot"); return true; }
                    ArrayDeque<int[]> q = new ArrayDeque<>();
                    q.add(new int[]{sx, sy, sz}); reach.add(key(sx, sy, sz));
                    int minY = sy, maxY = sy, hazards = 0;
                    int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
                    while (!q.isEmpty()) {
                        int[] p = q.poll();
                        int x = p[0], y = p[1], z = p[2];
                        if (isLava(x, y, z)) hazards++;
                        for (int[] d : dirs) {
                            int nx = x + d[0], nz = z + d[1];
                            if (nx < x1 || nx > x2 || nz < z1 || nz > z2) continue;
                            int ny = -999;
                            if (standable(nx, y, nz)) ny = y;
                            else if (standable(nx, y + 1, nz) && free(x, y + 2, z)) ny = y + 1;   // step / jump up one block
                            else if (free(nx, y, nz) && free(nx, y + 1, nz)) {                     // walk off an edge and fall
                                for (int yy = y - 1; yy > 0; yy--) {
                                    if (!free(nx, yy - 1, nz)) {
                                        if (standable(nx, yy, nz)) ny = yy;
                                        break;
                                    }
                                }
                            }
                            if (ny == -999) continue;
                            long k = key(nx, ny, nz);
                            if (reach.add(k)) { q.add(new int[]{nx, ny, nz}); minY = Math.min(minY, ny); maxY = Math.max(maxY, ny); }
                        }
                    }
                    msg(sender, "walk from " + sx + "," + sy + "," + sz + ": reachable standing spots " + reach.size()
                            + " y " + minY + ".." + maxY + " (in lava " + hazards + ")");
                    return true;
                }
                case "path": {
                    int x = i(a[1]), y = i(a[2]), z = i(a[3]);
                    msg(sender, "path to " + x + "," + y + "," + z + ": standable=" + standable(x, y, z) + " reachable=" + reach.contains(key(x, y, z)));
                    return true;
                }
                case "stuck":
                case "light": {
                    boolean light = a[0].equals("light");
                    int x1 = i(a[1]), z1 = i(a[2]), x2 = i(a[3]), z2 = i(a[4]), ymin = i(a[5]), ymax = i(a[6]);
                    List<int[]> bad = new ArrayList<>();
                    long cells = 0;
                    for (int x = x1; x <= x2; x++)
                        for (int z = z1; z <= z2; z++)
                            for (int y = ymin; y <= ymax; y++) {
                                if (!standable(x, y, z)) continue;
                                cells++;
                                if (light) {
                                    Block below = world().getBlockAt(x, y - 1, z);
                                    if (!spawnable(below.getType())) continue;
                                    if (world().getBlockAt(x, y, z).getLightLevel() <= 7) bad.add(new int[]{x, y, z});
                                } else if (!reach.contains(key(x, y, z))) bad.add(new int[]{x, y, z});
                            }
                    lastLines.clear();
                    for (int[] b : bad) lastLines.add(b[0] + " " + b[1] + " " + b[2]);
                    msg(sender, a[0] + ": standable spots " + cells + ", flagged " + bad.size());
                    for (String c : clusters(bad, 15)) msg(sender, "  " + c);
                    return true;
                }
                case "report": {
                    getDataFolder().mkdirs();
                    File f = new File(getDataFolder(), a[1] + ".txt");
                    try (PrintWriter pw = new PrintWriter(new FileWriter(f))) { for (String s : lastLines) pw.println(s); }
                    msg(sender, "wrote " + lastLines.size() + " lines to " + f);
                    return true;
                }
            }
        } catch (Exception e) {
            msg(sender, "error: " + e);
            e.printStackTrace();
            return true;
        }
        return false;
    }

    private static List<String> clusters(List<int[]> pts, int max) {
        Map<Long, int[]> m = new HashMap<>();
        for (int[] p : pts) m.put(key(p[0], p[1], p[2]), p);
        Set<Long> seen = new HashSet<>();
        List<int[]> res = new ArrayList<>();   // size, minx, maxx, miny, maxy, minz, maxz
        for (int[] p : pts) {
            long k0 = key(p[0], p[1], p[2]);
            if (!seen.add(k0)) continue;
            int[] c = {0, p[0], p[0], p[1], p[1], p[2], p[2]};
            ArrayDeque<int[]> st = new ArrayDeque<>(); st.add(p);
            while (!st.isEmpty()) {
                int[] q = st.poll(); c[0]++;
                c[1] = Math.min(c[1], q[0]); c[2] = Math.max(c[2], q[0]); c[3] = Math.min(c[3], q[1]); c[4] = Math.max(c[4], q[1]);
                c[5] = Math.min(c[5], q[2]); c[6] = Math.max(c[6], q[2]);
                for (int dx = -1; dx <= 1; dx++) for (int dy = -1; dy <= 1; dy++) for (int dz = -1; dz <= 1; dz++) {
                    long k = key(q[0] + dx, q[1] + dy, q[2] + dz);
                    int[] n = m.get(k);
                    if (n != null && seen.add(k)) st.add(n);
                }
            }
            res.add(c);
        }
        res.sort((x, y) -> y[0] - x[0]);
        List<String> out = new ArrayList<>();
        for (int i = 0; i < Math.min(max, res.size()); i++) {
            int[] c = res.get(i);
            out.add(c[0] + " spots x " + c[1] + ".." + c[2] + " y " + c[3] + ".." + c[4] + " z " + c[5] + ".." + c[6]);
        }
        if (res.size() > max) out.add("... " + (res.size() - max) + " more clusters");
        return out;
    }

    private static long key(int x, int y, int z) { return ((long) (x + 30000) << 32) | ((long) (z + 30000) << 8) | (y & 255); }

    private static final EnumSet<Material> PASS = EnumSet.of(Material.AIR, Material.LONG_GRASS, Material.YELLOW_FLOWER, Material.RED_ROSE,
            Material.DEAD_BUSH, Material.SAPLING, Material.TORCH, Material.REDSTONE_TORCH_ON, Material.REDSTONE_TORCH_OFF, Material.REDSTONE_WIRE,
            Material.STONE_PLATE, Material.WOOD_PLATE, Material.IRON_PLATE, Material.GOLD_PLATE, Material.CARPET, Material.SIGN_POST,
            Material.WALL_SIGN, Material.LADDER, Material.VINE, Material.SNOW, Material.WATER, Material.STATIONARY_WATER, Material.LAVA,
            Material.STATIONARY_LAVA, Material.IRON_DOOR_BLOCK, Material.WOODEN_DOOR, Material.TRAP_DOOR, Material.LEVER, Material.STONE_BUTTON,
            Material.WOOD_BUTTON, Material.DOUBLE_PLANT, Material.WEB, Material.BROWN_MUSHROOM, Material.RED_MUSHROOM, Material.FIRE,
            Material.SUGAR_CANE_BLOCK, Material.TRIPWIRE, Material.TRIPWIRE_HOOK, Material.RAILS, Material.WATER_LILY);
    private static final EnumSet<Material> TALL = EnumSet.of(Material.FENCE, Material.NETHER_FENCE, Material.COBBLE_WALL, Material.THIN_GLASS,
            Material.STAINED_GLASS_PANE, Material.IRON_FENCE, Material.FENCE_GATE, Material.SPRUCE_FENCE, Material.BIRCH_FENCE,
            Material.JUNGLE_FENCE, Material.DARK_OAK_FENCE, Material.ACACIA_FENCE, Material.SPRUCE_FENCE_GATE, Material.BIRCH_FENCE_GATE,
            Material.JUNGLE_FENCE_GATE, Material.DARK_OAK_FENCE_GATE, Material.ACACIA_FENCE_GATE);

    private boolean free(int x, int y, int z) { return PASS.contains(world().getBlockAt(x, y, z).getType()); }
    private boolean isLava(int x, int y, int z) { Material m = world().getBlockAt(x, y, z).getType(); return m == Material.LAVA || m == Material.STATIONARY_LAVA; }
    private boolean standable(int x, int y, int z) {
        if (y < 1 || y > 254) return false;
        Material below = world().getBlockAt(x, y - 1, z).getType();
        if (PASS.contains(below)) return false;                       // air, plants, plates, water and lava are not a floor
        if (TALL.contains(below)) return false;
        return free(x, y, z) && free(x, y + 1, z);
    }
    private static boolean spawnable(Material m) {
        return m.isSolid() && m.isOccluding() && m != Material.GLASS && m != Material.STAINED_GLASS && m != Material.BEDROCK;
    }

    private static int i(String s) { return Integer.parseInt(s); }
    private static void msg(CommandSender s, String m) { s.sendMessage("[wz] " + m); }
}

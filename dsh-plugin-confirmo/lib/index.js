/**
 * Confirmo companion plugin, node half.
 *
 * Registers same-origin proxy routes on the DSH web server:
 *
 * 1. GET /confirmo/sprites?page=&limit=&sort=  — live sprite list from
 *    api.sprites.confirmo.love (the list API only allows the gallery origin
 *    via CORS; server-side fetch has no such restriction).
 *
 * 2. GET /confirmo/sprite/<id>?url=<spriteUrl> — raw sprite sheet with a
 *    persistent disk cache under <DSH_HOME>/cache/confirmo/. The browser
 *    loads sheets through this route instead of hitting the remote CDN
 *    directly, so the original images survive browser-data clearing, are
 *    unlimited by browser quota, and are instantly re-servable. Only
 *    pub-sprites.confirmo.love URLs are accepted.
 *
 * 3. GET /confirmo/local/<file> — bundled assets served straight from the
 *    plugin package (no download, no cache). Used for the built-in default
 *    sprite (e.g. assets/mj.png).
 *
 * `inject: ['webServer']` mirrors the pattern of dsh-community-market: it
 * tells the cordis loader to only apply this plugin once the webServer
 * service exists, so `ctx.webServer.register(...)` is safe to call.
 */
import { mkdir, readFile, rename, stat, writeFile } from "node:fs/promises";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";

export const name = "confirmo";
export const inject = ["webServer"];

const PACKAGE_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const ASSETS_DIR = join(PACKAGE_ROOT, "assets");
const CACHE_DIR = join(process.env.DSH_HOME || join(homedir(), ".dsh"), "cache", "confirmo");
const ALLOWED_PREFIX = "https://pub-sprites.confirmo.love/";
const MIME = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp" };

function sanitizeId(id) {
  return String(id).replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 80) || "sprite";
}

/** Resolve the cached file for a sprite; download + persist it on a miss. */
async function getCachedSheet(id, url) {
  let ext;
  try {
    ext = extname(new URL(url).pathname) || ".png";
  } catch {
    ext = ".png";
  }
  const file = join(CACHE_DIR, sanitizeId(id) + ext);
  try {
    const st = await stat(file);
    if (st.isFile() && st.size > 0) return { file, ext };
  } catch { /* miss */ }
  const resp = await fetch(url, {
    headers: { "user-agent": "dsh-plugin-confirmo" },
    signal: AbortSignal.timeout(60000)
  });
  if (!resp.ok) throw new Error("download failed: " + resp.status);
  const buf = Buffer.from(await resp.arrayBuffer());
  if (!buf.length) throw new Error("empty download");
  await mkdir(CACHE_DIR, { recursive: true });
  const tmp = file + "." + process.pid + ".tmp";
  await writeFile(tmp, buf);
  await rename(tmp, file);
  return { file, ext };
}

function apply(ctx) {
  try {
    // 1) live sprite list proxy
    ctx.effect(() => ctx.webServer.register({
      kind: "exact",
      path: "/confirmo/sprites",
      handler: async (req, res) => {
        try {
          const u = new URL(req.url ?? "/", "http://x");
          const params = new URLSearchParams(u.search);
          if (!params.get("page")) params.set("page", "1");
          if (!params.get("limit")) params.set("limit", "20");
          if (!params.get("sort")) params.set("sort", "trending");
          const resp = await fetch(`https://api.sprites.confirmo.love/sprites?${params.toString()}`, {
            headers: { "user-agent": "dsh-plugin-confirmo" },
            signal: AbortSignal.timeout(15000)
          });
          const body = await resp.text();
          res.writeHead(resp.status, {
            "content-type": resp.headers.get("content-type") ?? "application/json",
            "cache-control": "no-store"
          });
          res.end(body);
        } catch (err) {
          res.writeHead(502, { "content-type": "application/json" });
          res.end(JSON.stringify({ error: String((err && err.message) || err) }));
        }
      }
    }), "confirmo: sprite list proxy route");

    // 2) raw sprite sheet with persistent disk cache
    ctx.effect(() => ctx.webServer.register({
      kind: "prefixes",
      path: "/confirmo/sprite",
      handler: async (req, res) => {
        try {
          const u = new URL(req.url ?? "/", "http://x");
          const url = u.searchParams.get("url") || "";
          if (!url.startsWith(ALLOWED_PREFIX)) {
            res.writeHead(400, { "content-type": "application/json" });
            res.end(JSON.stringify({ error: "url must be on " + ALLOWED_PREFIX }));
            return;
          }
          const id = decodeURIComponent(u.pathname.slice("/confirmo/sprite/".length));
          const { file, ext } = await getCachedSheet(id, url);
          const data = await readFile(file);
          res.writeHead(200, {
            "content-type": MIME[ext] ?? "application/octet-stream",
            "cache-control": "public, max-age=604800",
            "access-control-allow-origin": "*"
          });
          res.end(data);
        } catch (err) {
          res.writeHead(502, { "content-type": "application/json" });
          res.end(JSON.stringify({ error: String((err && err.message) || err) }));
        }
      }
    }), "confirmo: sprite sheet disk-cache route");

    // 3) bundled assets (built-in default sprite): GET /confirmo/local/<path>
    ctx.effect(() => ctx.webServer.register({
      kind: "prefixes",
      path: "/confirmo/local",
      handler: async (req, res) => {
        try {
          const u = new URL(req.url ?? "/", "http://x");
          const rel = decodeURIComponent(u.pathname.slice("/confirmo/local/".length));
          // path traversal guard: must resolve inside ASSETS_DIR
          const full = resolve(ASSETS_DIR, rel);
          if (full !== ASSETS_DIR && !full.startsWith(ASSETS_DIR + "/")) {
            res.writeHead(400, { "content-type": "application/json" });
            res.end(JSON.stringify({ error: "invalid local asset path" }));
            return;
          }
          const data = await readFile(full);
          const ext = extname(rel).toLowerCase();
          res.writeHead(200, {
            "content-type": MIME[ext] ?? "application/octet-stream",
            // local bundled assets change between releases: never cache them so a
            // re-served sheet always reflects the packaged file
            "cache-control": "no-cache",
            "access-control-allow-origin": "*"
          });
          res.end(data);
        } catch (err) {
          res.writeHead(404, { "content-type": "application/json" });
          res.end(JSON.stringify({ error: "asset not found" }));
        }
      }
    }), "confirmo: bundled asset route");
  } catch (err) {
    // route registration unavailable — browser half falls back to the CDN directly
    try { ctx.logger.warn("confirmo: failed to register routes: " + String((err && err.message) || err)); } catch (_) {}
  }
}
export { apply };

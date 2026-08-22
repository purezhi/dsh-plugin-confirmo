#!/usr/bin/env node
/**
 * Build lib/client.js from lib/client.src.js + sprite_list.json.
 * Injects the embedded sprite snapshot (from sprites.confirmo.love) into the
 * ModuleLoader bundle so the plugin needs no runtime API access (the sprite
 * API is CORS-restricted to the gallery origin; sheet images are open).
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url)); // package root (build.js sits next to sprite_list.json)

const list = JSON.parse(readFileSync(join(here, "sprite_list.json"), "utf8"));
let src = readFileSync(join(here, "lib", "client.src.js"), "utf8");
if (!src.includes("__SPRITE_LIST_JSON__")) {
  throw new Error("client.src.js does not contain __SPRITE_LIST_JSON__ placeholder");
}
const json = JSON.stringify(list);
src = src.replace("__SPRITE_LIST_JSON__", json);
writeFileSync(join(here, "lib", "client.js"), src);
console.log(`client.js built with ${list.length} embedded sprites (${json.length} bytes of JSON)`);

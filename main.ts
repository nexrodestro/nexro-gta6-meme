import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const EXPECTED_SIDE = 1080;

function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

function checkMemePng(path: string): void {
  const bytes = readFileSync(path);
  if (bytes.length < 33 || !bytes.subarray(0, 8).equals(PNG_SIGNATURE)) {
    fail(`${path} is not a PNG file`);
  }
  if (bytes.toString("ascii", 12, 16) !== "IHDR") {
    fail(`${path} has no IHDR chunk where one was expected`);
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width !== EXPECTED_SIDE || height !== EXPECTED_SIDE) {
    fail(`${path} is ${width}x${height}, expected ${EXPECTED_SIDE}x${EXPECTED_SIDE}`);
  }
}

function checkPostJson(path: string): void {
  const raw = readFileSync(path, "utf8");
  if (Buffer.byteLength(raw, "utf8") > 16384) {
    fail(`${path} is over the 16384 byte limit for POST.json`);
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    fail(`${path} is not valid JSON`);
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    fail(`${path} must hold a JSON object`);
  }
  const url = (parsed as Record<string, unknown>).url;
  if (typeof url !== "string" || url.length === 0) {
    fail(`${path} must hold a non-empty string "url"`);
  }
}

const botDir = resolve(process.env.MAKEFUN_BOT_DIR ?? "/bot");
const outDir = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? "/output");

const postSrc = join(botDir, "POST.json");
const memeSrc = join(botDir, "meme.png");

if (!existsSync(postSrc)) fail(`missing ${postSrc}`);
if (!existsSync(memeSrc)) fail(`missing ${memeSrc}`);

checkPostJson(postSrc);
checkMemePng(memeSrc);

mkdirSync(outDir, { recursive: true });
copyFileSync(postSrc, join(outDir, "POST.json"));
copyFileSync(memeSrc, join(outDir, "meme.png"));

import { readdirSync, readFileSync } from "node:fs";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { gzipSync } from "node:zlib";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const assetsDir = join(repoRoot, "apps/web/dist/assets");
const budgetPath = join(repoRoot, "apps/web/budget.json");

const budget = JSON.parse(readFileSync(budgetPath, "utf8"));
const assets = readdirSync(assetsDir);

function gzipKb(fileName) {
  return gzipSync(readFileSync(join(assetsDir, fileName))).length / 1024;
}

function totalKb(extension) {
  return assets
    .filter((fileName) => extname(fileName) === extension)
    .reduce((total, fileName) => total + gzipKb(fileName), 0);
}

const measured = {
  cssGzipKb: totalKb(".css"),
  jsGzipKb: totalKb(".js"),
};
measured.totalGzipKb = measured.cssGzipKb + measured.jsGzipKb;

const failures = Object.entries(budget).filter(([key, limit]) => measured[key] > limit);

for (const [key, limit] of Object.entries(budget)) {
  const actual = measured[key].toFixed(2);
  console.log(`${actual.padStart(7)} KB gzip / ${String(limit).padStart(4)} KB  ${key}`);
}

if (failures.length > 0) {
  console.error(
    "Web budget exceeded. Reduce the bundle or raise the budget with an explicit decision.",
  );
  process.exitCode = 1;
}

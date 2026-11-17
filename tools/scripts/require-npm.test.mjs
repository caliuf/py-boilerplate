import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const script = fileURLToPath(new URL("./require-npm.mjs", import.meta.url));

function runWithAgent(userAgent) {
  const env = { ...process.env };
  if (userAgent === undefined) {
    delete env.npm_config_user_agent;
  } else {
    env.npm_config_user_agent = userAgent;
  }
  return spawnSync(process.execPath, [script], { env, encoding: "utf8" });
}

test("allows npm", () => {
  const result = runWithAgent("npm/10.9.2 node/v26.5.0 linux x64 workspaces/false");
  assert.equal(result.status, 0);
});

test("allows a direct run without user agent", () => {
  const result = runWithAgent(undefined);
  assert.equal(result.status, 0);
});

for (const manager of ["pnpm", "yarn", "bun"]) {
  test(`blocks ${manager}`, () => {
    const result = runWithAgent(`${manager}/1.0.0 npm/? node/v26.5.0 linux x64`);
    assert.equal(result.status, 1);
    assert.match(result.stderr, new RegExp(manager));
    assert.match(result.stderr, /npm ci/);
  });
}

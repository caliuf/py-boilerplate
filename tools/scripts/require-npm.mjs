#!/usr/bin/env node
// Guard for the `preinstall` lifecycle script: this repository installs
// dependencies with npm only (see AGENTS.md and docs/development/ENVIRONMENT.md).
//
// npm, pnpm, yarn and bun all export `npm_config_user_agent`; the token before
// the first "/" is the package manager that is running the lifecycle script.
// A direct `node tools/scripts/require-npm.mjs` run has no user agent and is
// allowed, so the script can be executed and tested without a package manager.

const userAgent = process.env.npm_config_user_agent ?? "";
const manager = userAgent.split(" ")[0]?.split("/")[0] ?? "";
const supported = "npm";

if (manager !== "" && manager !== supported) {
  console.error(
    `✖ ${manager} is not supported in this repository: dependencies and scripts go through ${supported} and package-lock.json.`,
  );
  console.error(
    `  Run "npm ci" instead, and remove the ${manager} lockfile or workspace file it created.`,
  );
  console.error(
    `  The "preinstall" hook does not cover "${manager} exec" or installs run with --ignore-scripts.`,
  );
  process.exit(1);
}

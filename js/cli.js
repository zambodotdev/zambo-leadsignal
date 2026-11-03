#!/usr/bin/env node
"use strict";
/* zambo-leadsignal command line.
 *   zambo-leadsignal run --trade plumber --city "Austin Texas" [--note "..."]
 * Env: ZAMBO_TRADE, ZAMBO_CITY, ZAMBO_NOTE, ZAMBO_AGENT_ID, ZAMBO_MCP_URL. */
const { runSweep } = require("./run");

function arg(flag, env, dflt) {
  const i = process.argv.indexOf(flag);
  if (i >= 0) return process.argv[i + 1];
  return process.env[env] || dflt;
}

async function main() {
  if (process.argv[2] !== "run") {
    console.log('usage: zambo-leadsignal run --trade <trade> --city "<city>" [--note "..."]');
    return 2;
  }
  const trade = arg("--trade", "ZAMBO_TRADE");
  const city = arg("--city", "ZAMBO_CITY");
  const note = arg("--note", "ZAMBO_NOTE");
  if (!trade || !city) {
    console.log("run needs --trade and --city (or ZAMBO_TRADE / ZAMBO_CITY)");
    return 2;
  }
  const result = await runSweep(trade, city, note, process.env.ZAMBO_AGENT_ID);
  console.log(`done: job ${result.job_id}`);
  return 0;
}

main().then((code) => process.exit(code)).catch((err) => {
  console.error(err);
  process.exit(1);
});

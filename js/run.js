"use strict";
/* The lead signal run: five receipted steps, one brief, one wrap.
 * Mirrors zambo_leadsignal/run.py exactly. */
const fs = require("fs");
const path = require("path");
const { ZamboClient, receiptLink, resultText } = require("./client");

function slug(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40);
}

async function runSweep(trade, city, note, agentId, agentName) {
  agentId = agentId || "leadsignal-agent";
  agentName = agentName || "Lead Signal Agent";
  const stamp = new Date().toISOString().replace(/[-:T]/g, "").slice(0, 14);
  const jobId = `leadsignal-${slug(trade)}-${slug(city)}-${stamp}`;
  const client = new ZamboClient(agentId, agentName);
  await client.initialize();
  const receipts = {};

  async function step(tool, args) {
    const result = await client.callTool(tool, { ...args, _session_id: jobId });
    const link = receiptLink(result);
    receipts[tool] = link;
    console.log(`[${tool}] receipt: ${link}`);
    return resultText(result);
  }

  const briefFact = `Lead signal run ${jobId}: trade=${trade}, city=${city}. Operator note: ${note || "(none)"}. Steps: capability_search, prompt_shield, leadsignal, continuity_get_recent, wrap.`;
  await step("memory_remember", { fact: briefFact.slice(0, 480), agent_name: agentName });
  const landscape = await step("capability_search", { q: `${trade} services ${city} lead generation` });
  const shieldInput = note || `Find new ${trade} customers in ${city} this week.`;
  const shield = await step("prompt_shield", { prompt: shieldInput, mode: "fast" });
  const signals = await step("leadsignal", { trade, city });
  const recent = await step("continuity_get_recent", { limit: 20 });

  const receiptLines = Object.entries(receipts).filter(([, u]) => u).map(([t, u]) => `- ${t}: ${u}`).join("\n");
  const brief = `# Lead signal brief: ${trade} in ${city}\n\nJob: ${jobId} (UTC ${stamp})\n\n## Live signals (leadsignal)\n\n${signals}\n\n## Capability landscape (capability_search)\n\n${landscape}\n\n## Input screen (prompt_shield)\n\n${shield}\n\n## What this agent already had on record (continuity)\n\n${recent}\n\n## Receipts\n\n${receiptLines}\n\nEvery receipt recomputes at https://zambo.dev/verify/. A receipt proves the saved result was not changed since the call ran; it does not prove a lead is good. Work the signals, and let the record keep you honest about what you already chased.\n`;
  const out = path.join(process.cwd(), `leadsignal-brief-${jobId}.md`);
  fs.writeFileSync(out, brief);
  console.log(`[brief] written: ${out}`);

  const wrap = await client.callTool("workflow_close", {
    _session_id: jobId,
    summary: `Lead signal run for ${trade} in ${city}: live signals pulled, input screened, prior record checked, brief written to ${path.basename(out)}.`,
  });
  const wrapLink = receiptLink(wrap);
  console.log(`[wrap] workflow_close receipt: ${wrapLink}`);
  return { job_id: jobId, brief: out, receipts, wrap_receipt: wrapLink };
}

module.exports = { runSweep };

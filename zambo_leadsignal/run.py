"""The lead signal run: five receipted steps, one brief, one wrap.

    capability_search   what services and angles exist for this trade
    prompt_shield       screen the operator note before it steers work
    leadsignal          the live signals for (trade, city)
    continuity_get_recent   what this agent already found, so a repeat
                            run builds on the record instead of
                            starting from zero
    workflow_close      wrap the run; the wrap binds the job's own
                        receipts into one checkable record

Every call carries the run's job id as _session_id, so the wrap holds
exactly this run's steps and nothing else's.
"""

import json
import re
import time
from pathlib import Path

from .client import ZamboClient, receipt_link, result_text


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]


def run_sweep(trade, city, note=None, agent_id="leadsignal-agent",
              agent_name="Lead Signal Agent"):
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    job_id = f"leadsignal-{slug(trade)}-{slug(city)}-{stamp}"
    client = ZamboClient(agent_id, agent_name)
    client.initialize()
    receipts = {}

    def step(tool, args):
        result = client.call_tool(tool, {**args, "_session_id": job_id})
        link = receipt_link(result)
        receipts[tool] = link
        print(f"[{tool}] receipt: {link}")
        return result_text(result)

    # Open the job on the record.
    brief_fact = (
        f"Lead signal run {job_id}: trade={trade}, city={city}. "
        f"Operator note: {note or '(none)'}. Steps: capability_search, "
        "prompt_shield, leadsignal, continuity_get_recent, wrap."
    )
    step("memory_remember", {"fact": brief_fact[:480],
                             "agent_name": agent_name})

    landscape = step("capability_search",
                     {"q": f"{trade} services {city} lead generation"})
    shield_input = note or f"Find new {trade} customers in {city} this week."
    shield = step("prompt_shield", {"prompt": shield_input, "mode": "fast"})
    signals = step("leadsignal", {"trade": trade, "city": city})
    recent = step("continuity_get_recent", {"limit": 20})

    brief = (
        f"# Lead signal brief: {trade} in {city}\n\n"
        f"Job: {job_id} (UTC {stamp})\n\n"
        f"## Live signals (leadsignal)\n\n{signals}\n\n"
        f"## Capability landscape (capability_search)\n\n{landscape}\n\n"
        f"## Input screen (prompt_shield)\n\n{shield}\n\n"
        f"## What this agent already had on record (continuity)\n\n"
        f"{recent}\n\n"
        f"## Receipts\n\n"
        + "\n".join(f"- {t}: {u}" for t, u in receipts.items() if u)
        + "\n\nEvery receipt recomputes at https://zambo.dev/verify/. "
          "A receipt proves the saved result was not changed since the "
          "call ran; it does not prove a lead is good. Work the signals, "
          "and let the record keep you honest about what you already "
          "chased.\n"
    )
    out = Path.cwd() / f"leadsignal-brief-{job_id}.md"
    out.write_text(brief)
    print(f"[brief] written: {out}")

    wrap = client.call_tool(
        "workflow_close",
        {"_session_id": job_id,
         "summary": f"Lead signal run for {trade} in {city}: live signals "
                    f"pulled, input screened, prior record checked, brief "
                    f"written to {out.name}."},
    )
    wrap_link = receipt_link(wrap)
    print(f"[wrap] workflow_close receipt: {wrap_link}")
    return {"job_id": job_id, "brief": str(out), "receipts": receipts,
            "wrap_receipt": wrap_link}

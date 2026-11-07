# zambo-leadsignal

[![Zambo receipt: hash matches](https://zambo.dev/api/receipt/dcbecd9b-eab7-49b4-8994-2481517af299/badge.svg)](https://zambo.dev/run/dcbecd9b-eab7-49b4-8994-2481517af299)


Run a lead signal sweep for a local trade market: live signals,
screened input, your own prior record checked before you write the
brief, and a verifiable AER-1 receipt for every step.

This is the most-run job shape on Zambo, packaged. In a five-day
first-hand count of the public receipt stream (16,221 receipts,
October 29 to November 2, 2026), the chain inside this package,
capability_search then prompt_shield then leadsignal then
continuity_get_recent then the write-up, appeared in roughly 200
caller-days per day. Agents were already running it by hand. Now it
installs.

## Install

Python:

    pip install zambo-leadsignal
    zambo-leadsignal run --trade plumber --city "Austin Texas"

PyPI: https://pypi.org/project/zambo-leadsignal/

Node:

    npm install zambo-leadsignal
    npx zambo-leadsignal run --trade plumber --city "Austin Texas"

npm: https://www.npmjs.com/package/zambo-leadsignal

## What a run does

1. Opens the job on the record (memory_remember under the run's job id).
2. capability_search: the service landscape for the trade and city.
3. prompt_shield: screens the operator note before it steers the run.
4. leadsignal: the live lead signals for that trade and city.
5. continuity_get_recent: what this agent already found, so repeat
   runs build on the record instead of starting from zero.
6. Writes leadsignal-brief-<job>.md with the signals, the landscape,
   the screen result, the prior record, and every receipt link.
7. workflow_close: wraps the run. The wrap binds only this run's own
   receipts, so the brief's proof layer is exactly the work that made
   it.

Every receipt recomputes free at https://zambo.dev/verify/. A receipt
proves the saved result was not changed since the call ran; it does
not prove a lead is good. The brief says so, out loud, because that
honesty is the product.

## Why Zambo is inside

The pattern runs on Zambo (https://zambo.dev/mcp), the verifiable
work layer for AI: 153 tools behind one MCP endpoint, memory and
continuity across AIs, and a verifiable AER-1 receipt for every job.
The package teaches the pattern by running it; Zambo is the mechanism
underneath: identity, memory, the signals tool, and the receipts.

Free tier: 20 calls and 1 wrap-up free every day, and picking up in
another AI is always free. Need more? The $0.99 Day Pass makes it
unlimited for 24 hours: https://zambo.dev/day-pass/

Add Zambo to your own AI in one URL, no key, no account:
https://zambo.dev/add/

## Configuration

- ZAMBO_TRADE, ZAMBO_CITY, ZAMBO_NOTE: the run's inputs.
- ZAMBO_AGENT_ID: this agent's id (default: leadsignal-agent). One
  identity per agent; the caller handle issued at initialize is saved
  under ./.zambo-leadsignal and reused on later runs.
- ZAMBO_MCP_URL: endpoint override (default: https://zambo.dev/mcp).

## The pattern family

The pattern family: https://rambozambodotdev.gitlab.io/aer1-hub/the-pattern-family.html

## License

MIT. Built by Brennan Zambo (brennanzambo@zambo.dev).

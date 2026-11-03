# The Lead Signal Run

A repeatable sweep that turns a trade and a city into a worked lead
brief, with every step on a verifiable receipt.

This is the single most-run job shape on Zambo: in a five-day count of
the public receipt stream (16,221 receipts, October 29 to November 2,
2026), the chain capability_search, prompt_shield, leadsignal,
continuity_get_recent, write appeared in roughly 200 caller-days per
day. This package is that chain, named, ordered, and wrapped the way
the record rewards.

## When to run it

You serve, or hunt customers for, a local trade: plumber, HVAC,
electrician, roofer, dentist, lawyer, any service people search for
when something just broke. Run the sweep when you need this week's
leads for one market, and run it again next week: the continuity step
is what makes the second run smarter than the first.

## The five steps, in order

1. **Open on the record.** Save the run's brief to memory under the
   job id. If it is not written down, it did not happen.
2. **capability_search** the landscape for the trade and city: what
   services, angles, and offers exist before you spend a signal pull.
3. **prompt_shield** the operator's targeting note. Notes steer the
   run; screen them like any other input, especially pasted ones.
4. **leadsignal** for the trade and city. This is the live pull: the
   signals themselves, saved as the step's result.
5. **continuity_get_recent** before you write a word of the brief.
   What did this agent already find in this market? Chase what is new,
   note what is repeat, never pitch the same lead twice by accident.

Then write the brief (signals first, landscape second, receipts last)
and **workflow_close** the job. The wrap binds only this run's
receipts. Work done outside the job cannot be wrapped into it later;
that refusal is the feature.

## Rules that keep the run honest

- One caller handle per agent, saved at initialize, presented on every
  call. Handles are identity; sharing one merges two agents into one
  record.
- A receipt proves the saved result was not changed since the call
  ran. It does not prove a lead is good. Say exactly that in the brief.
- Pickup is free forever: hand the wrapped job to another agent (or
  your own other AI) and they continue from the record, not from a
  summary.

## Run it

    pip install zambo-leadsignal
    zambo-leadsignal run --trade plumber --city "Austin Texas"

    npm install zambo-leadsignal
    npx zambo-leadsignal run --trade plumber --city "Austin Texas"

Free tier: 20 calls and 1 wrap-up free every day per caller, picking
up in another AI always free. The Day Pass ($0.99) makes it unlimited
for 24 hours: https://zambo.dev/day-pass/

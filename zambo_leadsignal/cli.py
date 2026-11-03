"""zambo-leadsignal command line.

    zambo-leadsignal run --trade plumber --city "Austin Texas"
    zambo-leadsignal run --trade roofer --city Denver --note "storm damage focus"

Configuration also by environment: ZAMBO_TRADE, ZAMBO_CITY,
ZAMBO_NOTE, ZAMBO_AGENT_ID, ZAMBO_MCP_URL.
"""

import os
import sys

from .run import run_sweep


def _arg(flag, env, default=None):
    if flag in sys.argv:
        return sys.argv[sys.argv.index(flag) + 1]
    return os.environ.get(env, default)


def main():
    if len(sys.argv) < 2 or sys.argv[1] != "run":
        print(__doc__)
        return 2
    trade = _arg("--trade", "ZAMBO_TRADE")
    city = _arg("--city", "ZAMBO_CITY")
    note = _arg("--note", "ZAMBO_NOTE")
    if not trade or not city:
        print("run needs --trade and --city (or ZAMBO_TRADE / ZAMBO_CITY)")
        return 2
    result = run_sweep(trade, city, note=note,
                       agent_id=os.environ.get("ZAMBO_AGENT_ID",
                                               "leadsignal-agent"))
    print(f"done: job {result['job_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

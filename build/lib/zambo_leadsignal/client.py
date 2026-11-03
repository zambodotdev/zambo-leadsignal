"""Minimal Zambo MCP client: one agent identity, done right.

Step zero of the leadsignal pattern lives here. On initialize, the endpoint
issues a caller handle (in the initialize result's _meta and in the
X-Zambo-Caller-Handle response header). This client saves that handle
in the agent's own state file before anything else happens, and
presents it as _caller_handle on every call, with the agent's name as
_caller_label. Memory, job timelines, and the daily free allowance all
key to that handle. One handle per agent, never shared. Two agents on
one handle are one agent as far as the record is concerned.

Transport: requests when available (it handles proxies correctly),
standard library urllib otherwise. No other dependencies.
"""

import json
import os
import re
import urllib.request
from pathlib import Path

try:
    import requests

    _HAS_REQUESTS = True
except ImportError:  # pragma: no cover
    _HAS_REQUESTS = False

MCP_URL = os.environ.get("ZAMBO_MCP_URL", "https://zambo.dev/mcp")
RUN_URL_RE = re.compile(r"https://zambo\.dev/run/[0-9a-f-]{36}")


def state_dir():
    """Where this install keeps per-agent state files and contribution
    notes. Defaults to ./.zambo-leadsignal in the working directory; override
    with ZAMBO_LEADSIGNAL_STATE_DIR. State files hold caller handles: keep
    them private, never commit them."""
    return Path(os.environ.get("ZAMBO_LEADSIGNAL_STATE_DIR", Path.cwd() / ".zambo-leadsignal"))


class ZamboClient:
    """One agent's session with the Zambo MCP endpoint."""

    def __init__(self, agent_id, agent_name):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.session_id = None
        self.quota_handle = None
        self._next_id = 0
        self.state_file = state_dir() / f".zambo-state-{agent_id}.json"
        self.caller_handle = self._load_saved_handle()

    # -- identity persistence -------------------------------------------

    def _load_saved_handle(self):
        try:
            data = json.loads(self.state_file.read_text())
            return data.get("caller_handle")
        except Exception:
            return None

    def _save_handle(self):
        if self.caller_handle:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(
                json.dumps({"caller_handle": self.caller_handle}, indent=2)
            )

    # -- transport -------------------------------------------------------

    def _post(self, payload, expect_response=True):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "X-Agent-Id": self.agent_id,
            "X-Agent-Name": self.agent_name,
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        if _HAS_REQUESTS:
            resp = requests.post(
                MCP_URL, json=payload, headers=headers, timeout=60
            )
            resp.raise_for_status()
            if self.session_id is None:
                self.session_id = resp.headers.get("Mcp-Session-Id")
            header_handle = resp.headers.get("X-Zambo-Caller-Handle")
            raw = resp.text
        else:
            body = json.dumps(payload).encode()
            req = urllib.request.Request(MCP_URL, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                if self.session_id is None:
                    self.session_id = resp.headers.get("Mcp-Session-Id")
                header_handle = resp.headers.get("X-Zambo-Caller-Handle")
                raw = resp.read().decode()

        if header_handle and not self.caller_handle:
            self.caller_handle = header_handle
        if not expect_response:
            return None
        return self._parse_rpc(raw)

    @staticmethod
    def _parse_rpc(raw):
        message = None
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                try:
                    message = json.loads(line[5:])
                except Exception:
                    pass
        if message is None:
            message = json.loads(raw)
        if "error" in message:
            raise RuntimeError(f"MCP error: {message['error']}")
        return message.get("result", {})

    # -- MCP surface -----------------------------------------------------

    def initialize(self):
        result = self._post(
            {
                "jsonrpc": "2.0",
                "id": self._id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": self.agent_name, "version": "1.0.0"},
                },
            }
        )
        meta = result.get("_meta", {})
        if not self.caller_handle:
            self.caller_handle = meta.get("caller_handle")
        self.quota_handle = meta.get("quota_handle")
        self._save_handle()
        self._post(
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            expect_response=False,
        )
        return result

    def call_tool(self, name, arguments):
        # The caller handle rides in the arguments, the quota handle in
        # _meta, and the agent's id as the caller label, so the shared
        # job's record attributes every step to this agent.
        args = dict(arguments)
        if self.caller_handle:
            args["_caller_handle"] = self.caller_handle
        args.setdefault("_caller_label", self.agent_id)
        params = {"name": name, "arguments": args}
        if self.quota_handle:
            params["_meta"] = {"quota_handle": self.quota_handle}
        result = self._post(
            {
                "jsonrpc": "2.0",
                "id": self._id(),
                "method": "tools/call",
                "params": params,
            }
        )
        handle = (result.get("structuredContent") or {}).get("caller_handle")
        if handle and not self.caller_handle:
            self.caller_handle = handle
            self._save_handle()
        return result

    def _id(self):
        self._next_id += 1
        return self._next_id


def receipt_link(result):
    """Pull the AER-1 receipt link out of a tool result, if present."""
    structured = result.get("structuredContent") or {}
    for key in ("receipt_url", "run_url", "url"):
        value = structured.get(key)
        if isinstance(value, str) and "/run/" in value:
            return value
    match = RUN_URL_RE.search(json.dumps(result))
    return match.group(0) if match else None


def result_text(result):
    parts = []
    for block in result.get("content") or []:
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(parts)

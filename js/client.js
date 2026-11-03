"use strict";
/*
 * Minimal Zambo MCP client: one agent identity, done right.
 *
 * Step zero of the swarm pattern lives here. On initialize, the endpoint
 * issues a caller handle (in the initialize result's _meta and in the
 * X-Zambo-Caller-Handle response header). This client saves that handle
 * in the agent's own state file before anything else happens, and
 * presents it as _caller_handle on every call, with the agent's name as
 * _caller_label. Memory, job timelines, and the daily free allowance all
 * key to that handle. One handle per agent, never shared. Two agents on
 * one handle are one agent as far as the record is concerned.
 *
 * Transport: the global fetch (Node 18+). No dependencies.
 */

const fs = require("fs");
const path = require("path");

const MCP_URL = process.env.ZAMBO_MCP_URL || "https://zambo.dev/mcp";
const RUN_URL_RE = /https:\/\/zambo\.dev\/run\/[0-9a-f-]{36}/;

function stateDir() {
  // Where this install keeps per-agent state files and contribution
  // notes. Defaults to ./.zambo-leadsignal in the working directory; override
  // with ZAMBO_LEADSIGNAL_STATE_DIR. State files hold caller handles: keep
  // them private, never commit them.
  return process.env.ZAMBO_LEADSIGNAL_STATE_DIR || path.join(process.cwd(), ".zambo-leadsignal");
}

class ZamboClient {
  constructor(agentId, agentName) {
    this.agentId = agentId;
    this.agentName = agentName;
    this.sessionId = null;
    this.quotaHandle = null;
    this._nextId = 0;
    this.stateFile = path.join(stateDir(), `.zambo-state-${agentId}.json`);
    this.callerHandle = this._loadSavedHandle();
  }

  _loadSavedHandle() {
    try {
      const data = JSON.parse(fs.readFileSync(this.stateFile, "utf8"));
      return data.caller_handle || null;
    } catch {
      return null;
    }
  }

  _saveHandle() {
    if (this.callerHandle) {
      fs.mkdirSync(path.dirname(this.stateFile), { recursive: true });
      fs.writeFileSync(
        this.stateFile,
        JSON.stringify({ caller_handle: this.callerHandle }, null, 2)
      );
    }
  }

  async _post(payload, expectResponse = true) {
    const headers = {
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
      "X-Agent-Id": this.agentId,
      "X-Agent-Name": this.agentName,
    };
    if (this.sessionId) headers["Mcp-Session-Id"] = this.sessionId;
    const resp = await fetch(MCP_URL, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(60000),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status} from MCP endpoint`);
    if (this.sessionId === null) {
      this.sessionId = resp.headers.get("mcp-session-id");
    }
    const headerHandle = resp.headers.get("x-zambo-caller-handle");
    const raw = await resp.text();
    if (headerHandle && !this.callerHandle) this.callerHandle = headerHandle;
    if (!expectResponse) return null;
    return this._parseRpc(raw);
  }

  _parseRpc(raw) {
    let message = null;
    for (const line of raw.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (trimmed.startsWith("data:")) {
        try {
          message = JSON.parse(trimmed.slice(5));
        } catch {
          /* keep looking */
        }
      }
    }
    if (message === null) message = JSON.parse(raw);
    if (message.error) throw new Error(`MCP error: ${JSON.stringify(message.error)}`);
    return message.result || {};
  }

  async initialize() {
    const result = await this._post({
      jsonrpc: "2.0",
      id: this._id(),
      method: "initialize",
      params: {
        protocolVersion: "2025-03-26",
        capabilities: {},
        clientInfo: { name: this.agentName, version: "1.0.0" },
      },
    });
    const meta = result._meta || {};
    if (!this.callerHandle) this.callerHandle = meta.caller_handle || null;
    this.quotaHandle = meta.quota_handle || null;
    this._saveHandle();
    await this._post(
      { jsonrpc: "2.0", method: "notifications/initialized" },
      false
    );
    return result;
  }

  async callTool(name, argsIn) {
    // The caller handle rides in the arguments, the quota handle in
    // _meta, and the agent's id as the caller label, so the shared job's
    // record attributes every step to this agent.
    const args = { ...argsIn };
    if (this.callerHandle) args._caller_handle = this.callerHandle;
    if (args._caller_label === undefined) args._caller_label = this.agentId;
    const params = { name, arguments: args };
    if (this.quotaHandle) params._meta = { quota_handle: this.quotaHandle };
    const result = await this._post({
      jsonrpc: "2.0",
      id: this._id(),
      method: "tools/call",
      params,
    });
    const handle = (result.structuredContent || {}).caller_handle;
    if (handle && !this.callerHandle) {
      this.callerHandle = handle;
      this._saveHandle();
    }
    return result;
  }

  _id() {
    this._nextId += 1;
    return this._nextId;
  }
}

function receiptLink(result) {
  // Pull the AER-1 receipt link out of a tool result, if present.
  const structured = result.structuredContent || {};
  for (const key of ["receipt_url", "run_url", "url"]) {
    const value = structured[key];
    if (typeof value === "string" && value.includes("/run/")) return value;
  }
  const match = JSON.stringify(result).match(RUN_URL_RE);
  return match ? match[0] : null;
}

function resultText(result) {
  const parts = [];
  for (const block of result.content || []) {
    if (block.type === "text") parts.push(block.text || "");
  }
  return parts.join("\n");
}

module.exports = { ZamboClient, receiptLink, resultText, stateDir, MCP_URL };

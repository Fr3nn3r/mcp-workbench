# 🧪 MCP Workbench — Product Requirements Document (PRD)

**Project Name:** `mcp-workbench`  
**Owner:** OwlAI Engineering  
**Version:** 1.0  
**Status:** Draft  
**Last Updated:** 2025-03-28

---

## 🧭 Purpose

The goal of `mcp-workbench` is to provide an automated, version-aware compliance test suite for validating whether a given **MCP (Model Context Protocol)** server implementation conforms to the official specification (e.g., `2024-11-05`). This ensures interoperability, stability, and protocol correctness across server implementations.

---

## 🎯 Goals & Non-Goals

### Goals

- ✅ Validate MCP server behavior against a specific spec version
- ✅ Support all server-facing features (Prompts, Resources, Tools, Utilities)
- ✅ Detect violations of MUST/SHOULD requirements per feature
- ✅ Support version-specific test logic
- ✅ Provide clear CLI interface and human-readable test reports
- ✅ Enable integration into CI pipelines

### Non-Goals

- ❌ Testing client or host behavior (will be handled in future phases)
- ❌ Automated fuzzing or security testing
- ❌ Backend implementation or protocol enforcement (read-only test client)

---

## 👤 Target Users

- OwlAI engineers and QA testers
- Protocol implementers and server developers
- Integration engineers verifying conformance

---

## 💼 Use Cases

1. **Protocol Engineer** runs `mcp-workbench` against a dev server to check compliance.
2. **CI Pipeline** runs the tool after deploying a new MCP version.
3. **External Developer** validates their MCP-compatible server implementation before release.

---

## 🧱 Key Features & Requirements

| ID    | Feature                       | Description                                                                 | Priority | Type        |
|-------|-------------------------------|-----------------------------------------------------------------------------|----------|-------------|
| F1.1  | Version-aware test runner      | CLI supports `--spec-version`; tests run against correct assertions         | High     | Functional  |
| F1.2  | prompts/list test              | Verifies list of prompts returned with required structure                   | High     | Functional  |
| F1.3  | prompts/get test               | Verifies prompt content, roles, content types, and argument handling        | High     | Functional  |
| F1.4  | prompts/list_changed test      | Optionally detects notifications if `listChanged` is declared               | Medium   | Functional  |
| F2.1  | resources/list + read tests    | Validates resource listing and content reading                              | High     | Functional  |
| F2.2  | resources/list_changed         | Optional support for resource change notifications                          | Medium   | Functional  |
| F2.3  | resources/subscribe test       | Validates subscriptions and updated notifications                           | Medium   | Functional  |
| F3.1  | tools/list and tools/call test | Validates tool discovery, schema, result structure, error handling          | High     | Functional  |
| F4.1  | completion/complete test       | Validates completion behavior for prompts/resources                         | Medium   | Functional  |
| F5.1  | Error response handling        | Verifies standard JSON-RPC error codes for invalid input                    | High     | Functional  |
| F6.1  | Report output                  | Test runner shows pass/fail + reason per assertion (CLI + optional JSON)    | High     | UX          |
| F6.2  | CI-compatible return codes     | Exit code = 1 on failure of any MUST requirement                             | High     | UX          |

---

## ⚙️ Technical Requirements

- Python 3.9+
- Pure client-side JSON-RPC (via HTTP POST)
- Configurable server URL (`--server-url`)
- Configurable spec version (`--spec-version`)
- Modular test structure (one test file per feature group)
- Uses `pytest`, `httpx`, `pydantic`

---

## 📐 Architecture Overview

```
mcp-workbench/
├── tests/
│   ├── test_prompts_*.py
│   ├── test_resources_*.py
│   ├── test_tools_*.py
│   └── test_utilities_*.py
├── mcp/
│   ├── client.py         # JSON-RPC client
│   ├── protocol.py       # Data models
│   ├── spec_registry.py  # Supported versions & metadata
├── conftest.py           # Shared fixtures
├── requirements.txt
├── pytest.ini
└── cli.py                # Optional CLI wrapper
```

---

## 🧪 Testing & QA Strategy

- Use `pytest` as the test runner
- Fixtures share server and version configuration
- Each test is tagged by feature and requirement level (MUST/SHOULD)
- Compliance report printed to stdout + optional JSON

---

## 🚀 Milestones

| Sprint | Milestone                              | Features                                |
|--------|-----------------------------------------|------------------------------------------|
| 1      | Prompts compliance MVP                  | F1.1 → F1.4, F5.1, F6.1, F6.2             |
| 2      | Resources test support                  | F2.1 → F2.3                               |
| 3      | Tools and completion testing            | F3.1, F4.1                                |
| 4      | Full version switching + CI harness     | CLI polish, export, advanced reporting   |

---

## 📎 Open Questions

- Should version-specific requirements be stored as code, JSON, or markdown?
- Do we want machine-readable compliance output (e.g. JUnit XML or JSON)?
- Should we allow test skipping if a capability is not declared (e.g., listChanged)?
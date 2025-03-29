import pytest
import json
from pathlib import Path
from mcp.spec_registry import SUPPORTED_SPECS


def pytest_addoption(parser):
    parser.addoption(
        "--spec-version",
        action="store",
        default="2024-11-05",
        help="Target MCP spec version (e.g. 2024-11-05)",
    )


@pytest.fixture(scope="session")
def spec_version(request):
    version = request.config.getoption("--spec-version")
    if version not in SUPPORTED_SPECS:
        raise pytest.UsageError(f"Unsupported spec version: {version}")
    return version


def pytest_sessionstart(session):
    version = session.config.getoption("--spec-version")
    print(f"\n🧪 Running compliance checks for MCP spec version: {version}\n")


def pytest_configure(config):
    """Register the MCP requirement marker."""
    config.addinivalue_line(
        "markers",
        "mcp_requirement(feature, level): mark test with MCP feature and requirement level",
    )
    config.mcp_results = []


def pytest_runtest_makereport(item, call):
    """Capture test results for MCP compliance reporting."""
    if call.when != "call":
        return

    feature = level = None
    for mark in item.iter_markers(name="mcp_requirement"):
        feature = mark.kwargs.get("feature")
        level = mark.kwargs.get("level")

    if feature is None or level is None:
        return  # Skip tests without MCP requirement markers

    outcome = "PASS" if call.excinfo is None else "FAIL"
    if call.excinfo and call.excinfo.typename == "Skipped":
        outcome = "SKIPPED"

    item.config.mcp_results.append(
        {"test": item.nodeid, "feature": feature, "level": level, "outcome": outcome}
    )


def pytest_sessionfinish(session, exitstatus):
    """Print MCP compliance summary and write report to file."""
    results = session.config.mcp_results
    if not results:
        return  # No MCP tests were run

    print("\n=== MCP COMPLIANCE SUMMARY ===\n")

    must_failures = 0
    for r in results:
        print(f"[{r['outcome']}] {r['feature']} ({r['level']}) — {r['test']}")
        if r["level"] == "MUST" and r["outcome"] == "FAIL":
            must_failures += 1

    if must_failures > 0:
        print(f"\n❌ {must_failures} MUST-level failures found!")
        session.exitstatus = 1
    else:
        print("\n✅ All MUST-level requirements passed.")

    # Write JSON report
    Path("reports").mkdir(exist_ok=True)
    with open("reports/summary.json", "w") as f:
        json.dump(results, f, indent=2)

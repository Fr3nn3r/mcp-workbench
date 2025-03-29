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
    parser.addoption(
        "--server-url", action="store", help="URL of the MCP server to test"
    )
    parser.addoption(
        "--level",
        action="store",
        default="MUST,SHOULD",
        help="Comma-separated list of requirement levels to test (MUST,SHOULD)",
    )
    parser.addoption(
        "--json-report", action="store", help="Path to save the JSON report"
    )


@pytest.fixture(scope="session")
def spec_version(request):
    version = request.config.getoption("--spec-version")
    if version not in SUPPORTED_SPECS:
        raise pytest.UsageError(f"Unsupported spec version: {version}")
    return version


@pytest.fixture(scope="session")
def server_url(request):
    url = request.config.getoption("--server-url")
    if not url:
        pytest.skip("No server URL provided")
    return url


@pytest.fixture(scope="session")
def allowed_levels(request):
    return [level.upper() for level in request.config.getoption("--level").split(",")]


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


def pytest_runtest_setup(item):
    """Skip tests based on requirement level filtering."""
    mark = item.get_closest_marker("mcp_requirement")
    if mark is None:
        return  # Not an MCP test

    level = mark.kwargs.get("level", "").upper()
    allowed = [l.upper() for l in item.config.getoption("--level").split(",")]

    if level and level not in allowed:
        pytest.skip(
            f"Skipping test with level '{level}', not in allowed levels: {', '.join(allowed)}"
        )


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

    # Organize results by feature
    features = {}
    for r in results:
        feature = r["feature"]
        if feature not in features:
            features[feature] = []
        features[feature].append(r)

    # Write JSON report
    report_data = {
        "summary": {
            "total_tests": len(results),
            "passed": sum(1 for r in results if r["outcome"] == "PASS"),
            "failed": sum(1 for r in results if r["outcome"] == "FAIL"),
            "skipped": sum(1 for r in results if r["outcome"] == "SKIPPED"),
            "must_failures": must_failures,
        },
        "features": features,
        "tests": results,
    }

    # Get report path from command line or use default
    report_path = session.config.getoption("--json-report") or "reports/summary.json"
    report_dir = Path(report_path).parent
    report_dir.mkdir(exist_ok=True, parents=True)

    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)

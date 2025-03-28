"""Pytest configuration and hooks for MCP compliance reporting."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pytest
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.reports import TestReport

from tests._meta import MCP_REQUIREMENTS


def pytest_configure(config: Config) -> None:
    """Configure pytest with custom markers and initialize results storage."""
    config.addinivalue_line(
        "markers",
        "mcp_requirement(feature, level, req_id): mark test with MCP spec metadata",
    )

    # Initialize results storage
    if not hasattr(config, "mcp_results"):
        config.mcp_results = []

    # Create reports directory if it doesn't exist
    Path("reports").mkdir(exist_ok=True)


def pytest_runtest_makereport(item: Item, call) -> None:
    """Process test results and store compliance data."""
    if call.when == "call" or (call.when == "setup" and call.excinfo):
        outcome = "PASS" if call.excinfo is None else "FAIL"
        if hasattr(item, "iter_markers"):
            markers = [m for m in item.iter_markers(name="mcp_requirement")]
            if markers:
                marker = markers[0]
                feature = marker.kwargs.get("feature", "unknown")
                level = marker.kwargs.get("level", "unknown")
                req_id = marker.kwargs.get("req_id", None)

                result = {
                    "nodeid": item.nodeid,
                    "outcome": outcome,
                    "feature": feature,
                    "level": level,
                    "req_id": req_id,
                    "description": None,
                    "reason": str(call.excinfo) if call.excinfo else None,
                    "duration": call.duration if hasattr(call, "duration") else None,
                }

                # Add requirement description if available
                if feature in MCP_REQUIREMENTS:
                    for req in MCP_REQUIREMENTS[feature]:
                        if req.id == req_id:
                            result["description"] = req.description
                            break

                item.session.config.mcp_results.append(result)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Generate and save the compliance report."""
    results = session.config.mcp_results

    # Generate timestamp for the report
    timestamp = datetime.now().isoformat()

    # Create the full report structure
    report = {
        "timestamp": timestamp,
        "summary": {
            "total": len(results),
            "passed": len([r for r in results if r["outcome"] == "PASS"]),
            "failed": len([r for r in results if r["outcome"] == "FAIL"]),
            "skipped": len([r for r in results if r["outcome"] == "SKIPPED"]),
            "must_failures": len(
                [r for r in results if r["outcome"] == "FAIL" and r["level"] == "MUST"]
            ),
            "should_failures": len(
                [
                    r
                    for r in results
                    if r["outcome"] == "FAIL" and r["level"] == "SHOULD"
                ]
            ),
        },
        "results": results,
    }

    # Save JSON report
    with open("reports/summary.json", "w") as f:
        json.dump(report, f, indent=2)

    # Generate and print CLI summary
    print("\n=== MCP COMPLIANCE SUMMARY ===\n")

    # Print feature-wise summary
    features = sorted(set(r["feature"] for r in results))
    for feature in features:
        print(f"\n🔍 {feature}")
        feature_results = [r for r in results if r["feature"] == feature]
        for result in feature_results:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "SKIPPED": "⚠️",
                "XFAIL": "🔸",
                "XPASS": "🔹",
            }.get(result["outcome"], "❓")

            print(
                f"{status_icon} [{result['level']}] {result['req_id'] or 'unknown'}: "
                f"{result['description'] or result['nodeid']}"
            )
            if result["reason"]:
                print(f"   └─ {result['reason']}")

    # Print overall summary
    print("\n=== SUMMARY ===")
    print(f"Total Tests: {report['summary']['total']}")
    print(f"✅ Passed: {report['summary']['passed']}")
    print(f"❌ Failed: {report['summary']['failed']}")
    print(f"⚠️ Skipped: {report['summary']['skipped']}")

    if report["summary"]["must_failures"] > 0:
        print(f"\n❌ {report['summary']['must_failures']} MUST requirements failed!")
        session.exitstatus = 1

    if report["summary"]["should_failures"] > 0:
        print(f"\n⚠️ {report['summary']['should_failures']} SHOULD requirements failed")


@pytest.fixture
def client():
    """Provide a test client."""
    # Your existing client fixture code here
    pass

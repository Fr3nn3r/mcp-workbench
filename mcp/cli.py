import argparse
import subprocess
import sys
import os
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="MCP compliance runner")
    parser.add_argument(
        "--server-url", required=True, help="Base URL of the MCP server"
    )
    parser.add_argument("--spec-version", default="2024-11-05", help="MCP spec version")
    parser.add_argument(
        "--features",
        default="all",
        help="Comma-separated features (e.g., prompts,tools)",
    )
    parser.add_argument(
        "--level", default="MUST,SHOULD", help="Requirement levels to include"
    )
    parser.add_argument("--json-report", help="Path to save JSON report")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show verbose output"
    )
    args = parser.parse_args()

    # Pass config to pytest via env/args
    pytest_args = [
        "pytest",
        "-v" if args.verbose else "-q",
        f"--server-url={args.server_url}",
        f"--spec-version={args.spec_version}",
        f"--level={args.level}",
    ]

    if args.features != "all":
        feature_filter = " or ".join(args.features.split(","))
        pytest_args += ["-k", feature_filter]

    # Create reports directory if not exists
    if args.json_report:
        report_path = Path(args.json_report)
        report_dir = report_path.parent
        if not report_dir.exists():
            report_dir.mkdir(parents=True)

    # Run pytest
    print(f"🧪 Running MCP compliance checks for spec version: {args.spec_version}")
    result = subprocess.run(pytest_args, capture_output=True, text=True)

    # Print output
    print(result.stdout)
    if result.stderr:
        print("Errors:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)

    # Return appropriate exit code
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run `mvn clean install` in matching subdirectories and log failures.

Default behavior:
- Search recursively under this script's directory
- Match directory names using the pattern: elavon-*-ds-na
- Run `mvn clean install` in each matched directory
- Write failed build logs to: ./log-files/<timestamp>.log
"""

from __future__ import annotations

import argparse
import fnmatch
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List


DEFAULT_PATTERN = "elavon-*-ds-na"
DEFAULT_LOG_DIR = "log-files"
TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"


@dataclass
class BuildResult:
    directory: Path
    return_code: int
    output: str

    @property
    def succeeded(self) -> bool:
        return self.return_code == 0


def find_matching_directories(root: Path, pattern: str) -> List[Path]:
    """Find directories whose names match the provided glob-like pattern."""
    matches: List[Path] = []

    for candidate in root.rglob("*"):
        if candidate.is_dir() and fnmatch.fnmatch(candidate.name, pattern):
            matches.append(candidate)

    return sorted(matches)


def run_maven_build(directory: Path) -> BuildResult:
    """Execute `mvn clean install` inside `directory`."""
    cmd = ["mvn", "clean", "install"]

    completed = subprocess.run(
        cmd,
        cwd=directory,
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
    )

    merged_output = ""
    if completed.stdout:
        merged_output += completed.stdout
    if completed.stderr:
        if merged_output:
            merged_output += "\n"
        merged_output += completed.stderr

    return BuildResult(
        directory=directory,
        return_code=completed.returncode,
        output=merged_output.strip() or "<no output captured>",
    )


def ensure_log_path(root: Path, log_dir_name: str) -> Path:
    """Create log directory and return a timestamped log file path."""
    log_dir = root / log_dir_name
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    return log_dir / f"{timestamp}.log"


def write_failure_log(log_file: Path, failed_results: List[BuildResult]) -> None:
    """Write all failed build logs in a clean, appendable format."""
    with log_file.open("a", encoding="utf-8") as f:
        f.write(f"Build run timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Failed builds: {len(failed_results)}\n")
        f.write("=" * 80 + "\n\n")

        for result in failed_results:
            f.write(f"{result.directory.name}: logs of failed build\n")
            f.write(f"Path: {result.directory}\n")
            f.write(f"Exit code: {result.return_code}\n")
            f.write("-" * 80 + "\n")
            f.write(result.output)
            f.write("\n" + "-" * 80 + "\n\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Find subdirectories matching a pattern and run 'mvn clean install' in each. "
            "Failed runs are written to a timestamped log file."
        )
    )
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parent),
        help="Root directory to search from (default: script directory).",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help=f"Directory name pattern to match (default: {DEFAULT_PATTERN}).",
    )
    parser.add_argument(
        "--log-dir",
        default=DEFAULT_LOG_DIR,
        help=f"Log directory name under root (default: {DEFAULT_LOG_DIR}).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    if not root.exists() or not root.is_dir():
        print(f"Root path is not a directory: {root}")
        return 2

    if shutil.which("mvn") is None:
        print("Maven executable 'mvn' was not found in PATH.")
        return 3

    targets = find_matching_directories(root, args.pattern)

    if not targets:
        print(
            f"No subdirectories matching pattern '{args.pattern}' were found under: {root}"
        )
        return 0

    print(f"Found {len(targets)} matching subdirectories.")

    failed_results: List[BuildResult] = []

    for index, directory in enumerate(targets, start=1):
        print(f"[{index}/{len(targets)}] Running mvn clean install in: {directory}")

        result = run_maven_build(directory)

        if result.succeeded:
            print(f"PASS: {directory.name}")
        else:
            print(f"FAIL: {directory.name} (exit code {result.return_code})")
            failed_results.append(result)

    log_file = ensure_log_path(root, args.log_dir)

    if failed_results:
        write_failure_log(log_file, failed_results)
        print(f"Failed build logs written to: {log_file}")
    else:
        with log_file.open("a", encoding="utf-8") as f:
            f.write(f"Build run timestamp: {datetime.now().isoformat()}\n")
            f.write("No failed builds.\n")
        print(f"All builds passed. Run summary written to: {log_file}")

    print(
        f"Completed: total={len(targets)}, passed={len(targets) - len(failed_results)}, "
        f"failed={len(failed_results)}"
    )

    return 1 if failed_results else 0


if __name__ == "__main__":
    raise SystemExit(main())

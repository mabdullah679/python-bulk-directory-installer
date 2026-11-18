"""Tests for run_maven_builds.py using a fake `mvn` on PATH (no Maven needed).

Run: python3 -m unittest discover -s tests -v
"""
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "run_maven_builds.py"
# Fake mvn: fails when the working directory name contains "bad".
FAKE_MVN = '#!/bin/sh\ncase "$(basename "$PWD")" in *bad*) echo "BUILD FAILURE" >&2; exit 1;; esac\necho BUILD SUCCESS\n'


class RunMavenBuildsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "root"
        self.root.mkdir()
        self.bin = Path(self.tmp.name) / "bin"
        self.bin.mkdir()
        mvn = self.bin / "mvn"
        mvn.write_text(FAKE_MVN)
        mvn.chmod(mvn.stat().st_mode | stat.S_IEXEC)

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, *args, path=None):
        env = dict(os.environ, PATH=path if path is not None else f"{self.bin}{os.pathsep}{os.environ['PATH']}")
        return subprocess.run([sys.executable, "-I", str(SCRIPT), "--root", str(self.root), *args],
                              capture_output=True, text=True, env=env)

    def logs(self):
        return list((self.root / "log-files").glob("*.log"))

    def test_all_pass_exit_0_and_summary_log(self):
        (self.root / "elavon-a-ds-na").mkdir()
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("passed=1, failed=0", r.stdout)
        self.assertIn("No failed builds.", self.logs()[0].read_text())

    def test_failure_exit_1_and_logged(self):
        (self.root / "elavon-ok-ds-na").mkdir()
        (self.root / "elavon-bad-ds-na").mkdir()
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("total=2, passed=1, failed=1", r.stdout)
        log = self.logs()[0].read_text()
        self.assertIn("elavon-bad-ds-na: logs of failed build", log)
        self.assertIn("BUILD FAILURE", log)
        self.assertNotIn("elavon-ok-ds-na: logs", log)

    def test_custom_pattern_only_matches_pattern(self):
        (self.root / "elavon-bad-ds-na").mkdir()
        (self.root / "svc-one").mkdir()
        r = self.run_script("--pattern", "svc-*")
        self.assertEqual(r.returncode, 0)
        self.assertIn("passed=1, failed=0", r.stdout)

    def test_no_match_exit_0(self):
        r = self.run_script()
        self.assertEqual(r.returncode, 0)
        self.assertIn("No subdirectories matching", r.stdout)

    def test_invalid_root_exit_2(self):
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--root", str(self.root / "nope")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_mvn_missing_exit_3(self):
        r = self.run_script(path=str(Path(self.tmp.name) / "empty"))
        self.assertEqual(r.returncode, 3)


if __name__ == "__main__":
    unittest.main()

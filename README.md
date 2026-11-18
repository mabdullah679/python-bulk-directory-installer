# Multi-Directory Maven Installer

A stdlib-only Python script that finds subdirectories matching a name pattern, runs `mvn clean install` in each, and writes a timestamped log of the run (failed-build output included).

```
run_maven_builds.py --root DIR --pattern GLOB
   -> recursive scan for dirs matching GLOB
   -> `mvn clean install` in each (PASS/FAIL printed)
   -> DIR/log-files/YYYYMMDD-HHMMSS.log (failures, or "No failed builds.")
```

Not local/contained: Maven itself (and whatever repositories your projects' builds download from) must be supplied by you.

## Prerequisites
- Python 3.8+ (tested on 3.14); standard library only, nothing to `pip install`.
- Maven (`mvn`) on `PATH` for real runs. The tests do not need it.

## Run it
1. `python3 run_maven_builds.py --root /path/to/projects` (PowerShell: `python .\run_maven_builds.py --root "C:\path\to\projects"`).
2. Read PASS/FAIL lines and the final `Completed: total=, passed=, failed=` line.
3. Open the log named at the end of the output.

Defaults: `--root` is the script's own folder, `--pattern` is `elavon-*-ds-na`, `--log-dir` is `log-files` (created under the root). Use `--pattern "svc-*"` to match other folders.

If nothing happens: no matching directory gives "No subdirectories matching..." and exit 0; check `--root` and `--pattern` (the pattern matches the directory name, not the path).

## What it does
| Situation | Result |
|---|---|
| All matched builds succeed | exit 0, log contains `No failed builds.` |
| One or more builds fail | exit 1, log has name, path, exit code and captured mvn output per failure |
| No matching directories | exit 0, no log written |
| `--root` is not a directory | exit 2 |
| `mvn` not on `PATH` | exit 3 |

Builds run one after another, not in parallel.

## Tests
`python3 -m unittest discover -s tests -v`: 6 tests in [tests/test_run_maven_builds.py](tests/test_run_maven_builds.py) covering every exit code, pattern selection and the log contents. They put a fake `mvn` script on `PATH`, so they need no Maven and no network. They do not cover a real Maven build. CI: [ci.yml](.github/workflows/ci.yml).

## Layout
| Path | Role |
|---|---|
| [run_maven_builds.py](run_maven_builds.py) | the whole tool |
| [tests/test_run_maven_builds.py](tests/test_run_maven_builds.py) | unit tests with fake `mvn` |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | tests + gitleaks on PRs |

## Design notes
- A new log file per run (timestamped) rather than appending to one file, so earlier runs stay comparable.
- Failures are collected and logged at the end instead of stopping at the first one, so one bad module does not hide the rest.

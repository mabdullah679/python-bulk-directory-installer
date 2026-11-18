# python-bulk-directory-installer

Single-file Python 3 script (stdlib only) that runs `mvn clean install` in every subdirectory matching a glob and logs the failures. Global rules: `~/.claude/CLAUDE.md`.

## Commands
- Run: `python3 run_maven_builds.py [--root DIR] [--pattern GLOB] [--log-dir NAME]`
- Tests: `python3 -m unittest discover -s tests -v` (6 tests; use a fake `mvn`, so Maven is not needed)

## Conventions / don't
- Exit codes are part of the contract: 0 ok/no match, 1 build failed, 2 bad `--root`, 3 `mvn` not on PATH. Tests pin them.
- Default pattern `elavon-*-ds-na` is the owner's original use case; leave it unless asked.
- Never commit `log-files/` (gitignored). Branch + PR only; never push to `main`.

# Multi-Directory Maven Installer

This script finds subdirectories that match a name pattern, runs `mvn clean install` inside each one, and writes failed build logs to a timestamped log file.

## Prerequisites

- Python 3.8+
- Maven (`mvn`) available in your PATH

## File in this project

- `run_maven_builds.py`

## Quick start (default behavior)

From this project folder, run:

```powershell
python .\run_maven_builds.py
```

Default behavior:

- Searches recursively from this script's folder
- Matches subdirectory names with pattern `elavon-*-ds-na`
- Runs `mvn clean install` in each matched folder
- Writes logs to `log-files\YYYYMMDD-HHMMSS.log`

## Run for a desired target subdirectory

If you want to scan only a specific folder tree, pass `--root`:

```powershell
python .\run_maven_builds.py --root "C:\path\to\your\target\folder"
```

## Use a custom matching pattern

```powershell
python .\run_maven_builds.py --root "C:\path\to\your\target\folder" --pattern "elavon-*-ds-na"
```

## Use a custom log folder name

```powershell
python .\run_maven_builds.py --log-dir "log-files"
```

## Output and logs

- Successful builds are printed to the console as `PASS`
- Failed builds are printed as `FAIL`
- Every run creates a new timestamped log file so multiple runs are preserved
- For failures, each entry is recorded in this format:

```text
subdirectory-name: logs of failed build
Path: ...
Exit code: ...
<captured mvn output>
```

## Exit codes

- `0`: all builds passed, or no matching directories found
- `1`: one or more builds failed
- `2`: invalid `--root` path
- `3`: Maven not found in PATH

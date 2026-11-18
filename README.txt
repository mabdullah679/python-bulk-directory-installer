MULTI-DIRECTORY MAVEN INSTALLER

This is one Python script. You point it at a folder. It looks through that folder (and everything under it) for sub-folders whose names match a pattern, runs "mvn clean install" in each one, one after another, and writes a log file for the run. It prints PASS or FAIL for each folder as it goes.

What you need: Python 3.8 or newer (no extra packages) and Maven on your PATH. The tests do not need Maven. Maven itself and anything your builds download are outside this project.

How to run it: python3 run_maven_builds.py --root /path/to/projects (on Windows PowerShell: python .\run_maven_builds.py --root "C:\path\to\projects"). If you leave out --root it uses the folder the script is in. The default pattern is elavon-*-ds-na, which is the owner's original use case; change it with --pattern, for example --pattern "svc-*". The pattern matches the folder name only, not the full path. Logs go to a folder called log-files under the root (change with --log-dir), one new file per run named by date and time.

If nothing seems to happen, it found no matching folders. It says so and exits with 0. Check --root and --pattern.

What comes out: if every build passes, exit code 0 and the log says "No failed builds." If any build fails, exit code 1 and the log lists, for each failure, the folder name, its path, the exit code and the captured Maven output. Exit code 2 means --root is not a folder. Exit code 3 means Maven was not found on PATH. If no folder matched, exit 0 and no log file is written.

Tests: run "python3 -m unittest discover -s tests -v". There are 6 tests. They use a fake "mvn" so they need no Maven and no network. They check every exit code, the pattern selection and the log contents. They do not test a real Maven build.

Where things are: run_maven_builds.py is the whole tool, tests/test_run_maven_builds.py is the test file, .github/workflows/ci.yml runs the tests and a secret scan on pull requests.

Why it works this way: each run gets its own log file so old runs can be compared, and failures are collected and written at the end so one bad project does not hide the others.

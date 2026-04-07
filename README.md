# AI Terminal Assistant

Type what you want to do in plain English. The assistant translates it to the right shell command for your OS, explains what it does, and asks before running anything.

## Features

- **Natural language → shell command** via Claude
- **Safety confirmation** before every command, with a red warning for destructive operations
- **OS-aware** — reads your OS, shell, cwd, and Python version so generated commands are always correct
- **C file scanner** — a Python C extension (`scanner.c`) for fast recursive directory scanning, demonstrates dropping to low-level code for performance

## Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

#optional
# Build the C extension (requires gcc / clang)
cd scanner && python setup.py build_ext --inplace && cd ..

export ANTHROPIC_API_KEY="your-api-key"

python main.py

```

## Usage

```bash
python main.py
```

```
> find all python files modified in the last 3 days
  Command:      find . -name "*.py" -mtime -3
  What it does: Finds all Python files modified in the last 3 days

  Run it? [y/N] y

> delete all __pycache__ folders
  Command:      find . -type d -name "__pycache__" -exec rm -rf {} +
  What it does: Recursively removes all __pycache__ directories

  ⚠  This command may be irreversible.
  Run it? [y/N]

> scan ./my_project 100000
  Scanning './my_project' (min size: 100000 bytes) using C extension...
  1024.3 KB   ./my_project/data/dataset.csv
   512.1 KB   ./my_project/models/weights.pkl
```

## Architecture

```
main.py                  — REPL loop
assistant/
  context.py             — gathers OS/env info passed to Claude
  interpreter.py         — sends request to Claude, parses JSON response
  executor.py            — confirms with user, runs via subprocess
scanner/
  scanner.c              — C extension: fast recursive file walk using readdir()
  setup.py               — builds the extension with setuptools
```

## Building the C Extension

The `scanner` module is a Python C extension that uses POSIX `readdir()` to walk directories faster than Python's `os.walk`. It demonstrates direct OS communication via system calls and the Python/C API.

```bash
cd scanner
python setup.py build_ext --inplace
# Produces: scanner.cpython-3xx-linux-gnu.so (or .pyd on Windows)
```

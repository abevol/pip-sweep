[English] | [中文](README_ZH.md)

# pip-sweep

`pip-sweep` is a command-line tool to clean Python package dependencies using the **Mark-Sweep garbage collection algorithm**.

When you uninstall large frameworks like `django`, running `pip uninstall` only removes the main package itself, leaving a large number of downstream dependencies installed in your environment, creating "dependency garbage".

`pip-sweep` intelligently analyzes the dependency graph of the current environment to safely identify and completely uninstall those orphaned packages that are **only required by the target package and not used by any other surviving packages**.

## ⚠️ Important: Environment & Isolation Limits

`pip-sweep` operates on the **Python environment in which it is running**. 

- **Virtual Environments (venv/conda)**: To clean packages inside a virtual environment, you must activate the environment first, install `pip-sweep` inside it, and then run it.
- **Global Environment**: To clean globally installed packages, `pip-sweep` must be run by the global Python interpreter (e.g., global `pip-sweep` command or `python -m pip_sweep.cli`).
- **`pipx` and `uvx` Warning**: Since `pipx run` and `uvx` execute tools within their own **isolated private virtual environments**, running `pip-sweep` via them will **only see and clean their private environment**, and **CANNOT** detect or clean your global or active virtual environment packages.

---

## ✨ Features

- 🧩 **Mark-Sweep Garbage Collection**: Accurate dependency propagation algorithm to prevent accidental uninstallation.
- 🛡️ **System Protection**: Protects `pip`, `setuptools`, `wheel`, and other baseline infrastructure packages by default.
- 🔍 **Dry-Run Mode**: Supports `-d` / `--dry-run` to preview the uninstallation plan safely.
- 💎 **Multi-package Support**: Clean multiple target packages at once.

## 🚀 Quick Start & Installation

### For Active Virtual Environment or Global Environment
Install `pip-sweep` into the target environment first:
```bash
pip install pip-sweep
# Or using uv
uv pip install pip-sweep
```

Run the cleaner:
```bash
# General CLI usage
pip-sweep headroom-ai

# Or run via Python module entrance
python -m pip_sweep.cli headroom-ai
```

## 📖 Command-line Usage

```text
usage: pip-sweep [-h] [-d] [-y] [-v] packages [packages ...]

pip-sweep: A Python dependency cleaner using Mark-Sweep garbage collection algorithm.

positional arguments:
  packages              One or more target Python packages to clean

options:
  -h, --help            Show this help message and exit
  -d, --dry-run         Analyze and print the clean plan only, without actual uninstallation
  -y, --yes             Automatically confirm the uninstallation plan, skipping confirmation prompts
  -v, --verbose         Verbose output, showing kept packages and their specific reasons
  --version             Show program's version number and exit
```

## 🔧 Local Development

To debug or contribute to the project locally:

```bash
# Clone the repository
git clone https://github.com/abevol/pip-sweep.git
cd pip-sweep

# Create venv and install in editable mode
uv pip install -e .
```

## 📝 License

MIT License © 2026 pip-sweep developers

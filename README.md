[English] | [中文](README_ZH.md)

# pip-sweep

`pip-sweep` is a command-line tool to clean Python package dependencies using the **Mark-Sweep garbage collection algorithm**.

When you uninstall large frameworks like `django`, running `pip uninstall` only removes the main package itself, leaving a large number of downstream dependencies installed in your environment, creating "dependency garbage".

`pip-sweep` intelligently analyzes the dependency graph of the current environment to safely identify and completely uninstall those orphaned packages that are **only required by the target package and not used by any other surviving packages**.

## ⚠️ Critical: Execution Environment & pipx/uvx Incompatibility

`pip-sweep` operates strictly on the **active Python environment in which it is running**. 

- **Virtual Environments (venv/conda)**: To clean packages inside a virtual environment, you must activate the environment, install `pip-sweep` inside it, and run it.
- **Global Environment**: To clean globally installed packages, `pip-sweep` must be run by the global Python interpreter.
- **`pipx run` / `uvx` Incompatibility**: Using `pipx run pip-sweep` or `uvx pip-sweep` **WILL NOT WORK**. These tools run the cleaner inside an **isolated, empty, temporary virtual environment** containing only `pip-sweep` itself. Consequently, they cannot see or clean your active virtual environment or global packages. **Do not use `pipx run` or `uvx` to execute this tool.**

---

## ✨ Features

- 🧩 **Mark-Sweep Garbage Collection**: Accurate dependency propagation algorithm to prevent accidental uninstallation.
- 🛡️ **System Protection**: Protects `pip`, `setuptools`, `wheel`, and other baseline infrastructure packages by default.
- 🔍 **Dry-Run Mode**: Supports `-d` / `--dry-run` to preview the uninstallation plan safely.
- 💎 **Multi-package Support**: Clean multiple target packages at once.

## 🚀 Installation & Usage

To clean packages in a virtual or global environment, you must install `pip-sweep` directly into that target environment:

### 1. Install into target environment
```bash
pip install pip-sweep
# Or using uv
uv pip install pip-sweep
```

### 2. Run the cleaner
```bash
# Run via CLI alias
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

To debug or contribute locally:

```bash
# Clone the repository
git clone https://github.com/abevol/pip-sweep.git
cd pip-sweep

# Create venv and install in editable mode
uv pip install -e .
```

## 📝 License

MIT License © 2026 pip-sweep developers

[English] | [中文](README_ZH.md)

# pip-sweep

`pip-sweep` is a command-line tool to clean Python package dependencies using the **Mark-Sweep garbage collection algorithm**.

When you uninstall large frameworks like `django`, running `pip uninstall` only removes the main package itself, leaving a large number of downstream dependencies installed in your environment, creating "dependency garbage".

`pip-sweep` intelligently analyzes the dependency graph of the current environment to safely identify and completely uninstall those orphaned packages that are **only required by the target package and not used by any other surviving packages**.

## ✨ Features

- 🧩 **Mark-Sweep Garbage Collection**: Accurate dependency propagation algorithm to prevent accidental uninstallation.
- 🛡️ **System Protection**: Protects `pip`, `setuptools`, `wheel`, and other baseline infrastructure packages by default.
- 🔍 **Dry-Run Mode**: Supports `-d` / `--dry-run` to preview the uninstallation plan safely.
- 💎 **Multi-package Support**: Clean multiple target packages at once.
- 🚀 **Modern Toolchain Friendly**: Full support for `uv` and `pipx` instant execution via `uvx` and `pipx run`.

## 🚀 Quick Start

No need to install globally, you can run it directly using modern package managers:

```bash
# Using uvx (Recommended)
uvx --from . pip-sweep headroom-ai

# Using pipx
pipx run --spec . pip-sweep headroom-ai
```

## 💻 Installation

To install `pip-sweep` globally:

```bash
pipx install .
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
git clone https://github.com/yourusername/pip-sweep.git
cd pip-sweep

# Create venv and install in editable mode
uv pip install -e .
```

## 📝 License

MIT License © 2026 pip-sweep developers

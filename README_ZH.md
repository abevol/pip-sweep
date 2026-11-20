[English](README.md) | [中文]

# pip-sweep

`pip-sweep` 是一个基于 **Mark-Sweep（标记-清除）算法** 的 Python 依赖包清理工具。

当您卸载 `django` 或其他大型框架时，仅仅执行 `pip uninstall` 只会删除主包本身，而它们引入的大量下游依赖包则会残留在环境中，形成“依赖垃圾”。

`pip-sweep` 能智能地分析当前环境的依赖关系图，安全地找出那些**仅被目标包依赖，且没有被其他任何存活包依赖**的孤立包，并进行一键彻底清理。

## ⚠️ 重要：执行环境一致性与 pipx/uvx 不兼容说明

`pip-sweep` 的运行和清理范围**完全受限于当前运行它的 Python 解释器环境**。

- **虚拟环境 (venv/conda)**：若要清理某个虚拟环境中的依赖包，您必须先激活该环境，在此环境内安装 `pip-sweep`，然后再执行清理。
- **全局环境**：若要清理系统全局环境的依赖包，必须由全局的 Python 解释器来运行它。
- **`pipx run` / `uvx` 不兼容警告**：使用 `pipx run pip-sweep` 或 `uvx pip-sweep` **无法正常工作**。这些命令会在一个**仅包含 `pip-sweep` 工具自身的隔离、临时私有环境**中执行清理，因此它们**无法**读取或清理您激活的虚拟环境或系统全局环境中的包。**请勿使用 `pipx run` 或 `uvx` 执行此工具。**

---

## ✨ 特性

- 🧩 **Mark-Sweep 垃圾回收**：精准化的依赖传播算法，规避误卸载。
- 🛡️ **系统保护**：默认保护 `pip`、`setuptools`、`wheel` 等核心工具包。
- 🔍 **模拟预览 (Dry-Run)**：支持 `-d` / `--dry-run` 预览清单，安全无忧。
- 💎 **多包清理**：支持一次性指定多个目标包进行清理。
- 📌 **指定需要保留的包**：支持 `-e` / `--exclude` 在卸载时指定需要保留的包（及其自身依赖）。

## 🚀 安装与使用

要清理依赖包，您必须在目标 Python 环境内运行 `pip-sweep`。

### 1. 激活您的目标虚拟环境（若有）

根据您的操作系统与终端 Shell，选择相应的激活命令：

* **macOS / Linux (bash/zsh)**:
  ```bash
  source .venv/bin/activate
  ```
* **Windows (PowerShell)**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
* **Windows (cmd.exe)**:
  ```cmd
  .venv\Scripts\activate.bat
  ```
* **Conda 虚拟环境**:
  ```bash
  conda activate myenv
  ```

*(注：如果您想清理系统全局环境的包，请跳过此激活步骤)。*

### 2. 安装到已激活的环境中
```bash
pip install pip-sweep
# 或者使用 uv
uv pip install pip-sweep
```

### 3. 执行清理
```bash
pip-sweep <package-name>
```

#### 3.1 卸载时保留指定的包

使用 `-e` / `--exclude` 保留那些本来会随目标一起被卸载的包

```bash
# 保留 rfc3986 和 requests-toolbelt (以及它们依赖的包)
pip-sweep twine -e rfc3986 requests-toolbelt

# 等价写法: 重复使用 -e, 或用逗号分隔
pip-sweep twine -e rfc3986 -e requests-toolbelt
pip-sweep twine -e rfc3986,requests-toolbelt
```

被保留的包本身及其依赖子树都会存活，目标自身不允许被排除。

> [!TIP]
>
> 由于 `-e` 接受空格分隔的列表，使用空格作为分隔符时，请把它放在目标包之后，否则 argparse 会把后面的包名当作保留列表的一部分。

## 📖 命令行参数及用法

```text
usage: pip-sweep [-h] [-d] [-y] [-v] [-e PACKAGE [PACKAGE ...]] packages [packages ...]

pip-sweep: 采用 Mark-Sweep 垃圾回收算法的 Python 依赖包清理工具。

positional arguments:
  packages              要清理的一个或多个目标 Python 包名称

options:
  -h, --help             显示帮助信息并退出
  -d, --dry-run          仅分析并打印清理计划，不执行实际卸载
  -y, --yes              自动确认卸载计划，跳过确认交互提示
  -v, --verbose          详细输出，显示判定存活的包及具体原因
  -e, --exclude PACKAGE [PACKAGE ...]
                         要保留的包名列表（可空格分隔多个，也可用 -e 重复指定），
                         这些包及其依赖不会被卸载
  --version              显示当前版本并退出
```

## 🔧 本地开发

如果您想在本地调试或贡献代码，可以使用 `uv` 创建虚拟环境并以可编辑模式安装：

```bash
# 克隆代码库
git clone https://github.com/abevol/pip-sweep.git
cd pip-sweep

# 创建 venv 并安装
uv pip install -e .
```

## 📝 开源协议

MIT License © 2026 pip-sweep developers

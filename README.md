# pip-sweep

`pip-sweep` 是一个基于 **Mark-Sweep（标记-清除）算法** 的 Python 依赖包清理工具。

当您卸载 `django` 或其他大型框架时，仅仅执行 `pip uninstall` 只会删除主包本身，而它们引入的大量下游依赖包则会残留在环境中，形成“依赖垃圾”。

`pip-sweep` 能智能地分析当前环境的依赖关系图，安全地找出那些**仅被目标包依赖，且没有被其他任何存活包依赖**的孤立包，并进行一键彻底清理。

## ✨ 特性

- 🧩 **Mark-Sweep 垃圾回收**：精准化的依赖传播算法，规避误卸载。
- 🛡️ **系统保护**：默认保护 `pip`、`setuptools`、`wheel` 等核心工具包。
- 🔍 **模拟预览 (Dry-Run)**：支持 `-d` / `--dry-run` 预览清单，安全无忧。
- 💎 **多包清理**：支持一次性指定多个目标包进行清理。
- 🚀 **现代工具链友好**：完整支持 `uv` 和 `pipx` 的 `uvx` 及 `pipx run` 即时执行。

## 🚀 快速开始

您无需在全局手动安装，直接使用现代工具即可一键运行：

```bash
# 使用 uvx （推荐）
uvx pip-sweep headroom-ai

# 使用 pipx
pipx run pip-sweep headroom-ai
```

## 💻 安装使用

如果您希望将 `pip-sweep` 安装到全局命令行：

```bash
pipx install pip-sweep
```

## 📖 命令行参数及用法

```text
usage: pip-sweep [-h] [-d] [-y] [-v] packages [packages ...]

pip-sweep: 采用 Mark-Sweep 垃圾回收算法的 Python 依赖包清理工具。

positional arguments:
  packages              要清理的一个或多个目标 Python 包名称

options:
  -h, --help             显示帮助信息并退出
  -d, --dry-run          仅分析并打印清理计划，不执行实际卸载
  -y, --yes              自动确认卸载计划，跳过确认交互提示
  -v, --verbose          详细输出，显示判定存活的包及具体原因
  --version              显示当前版本并退出
```

## 🔧 本地开发

如果您想在本地调试或贡献代码，可以使用 `uv` 创建虚拟环境并以可编辑模式安装：

```bash
# 克隆代码库
git clone https://github.com/yourusername/pip-sweep.git
cd pip-sweep

# 创建 venv 并安装
uv pip install -e .
```

## 📝 开源协议

MIT License © 2026 pip-sweep developers

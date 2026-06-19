import argparse
import sys
import locale
import os
from pip_sweep.core import DependencySweeper, normalize
from pip_sweep import __version__

# 自动检测系统默认语言，支持环境变量覆盖
try:
    env_lang = os.environ.get("LANG", "") or os.environ.get("LC_ALL", "") or os.environ.get("LC_CTYPE", "")
    if env_lang:
        IS_ZH = "zh" in env_lang.lower()
    else:
        default_lang, _ = locale.getdefaultlocale()
        IS_ZH = default_lang and default_lang.lower().startswith('zh')
except Exception:
    IS_ZH = False

# 多语言字典
LOCALES = {
    "zh": {
        "description": "pip-sweep: 采用 Mark-Sweep 垃圾回收算法的 Python 依赖包清理工具。",
        "help_packages": "要清理的一个或多个目标 Python 包名称",
        "help_dry_run": "仅分析并打印清理计划，不执行实际卸载",
        "help_yes": "自动确认卸载计划，跳过确认交互提示",
        "help_verbose": "详细输出，显示判定存活的包及具体原因",
        "help_version": "显示当前版本并退出",
        "scanning": "⏳ 正在扫描全局/虚拟环境中的已安装包...",
        "found_packages": "   已发现 {count} 个已安装包",
        "not_found_warning": "⚠️  警告：在当前环境中找不到包：{packages}",
        "error_no_installed": "❌ 错误：指定的目标包在当前环境中均未安装，无法进行清理。",
        "running_algorithm": "⏳ 正在运行 Mark-Sweep 算法分析依赖图...",
        "to_uninstall_title": "🗑️   将被彻底卸载的包 (目标主包及不再被其他包需要的孤立依赖，共 {count} 个):",
        "to_keep_title": "⚠️   闭包内将被保留的包 (共 {count} 个):",
        "none": "(无)",
        "no_garbage": "💡 提示：分析完毕，没有发现需要卸载的孤立包。",
        "dry_run_info": "💡 提示：当前处于 Dry-run 模拟模式，已跳过实际卸载操作。",
        "confirm_prompt": "❓ 确认要彻底卸载以上 {count} 个包吗？(y/N): ",
        "cancelled": "已取消操作。",
        "user_cancelled": "\n操作已被用户取消。",
        "uninstalling": "🚀 开始批量卸载中...",
        "uninstall_failed": "❌ 卸载失败！\n{detail}",
        "success": "✅ 深度清理完成！",
        "cache_tip": "💡 提示：请执行 `pip cache purge` 以清理 pip 下载缓存。",
        "reason_core_infrastructure": "核心环境基石",
        "reason_independent_tool": "独立顶层工具 (入度为0)",
        "reason_external_dependency": "被外部依赖: {parents}",
        "reason_surviving_subtree": "属于存活子树"
    },
    "en": {
        "description": "pip-sweep: A Python dependency cleaner using Mark-Sweep garbage collection algorithm.",
        "help_packages": "One or more target Python packages to clean",
        "help_dry_run": "Analyze and print the clean plan only, without actual uninstallation",
        "help_yes": "Automatically confirm the uninstallation plan, skipping confirmation prompts",
        "help_verbose": "Verbose output, showing kept packages and their specific reasons",
        "help_version": "Show program's version number and exit",
        "scanning": "⏳ Scanning installed packages in global/virtual environment...",
        "found_packages": "   Found {count} installed packages",
        "not_found_warning": "⚠️  Warning: Package(s) not found in the current environment: {packages}",
        "error_no_installed": "❌ Error: None of the specified target packages are installed in the current environment.",
        "running_algorithm": "⏳ Running Mark-Sweep algorithm to analyze dependency graph...",
        "to_uninstall_title": "🗑️   Packages to be completely uninstalled (targets & orphaned dependencies, {count} in total):",
        "to_keep_title": "⚠️   Packages to be kept in the closure ({count} in total):",
        "none": "(None)",
        "no_garbage": "💡 Info: Analysis completed, no orphaned packages found to uninstall.",
        "dry_run_info": "💡 Info: Dry-run simulation mode is active, skipped actual uninstallation.",
        "confirm_prompt": "❓ Are you sure you want to completely uninstall the {count} package(s) above? (y/N): ",
        "cancelled": "Operation cancelled.",
        "user_cancelled": "\nOperation cancelled by user.",
        "uninstalling": "🚀 Starting batch uninstallation...",
        "uninstall_failed": "❌ Uninstallation failed!\n{detail}",
        "success": "✅ Deep clean completed successfully!",
        "cache_tip": "💡 Info: Please run `pip cache purge` to clear the pip download cache.",
        "reason_core_infrastructure": "Core environment infrastructure",
        "reason_independent_tool": "Independent top-level tool (in-degree is 0)",
        "reason_external_dependency": "Required by external package(s): {parents}",
        "reason_surviving_subtree": "Belongs to a surviving subtree"
    }
}

def get_txt(key, **kwargs):
    lang = "zh" if IS_ZH else "en"
    text = LOCALES[lang].get(key, LOCALES["en"].get(key, ""))
    return text.format(**kwargs)

def parse_args():
    parser = argparse.ArgumentParser(
        description=get_txt("description")
    )
    parser.add_argument(
        "packages",
        nargs="+",
        help=get_txt("help_packages")
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help=get_txt("help_dry_run")
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help=get_txt("help_yes")
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help=get_txt("help_verbose")
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"pip-sweep {__version__}",
        help=get_txt("help_version")
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    sweeper = DependencySweeper()
    
    print(get_txt("scanning"))
    sweeper.build_dependency_graph()
    print(get_txt("found_packages", count=len(sweeper.all_installed)))
    
    input_packages = args.packages
    not_installed = []
    installed_targets = []
    
    for pkg in input_packages:
        norm_pkg = normalize(pkg)
        if norm_pkg not in sweeper.all_installed:
            not_installed.append(pkg)
        else:
            installed_targets.append(pkg)
            
    if not_installed:
        print(get_txt("not_found_warning", packages=', '.join(not_installed)))
        
    if not installed_targets:
        print(get_txt("error_no_installed"))
        sys.exit(1)
        
    print(get_txt("running_algorithm"))
    to_uninstall, kept_packages = sweeper.find_garbage(installed_targets)
    
    print("-" * 70)
    print(get_txt("to_uninstall_title", count=len(to_uninstall)))
    if to_uninstall:
        for pkg in sorted(to_uninstall):
            print(f"    - {pkg}")
    else:
        print(f"    {get_txt('none')}")
        
    if kept_packages and (args.verbose or args.dry_run):
        print("\n" + get_txt("to_keep_title", count=len(kept_packages)))
        for pkg, reason_key, extra_info in sorted(kept_packages):
            if reason_key == "external_dependency":
                reason_desc = get_txt("reason_external_dependency", parents=extra_info)
            else:
                reason_desc = get_txt(f"reason_{reason_key}")
            print(f"    - {pkg} ({reason_desc})")
            
    print("-" * 70)
    print("")
    
    if not to_uninstall:
        print(get_txt("no_garbage"))
        return
        
    if args.dry_run:
        print(get_txt("dry_run_info"))
        return
        
    if not args.yes:
        try:
            confirm = input(get_txt("confirm_prompt", count=len(to_uninstall))).strip().lower()
        except KeyboardInterrupt:
            print(get_txt("user_cancelled"))
            sys.exit(0)
        if confirm != 'y':
            print(get_txt("cancelled"))
            sys.exit(0)
            
    print(get_txt("uninstalling"))
    sorted_uninstall = sorted(
        to_uninstall,
        key=lambda x: (normalize(x) in [normalize(t) for t in installed_targets], x)
    )
    
    success, detail = sweeper.uninstall_packages(sorted_uninstall)
    if not success:
        print(get_txt("uninstall_failed", detail=detail))
        sys.exit(1)
    else:
        print(get_txt("success"))
        print(get_txt("cache_tip"))

if __name__ == "__main__":
    main()

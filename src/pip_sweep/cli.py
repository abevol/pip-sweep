import argparse
import sys
from pip_sweep.core import DependencySweeper, normalize
from pip_sweep import __version__

def parse_args():
    parser = argparse.ArgumentParser(
        description="pip-sweep: 采用 Mark-Sweep 垃圾回收算法的 Python 依赖包清理工具。"
    )
    parser.add_argument(
        "packages",
        nargs="+",
        help="要清理的一个或多个目标 Python 包名称"
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="仅分析并打印清理计划，不执行实际卸载"
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="自动确认卸载计划，跳过确认交互提示"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出，显示判定存活的包及具体原因"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"pip-sweep {__version__}",
        help="显示当前版本并退出"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    sweeper = DependencySweeper()
    
    print("⏳ 正在扫描全局/虚拟环境中的已安装包...")
    sweeper.build_dependency_graph()
    print(f"   已发现 {len(sweeper.all_installed)} 个已安装包")
    
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
        print(f"⚠️  警告：在当前环境中找不到包：{', '.join(not_installed)}")
        
    if not installed_targets:
        print("❌ 错误：指定的目标包在当前环境中均未安装，无法进行清理。")
        sys.exit(1)
        
    print("⏳ 正在运行 Mark-Sweep 算法分析依赖图...")
    to_uninstall, kept_packages = sweeper.find_garbage(installed_targets)
    
    print("-" * 70)
    print(f"🗑️   将被彻底卸载的包 (目标主包及不再被其他包需要的孤立依赖，共 {len(to_uninstall)} 个):")
    if to_uninstall:
        for pkg in sorted(to_uninstall):
            print(f"    - {pkg}")
    else:
        print("    (无)")
        
    if kept_packages and (args.verbose or args.dry_run):
        print(f"\n⚠️   闭包内将被保留的包 (共 {len(kept_packages)} 个):")
        for pkg, reason in sorted(kept_packages):
            print(f"    - {pkg} (原因: {reason})")
            
    print("-" * 70)
    print("")
    
    if not to_uninstall:
        print("💡 提示：分析完毕，没有发现需要卸载的孤立包。")
        return
        
    if args.dry_run:
        print("💡 提示：当前处于 Dry-run 模拟模式，已跳过实际卸载操作。")
        return
        
    if not args.yes:
        try:
            confirm = input(f"❓ 确认要彻底卸载以上 {len(to_uninstall)} 个包吗？(y/N): ").strip().lower()
        except KeyboardInterrupt:
            print("\n操作已被用户取消。")
            sys.exit(0)
        if confirm != 'y':
            print("已取消操作。")
            sys.exit(0)
            
    print(f"🚀 开始批量卸载中...")
    sorted_uninstall = sorted(
        to_uninstall,
        key=lambda x: (normalize(x) in [normalize(t) for t in installed_targets], x)
    )
    
    success, detail = sweeper.uninstall_packages(sorted_uninstall)
    if not success:
        print(f"❌ 卸载失败！\n{detail}")
        sys.exit(1)
    else:
        print("✅ 深度清理完成！")
        print("💡 提示：请执行 `pip cache purge` 以清理 pip 下载缓存。")

if __name__ == "__main__":
    main()

import importlib.metadata
import re
import subprocess
import sys
from collections import defaultdict, deque
from typing import Set, Dict, List, Tuple

def normalize(name: str) -> str:
    return re.sub(r'[-_.]+', '-', name).lower()

class DependencySweeper:
    CORE_INFRASTRUCTURE = {
        'pip', 'setuptools', 'wheel', 'pkg-resources', 'distribute', 'ensurepip'
    }

    def __init__(self):
        self.forward_graph = defaultdict(set)
        self.reverse_graph = defaultdict(set)
        self.all_installed = set()
        self.original_names = {}

    def build_dependency_graph(self):
        """扫描当前环境并构建依赖关系图"""
        all_distributions = []
        for dist in importlib.metadata.distributions():
            pkg_name = normalize(dist.name)
            self.all_installed.add(pkg_name)
            self.original_names[pkg_name] = dist.name
            all_distributions.append((pkg_name, dist.requires))

        for pkg_name, reqs in all_distributions:
            if not reqs:
                continue
            for req_str in reqs:
                req_main = req_str.split(';')[0].strip()
                match = re.match(r'^([a-zA-Z0-9_-]+)', req_main)
                if match:
                    dep_name = normalize(match.group(1))
                    if dep_name in self.all_installed:
                        self.forward_graph[pkg_name].add(dep_name)
                        self.reverse_graph[dep_name].add(pkg_name)

    def get_dependency_closure(self, targets: List[str]) -> Set[str]:
        """获取目标包集合的合并依赖闭包"""
        closure = set()
        queue = deque()
        for t in targets:
            norm_t = normalize(t)
            if norm_t in self.all_installed:
                closure.add(norm_t)
                queue.append(norm_t)
        
        while queue:
            current = queue.popleft()
            for dep in self.forward_graph.get(current, []):
                if dep not in closure and dep in self.all_installed:
                    closure.add(dep)
                    queue.append(dep)
        return closure

    def find_garbage(self, targets: List[str]) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """
        核心 Mark-Sweep 垃圾回收算法
        返回: (to_uninstall, kept_packages_with_reasons)
        其中 reasons 结构为: (pkg_name, reason_key, extra_info)
        """
        targets_norm = [normalize(t) for t in targets]
        installed_targets_norm = [t for t in targets_norm if t in self.all_installed]
        if not installed_targets_norm:
            return [], []

        closure = self.get_dependency_closure(installed_targets_norm)

        # 阶段 1：Mark
        survivors = set()
        for pkg in self.all_installed:
            if pkg not in closure:
                survivors.add(pkg)
                continue
            if pkg in self.CORE_INFRASTRUCTURE:
                survivors.add(pkg)
                continue
            if pkg not in targets_norm and len(self.reverse_graph.get(pkg, set())) == 0:
                survivors.add(pkg)
                continue
            parents = self.reverse_graph.get(pkg, set())
            if any(p not in closure for p in parents):
                survivors.add(pkg)

        # 阶段 2：Propagation
        final_kept = set(survivors)
        queue = deque(survivors)
        while queue:
            current = queue.popleft()
            for dep in self.forward_graph.get(current, []):
                if dep in self.all_installed and dep not in final_kept:
                    final_kept.add(dep)
                    queue.append(dep)

        # 阶段 3：Sweep
        to_uninstall_norm = [pkg for pkg in closure if pkg not in final_kept]
        
        kept_packages = []
        for pkg in sorted(final_kept):
            if pkg in closure:
                if pkg in self.CORE_INFRASTRUCTURE:
                    reason_key = "core_infrastructure"
                    extra_info = ""
                elif pkg not in targets_norm and len(self.reverse_graph.get(pkg, set())) == 0:
                    reason_key = "independent_tool"
                    extra_info = ""
                else:
                    ext_parents = [p for p in self.reverse_graph.get(pkg, set()) if p not in closure]
                    if ext_parents:
                        reason_key = "external_dependency"
                        extra_info = ", ".join(self.original_names.get(p, p) for p in ext_parents)
                    else:
                        reason_key = "surviving_subtree"
                        extra_info = ""
                kept_packages.append((self.original_names.get(pkg, pkg), reason_key, extra_info))

        to_uninstall = [self.original_names.get(pkg, pkg) for pkg in to_uninstall_norm]
        return to_uninstall, kept_packages

    def uninstall_packages(self, packages: List[str]) -> Tuple[bool, str]:
        """批量卸载指定的包"""
        if not packages:
            return True, "No packages to uninstall."
        
        cmd = [sys.executable, "-m", "pip", "uninstall"] + packages + ["-y"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return False, result.stderr
        return True, result.stdout

from typing import Dict, Set
import logging
from src.repo_manager import RepositoryManager

class DependencyAnalyzer:
    def __init__(self, max_depth: int):
        self.max_depth = max_depth
        self.dependencies: Dict[str, Set[str]] = {}
        self.repo_manager = RepositoryManager()
        self.debug_mode = False

    def analyze_dependencies(self, package: str, current_depth: int = 0) -> None:
        """Recursively analyze package dependencies up to max_depth."""
        if current_depth >= self.max_depth or package in self.dependencies:
            return
            
        direct_deps = self.repo_manager.get_package_dependencies(package)
        if self.debug_mode:
            logging.info(f"Package {package} has dependencies: {direct_deps}")
            
        self.dependencies[package] = direct_deps
        
        for dep in direct_deps:
            self.analyze_dependencies(dep, current_depth + 1)

    def sanitize_node_id(self, name: str) -> str:
        """Sanitize package name for use as node ID in Mermaid."""
        return name.replace('-', '_').replace('.', '_').replace('+', 'plus')

    def generate_mermaid(self) -> str:
        """Generate Mermaid graph description."""
        if not self.dependencies:
            return "graph LR\n    A[No dependencies found]"

        mermaid_lines = ["graph LR"]
        visited_edges = set()
        
        # Add nodes first
        nodes = set()
        for package in self.dependencies.keys():
            nodes.add(package)
            nodes.update(self.dependencies[package])
        
        # Calculate depth for each node
        depths: Dict[str, int] = {}
        
        def calculate_depth(pkg: str, depth: int = 0) -> None:
            if pkg not in depths or depth < depths[pkg]:
                depths[pkg] = depth
                if pkg in self.dependencies:
                    for dep in self.dependencies[pkg]:
                        calculate_depth(dep, depth + 1)
        
        # Calculate depths starting from root package
        root_package = list(self.dependencies.keys())[0]
        calculate_depth(root_package)
        
        # Add nodes with style based on depth
        for node in sorted(nodes):
            node_id = self.sanitize_node_id(node)
            depth = depths.get(node, 0)
            # Более светлые оттенки для большей глубины
            color = f"#{'f' * (depth + 1)}{'e' * (11 - depth)}"
            mermaid_lines.append(f'    {node_id}["{node}"]')
            mermaid_lines.append(f'    style {node_id} fill:{color}')
        
        # Add edges
        for package, deps in sorted(self.dependencies.items()):
            pkg_id = self.sanitize_node_id(package)
            for dep in sorted(deps):
                dep_id = self.sanitize_node_id(dep)
                edge = f"{pkg_id}-->{dep_id}"
                if edge not in visited_edges:
                    mermaid_lines.append(f"    {pkg_id} --> {dep_id}")
                    visited_edges.add(edge)
        
        return "\n".join(mermaid_lines)
    
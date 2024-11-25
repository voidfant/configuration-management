from typing import Dict, Set

from src.repo_manager import RepositoryManager

class DependencyAnalyzer:
    def __init__(self, max_depth: int):
        self.max_depth = max_depth
        self.dependencies: Dict[str, Set[str]] = {}
        self.repo_manager = RepositoryManager()

    def analyze_dependencies(self, package: str, current_depth: int = 0) -> None:
        """Recursively analyze package dependencies up to max_depth."""
        if current_depth >= self.max_depth or package in self.dependencies:
            return
            
        direct_deps = self.repo_manager.get_package_dependencies(package)
        self.dependencies[package] = direct_deps
        
        for dep in direct_deps:
            self.analyze_dependencies(dep, current_depth + 1)

    def sanitize_node_id(self, name: str) -> str:
        """Sanitize package name for use as node ID in Mermaid."""
        return name.replace('-', '_').replace('.', '_')

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
        
        for node in sorted(nodes):
            node_id = self.sanitize_node_id(node)
            mermaid_lines.append(f'    {node_id}["{node}"]')
        
        # Add edges
        for package, deps in sorted(self.dependencies.items()):
            pkg_id = self.sanitize_node_id(package)
            for dep in sorted(deps):
                dep_id = self.sanitize_node_id(dep)
                edge = f"{pkg_id}-->{dep_id}"
                if edge not in visited_edges:
                    mermaid_lines.append(f"    {pkg_id} --> {dep_id}")
                    visited_edges.add(edge)
        
        # Add legend for depth levels
        current_pkg = None
        max_depth_found = 0
        depths: Dict[str, int] = {}
        
        def calculate_depth(pkg: str, depth: int = 0) -> None:
            if pkg not in depths or depth < depths[pkg]:
                depths[pkg] = depth
                if pkg in self.dependencies:
                    for dep in self.dependencies[pkg]:
                        calculate_depth(dep, depth + 1)
        
        calculate_depth(list(self.dependencies.keys())[0])
        
        if depths:
            max_depth_found = max(depths.values())
            mermaid_lines.append("\n    %% Depth levels")
            for pkg, depth in sorted(depths.items()):
                pkg_id = self.sanitize_node_id(pkg)
                color = f"fill:#{'e' * (11 - depth)}{'5' * depth}"
                mermaid_lines.append(f"    style {pkg_id} {color}")
            
            # Add legend
            mermaid_lines.append("\n    %% Legend")
            for i in range(max_depth_found + 1):
                legend_id = f"depth{i}"
                color = f"fill:#{'e' * (11 - i)}{'5' * i}"
                mermaid_lines.append(f"    {legend_id}[\"Depth {i}\"]")
                mermaid_lines.append(f"    style {legend_id} {color}")
        
        return "\n".join(mermaid_lines)

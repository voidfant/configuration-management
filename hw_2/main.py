import os
import logging
import argparse
import webbrowser

from src.common.repository import Repository
from src.dependency_analyzer import DependencyAnalyzer
from src.dependency_visualizer import DependencyVisualizer


def parse_args():
    parser = argparse.ArgumentParser(description='Visualize Ubuntu package dependencies')
    parser.add_argument('--visualizer', required=True, help='Path to graph visualizer')
    parser.add_argument('--package', required=True, help='Package to analyze')
    parser.add_argument('--max-depth', type=int, default=3, help='Maximum dependency depth')
    parser.add_argument('--repo-url', help='Ubuntu repository URL',
                       default='http://archive.ubuntu.com/ubuntu')
    parser.add_argument('--distribution', help='Ubuntu distribution',
                       default='jammy')
    parser.add_argument('--component', help='Repository component',
                       default='main')
    
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO)
    
    # Analyze dependencies
    analyzer = DependencyAnalyzer(args.max_depth)
    if args.repo_url or args.distribution or args.component:
        analyzer.repo_manager.repository = Repository(
            name="custom",
            url=args.repo_url,
            distribution=args.distribution,
            component=args.component
        )
    
    analyzer.analyze_dependencies(args.package)
    
    # Generate Mermaid diagram
    mermaid_content = analyzer.generate_mermaid()
    # Visualize the graph
    visualizer = DependencyVisualizer(args.visualizer)
    visualizer.visualize(mermaid_content)

if __name__ == '__main__':
    main()

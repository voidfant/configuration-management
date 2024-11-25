import os
import logging
import tempfile
import subprocess

class DependencyVisualizer:
    def __init__(self, visualizer_path: str):
        self.visualizer_path = visualizer_path
        
    def visualize(self, mermaid_content: str) -> None:
        """Visualize the Mermaid graph using external visualizer."""
        with open('temp.mmd', mode='w+') as f:
            f.write(mermaid_content)
            temp_file = f.name
        print(mermaid_content)
        try:
            subprocess.run([self.visualizer_path, '-i', temp_file], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to visualize graph: {e}")

import gzip
import unittest
from unittest.mock import patch, MagicMock
from src.repo_manager import RepositoryManager
from src.dependency_analyzer import DependencyAnalyzer
from src.dependency_visualizer import DependencyVisualizer
import subprocess


class TestRepositoryManager(unittest.TestCase):
    def setUp(self):
        self.repo_manager = RepositoryManager()
        self.repo_manager.debug_mode = True

    def create_mock_packages_content(self, component: str) -> bytes:
        content = f"""Package: test-package-{component}
Version: 1.0
Depends: lib1, lib2 (>= 1.0), lib3 | lib4

Package: lib1
Version: 1.0
Depends: lib5

Package: lib2
Version: 2.0
Depends: lib6
"""
        return gzip.compress(content.encode('utf-8'))

    def test_parse_packages_file(self):
        test_content = """Package: pkg1
Version: 1.0
Depends: lib1, lib2 (>= 1.0), lib3 | lib4

Package: pkg2
Version: 1.0
Depends: lib1, lib5
"""
        packages = self.repo_manager.parse_packages_file(test_content)

        self.assertIn("pkg1", packages)
        self.assertIn("pkg2", packages)
        self.assertEqual(packages["pkg1"].depends, {"lib1", "lib2"})
        self.assertEqual(packages["pkg2"].depends, {"lib1", "lib5"})


class TestDependencyAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = DependencyAnalyzer(max_depth=2)
        self.analyzer.debug_mode = True
        self.analyzer.dependencies = {}

    @patch.object(RepositoryManager, 'get_package_dependencies')
    def test_analyze_dependencies_max_depth(self, mock_get_deps):
        def get_mock_deps(package):
            deps = {
                "pkg1": {"pkg2", "pkg3"},
                "pkg2": {"pkg4"},
                "pkg3": {"pkg5"},
                "pkg4": {"pkg6"},
                "pkg5": {"pkg6"}
            }
            return deps.get(package, set())

        mock_get_deps.side_effect = get_mock_deps

        self.analyzer.analyze_dependencies("pkg1")

        self.assertIn("pkg1", self.analyzer.dependencies)
        self.assertIn("pkg2", self.analyzer.dependencies)
        self.assertIn("pkg3", self.analyzer.dependencies)
        self.assertNotIn("pkg6", self.analyzer.dependencies)  # Limited by max_depth

    def test_sanitize_node_id(self):
        test_cases = [
            ("simple-package", "simple_package"),
            ("package.name", "package_name"),
            ("package-with.both-symbols", "package_with_both_symbols"),
            ("c++", "cplusplus"),
            ("complex+package-name.test", "complexpluspackage_name_test")
        ]

        for input_name, expected_output in test_cases:
            self.assertEqual(self.analyzer.sanitize_node_id(input_name), expected_output)

    def test_generate_mermaid_empty(self):
        mermaid = self.analyzer.generate_mermaid()
        self.assertIn("No dependencies found", mermaid)

    def test_generate_mermaid_with_dependencies(self):
        self.analyzer.dependencies = {
            "pkg1": {"pkg2", "pkg3"},
            "pkg2": {"pkg4"},
            "pkg3": set()
        }

        mermaid = self.analyzer.generate_mermaid()

        self.assertIn("graph LR", mermaid)
        self.assertIn('pkg1["pkg1"]', mermaid)
        self.assertIn('pkg2["pkg2"]', mermaid)
        self.assertIn('pkg3["pkg3"]', mermaid)
        self.assertIn('pkg4["pkg4"]', mermaid)
        self.assertIn("pkg1 --> pkg2", mermaid)
        self.assertIn("pkg1 --> pkg3", mermaid)
        self.assertIn("pkg2 --> pkg4", mermaid)
        self.assertIn("style pkg1 fill:#", mermaid)


class TestDependencyVisualizer(unittest.TestCase):
    def setUp(self):
        self.visualizer = DependencyVisualizer("node_modules/.bin/mmdc")

    @patch('subprocess.run')
    def test_visualize(self, mock_run):
        mermaid_content = "graph LR\n    A --> B"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = "temp.mmd"
            self.visualizer.visualize(mermaid_content)

            mock_run.assert_called_once()
            self.assertEqual(mock_run.call_args[0][0], ["node_modules/.bin/mmdc", "-i", "temp.mmd"])


if __name__ == '__main__':
    unittest.main()

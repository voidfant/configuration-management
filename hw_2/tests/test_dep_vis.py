import gzip
import unittest
from unittest.mock import patch, MagicMock

from src.repo_manager import RepositoryManager
from src.dependency_analyzer import DependencyAnalyzer
from src.dependency_visualizer import DependencyVisualizer

class TestRepositoryManager(unittest.TestCase):
    def setUp(self):
        self.repo_manager = RepositoryManager()

    @patch('urllib.request.urlopen')
    def test_download_packages_file(self, mock_urlopen):
        # Prepare mock response
        mock_response = MagicMock()
        mock_gzip_content = gzip.compress(b"""Package: test-package
Depends: lib1, lib2 (>= 1.0), lib3 | lib4
""")
        mock_response.read.return_value = mock_gzip_content
        mock_urlopen.return_value.__enter__.return_value = mock_response

        content = self.repo_manager.download_packages_file()
        self.assertIn("Package: test-package", content)

    def test_parse_packages_file(self):
        test_content = """Package: pkg1
Depends: lib1, lib2 (>= 1.0), lib3 | lib4

Package: pkg2
Depends: lib1, lib5
"""
        packages = self.repo_manager.parse_packages_file(test_content)
        
        self.assertIn("pkg1", packages)
        self.assertIn("pkg2", packages)
        self.assertEqual(packages["pkg1"].depends, {"lib1", "lib2"})
        self.assertEqual(packages["pkg2"].depends, {"lib1", "lib5"})

    @patch('urllib.request.urlopen')
    def test_get_package_dependencies(self, mock_urlopen):
        # Mock repository data
        mock_response = MagicMock()
        mock_gzip_content = gzip.compress(b"""Package: test-package
Depends: lib1, lib2 (>= 1.0), lib3 | lib4
""")
        mock_response.read.return_value = mock_gzip_content
        mock_urlopen.return_value.__enter__.return_value = mock_response

        deps = self.repo_manager.get_package_dependencies("test-package")
        self.assertEqual(deps, {"lib1", "lib2"})

class TestDependencyAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = DependencyAnalyzer(max_depth=2)

    @patch.object(RepositoryManager, 'get_package_dependencies')
    def test_analyze_dependencies_max_depth(self, mock_get_deps):
        # Mock dependencies
        def get_mock_deps(package):
            deps = {
                "pkg1": {"pkg2"},
                "pkg2": {"pkg3"},
                "pkg3": {"pkg4"}
            }
            return deps.get(package, set())

        mock_get_deps.side_effect = get_mock_deps

        self.analyzer.analyze_dependencies("pkg1")
        self.assertEqual(len(self.analyzer.dependencies), 2)  # Only pkg1 and pkg2 due to max_depth=2

    def test_generate_mermaid(self):
        self.analyzer.dependencies = {
            "pkg1": {"pkg2", "pkg3"},
            "pkg2": {"pkg3"},
        }
        
        mermaid = self.analyzer.generate_mermaid()
        self.assertIn("graph LR", mermaid)
        self.assertIn("pkg1[pkg1] --> pkg2[pkg2]", mermaid)
        self.assertIn("pkg1[pkg1] --> pkg3[pkg3]", mermaid)
        self.assertIn("pkg2[pkg2] --> pkg3[pkg3]", mermaid)

class TestDependencyVisualizer(unittest.TestCase):
    def setUp(self):
        self.visualizer = DependencyVisualizer("/path/to/visualizer")

    @patch('subprocess.run')
    def test_visualize(self, mock_run):
        mermaid_content = "graph LR\n    A-->B"
        
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = "test.mmd"
            self.visualizer.visualize(mermaid_content)
            
            # Check if visualizer was called with correct file
            mock_run.assert_called_once()
            self.assertEqual(mock_run.call_args[0][0], ["/path/to/visualizer", "test.mmd"])


if __name__ == '__main__':
    unittest.main()

import re
import gzip
import urllib
import logging
from typing import Dict, Set
from urllib.error import URLError
from urllib.request import urlopen

from src.common.repository import Repository
from src.common.package_info import PackageInfo

class RepositoryManager:
    def __init__(self):
        # Default Ubuntu repository
        self.repository = Repository(
            name="ubuntu-main",
            url="http://archive.ubuntu.com/ubuntu",
            distribution="jammy",  # Ubuntu 22.04 LTS
            component="main"
        )
        self.packages_cache: Dict[str, PackageInfo] = {}
        
    def download_packages_file(self) -> str:
        """Download and decompress Packages.gz file from repository."""
        packages_url = f"{self.repository.url}/dists/{self.repository.distribution}/{self.repository.component}/binary-amd64/Packages.gz"
        
        try:
            with urlopen(packages_url) as response:
                with gzip.GzipFile(fileobj=response) as gz_file:
                    return gz_file.read().decode('utf-8')
        except URLError as e:
            logging.error(f"Failed to download Packages file: {e}")
            return ""

    def parse_packages_file(self, content: str) -> Dict[str, PackageInfo]:
        """Parse Packages file content and extract package information."""
        packages: Dict[str, PackageInfo] = {}
        current_package = ""
        current_depends: Set[str] = set()

        for line in content.splitlines():
            if line.startswith("Package: "):
                if current_package:
                    packages[current_package] = PackageInfo(current_package, current_depends)
                current_package = line.split("Package: ")[1].strip()
                current_depends = set()
            elif line.startswith("Depends: "):
                # Parse dependencies, handling versions and alternatives
                deps_str = line.split("Depends: ")[1]
                # Split by comma and handle each dependency
                for dep in deps_str.split(","):
                    dep = dep.strip()
                    # Extract package name without version or architecture constraints
                    match = re.match(r'^([a-zA-Z0-9\-\.]+)(?:\s|$|\(|\[)', dep)
                    if match:
                        dep_name = match.group(1)
                        if "|" not in dep:  # Skip alternative dependencies
                            current_depends.add(dep_name)

        # Add last package
        if current_package:
            packages[current_package] = PackageInfo(current_package, current_depends)

        return packages

    def load_repository_data(self) -> None:
        """Load and parse repository data."""
        content = self.download_packages_file()
        if content:
            self.packages_cache = self.parse_packages_file(content)
        else:
            logging.error("Failed to load repository data")

    def get_package_dependencies(self, package: str) -> Set[str]:
        """Get dependencies for a package from loaded repository data."""
        if not self.packages_cache:
            self.load_repository_data()
            
        if package in self.packages_cache:
            return self.packages_cache[package].depends
        return set()

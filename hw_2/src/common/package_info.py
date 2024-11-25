from typing import Set
from dataclasses import dataclass

@dataclass
class PackageInfo:
    name: str
    depends: Set[str]

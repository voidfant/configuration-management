from dataclasses import dataclass

@dataclass
class File:
    name: str
    content: bytes
    is_directory: bool
    modified_time: float

from dataclasses import dataclass

@dataclass
class Repository:
    name: str
    url: str
    distribution: str
    component: str

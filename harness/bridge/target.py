"""The code under modernization: a Maven project folder plus its target.json."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

from .bob import ROOT


@dataclass
class Target:
    root: Path
    name: str
    title: str
    source: Path       # relative to root
    package: str
    cls: str
    test_dir: Path     # relative to root
    stakeholder: str
    control_names: list
    mutants_file: Path

    @classmethod
    def load(cls, root) -> "Target":
        root = Path(root)
        if not root.is_absolute():
            root = ROOT / root
        cfg = json.loads((root / "target.json").read_text(encoding="utf-8"))
        return cls(root=root, name=cfg["name"], title=cfg.get("title", cfg["name"]), source=Path(cfg["source"]),
                   package=cfg["package"], cls=cfg["class"], test_dir=Path(cfg["test_dir"]),
                   stakeholder=cfg.get("stakeholder", "its callers"), control_names=cfg.get("controls", []),
                   mutants_file=(root / cfg["mutants"]).resolve())

    def original_source(self) -> str:
        return (self.root / self.source).read_text(encoding="utf-8")

    def controls(self) -> dict:
        return {n: (self.root / self.test_dir / f"{n}.java").read_text(encoding="utf-8") for n in self.control_names}

    def mutants(self) -> list:
        return json.loads(self.mutants_file.read_text(encoding="utf-8"))

    def step(self, step: str) -> str:
        """Session names for the original invoice target stay unprefixed so earlier recordings still replay."""
        return step if self.name == "invoice" else f"{self.name}-{step}"


def current() -> Target:
    return Target.load(os.environ.get("BRIDGE_TARGET", "sample"))

"""Register file and register result status tracking."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RegisterEntry:
    name: str
    value: float = 0.0
    qi: Optional[str] = None

    def to_dict(self) -> dict:
        return {"name": self.name, "value": self.value, "qi": self.qi}


class RegisterFile:
    def __init__(self) -> None:
        self._registers: dict[str, RegisterEntry] = {}

        for idx in range(16):
            self._registers[f"F{idx}"] = RegisterEntry(name=f"F{idx}", value=0.0)

        for idx in range(8):
            self._registers[f"R{idx}"] = RegisterEntry(name=f"R{idx}", value=0.0)

    def get_value(self, name: str) -> float:
        return self._registers[name].value

    def get_tag(self, name: str) -> Optional[str]:
        return self._registers[name].qi

    def set_waiting(self, name: str, tag: str) -> None:
        self._registers[name].qi = tag

    def write_back(self, tag: str, value: float) -> None:
        # Multiple architectural registers can transiently map to a single tag.
        for reg in self._registers.values():
            if reg.qi == tag:
                reg.value = value
                reg.qi = None

    def as_list(self) -> list[dict]:
        def _key(reg_name: str) -> tuple[int, int]:
            prefix = 0 if reg_name.startswith("F") else 1
            return prefix, int(reg_name[1:])

        ordered = sorted(self._registers.values(), key=lambda entry: _key(entry.name))
        return [entry.to_dict() for entry in ordered]

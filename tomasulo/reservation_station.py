"""Reservation station models and helpers."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReservationStationEntry:
    name: str
    busy: bool = False
    op: Optional[str] = None
    vj: Optional[float] = None
    vk: Optional[float] = None
    qj: Optional[str] = None
    qk: Optional[str] = None
    dest_reg: Optional[str] = None
    cycles_remaining: int = 0
    result: Optional[float] = None
    executing: bool = False
    ready_to_write: bool = False
    instruction_index: Optional[int] = None

    def operands_ready(self) -> bool:
        return self.qj is None and self.qk is None

    def clear(self) -> None:
        self.busy = False
        self.op = None
        self.vj = None
        self.vk = None
        self.qj = None
        self.qk = None
        self.dest_reg = None
        self.cycles_remaining = 0
        self.result = None
        self.executing = False
        self.ready_to_write = False
        self.instruction_index = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "busy": self.busy,
            "op": self.op,
            "Vj": self.vj,
            "Vk": self.vk,
            "Qj": self.qj,
            "Qk": self.qk,
            "dest_reg": self.dest_reg,
            "cycles_remaining": self.cycles_remaining,
            "result": self.result,
            "executing": self.executing,
            "ready_to_write": self.ready_to_write,
            "instruction_index": self.instruction_index,
        }


def build_default_stations() -> list[ReservationStationEntry]:
    names = ["ADD1", "ADD2", "ADD3", "MUL1", "MUL2", "LOAD1", "LOAD2"]
    return [ReservationStationEntry(name=name) for name in names]

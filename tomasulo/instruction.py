"""Instruction definitions and parser helpers."""

from __future__ import annotations

from dataclasses import dataclass
import re


_LOAD_PATTERN = re.compile(r"^LOAD\s+([A-Za-z]\d+)\s*,\s*(-?\d+)\(([A-Za-z]\d+)\)$")
_ARITH_PATTERN = re.compile(
    r"^(ADD|SUB|MUL|DIV)\s+([A-Za-z]\d+)\s*,\s*([A-Za-z]\d+)\s*,\s*([A-Za-z]\d+)$"
)


@dataclass
class Instruction:
    op: str
    dest: str
    src1: str
    src2: str
    issue_cycle: int | None = None
    exec_start: int | None = None
    exec_end: int | None = None
    write_cycle: int | None = None
    state: str = "WAITING"

    def text(self) -> str:
        if self.op == "LOAD":
            return f"{self.op} {self.dest}, {self.src2}({self.src1})"
        return f"{self.op} {self.dest}, {self.src1}, {self.src2}"

    def to_dict(self) -> dict:
        return {
            "op": self.op,
            "dest": self.dest,
            "src1": self.src1,
            "src2": self.src2,
            "issue_cycle": self.issue_cycle,
            "exec_start": self.exec_start,
            "exec_end": self.exec_end,
            "write_cycle": self.write_cycle,
            "state": self.state,
            "text": self.text(),
        }


def parse_instruction_line(line: str) -> Instruction:
    normalized = line.strip().upper()

    if not normalized:
        raise ValueError("Instruction line is empty")

    load_match = _LOAD_PATTERN.match(normalized)
    if load_match:
        dest, offset, base_reg = load_match.groups()
        return Instruction(op="LOAD", dest=dest, src1=base_reg, src2=offset)

    arith_match = _ARITH_PATTERN.match(normalized)
    if arith_match:
        op, dest, src1, src2 = arith_match.groups()
        return Instruction(op=op, dest=dest, src1=src1, src2=src2)

    raise ValueError(f"Invalid instruction format: {line}")


def parse_instruction_file(file_path: str) -> list[Instruction]:
    instructions: list[Instruction] = []

    with open(file_path, "r", encoding="utf-8") as infile:
        for raw in infile:
            stripped = raw.strip()
            if not stripped:
                continue
            instructions.append(parse_instruction_line(stripped))

    return instructions

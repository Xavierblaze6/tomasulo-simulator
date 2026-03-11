"""Main Tomasulo simulation engine."""

from __future__ import annotations

from copy import deepcopy

from .cdb import CommonDataBus
from .functional_units import get_latency, rs_names_for_op
from .instruction import Instruction
from .register_file import RegisterFile
from .reservation_station import ReservationStationEntry, build_default_stations


class TomasuloSimulator:
    def __init__(self, instructions: list[Instruction]) -> None:
        self.instructions: list[Instruction] = deepcopy(instructions)
        self.pc = 0
        self.cycle = 0

        self.register_file = RegisterFile()
        self.reservation_stations: list[ReservationStationEntry] = build_default_stations()
        self.cdb = CommonDataBus()

        # Small deterministic memory image used by LOAD instructions.
        self.memory: dict[int, float] = {
            0: 2.0,
            4: 3.0,
            8: 5.0,
            12: 7.0,
        }

        self.history: list[dict] = []
        self.history_index = 0
        self._record_snapshot()

    def _record_snapshot(self) -> None:
        self.history.append(self._serialize_state())
        self.history_index = len(self.history) - 1

    def get_current_state(self) -> dict:
        return self.history[self.history_index]

    def next_cycle(self) -> dict:
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            return self.get_current_state()

        self._advance_one_cycle()
        self._record_snapshot()
        return self.get_current_state()

    def previous_cycle(self) -> dict:
        if self.history_index > 0:
            self.history_index -= 1
        return self.get_current_state()

    def _advance_one_cycle(self) -> None:
        self.cycle += 1

        self._write_result_stage()
        self._execute_stage()
        self._issue_stage()

    def _write_result_stage(self) -> None:
        ready = [
            rs for rs in self.reservation_stations if rs.busy and rs.ready_to_write and rs.instruction_index is not None
        ]
        if not ready:
            return

        # CDB can only broadcast one result per cycle.
        station = min(ready, key=lambda item: item.instruction_index)

        self.cdb.broadcast(
            tag=station.name,
            value=station.result if station.result is not None else 0.0,
            reservation_stations=self.reservation_stations,
            register_file=self.register_file,
        )

        inst = self.instructions[station.instruction_index]
        inst.write_cycle = self.cycle
        inst.state = "DONE"

        station.clear()

    def _execute_stage(self) -> None:
        for station in self.reservation_stations:
            if not station.busy or station.ready_to_write:
                continue

            if not station.executing:
                if not station.operands_ready():
                    continue

                station.executing = True
                station.cycles_remaining = get_latency(station.op)

                if station.instruction_index is not None:
                    inst = self.instructions[station.instruction_index]
                    if inst.exec_start is None:
                        inst.exec_start = self.cycle
                        inst.state = "EXECUTE"

            elif station.executing and station.cycles_remaining > 0:
                station.cycles_remaining -= 1
                if station.cycles_remaining == 0:
                    station.result = self._compute_result(station)
                    station.ready_to_write = True
                    station.executing = False

                    if station.instruction_index is not None:
                        inst = self.instructions[station.instruction_index]
                        inst.exec_end = self.cycle

    def _issue_stage(self) -> None:
        if self.pc >= len(self.instructions):
            return

        inst = self.instructions[self.pc]
        free_station = self._find_free_station(inst.op)

        if free_station is None:
            inst.state = "STALL"
            return

        self._populate_station(free_station, inst, self.pc)
        inst.issue_cycle = self.cycle
        inst.state = "ISSUE"
        self.register_file.set_waiting(inst.dest, free_station.name)
        self.pc += 1

    def _find_free_station(self, op: str) -> ReservationStationEntry | None:
        eligible = set(rs_names_for_op(op))
        for station in self.reservation_stations:
            if station.name in eligible and not station.busy:
                return station
        return None

    def _populate_station(self, station: ReservationStationEntry, inst: Instruction, idx: int) -> None:
        station.busy = True
        station.op = inst.op
        station.dest_reg = inst.dest
        station.instruction_index = idx

        if inst.op == "LOAD":
            self._bind_operand_into_station(station, "j", inst.src1)
            station.vk = float(inst.src2)
            station.qk = None
            return

        self._bind_operand_into_station(station, "j", inst.src1)
        self._bind_operand_into_station(station, "k", inst.src2)

    def _bind_operand_into_station(self, station: ReservationStationEntry, side: str, reg_name: str) -> None:
        tag = self.register_file.get_tag(reg_name)
        if tag is None:
            value = self.register_file.get_value(reg_name)
            if side == "j":
                station.vj = value
                station.qj = None
            else:
                station.vk = value
                station.qk = None
            return

        if side == "j":
            station.vj = None
            station.qj = tag
        else:
            station.vk = None
            station.qk = tag

    def _compute_result(self, station: ReservationStationEntry) -> float:
        if station.op == "LOAD":
            base = int(station.vj or 0)
            offset = int(station.vk or 0)
            address = base + offset
            return float(self.memory.get(address, 0.0))

        left = float(station.vj or 0.0)
        right = float(station.vk or 0.0)

        if station.op == "ADD":
            return left + right
        if station.op == "SUB":
            return left - right
        if station.op == "MUL":
            return left * right
        if station.op == "DIV":
            return left / right if right != 0 else 0.0

        raise ValueError(f"Unsupported operation in station {station.name}: {station.op}")

    def _serialize_state(self) -> dict:
        return {
            "cycle": self.cycle,
            "pc": self.pc,
            "instructions": [inst.to_dict() for inst in self.instructions],
            "reservation_stations": [rs.to_dict() for rs in self.reservation_stations],
            "registers": self.register_file.as_list(),
            "is_complete": self.is_complete(),
        }

    def is_complete(self) -> bool:
        if self.pc < len(self.instructions):
            return False

        if any(rs.busy for rs in self.reservation_stations):
            return False

        return all(inst.write_cycle is not None for inst in self.instructions)

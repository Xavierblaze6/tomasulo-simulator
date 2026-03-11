"""Common Data Bus implementation."""

from __future__ import annotations

from .register_file import RegisterFile
from .reservation_station import ReservationStationEntry


class CommonDataBus:
    def broadcast(
        self,
        tag: str,
        value: float,
        reservation_stations: list[ReservationStationEntry],
        register_file: RegisterFile,
    ) -> None:
        # Wake up all RS entries that are waiting on this producer tag.
        for station in reservation_stations:
            if not station.busy:
                continue

            if station.qj == tag:
                station.qj = None
                station.vj = value

            if station.qk == tag:
                station.qk = None
                station.vk = value

        register_file.write_back(tag=tag, value=value)

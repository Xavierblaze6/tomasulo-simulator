"""Functional unit configuration for Tomasulo simulation."""

OP_LATENCIES = {
    "ADD": 2,
    "SUB": 2,
    "MUL": 4,
    "DIV": 6,
    "LOAD": 3,
}

RS_GROUPS = {
    "ADD": ["ADD1", "ADD2", "ADD3"],
    "SUB": ["ADD1", "ADD2", "ADD3"],
    "MUL": ["MUL1", "MUL2"],
    "DIV": ["MUL1", "MUL2"],
    "LOAD": ["LOAD1", "LOAD2"],
}


def get_latency(op: str) -> int:
    return OP_LATENCIES[op]


def rs_names_for_op(op: str) -> list[str]:
    return RS_GROUPS[op]

# Tomasulo Algorithm Simulator

A complete Python implementation of a Tomasulo Algorithm simulator with a Flask dashboard for cycle-by-cycle visualization.

## Project Description

This project simulates out-of-order execution using Tomasulo's algorithm with register renaming, reservation stations, and a Common Data Bus (CDB). The web dashboard lets you move forward and backward by cycle to inspect the internal machine state.

## How Tomasulo Works (Brief)

Tomasulo's algorithm breaks execution into three stages:

1. **Issue**: Issue one instruction in program order if a matching reservation station is free. Source operands are either read immediately or tagged with the producer reservation station.
2. **Execute**: Reservation stations start execution only when operands are ready. Each operation takes a fixed latency (ADD/SUB=2, MUL=4, DIV=6, LOAD=3).
3. **Write Result**: Completed stations broadcast results on the CDB. Waiting operands and destination register tags are updated, and the station is freed.

## Setup and Run

Requirements:

- Python 3.10+
- Flask

Install dependencies:

```bash
pip install flask
```

Run the app:

```bash
python app.py
```

Open:

- `http://localhost:5000`

## Screenshot Placeholder

Add screenshots here after running the dashboard:

- `docs/screenshot-main.png`

## File Structure

```text
tomasulo-simulator/
├── app.py
├── tomasulo/
│   ├── __init__.py
│   ├── core.py
│   ├── instruction.py
│   ├── reservation_station.py
│   ├── register_file.py
│   ├── functional_units.py
│   └── cdb.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── instructions.txt
└── README.md
```

## Notes

- Full simulator state is serialized to JSON-compatible dictionaries for easy rendering.
- A complete snapshot is stored after every computed cycle, enabling the **Previous Cycle** button.
- Instruction parsing happens at startup from `instructions.txt`.

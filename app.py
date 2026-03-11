"""Flask entry point for the Tomasulo algorithm dashboard."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, redirect, render_template, url_for

from tomasulo import TomasuloSimulator, parse_instruction_file

app = Flask(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent
INSTRUCTION_FILE = PROJECT_ROOT / "instructions.txt"


def build_simulator() -> TomasuloSimulator:
    instructions = parse_instruction_file(str(INSTRUCTION_FILE))
    return TomasuloSimulator(instructions=instructions)


simulator = build_simulator()


@app.get("/")
def index():
    state = simulator.get_current_state()
    return render_template("index.html", state=state)


@app.post("/next")
def next_cycle():
    simulator.next_cycle()
    return redirect(url_for("index"))


@app.post("/prev")
def previous_cycle():
    simulator.previous_cycle()
    return redirect(url_for("index"))


@app.post("/reset")
def reset():
    global simulator
    simulator = build_simulator()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)

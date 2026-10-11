#!/usr/bin/env python3
"""Additional isolated original/source timer-stop cases using the prior fixture."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "audio-transition-timer-closure-2026-10-08" / "verify.py"
scope = {"__file__": str(PRIOR)}
exec(compile(PRIOR.read_text().split("rows=[];cases=[]")[0], str(PRIOR), "exec"), scope)
run = scope["run"]
cases = [
    {"kind": "stop", "initial": 0x12345678, "clock_clients": 0x10000, "mask": 0},
    {"kind": "stop", "initial": 0x12345678, "clock_clients": 0x10001, "mask": 1},
    {"kind": "stop", "initial": 0x55AA55AA, "clock_clients": 0x10000, "mask": 1},
    {"kind": "stop", "initial": 0x55AA55AA, "clock_clients": 0x10001, "mask": 0},
]
rows = []
for case in cases:
    original = run(False, **case)
    source = run(True, **case)
    assert original == source, (case, original, source)
    rows.append({"inputs": case, "original_and_source": original})
(HERE / "timer-stop-extra-execution.json").write_text(json.dumps({
    "status": "PASS", "fresh_cases": len(rows), "comparisons": rows,
    "source_fixture": str(PRIOR),
    "limits": "Fresh synthetic state cases use the prior GCC-built source ELF and real original clock-release child; the selected Clang object text is separately matched to its previous source build. No live clock/timer behavior."
}, indent=2) + "\n")
print("PASS", len(rows), "fresh timer-stop original/source cases")

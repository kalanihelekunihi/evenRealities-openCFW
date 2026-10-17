#!/usr/bin/env python3
"""Bind checked calendar wrapper and Conversate elapsed label to Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-elapsed-label-5b22fa"
PRIOR = BASE / "main-conversate-notify-5b1d2a/candidate.o"
CURRENT = HERE / "candidate.o"
CALENDAR = BASE / "main-time-epoch-calendar-44a100/oracle-receipt.json"
ORACLE = HERE / "oracle-receipt.json"
SOURCES = [ROOT / "g2/components/audio/uart_thread_source_candidate" / name for name in
           ("conversate_elapsed_label_5b22fa.c",
            "time_epoch_to_calendar_449ed4_44a100.c")]
OUT = HERE / "receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def undefined(path):
    lines = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()
    return sorted({line.split()[-1] for line in lines if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    calendar = json.loads(CALENDAR.read_text())
    assert oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_ELAPSED_LABEL_5B22FA_C"
    assert oracle["cases"] == 120
    assert calendar["status"] == "PASS_DIRECT_MAIN_TIME_EPOCH_CALENDAR_44A100_C"
    assert calendar["cases"] == 52
    assert oracle["sources"][0]["sha256"] == sha(SOURCES[0])
    assert calendar["source_sha256"] == sha(SOURCES[1])
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed = sorted(set(prior) - set(current))
    added = sorted(set(current) - set(prior))
    assert len(prior) == 112 and len(current) == 111
    assert removed == ["audio_conversate_route_scroll_5b22fa"] and not added
    names = subprocess.check_output(["arm-none-eabi-nm", "-S", str(CURRENT)], text=True)
    assert "00000014 B audio_conversate_clock_label_buffer_20073cac" in names
    record = {
        "status": "PASS_MAIN_CONVERSATE_ELAPSED_LABEL_5B22FA_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "sources": [ref(path) for path in SOURCES],
        "calendar_oracle": ref(CALENDAR), "oracle": ref(ORACLE),
        "calendar_cases": 52, "label_cases": 120,
        "native_bodies": ["0x449ed4..0x449fd9", "0x44a100..0x44a107",
                          "0x46650c..0x466511", "0x5b22fa..0x5b23ad"],
        "unresolved_before": 112, "unresolved_after": 111,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Calendar and elapsed-label fields are checked under controlled formatter and LVGL lower contracts; whole-image linker integration, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

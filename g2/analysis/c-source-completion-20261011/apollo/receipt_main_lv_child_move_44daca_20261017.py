#!/usr/bin/env python3
"""Bind directly checked LVGL child-order move to current Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-lv-child-move-44daca"
PRIOR = BASE / "main-conversate-tag-lookup-5964e2/candidate.o"
CURRENT = HERE / "candidate.o"
ORACLE = HERE / "oracle-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_lv_child_move_44daca.c"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_LV_CHILD_MOVE_44DACA_C"
    assert oracle["cases"] == 48 and oracle["source_sha256"] == sha(SOURCE)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed = sorted(set(prior) - set(current))
    added = sorted(set(current) - set(prior))
    assert len(prior) == 115 and len(current) == 114
    assert removed == ["audio_uart_page_44daca"] and not added
    record = {
        "status": "PASS_MAIN_LV_CHILD_MOVE_44DACA_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "oracle_cases": 48, "native_body": "0x44daca..0x44dbc3",
        "unresolved_before": 115, "unresolved_after": 114,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Null and fatal LVGL child-move branches remain bounded by stock disassembly; other Main imports, exact placement, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

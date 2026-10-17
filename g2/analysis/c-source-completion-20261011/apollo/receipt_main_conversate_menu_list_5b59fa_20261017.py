#!/usr/bin/env python3
"""Bind the directly checked Conversate menu-list route to Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-menu-list-5b59fa"
PRIOR = BASE / "main-conversate-menu-icon-76a2a0/candidate.o"
CURRENT = HERE / "candidate.o"
ORACLE = HERE / "oracle-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/conversate_ui_menu_list_5b59fa.c"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_MENU_LIST_5B59FA_C"
    assert oracle["cases"] == 54 and oracle["source_sha256"] == sha(SOURCE)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed = sorted(set(prior) - set(current))
    added = sorted(set(current) - set(prior))
    assert len(prior) == 116 and len(current) == 115
    assert removed == ["audio_conversate_ui_route_5b59fa"] and not added
    record = {
        "status": "PASS_MAIN_CONVERSATE_MENU_LIST_5B59FA_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "oracle_cases": 54, "native_body": "0x5b59fa..0x5b5b95",
        "unresolved_before": 116, "unresolved_after": 115,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "LVGL, locale, list getter and button factory are bounded lower contracts; other Main imports, exact placement, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

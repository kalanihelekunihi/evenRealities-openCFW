#!/usr/bin/env python3
"""Bind the directly checked Conversate menu-page route to Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-menu-page-5b58e8"
PRIOR = BASE / "main-conversate-menu-style-5b5720/candidate.o"
CURRENT = HERE / "candidate.o"
ORACLE = HERE / "oracle-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/conversate_ui_menu_page_5b58e8.c"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_MENU_PAGE_5B58E8_C"
    assert oracle["cases"] == 30 and oracle["source_sha256"] == sha(SOURCE)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed = sorted(set(prior) - set(current))
    added = sorted(set(current) - set(prior))
    assert len(prior) == len(current) == 117
    assert removed == ["audio_conversate_ui_route_5b58e8"]
    assert added == ["audio_conversate_menu_request_prep_notes_5b1e52"]
    record = {
        "status": "PASS_MAIN_CONVERSATE_MENU_PAGE_5B58E8_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "oracle_cases": 30, "native_body": "0x5b58e8..0x5b59f9",
        "unresolved_before": 117, "unresolved_after": 117,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Menu prep-note request sender 0x5b1e52 needs source ownership; called lower contracts, other Main imports, exact placement, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

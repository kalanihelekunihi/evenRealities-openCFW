#!/usr/bin/env python3
"""Bind the directly checked Conversate prep-note list sender to Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-menu-request-5b1e52"
PRIOR = BASE / "main-conversate-menu-page-5b58e8/candidate.o"
CURRENT = HERE / "candidate.o"
ORACLE = HERE / "oracle-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/conversate_menu_request_prep_notes_5b1e52.c"
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
    assert oracle["status"] == "PASS_BOUNDED_MAIN_CONVERSATE_MENU_REQUEST_5B1E52_C"
    assert oracle["cases"] == 120 and oracle["source_sha256"] == sha(SOURCE)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed = sorted(set(prior) - set(current))
    added = sorted(set(current) - set(prior))
    assert len(prior) == 117 and len(current) == 116
    assert removed == ["audio_conversate_menu_request_prep_notes_5b1e52"]
    assert not added
    record = {
        "status": "PASS_MAIN_CONVERSATE_MENU_REQUEST_5B1E52_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "oracle_cases": 120, "native_body": "0x5b1e52..0x5b1f2d",
        "unresolved_before": 117, "unresolved_after": 116,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Nanopb encode, BLE sender and role lookup are bounded lower contracts; other Main imports, exact placement, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

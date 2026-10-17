#!/usr/bin/env python3
"""Bind directly checked display layer register preparation to Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-layer-prepare-471cd6"
PRIOR = BASE / "main-display-current-set-442456/candidate.o"
CURRENT = HERE / "candidate.o"
ORACLE = HERE / "oracle-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_layer_prepare_471cd6.c"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_DISPLAY_LAYER_PREPARE_471CD6_C"
    assert oracle["cases"] == 184 and oracle["source_sha256"] == sha(SOURCE)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed = sorted(set(prior) - set(current))
    added = sorted(set(current) - set(prior))
    assert len(prior) == 110 and len(current) == 109
    assert removed == ["audio_uart_display_layer_prepare"] and not added
    record = {
        "status": "PASS_MAIN_DISPLAY_LAYER_PREPARE_471CD6_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "oracle_cases": 184, "native_bodies": oracle["native_bodies"],
        "unresolved_before": 110, "unresolved_after": 109,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Layer MMIO and pin grouping match emulated stock paths with controlled mux/critical lower calls; board electrical behavior, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

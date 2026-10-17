#!/usr/bin/env python3
"""Bind the byte-checked Conversate menu icon to the Main candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-menu-icon-76a2a0"
PRIOR = BASE / "main-conversate-menu-request-5b1e52/candidate.o"
CURRENT = HERE / "candidate.o"
ORACLE = HERE / "oracle-receipt.json"
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
    assert oracle["status"] == "PASS_MAIN_CONVERSATE_MENU_ICON_76A2A0_SOURCE_DATA"
    assert oracle["pixel_bytes"] == 0x240
    prior, current = undefined(PRIOR), undefined(CURRENT)
    assert len(prior) == 116 and current == prior
    record = {
        "status": "PASS_MAIN_CONVERSATE_MENU_ICON_76A2A0_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": oracle["source"], "oracle": ref(ORACLE),
        "stock_descriptor_address": "0x76a2a0",
        "stock_pixels_address": "0x6ac3c0", "pixel_bytes": 0x240,
        "unresolved_before": 116, "unresolved_after": 116,
        "removed_imports": [], "new_imports": [],
        "remaining_gate": oracle["remaining_gate"],
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

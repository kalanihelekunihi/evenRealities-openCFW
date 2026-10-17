#!/usr/bin/env python3
"""Bind the directly checked Conversate tag lookup to current Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-tag-lookup-5964e2"
PRIOR = BASE / "main-conversate-tag-icon-get-5b0af6/candidate.o"
CURRENT = HERE / "candidate.o"
ORACLE = HERE / "oracle-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/conversate_tag_get_by_index_5964e2.c"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_TAG_LOOKUP_5964E2_C"
    assert oracle["cases"] == 70 and oracle["source_sha256"] == sha(SOURCE)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed = sorted(set(prior) - set(current))
    added = sorted(set(current) - set(prior))
    assert len(prior) == 116 and len(current) == 115
    assert removed == ["audio_conversate_tag_get_by_index_5964e2"] and not added
    record = {
        "status": "PASS_MAIN_CONVERSATE_TAG_LOOKUP_5964E2_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "oracle_cases": 70, "native_body": "0x5964e2..0x59674d",
        "unresolved_before": 116, "unresolved_after": 115,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "LVGL positioning 0x44daca remains the tag-update route's unresolved lower provider; other Main imports, exact placement, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

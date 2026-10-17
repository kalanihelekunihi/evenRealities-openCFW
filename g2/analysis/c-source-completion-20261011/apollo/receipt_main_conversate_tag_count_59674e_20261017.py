#!/usr/bin/env python3
"""Bind the direct tag-count oracle to the current Main object."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-tag-count-59674e"
PRIOR = BASE / "main-conversate-menu-list-5b59fa/candidate.o"
CURRENT = HERE / "candidate.o"
ORACLE = HERE / "oracle-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/conversate_tag_storage_count_59674e.c"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_TAG_COUNT_59674E_C"
    assert oracle["cases"] == 60 and oracle["source_sha256"] == sha(SOURCE)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    assert len(prior) == 115 and current == prior
    record = {
        "status": "PASS_MAIN_CONVERSATE_TAG_COUNT_59674E_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "oracle_cases": 60, "native_body": "0x59674e..0x5967a5",
        "unresolved_before": 115, "unresolved_after": 115,
        "removed_imports": [], "new_imports": [],
        "remaining_gate": "Tag-update route 0x5b6426 and its other helpers remain open; other Main imports, exact placement, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

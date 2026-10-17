#!/usr/bin/env python3
"""Bind directly checked Conversate tag storage exit to current Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-tag-storage-deinit-59624e"
PRIOR = BASE / "main-conversate-tag-node-free-596188/candidate.o"
CURRENT = HERE / "candidate.o"
ORACLE = HERE / "oracle-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/conversate_tag_storage_deinit_59624e.c"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_TAG_STORAGE_DEINIT_59624E_C"
    assert oracle["cases"] == 30 and oracle["source_sha256"] == sha(SOURCE)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed = sorted(set(prior) - set(current))
    added = sorted(set(current) - set(prior))
    assert len(prior) == 114 and len(current) == 113
    assert removed == ["audio_conversate_ui_exit_child_59624e"] and not added
    record = {
        "status": "PASS_MAIN_CONVERSATE_TAG_STORAGE_DEINIT_59624E_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "oracle_cases": 30, "native_body": "0x59624e..0x59635f",
        "unresolved_before": 114, "unresolved_after": 113,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Conversate tag storage exit is checked for initialized and finite valid circular lists; malformed list behavior, other Main imports, exact placement, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

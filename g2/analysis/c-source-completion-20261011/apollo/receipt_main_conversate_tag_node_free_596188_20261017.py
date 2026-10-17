#!/usr/bin/env python3
"""Bind checked tag-node teardown providers to current Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-tag-node-free-596188"
PRIOR = BASE / "main-lv-child-move-44daca/candidate.o"
CURRENT = HERE / "candidate.o"
ORACLE = HERE / "oracle-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/conversate_tag_node_free_596188.c"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_TAG_NODE_FREE_596188_C"
    assert oracle["cases"] == 12 and oracle["source_sha256"] == sha(SOURCE)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    assert len(prior) == len(current) == 114 and prior == current
    names = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CURRENT)], text=True)
    assert "audio_conversate_tag_node_destruct_596094" in names
    assert "audio_conversate_tag_node_free_596188" in names
    record = {
        "status": "PASS_MAIN_CONVERSATE_TAG_NODE_FREE_596188_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "oracle_cases": 12, "native_bodies": oracle["native_bodies"],
        "unresolved_before": 114, "unresolved_after": 114,
        "removed_imports": [], "new_imports": [],
        "remaining_gate": "Tag-node cleanup providers are linked, but the list-exit caller at 0x59624e remains unresolved; other Main imports, exact placement, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

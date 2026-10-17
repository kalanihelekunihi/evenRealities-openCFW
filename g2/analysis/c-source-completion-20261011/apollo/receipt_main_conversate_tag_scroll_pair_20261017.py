#!/usr/bin/env python3
"""Bind tag visible-index and scroll helpers to the current Main object."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-tag-scroll-5b63d4"
VISIBLE = BASE / "main-conversate-tag-visible-5b0b58"
PRIOR = BASE / "main-conversate-tag-count-59674e/candidate.o"
CURRENT = HERE / "candidate.o"
OUT = HERE / "receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def undefined(path):
    lines = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()
    return sorted({line.split()[-1] for line in lines if line.strip()})


def main():
    scroll_oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    visible_oracle = json.loads((VISIBLE / "oracle-receipt.json").read_text())
    assert scroll_oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_TAG_SCROLL_5B63D4_C"
    assert visible_oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_TAG_VISIBLE_INDEX_5B0B58_C"
    assert scroll_oracle["cases"] == 80 and visible_oracle["cases"] == 280
    for oracle in (scroll_oracle, visible_oracle):
        assert sha(ROOT / oracle["source"]) == oracle["source_sha256"]
    prior, current = undefined(PRIOR), undefined(CURRENT)
    assert len(prior) == 115 and current == prior
    record = {
        "status": "PASS_MAIN_CONVERSATE_TAG_SCROLL_PAIR_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "scroll_source": ref(ROOT / scroll_oracle["source"]),
        "visible_source": ref(ROOT / visible_oracle["source"]),
        "scroll_oracle": ref(HERE / "oracle-receipt.json"),
        "visible_oracle": ref(VISIBLE / "oracle-receipt.json"),
        "scroll_cases": 80, "visible_cases": 280,
        "unresolved_before": 115, "unresolved_after": 115,
        "removed_imports": [], "new_imports": [],
        "remaining_gate": "Tag-update route 0x5b6426 and further tag helpers remain open; LVGL, logging, other Main imports, exact placement, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

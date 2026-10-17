#!/usr/bin/env python3
"""Bind tag icon map data and native icon getter to current Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-tag-icon-get-5b0af6"
DATA = BASE / "main-conversate-tag-icon-map-2000052c"
PRIOR = BASE / "main-conversate-auto-pop-5967bc/candidate.o"
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
    getter = json.loads((HERE / "oracle-receipt.json").read_text())
    data = json.loads((DATA / "oracle-receipt.json").read_text())
    assert getter["status"] == "PASS_DIRECT_MAIN_CONVERSATE_TAG_ICON_GET_5B0AF6_C"
    assert data["status"] == "PASS_MAIN_CONVERSATE_TAG_ICON_MAP_2000052C_SOURCE_DATA"
    assert getter["cases"] == 40 and data["pixel_bytes_total"] == 2304
    assert sha(ROOT / getter["source"]) == getter["source_sha256"]
    assert sha(ROOT / data["source"]["path"]) == data["source"]["sha256"]
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed = sorted(set(prior) - set(current))
    added = sorted(set(current) - set(prior))
    assert len(prior) == 117 and len(current) == 116
    assert removed == ["audio_conversate_tag_icon_get_5b0af6"] and not added
    record = {
        "status": "PASS_MAIN_CONVERSATE_TAG_ICON_MAP_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "getter_source": ref(ROOT / getter["source"]),
        "map_source": data["source"],
        "getter_oracle": ref(HERE / "oracle-receipt.json"),
        "map_oracle": ref(DATA / "oracle-receipt.json"),
        "getter_cases": 40, "icon_count": 4, "pixel_bytes_total": 2304,
        "unresolved_before": 117, "unresolved_after": 116,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Tag lookup 0x5964e2 and LVGL positioning 0x44daca remain open; final initialized RAM placement and adjacent icon-table words, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

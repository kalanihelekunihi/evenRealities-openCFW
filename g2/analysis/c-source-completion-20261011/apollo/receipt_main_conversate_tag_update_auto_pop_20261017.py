#!/usr/bin/env python3
"""Bind tag-update route and auto-pop predicate to the Main candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-auto-pop-5967bc"
ROUTE = BASE / "main-conversate-tag-update-5b6426"
PRIOR = BASE / "main-conversate-tag-scroll-5b63d4/candidate.o"
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
    route_oracle = json.loads((ROUTE / "oracle-receipt.json").read_text())
    auto_oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    assert route_oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_TAG_UPDATE_5B6426_C"
    assert auto_oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_AUTO_POP_5967BC_C"
    assert route_oracle["cases"] == 216 and auto_oracle["cases"] == 60
    for oracle in (route_oracle, auto_oracle):
        assert sha(ROOT / oracle["source"]) == oracle["source_sha256"]
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed = sorted(set(prior) - set(current))
    added = sorted(set(current) - set(prior))
    assert len(prior) == 115 and len(current) == 117
    assert removed == ["audio_conversate_ui_route_5b6426"]
    assert added == ["audio_conversate_tag_get_by_index_5964e2",
                     "audio_conversate_tag_icon_get_5b0af6",
                     "audio_uart_page_44daca"]
    record = {
        "status": "PASS_MAIN_CONVERSATE_TAG_UPDATE_AUTO_POP_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "route_source": ref(ROOT / route_oracle["source"]),
        "auto_source": ref(ROOT / auto_oracle["source"]),
        "route_oracle": ref(ROUTE / "oracle-receipt.json"),
        "auto_oracle": ref(HERE / "oracle-receipt.json"),
        "route_cases": 216, "auto_cases": 60,
        "unresolved_before": 115, "unresolved_after": 117,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Tag lookup 0x5964e2, icon mapping 0x5b0af6 and LVGL page positioning 0x44daca need source ownership; other Main imports, exact placement, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

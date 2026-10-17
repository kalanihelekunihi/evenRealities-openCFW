#!/usr/bin/env python3
"""Bind the directly checked loading route and minimum RAM owner to Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-conversate-ui-display-loading-5b30c8"
PRIOR = BASE / "main-conversate-ui-slot-fade-5b1072/candidate.o"
CURRENT = HERE / "candidate-with-buffer.o"
ORACLE = HERE / "oracle-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/conversate_ui_display_loading_5b30c8.c"
BUFFER = ROOT / "g2/components/audio/uart_thread_source_candidate/conversate_ui_loading_text_minimum_200711dc.c"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_CONVERSATE_DISPLAY_LOADING_5B30C8_C"
    assert oracle["cases"] == 320 and oracle["source_sha256"] == sha(SOURCE)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed = sorted(set(prior) - set(current))
    added = sorted(set(current) - set(prior))
    assert len(prior) == 118 and len(current) == 117
    assert removed == ["audio_conversate_ui_route_5b30c8"] and not added
    sections = subprocess.check_output(["arm-none-eabi-readelf", "-SW", str(HERE / "loading-text.o")], text=True)
    assert ".bss.g2_conversate_loading_text_200711dc NOBITS" in sections
    assert "0000c9" in sections
    record = {
        "status": "PASS_MAIN_CONVERSATE_DISPLAY_LOADING_MINIMUM_RAM_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "route_source": ref(SOURCE), "buffer_source": ref(BUFFER),
        "route_oracle": ref(ORACLE), "oracle_cases": 320,
        "native_body": "0x5b30c8..0x5b3249", "buffer_stock_address": "0x200711dc",
        "buffer_minimum_bytes": 201, "buffer_section": "NOBITS",
        "unresolved_before": 118, "unresolved_after": 117,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Exact stock RAM allocation, final placement, oversized snprintf return behavior, called lower contracts, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()

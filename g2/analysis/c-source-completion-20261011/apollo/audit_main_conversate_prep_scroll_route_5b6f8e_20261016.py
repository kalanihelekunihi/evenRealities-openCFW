#!/usr/bin/env python3
"""Pin source-linked prep-note scroll bounds and route."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-prep-scroll-route-5b6f8e"
PRIOR = BASE / "main-conversate-expand-animation-5b7704/candidate.o"
CANDIDATE = HERE / "candidate.o"
ROUTE = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_scroll_route_5b6f8e.c"
BOUNDS = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_scroll_bounds_5b6a06.c"
BOUNDS_HERE = BASE / "main-conversate-prep-scroll-bounds-5b6a06"
VERIFY_ROUTE = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_prep_scroll_route_5b6f8e_20261016.py"
VERIFY_BOUNDS = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_prep_scroll_bounds_5b6a06_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_route_5b6f8e"}
    if (len(before), len(after)) != (137, 136) or before-after != removed or after-before:
        raise RuntimeError("Conversate prep scroll frontier changed")
    bounds = json.loads((BOUNDS_HERE / "oracle-receipt.json").read_text())
    route = json.loads((HERE / "oracle-receipt.json").read_text())
    if (bounds["status"] != "PASS_DIRECT_MAIN_CONVERSATE_PREP_SCROLL_BOUNDS_5B6A06_C" or
            bounds["cases"] != 600 or bounds["source_sha256"] != sha(BOUNDS) or
            bounds["oracle_elf_sha256"] != sha(ROOT / bounds["oracle_elf"])):
        raise RuntimeError("Conversate prep scroll bounds oracle changed")
    if (route["status"] != "PASS_DIRECT_MAIN_CONVERSATE_PREP_SCROLL_ROUTE_5B6F8E_C" or
            route["cases"] != 1620 or route["native_body"] != "0x5b6f8e..0x5b705f" or
            route["source_sha256"][str(ROUTE.relative_to(ROOT))] != sha(ROUTE) or
            route["source_sha256"][str(BOUNDS.relative_to(ROOT))] != sha(BOUNDS) or
            route["oracle_elf_sha256"] != sha(ROOT / route["oracle_elf"])):
        raise RuntimeError("Conversate prep scroll route oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for symbol in ("audio_conversate_ui_route_5b6f8e",
                   "audio_conversate_prep_note_line_count_5b4770",
                   "audio_conversate_prep_scroll_max_5b6a06",
                   "audio_conversate_prep_scroll_clamp_5b6a3a"):
        if f" {symbol}\n" not in defined:
            raise RuntimeError("Conversate prep scroll body missing: " + symbol)
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_PREP_SCROLL_ROUTE_5B6F8E_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "sources": [ref(BOUNDS), ref(ROUTE)],
              "verifiers": [ref(VERIFY_BOUNDS), ref(VERIFY_ROUTE)],
              "oracle_receipts": [ref(BOUNDS_HERE / "oracle-receipt.json"),
                                  ref(HERE / "oracle-receipt.json")],
              "native_bodies": bounds["native_bodies"] + [route["native_body"]],
              "oracle_cases": bounds["cases"] + route["cases"],
              "unresolved_before": 137, "unresolved_after": 136,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Remaining Main imports and source-owned image configuration are open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

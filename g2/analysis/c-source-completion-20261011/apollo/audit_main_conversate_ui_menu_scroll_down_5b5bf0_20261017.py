#!/usr/bin/env python3
"""Bind the stock-replayed Conversate menu scroll-down C body to Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261017"
PRIOR = BASE / "main-locale-data-20001588/candidate.o"
HERE = BASE / "main-conversate-ui-menu-scroll-down-5b5bf0"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_menu_scroll_down_5b5bf0.c"
ORACLE = HERE / "oracle-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_MENU_SCROLL_DOWN_5B5BF0_C" or
            oracle["cases"] != 128 or oracle["native_body"] != "0x5b5bf0..0x5b5cc7" or
            oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"]) or
            oracle["source_complete"] or oracle["flashable"] or oracle["hardware_proof"]):
        raise RuntimeError("menu scroll oracle changed")
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_route_5b5bf0"}
    if len(before) != 120 or len(after) != 119 or before-after != removed or after-before:
        raise RuntimeError("Main menu-scroll import frontier changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " T audio_conversate_ui_route_5b5bf0\n" not in defined:
        raise RuntimeError("menu scroll body missing")
    record = {"status": "PASS_MAIN_CONVERSATE_MENU_SCROLL_DOWN_5B5BF0_INTEGRATION",
              "source": ref(SOURCE), "oracle_receipt": ref(ORACLE),
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "oracle_cases": 128, "native_body": "0x5b5bf0..0x5b5cc7",
              "unresolved_before": 120, "unresolved_after": 119,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Other Main imports, final placement, whole-image source and hardware behavior remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

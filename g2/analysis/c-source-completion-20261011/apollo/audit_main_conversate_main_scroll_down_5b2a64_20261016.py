#!/usr/bin/env python3
"""Pin stock-compared Conversate main-page scroll-down route."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-main-scroll-down-5b2a64"
PRIOR = BASE / "main-conversate-main-scroll-up-5b29bc/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_main_scroll_down_5b2a64.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_main_scroll_down_5b2a64_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_route_5b2a64"}
    added = {"audio_conversate_main_list_scroll_58a680"}
    if (len(before), len(after)) != (132, 132) or before - after != removed or after - before != added:
        raise RuntimeError("Conversate scroll-down frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_MAIN_SCROLL_DOWN_5B2A64_C" or
            oracle["cases"] != 1920 or oracle["native_body"] != "0x5b2a64..0x5b2b73" or
            oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"]) or
            oracle["source_complete"] or oracle["flashable"] or oracle["hardware_proof"]):
        raise RuntimeError("Conversate scroll-down oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_ui_route_5b2a64\n" not in defined:
        raise RuntimeError("Conversate scroll-down body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_MAIN_SCROLL_DOWN_5B2A64_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY), "oracle_receipt": ref(oracle_path),
              "native_body": oracle["native_body"], "oracle_cases": oracle["cases"],
              "unresolved_before": 132, "unresolved_after": 132,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Bounce animation 0x58a680, other Main imports and image configuration remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

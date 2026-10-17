#!/usr/bin/env python3
"""Pin stock-compared Conversate list-slot alpha and fade C bodies."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-list-slot-alpha-fade-5b0c72"
PRIOR = BASE / "main-conversate-list-view-mode-5b0edc/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_list_slot_alpha_fade_5b0c72.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_list_slot_alpha_fade_5b0c72_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_list_slot_alpha_5b0c72",
               "audio_conversate_list_slot_fade_5b0ca0"}
    if (len(before), len(after)) != (135, 133) or before - after != removed or after - before:
        raise RuntimeError("Conversate slot alpha/fade frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_LIST_SLOT_ALPHA_FADE_5B0C72_C" or
            oracle["cases"] != 576 or
            oracle["native_bodies"] != ["0x5b0c4e..0x5b0c71", "0x5b0c72..0x5b0c9f",
                                        "0x5b0ca0..0x5b0d23"] or
            oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"]) or
            oracle["source_complete"] or oracle["flashable"] or oracle["hardware_proof"]):
        raise RuntimeError("Conversate slot alpha/fade oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for symbol in ("audio_conversate_list_slot_opacity_callback_5b0c4e",
                   "audio_conversate_list_slot_alpha_5b0c72",
                   "audio_conversate_list_slot_fade_5b0ca0"):
        if f" {symbol}\n" not in defined:
            raise RuntimeError("Conversate slot alpha/fade body missing: " + symbol)
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_LIST_SLOT_ALPHA_FADE_5B0C72_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY), "oracle_receipt": ref(oracle_path),
              "native_bodies": oracle["native_bodies"], "oracle_cases": oracle["cases"],
              "unresolved_before": 135, "unresolved_after": 133,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Other Main imports and image configuration remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

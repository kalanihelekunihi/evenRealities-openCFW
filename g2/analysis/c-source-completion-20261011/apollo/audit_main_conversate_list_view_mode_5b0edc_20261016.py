#!/usr/bin/env python3
"""Pin stock-compared Conversate list-view mode C bodies."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-list-view-mode-5b0edc"
PRIOR = BASE / "main-conversate-main-page-refresh-5b13fe/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_list_view_mode_5b0edc.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_list_view_mode_5b0edc_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_list_view_mode_set_5b0edc"}
    added = {"audio_conversate_list_slot_alpha_5b0c72",
             "audio_conversate_list_slot_fade_5b0ca0"}
    if (len(before), len(after)) != (134, 135) or before - after != removed or after - before != added:
        raise RuntimeError("Conversate list-view mode frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_LIST_VIEW_MODE_5B0EDC_C" or
            oracle["cases"] != 2186 or
            oracle["native_bodies"] != ["0x5b0c30..0x5b0c51", "0x5b0d24..0x5b0d63",
                                        "0x5b0edc..0x5b1071"] or
            oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"]) or
            oracle["source_complete"] or oracle["flashable"] or oracle["hardware_proof"]):
        raise RuntimeError("Conversate list-view mode oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for symbol in ("audio_conversate_list_view_mode_rank_5b0c30",
                   "audio_conversate_list_view_apply_5b0d24",
                   "audio_conversate_ui_list_view_mode_set_5b0edc"):
        if f" {symbol}\n" not in defined:
            raise RuntimeError("Conversate list-view body missing: " + symbol)
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_LIST_VIEW_MODE_5B0EDC_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY), "oracle_receipt": ref(oracle_path),
              "native_bodies": oracle["native_bodies"], "oracle_cases": oracle["cases"],
              "unresolved_before": 134, "unresolved_after": 135,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "List-slot alpha and fade, other Main imports and image configuration remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

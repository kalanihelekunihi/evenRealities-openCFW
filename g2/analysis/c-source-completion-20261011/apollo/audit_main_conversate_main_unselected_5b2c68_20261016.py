#!/usr/bin/env python3
"""Pin the stock-compared Conversate main-page unselect route."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-main-unselected-5b2c68"
PRIOR = BASE / "main-conversate-transcribe-label-update-5b32b4/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_main_unselected_5b2c68.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_main_unselected_5b2c68_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_route_5b2c68"}
    added = {"audio_conversate_tag_unselect_5969a4",
             "audio_conversate_ui_list_view_mode_set_5b0edc",
             "audio_conversate_ui_main_page_refresh_5b13fe"}
    if (len(before), len(after)) != (134, 136) or before - after != removed or after - before != added:
        raise RuntimeError("Conversate main-page unselect frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_MAIN_UNSELECTED_5B2C68_C" or
            oracle["cases"] != 80 or oracle["native_body"] != "0x5b2c68..0x5b2d17" or
            oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"]) or
            oracle["source_complete"] or oracle["flashable"] or oracle["hardware_proof"]):
        raise RuntimeError("Conversate main-page unselect oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_ui_route_5b2c68\n" not in defined:
        raise RuntimeError("Conversate main-page unselect body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_MAIN_UNSELECTED_5B2C68_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY), "oracle_receipt": ref(oracle_path),
              "native_body": oracle["native_body"], "oracle_cases": oracle["cases"],
              "unresolved_before": 134, "unresolved_after": 136,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "List-view mode, tag unselect, main-page refresh, other Main imports and image configuration remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

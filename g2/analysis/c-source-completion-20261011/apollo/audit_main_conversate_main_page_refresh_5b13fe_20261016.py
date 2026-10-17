#!/usr/bin/env python3
"""Pin stock-compared Conversate list count and main-page refresh bodies."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-main-page-refresh-5b13fe"
PRIOR = BASE / "main-conversate-tag-unselect-5969a4/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_main_page_refresh_5b13fe.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_main_page_refresh_5b13fe_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_main_page_refresh_5b13fe"}
    if (len(before), len(after)) != (135, 134) or before - after != removed or after - before:
        raise RuntimeError("Conversate main-page refresh frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_MAIN_PAGE_REFRESH_5B13FE_C" or
            oracle["cases"] != 328 or
            oracle["native_bodies"] != ["0x5b0c18..0x5b0c2f", "0x5b13fe..0x5b14cd"] or
            oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"]) or
            oracle["source_complete"] or oracle["flashable"] or oracle["hardware_proof"]):
        raise RuntimeError("Conversate main-page refresh oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for symbol in ("audio_conversate_ui_list_count_5b0c18",
                   "audio_conversate_ui_main_page_refresh_5b13fe"):
        if f" {symbol}\n" not in defined:
            raise RuntimeError("Conversate main-page refresh body missing: " + symbol)
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_MAIN_PAGE_REFRESH_5B13FE_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY), "oracle_receipt": ref(oracle_path),
              "native_bodies": oracle["native_bodies"], "oracle_cases": oracle["cases"],
              "unresolved_before": 135, "unresolved_after": 134,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "List-view mode, other Main imports and image configuration remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

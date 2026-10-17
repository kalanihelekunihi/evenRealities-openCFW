#!/usr/bin/env python3
"""Pin source-linked Conversate note collapse completion callback."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-note-collapse-complete-5b7518"
PRIOR = BASE / "main-conversate-note-collapse-5b7556/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_note_collapse_complete_5b7518.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_note_collapse_complete_5b7518_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_note_collapse_complete_5b7518"}
    added = {"audio_conversate_lv_object_delete_44d90e"}
    if (len(before), len(after)) != (139, 139) or before-after != removed or after-before != added:
        raise RuntimeError("Conversate note completion frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_NOTE_COLLAPSE_COMPLETE_5B7518_C" or
            oracle["cases"] != 24 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate note completion oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_note_collapse_complete_5b7518\n" not in defined:
        raise RuntimeError("Conversate note completion body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_NOTE_COLLAPSE_COMPLETE_5B7518_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": oracle["native_body"], "oracle_cases": 24,
              "unresolved_before": 139, "unresolved_after": 139,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Native asynchronous LVGL delete 0x44d90e and expand scheduler 0x5b7704 remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

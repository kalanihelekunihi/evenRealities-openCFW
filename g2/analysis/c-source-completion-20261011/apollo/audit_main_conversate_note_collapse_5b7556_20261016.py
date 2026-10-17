#!/usr/bin/env python3
"""Pin the source-linked Conversate note collapse transition."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-note-collapse-5b7556"
PRIOR = BASE / "main-conversate-auto-duration-label-5b68d6/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_note_collapse_5b7556.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_note_collapse_5b7556_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_route_5b7556"}
    added = {"audio_conversate_note_collapse_complete_5b7518",
             "audio_conversate_expand_animation_5b7704"}
    if (len(before), len(after)) != (138, 139) or before-after != removed or after-before != added:
        raise RuntimeError("Conversate note collapse frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_NOTE_COLLAPSE_5B7556_C" or
            oracle["cases"] != 32 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate note collapse oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_ui_route_5b7556\n" not in defined:
        raise RuntimeError("Conversate note collapse body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_NOTE_COLLAPSE_5B7556_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": oracle["native_body"], "oracle_cases": 32,
              "unresolved_before": 138, "unresolved_after": 139,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Native completion callback 0x5b7518 and animation scheduler 0x5b7704 remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

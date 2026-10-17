#!/usr/bin/env python3
"""Pin the stock-compared indexed prep-note line-text C body."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-prep-note-line-text-5b4776"
PRIOR = BASE / "main-conversate-prep-note-pool-5b6ac0/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_note_line_text_5b4776.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_prep_note_line_text_5b4776_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_prep_note_line_text_5b4776"}
    if (len(before), len(after)) != (136, 135) or before - after != removed or after - before:
        raise RuntimeError("Conversate prep note line-text frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_LINE_TEXT_5B4776_C" or
            oracle["cases"] != 180 or oracle["native_body"] != "0x5b4776..0x5b4845" or
            oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"]) or
            oracle["source_complete"] or oracle["flashable"] or oracle["hardware_proof"]):
        raise RuntimeError("Conversate prep note line-text oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_prep_note_line_text_5b4776\n" not in defined:
        raise RuntimeError("Conversate prep note line-text body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_LINE_TEXT_5B4776_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY), "oracle_receipt": ref(oracle_path),
              "native_body": oracle["native_body"], "oracle_cases": oracle["cases"],
              "unresolved_before": 136, "unresolved_after": 135,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Remaining Main imports and image configuration remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pin recursive Conversate child style clear in the Main C candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261017"
PRIOR = BASE / "main-conversate-ui-menu-scroll-down-5b5bf0/candidate.o"
HERE = BASE / "main-conversate-ui-child-style-clear-5b3340"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_child_style_clear_5b3340.c"
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
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_CHILD_STYLE_CLEAR_5B3340_C" or
            oracle["cases"] != 96 or oracle["native_body"] != "0x5b3340..0x5b3383" or
            oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"]) or
            oracle["source_complete"] or oracle["flashable"] or oracle["hardware_proof"]):
        raise RuntimeError("child style clear oracle changed")
    before, after = imports(PRIOR), imports(CANDIDATE)
    if len(before) != 119 or after != before:
        raise RuntimeError("child style clear frontier changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " T audio_conversate_ui_child_style_clear_5b3340\n" not in defined:
        raise RuntimeError("child style clear body missing")
    record = {"status": "PASS_MAIN_CONVERSATE_CHILD_STYLE_CLEAR_5B3340_INTEGRATION",
              "source": ref(SOURCE), "oracle_receipt": ref(ORACLE),
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "oracle_cases": 96, "native_body": "0x5b3340..0x5b3383",
              "unresolved_before": 119, "unresolved_after": 119,
              "removed_imports": [], "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Adjacent route 0x5b3398, other Main imports, final placement and whole-image proof remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

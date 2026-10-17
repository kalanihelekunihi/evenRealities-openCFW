#!/usr/bin/env python3
"""Pin composed Conversate timer-manager init integration."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-timer-init-5b3cba"
PRIOR = BASE / "main-conversate-ui-init-5b14ce/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_init_5b3cba.c"
CLEAR = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_clear_5b38cc.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_timer_init_5b3cba_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_timer_init_5b3cba"}
    if (len(before), len(after)) != (126, 125) or before-after != removed or after-before:
        raise RuntimeError("Conversate timer-manager init frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_COMPOSED_MAIN_CONVERSATE_TIMER_INIT_C" or
            oracle["cases"] != 60 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["clear_source_sha256"] != sha(CLEAR) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate timer-manager init oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_timer_init_5b3cba\n" not in defined:
        raise RuntimeError("Conversate timer-manager init body missing")
    record = {"status": "PASS_COMPOSED_MAIN_CONVERSATE_TIMER_INIT_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "clear_source": ref(CLEAR), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": "0x5b3cba..0x5b3d03", "oracle_cases": 60,
              "unresolved_before": 126, "unresolved_after": 125,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Conversate UI style 0x5b0ac4 and wider UI composition remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

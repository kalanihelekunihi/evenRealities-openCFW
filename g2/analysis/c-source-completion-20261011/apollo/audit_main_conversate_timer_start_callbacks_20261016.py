#!/usr/bin/env python3
"""Pin direct Conversate timer start callback integration."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-timer-start-callbacks"
PRIOR = BASE / "main-conversate-timer-3-stop-5b38b6/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_start_callbacks_20261016.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_timer_start_callbacks_20261016.py"
REMOVED = {"audio_conversate_timer_1_start_5b3766",
           "audio_conversate_timer_2_start_5b37d8",
           "audio_conversate_timer_3_start_5b384c"}
ADDED = {"audio_conversate_timer_start_5b3570"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    if (len(before), len(after)) != (128, 126) or before-after != REMOVED or after-before != ADDED:
        raise RuntimeError("Conversate timer start callback frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_TIMER_START_CALLBACKS_C" or
            oracle["cases"] != 180 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate timer start callback oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for name in REMOVED:
        if f" {name}\n" not in defined:
            raise RuntimeError(f"Conversate timer start callback missing: {name}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TIMER_START_CALLBACKS_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_bodies": ["0x5b3766..0x5b37c7", "0x5b37d8..0x5b383b", "0x5b384c..0x5b38b5"],
              "oracle_cases": 180, "unresolved_before": 128, "unresolved_after": 126,
              "removed_imports": sorted(REMOVED), "new_imports": sorted(ADDED),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Shared timer start 0x5b3570 and composed timer lifecycle remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pin direct shared Conversate timer stop integration."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-timer-stop-5b35d0"
PRIOR = BASE / "main-conversate-timer-stop-wrappers/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_stop_5b35d0.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_timer_stop_5b35d0_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_timer_stop_5b35d0"}
    if (len(before), len(after)) != (130, 129) or before-after != removed or after-before:
        raise RuntimeError("Conversate shared timer stop frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_TIMER_STOP_C" or
            oracle["cases"] != 60 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate shared timer stop oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_timer_stop_5b35d0\n" not in defined:
        raise RuntimeError("Conversate shared timer stop body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TIMER_STOP_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": "0x5b35d0..0x5b3627", "oracle_cases": 60,
              "unresolved_before": 130, "unresolved_after": 129,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Four other timer callback bodies and composed lifecycle remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

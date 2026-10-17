#!/usr/bin/env python3
"""Pin direct Conversate loading and selection timer stop wrappers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-timer-stop-wrappers"
PRIOR = BASE / "main-conversate-timer-remove-5b36be/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_stop_wrappers_5b37c8_5b383c.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_timer_stop_wrappers_20261016.py"
REMOVED = {"audio_conversate_timer_1_stop_5b37c8", "audio_conversate_timer_2_stop_5b383c"}
ADDED = {"audio_conversate_timer_stop_5b35d0"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    if (len(before), len(after)) != (131, 130) or before-after != REMOVED or after-before != ADDED:
        raise RuntimeError("Conversate timer stop wrapper frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_TIMER_STOP_WRAPPERS_C" or
            oracle["cases"] != 6 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate timer stop wrapper oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for name in REMOVED:
        if f" {name}\n" not in defined:
            raise RuntimeError(f"Conversate timer stop wrapper missing: {name}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TIMER_STOP_WRAPPERS_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_bodies": ["0x5b37c8..0x5b37d7", "0x5b383c..0x5b384b"],
              "oracle_cases": 6, "unresolved_before": 131, "unresolved_after": 130,
              "removed_imports": sorted(REMOVED), "new_imports": sorted(ADDED),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Shared timer stop 0x5b35d0 and four other table callback bodies remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

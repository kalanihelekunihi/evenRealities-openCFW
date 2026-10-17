#!/usr/bin/env python3
"""Pin direct Conversate auto-extend callback integration."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-cleanup-commit-5b3a88"
PRIOR = BASE / "main-conversate-ui-cleanup-flush-5b39b4/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_cleanup_commit_5b3a88.c"
HELPER = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_expired_5b3628.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_ui_cleanup_commit_5b3a88_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_cleanup_commit_5b3a88"}
    if (len(before), len(after)) != (121, 120) or before-after != removed or after-before:
        raise RuntimeError("Conversate auto-extend frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_UI_CLEANUP_COMMIT_C" or
            oracle["cases"] != 2592 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["helper_sha256"] != sha(HELPER) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate auto-extend oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for symbol in ("audio_conversate_ui_cleanup_commit_5b3a88", "audio_conversate_timer_expired_5b3628"):
        if f" {symbol}\n" not in defined:
            raise RuntimeError(f"Conversate body missing: {symbol}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_UI_CLEANUP_COMMIT_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "helper": ref(HELPER), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": "0x5b3a88..0x5b3c29", "oracle_cases": 2592,
              "unresolved_before": 121, "unresolved_after": 120,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Wider Conversate UI and image gates remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

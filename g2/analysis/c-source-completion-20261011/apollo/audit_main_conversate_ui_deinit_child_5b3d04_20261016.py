#!/usr/bin/env python3
"""Pin bounded Conversate timer-manager deinit source integration."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-deinit-child-5b3d04"
PRIOR = BASE / "main-conversate-ui-exit-finalize-5b156c/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_deinit_child_5b3d04.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_ui_deinit_child_5b3d04_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_deinit_child_5b3d04"}
    added = {"audio_conversate_timer_clear_5b38cc", "audio_conversate_timer_remove_5b36be"}
    if (len(before), len(after)) != (126, 127) or before-after != removed or after-before != added:
        raise RuntimeError("Conversate timer deinit frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_TIMER_DEINIT_C" or
            oracle["cases"] != 20 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate timer deinit oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_ui_deinit_child_5b3d04\n" not in defined:
        raise RuntimeError("Conversate timer deinit body missing")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_TIMER_DEINIT_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": "0x5b3d04..0x5b3d61", "oracle_cases": 20,
              "unresolved_before": 126, "unresolved_after": 127,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Timer remove 0x5b36be and clear 0x5b38cc remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pin bounded UI dispatcher C integration and its exact frontier expansion."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-action-5b1724"
PRIOR = BASE / "main-conversate-ui-event-name-5b16fc/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_action_5b1724.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_ui_action_5b1724_20261016.py"
MATRIX = G2 / "analysis/c-source-completion-20261011/apollo/main-conversate-ui-action-matrix-20261016.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_action_5b1724"}
    added = {"audio_conversate_ui_action_matrix_686920",
             "audio_conversate_ui_transition_5b3d86"}
    if (len(before), len(after)) != (120, 121) or before-after != removed or after-before != added:
        raise RuntimeError("Conversate UI action frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    matrix = json.loads(MATRIX.read_text())
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_UI_ACTION_C" or
            oracle["cases"] != 1440 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"]) or
            matrix["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_UI_ACTION_MATRIX" or
            matrix["active_routes"] != 50):
        raise RuntimeError("Conversate UI action evidence changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_ui_action_5b1724\n" not in defined:
        raise RuntimeError("Conversate UI action body missing")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_ACTION_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "matrix_evidence": ref(MATRIX),
              "native_body": "0x5b1724..0x5b198b", "oracle_cases": 1440,
              "unresolved_before": 120, "unresolved_after": 121,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "C dispatcher is linked, but its 50 native handler routes need source ownership and transition helper 0x5b3d86 remains open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

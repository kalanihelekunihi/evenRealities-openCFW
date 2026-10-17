#!/usr/bin/env python3
"""Pin bounded Conversate UI initialization integration."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-init-5b14ce"
PRIOR = BASE / "main-conversate-timer-start-5b3570/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_init_5b14ce.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_ui_init_5b14ce_20261016.py"
ADDED = {"audio_conversate_timer_init_5b3cba", "audio_conversate_ui_style_5b0ac4"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_start_5b14ce"}
    if (len(before), len(after)) != (125, 126) or before-after != removed or after-before != ADDED:
        raise RuntimeError("Conversate UI initialization frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_UI_INIT_C" or
            oracle["cases"] != 45 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate UI initialization oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_ui_start_5b14ce\n" not in defined:
        raise RuntimeError("Conversate UI initialization body missing")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_INIT_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": "0x5b14ce..0x5b156b", "oracle_cases": 45,
              "unresolved_before": 125, "unresolved_after": 126,
              "removed_imports": sorted(removed), "new_imports": sorted(ADDED),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Conversate style 0x5b0ac4, timer-manager init 0x5b3cba and wider UI composition remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

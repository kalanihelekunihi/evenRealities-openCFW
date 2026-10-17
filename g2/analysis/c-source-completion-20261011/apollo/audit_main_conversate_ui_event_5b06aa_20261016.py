#!/usr/bin/env python3
"""Pin bounded Conversate UI event callback source integration."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-event-5b06aa"
PRIOR = BASE / "main-conversate-ui-callback-ram/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_event_callback_5b06aa.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_ui_event_5b06aa_20261016.py"
ADDED = {"audio_conversate_ui_action_5b1724", "audio_conversate_ui_cancel_5b23ae",
         "audio_conversate_ui_cleanup_5b3d62", "audio_conversate_ui_close_notify_5b1d2a",
         "audio_conversate_ui_exit_child_59624e", "audio_conversate_ui_exit_finalize_5b156c",
         "audio_conversate_ui_start_5b14ce", "audio_conversate_ui_stop_5b03d8"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    if (len(before), len(after)) != (118, 125):
        raise RuntimeError("Conversate UI callback import count changed")
    if before-after != {"audio_uart_registry_callback_5b06aa"} or after-before != ADDED:
        raise RuntimeError("Conversate UI callback frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_UI_EVENT_C" or
            oracle["cases"] != 210 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate UI callback oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_uart_registry_callback_5b06aa\n" not in defined:
        raise RuntimeError("Conversate UI callback body missing")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_EVENT_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": "0x5b06aa..0x5b08a1", "oracle_cases": 210,
              "unresolved_before": 118, "unresolved_after": 125,
              "removed_imports": ["audio_uart_registry_callback_5b06aa"],
              "new_imports": sorted(ADDED),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Eight newly explicit child providers and wider caller composition remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

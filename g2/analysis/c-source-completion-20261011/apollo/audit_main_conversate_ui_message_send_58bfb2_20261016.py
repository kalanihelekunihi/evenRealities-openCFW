#!/usr/bin/env python3
"""Pin source-linked exit-prompt sender and its direct child frontier."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-message-send-58bfb2"
PRIOR = BASE / "main-conversate-ui-route-5b1998/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_message_send_58bfb2.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_ui_message_send_58bfb2_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_message_send_58bfb2"}
    added = {"audio_conversate_exit_prompt_prepare_58bda8",
             "audio_conversate_exit_prompt_show_58bf12"}
    if (len(before), len(after)) != (140, 141) or before-after != removed or after-before != added:
        raise RuntimeError("Conversate message sender frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_UI_MESSAGE_SEND_58BFB2_C" or
            oracle["cases"] != 360 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"]) or
            oracle["ram_cells"] != {"state": "0x200745d0..0x200745db",
                                    "hold": "0x20000be4..0x20000be7"}):
        raise RuntimeError("Conversate message sender oracle changed")
    with CANDIDATE.open("rb") as stream:
        elf = ELFFile(stream)
        for section, size in ((".g2_conversate_exit_prompt_state_200745d0", 12),
                              (".g2_conversate_exit_prompt_hold_20000be4", 4)):
            match = elf.get_section_by_name(section)
            if match is None or match["sh_size"] != size:
                raise RuntimeError(f"Conversate message sender RAM section changed: {section}")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_ui_message_send_58bfb2\n" not in defined:
        raise RuntimeError("Conversate message sender body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_UI_MESSAGE_SEND_58BFB2_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": oracle["native_body"], "oracle_cases": 360,
              "ram_cells": oracle["ram_cells"],
              "unresolved_before": 140, "unresolved_after": 141,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Prompt prepare/show bodies, final RAM placement and remaining image imports are open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

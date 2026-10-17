#!/usr/bin/env python3
"""Pin direct Conversate timer callback-dispatch integration."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-timer-remove-5b36be"
PRIOR = BASE / "main-conversate-timer-clear-5b38cc/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_remove_5b36be.c"
LINKER = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_timer_callbacks_75ea90.ld"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_timer_remove_5b36be_20261016.py"
ADDED = {"audio_conversate_timer_1_start_5b3766", "audio_conversate_timer_1_stop_5b37c8",
         "audio_conversate_timer_2_start_5b37d8", "audio_conversate_timer_2_stop_5b383c",
         "audio_conversate_timer_3_start_5b384c", "audio_conversate_timer_3_stop_5b38b6"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_timer_remove_5b36be"}
    if (len(before), len(after)) != (126, 131) or before-after != removed or after-before != ADDED:
        raise RuntimeError("Conversate timer callback frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_TIMER_REMOVE_C" or
            oracle["cases"] != 80 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["linker_sha256"] != sha(LINKER) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate timer callback oracle changed")
    with CANDIDATE.open("rb") as stream:
        section = ELFFile(stream).get_section_by_name(".g2_conversate_timer_callbacks_75ea90")
        if section is None or section["sh_addr"] != 0x75ea90 or section["sh_size"] != 0x20:
            raise RuntimeError("Conversate timer callback table moved")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_timer_remove_5b36be\n" not in defined:
        raise RuntimeError("Conversate timer callback dispatcher missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TIMER_REMOVE_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "linker_script": ref(LINKER),
              "verifier": ref(VERIFY), "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": "0x5b36be..0x5b3717", "oracle_cases": 80,
              "callback_table": "0x75ea90..0x75eaaf", "callback_entries": 6,
              "unresolved_before": 126, "unresolved_after": 131,
              "removed_imports": sorted(removed), "new_imports": sorted(ADDED),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Six table callback bodies and wider timer lifecycle remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

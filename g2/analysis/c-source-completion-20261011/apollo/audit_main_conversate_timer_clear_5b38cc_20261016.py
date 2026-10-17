#!/usr/bin/env python3
"""Pin direct Conversate timer-manager RAM clear integration."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-timer-clear-5b38cc"
PRIOR = BASE / "main-conversate-ui-deinit-child-5b3d04/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_clear_5b38cc.c"
LINKER = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_timer_mgr_ram_20261016.ld"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_timer_clear_5b38cc_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_timer_clear_5b38cc"}
    if (len(before), len(after)) != (127, 126) or before-after != removed or after-before:
        raise RuntimeError("Conversate timer clear frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_TIMER_CLEAR_C" or
            oracle["cases"] != 5 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["linker_sha256"] != sha(LINKER) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate timer clear oracle changed")
    with CANDIDATE.open("rb") as stream:
        section = ELFFile(stream).get_section_by_name(".g2_conversate_timer_mgr_ram_20073a3c")
        if (section is None or section["sh_addr"] != 0x20073a3c or
                section["sh_size"] != 0x1c or section["sh_type"] != "SHT_NOBITS"):
            raise RuntimeError("Conversate timer-manager RAM moved")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_timer_clear_5b38cc\n" not in defined:
        raise RuntimeError("Conversate timer clear body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TIMER_CLEAR_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "linker_script": ref(LINKER),
              "verifier": ref(VERIFY), "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": "0x5b38cc..0x5b38ed", "oracle_cases": 5,
              "ram_start": "0x20073a3c", "ram_size": 28,
              "unresolved_before": 127, "unresolved_after": 126,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Timer remove 0x5b36be and full timer-manager RAM extent remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

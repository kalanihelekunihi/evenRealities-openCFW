#!/usr/bin/env python3
"""Pin six direct stock-matched Conversate reset/accessor leaves into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261016"
HERE = BASE / "main-conversate-data-reset-helpers"
NAMES = ["audio_conversate_transcribe_reset_5b430e",
         "audio_conversate_transcribe_get_5b4364",
         "audio_conversate_reply_list_clear_5b43d4",
         "audio_conversate_reply_list_get_5b43e8",
         "audio_conversate_prep_note_reset_5b473a",
         "audio_conversate_prep_note_get_5b4766"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-context-ram/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    if len(before) != 119 or after != before:
        raise RuntimeError("Conversate reset helpers changed import frontier")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_DATA_RESET_HELPERS_C" or
            oracle["cases"] != 60 or oracle["source_sha256"] != sha(source) or
            oracle["stock_payload_sha256"] !=
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("Conversate reset helpers oracle changed")
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {item.name: item for item in elf.get_section_by_name(".symtab").iter_symbols()}
        for name in NAMES:
            if name not in symbols or symbols[name]["st_info"]["type"] != "STT_FUNC" or \
                    symbols[name]["st_size"] == 0:
                raise RuntimeError(f"Reset/accessor body missing: {name}")
        for name, address, size in (
                (".g2_conversate_context_200d5bd8", 0x200d5bd8, 0xfac),
                (".g2_conversate_reply_list_200d6b84", 0x200d6b84, 0xaac),
                (".g2_conversate_prep_note_ram_200d7630", 0x200d7630, 0xb4b1),
                (".g2_conversate_transcribe_output_200e2ae4", 0x200e2ae4, 0x1008)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"Reset helper RAM changed: {name}")
    record = {
        "status": "PASS_DIRECT_MAIN_CONVERSATE_DATA_RESET_HELPERS_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 60,
        "native_bodies": ["0x5b430e..0x5b4363", "0x5b4364..0x5b4377",
                          "0x5b43d4..0x5b43e7", "0x5b43e8..0x5b43ed",
                          "0x5b473a..0x5b4765", "0x5b4766..0x5b4769"],
        "provider_symbols": NAMES,
        "unresolved_before": 119, "unresolved_after": 119,
        "removed_imports": [], "new_imports": [],
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Wider callback composition, startup and Main image remain open.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()

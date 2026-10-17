#!/usr/bin/env python3
"""Pin prep-note list update and adjacent reply/list RAM layout."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-prep-note-list-update-5b4378"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-prep-note-finish-5b476a/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    removed = {"audio_conversate_prep_note_list_update_5b4378",
               "audio_conversate_reply_status_200d6b84"}
    if len(before) != 127 or len(after) != 125 or before - after != removed or after - before:
        raise RuntimeError("prep-note list import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_LIST_UPDATE_5B4378_C" or
            oracle["cases"] != 20 or oracle["source_sha256"] != sha(source) or
            oracle["stock_payload_sha256"] !=
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("prep-note list oracle changed")
    previous = json.loads((BASE / "main-conversate-prep-note-finish-5b476a/receipt.json").read_text())
    fixed = {name: (int(row["address"], 16), row["size"])
             for name, row in previous["fixed_ram_sections"].items()}
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in fixed.items():
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"fixed RAM section changed: {name}")
        for name, address, size in (
                (".g2_conversate_reply_list_200d6b84", 0x200d6b84, 0xaac),
                (".g2_conversate_prep_note_ram_200d7630", 0x200d7630, 0xb4b1),
                (".g2_conversate_machine_context_200e3aec", 0x200e3aec, 8),
                (".g2_conversate_ui_settings_extension_20071369", 0x20071369, 0x94)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"RAM section changed: {name}")
        for name, address, size, edges in (
                (".g2_conversate_event_names_200004f4", 0x200004f4, 52, 13),
                (".g2_conversate_ui_state_names_20000540", 0x20000540, 28, 7)):
            section = elf.get_section_by_name(name)
            relocs = elf.get_section_by_name(".rel" + name)
            if (section is None or section["sh_type"] != "SHT_PROGBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size or
                    relocs is None or relocs.num_relocations() != edges):
                raise RuntimeError(f"name table changed: {name}")
    linker = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_reply_list_ram_20261016.ld"
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_LIST_UPDATE_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 20,
        "linker_script": ref(linker),
        "native_body": "0x5b4378..0x5b43d3", "native_body_bytes": 92,
        "unresolved_before": 127, "unresolved_after": 125,
        "removed_imports": sorted(removed), "new_imports": [],
        "fixed_ram_sections": previous["fixed_ram_sections"],
        "reply_list_ram": {"address": "0x200d6b84", "size": 0xaac,
                           "reply_status_bytes": 4, "list_bytes": 2728,
                           "next_region_address": "0x200d7630"},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Startup and wider prep-note/Main behavior remain.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()

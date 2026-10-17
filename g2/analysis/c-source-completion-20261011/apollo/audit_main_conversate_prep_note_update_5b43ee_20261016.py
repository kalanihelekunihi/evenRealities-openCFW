#!/usr/bin/env python3
"""Pin bounded prep-note update C integration and overlapping RAM layout."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-prep-note-update-5b43ee"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-tag-storage-59619e/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    if (len(before) != 132 or len(after) != 131 or
            before - after != {"audio_conversate_prep_note_update_5b43ee"} or
            after - before):
        raise RuntimeError("prep-note update import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_UPDATE_5B43EE_C" or
            oracle["cases"] != 35 or oracle["source_sha256"] != sha(source) or
            oracle["stock_payload_sha256"] !=
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("prep-note update oracle changed")
    previous = json.loads((BASE / "main-conversate-tag-storage-59619e/receipt.json").read_text())
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
                (".g2_conversate_tag_storage_200e3af4", 0x200e3af4, 12),
                (".g2_conversate_prep_note_ram_200d7630", 0x200d7630, 0xb4b1)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"state RAM section changed: {name}")
        for name, address, size, edges in (
                (".g2_conversate_event_names_200004f4", 0x200004f4, 52, 13),
                (".g2_conversate_ui_state_names_20000540", 0x20000540, 28, 7)):
            section = elf.get_section_by_name(name)
            relocs = elf.get_section_by_name(".rel" + name)
            if (section is None or section["sh_type"] != "SHT_PROGBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size or
                    relocs is None or relocs.num_relocations() != edges):
                raise RuntimeError(f"name table changed: {name}")
    linker = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_prep_note_ram_20261016.ld"
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_UPDATE_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 35,
        "linker_script": ref(linker),
        "native_body": "0x5b43ee..0x5b44d7", "native_body_bytes": 234,
        "unresolved_before": 132, "unresolved_after": 131,
        "removed_imports": ["audio_conversate_prep_note_update_5b43ee"],
        "new_imports": [], "fixed_ram_sections": previous["fixed_ram_sections"],
        "prep_note_ram": {"address": "0x200d7630", "size": 0xb4b1,
                          "title_record_bytes": 136,
                          "clear_ranges": [{"address": "0x200df430", "size": 14001},
                                           {"address": "0x200d86c4", "size": 28012}],
                          "overlap_bytes": 4},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Broader Main coverage and startup RAM initialization remain open.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()

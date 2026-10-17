#!/usr/bin/env python3
"""Pin bounded Conversate tag-storage initializer C integration."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-tag-storage-59619e"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    prior = BASE / "main-conversate-app-open-5b4a90/candidate.o"
    candidate = HERE / "candidate.o"
    before, after = imports(prior), imports(candidate)
    if (len(before) != 133 or len(after) != 132 or
            before - after != {"audio_conversate_tag_storage_init_59619e"} or
            after - before):
        raise RuntimeError("Conversate tag-storage import frontier changed")
    oracle_path = HERE / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    source = ROOT / oracle["source"]
    if (oracle["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_TAG_STORAGE_INIT_59619E_C"
            or oracle["cases"] != 20 or oracle["source_sha256"] != sha(source)
            or oracle["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"):
        raise RuntimeError("Conversate tag-storage oracle changed")
    previous = json.loads((BASE / "main-conversate-app-open-5b4a90/receipt.json").read_text())
    fixed = {name: (int(row["address"], 16), row["size"])
             for name, row in previous["fixed_ram_sections"].items()}
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in fixed.items():
            section = elf.get_section_by_name(name)
            if section is None or section["sh_type"] != "SHT_NOBITS" or section["sh_addr"] != address or section["sh_size"] != size:
                raise RuntimeError(f"fixed RAM section changed: {name}")
        state = elf.get_section_by_name(".g2_conversate_tag_storage_200e3af4")
        symbol_table = elf.get_section_by_name(".symtab")
        state_symbol = next((symbol for symbol in symbol_table.iter_symbols()
                             if symbol.name == "audio_conversate_tag_storage_state_200e3af4"), None)
        if (state is None or state["sh_type"] != "SHT_NOBITS" or
                state["sh_addr"] != 0x200e3af4 or state["sh_size"] != 12 or
                state_symbol is None or state_symbol["st_value"] != 0 or
                state_symbol["st_shndx"] != elf.get_section_index(".g2_conversate_tag_storage_200e3af4")):
            raise RuntimeError("tag-storage RAM state changed")
        for name, address, size, edges in (
                (".g2_conversate_event_names_200004f4", 0x200004f4, 52, 13),
                (".g2_conversate_ui_state_names_20000540", 0x20000540, 28, 7)):
            section = elf.get_section_by_name(name)
            relocs = elf.get_section_by_name(".rel" + name)
            if section is None or section["sh_type"] != "SHT_PROGBITS" or section["sh_addr"] != address or section["sh_size"] != size or relocs is None or relocs.num_relocations() != edges:
                raise RuntimeError(f"initialized name table changed: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_TAG_STORAGE_INIT_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "source": ref(source), "oracle_receipt": ref(oracle_path), "oracle_cases": 20,
        "native_body": "0x59619e..0x59624d", "native_body_bytes": 176,
        "unresolved_before": 133, "unresolved_after": 132,
        "removed_imports": ["audio_conversate_tag_storage_init_59619e"],
        "new_imports": [],
        "fixed_ram_sections": previous["fixed_ram_sections"],
        "tag_storage_state": {"address": "0x200e3af4", "size": 12, "type": "SHT_NOBITS"},
        "linker_script": ref(G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_tag_storage_20261016.ld"),
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Tag-storage initializer and 12-byte RAM state are source-owned; other lower providers and broader Main coverage remain.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__": main()

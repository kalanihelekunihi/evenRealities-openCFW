#!/usr/bin/env python3
"""Authenticate source-owned Conversate name tables against stock low-RAM init."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from decode_main_low_ram_20261016 import decode, DECODED_SHA

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-name-tables"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE_ADDR = 0x438000
SPEC = {".g2_conversate_event_names_200004f4": (0x200004f4, 13),
        ".g2_conversate_ui_state_names_20000540": (0x20000540, 7)}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
def imports(path):
    return set(line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip())


def main():
    prior = BASE / "main-conversate-ui-state-helpers/candidate.o"
    candidate = HERE / "candidate.o"
    removed = {"audio_conversate_event_names_200004f4",
               "audio_conversate_ui_state_names_20000540",
               "audio_conversate_ui_state_20071368"}
    before, after = imports(prior), imports(candidate)
    if len(before) != 133 or len(after) != 130 or before - after != removed or after - before:
        raise RuntimeError("Conversate name-table import frontier changed")
    decoded = decode()
    if hashlib.sha256(decoded).hexdigest() != DECODED_SHA:
        raise RuntimeError("stock low-RAM decoded hash changed")
    payload = STOCK.read_bytes()[32:]

    def stock_string(address):
        if not (BASE_ADDR <= address < BASE_ADDR + len(payload)):
            raise RuntimeError(f"stock string pointer outside payload: {address:#x}")
        return payload[address-BASE_ADDR:].split(b"\0", 1)[0].decode("ascii")

    previous = json.loads((BASE / "main-conversate-ui-state-helpers/receipt.json").read_text())
    fixed = {name: (int(row["address"], 16), row["size"])
             for name, row in previous["fixed_ram_sections"].items()}
    matches = {}
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = elf.get_section_by_name(".symtab")
        for name, (address, count) in SPEC.items():
            section = elf.get_section_by_name(name)
            relocs = elf.get_section_by_name(".rel" + name)
            if (section is None or section["sh_type"] != "SHT_PROGBITS" or
                    section["sh_addr"] != address or section["sh_size"] != 4*count or
                    relocs is None or relocs.num_relocations() != count):
                raise RuntimeError(f"initialized name table layout changed: {name}")
            data = section.data()
            rows = []
            for index, relocation in enumerate(relocs.iter_relocations()):
                if relocation["r_offset"] != index*4 or relocation["r_info_type"] != 2:
                    raise RuntimeError(f"name-table relocation changed: {name}:{index}")
                symbol = symbols.get_symbol(relocation["r_info_sym"])
                if not isinstance(symbol["st_shndx"], int):
                    raise RuntimeError("name-table target is not a C section")
                target_section = elf.get_section(symbol["st_shndx"])
                addend = struct.unpack_from("<I", data, index*4)[0]
                target_offset = symbol["st_value"] + addend - target_section["sh_addr"]
                target = target_section.data()[target_offset:].split(b"\0", 1)[0].decode("ascii")
                stock_pointer = struct.unpack_from("<I", decoded, address-0x20000000+index*4)[0]
                expected = stock_string(stock_pointer)
                if target != expected:
                    raise RuntimeError(f"name-table string mismatch {name}:{index}: {target!r} != {expected!r}")
                rows.append({"index": index, "stock_pointer": hex(stock_pointer), "string": expected})
            matches[name] = rows
        state_section = elf.get_section_by_name(".g2_conversate_ui_state_20071368")
        if (state_section is None or state_section["sh_type"] != "SHT_NOBITS" or
                state_section["sh_addr"] != 0x20071368 or state_section["sh_size"] != 1):
            raise RuntimeError("UI-state byte layout changed")
        for name, (address, size) in fixed.items():
            section = elf.get_section_by_name(name)
            if section is None or section["sh_type"] != "SHT_NOBITS" or section["sh_addr"] != address or section["sh_size"] != size:
                raise RuntimeError(f"prior fixed RAM changed: {name}")
    sources = [G2 / "components/audio/uart_thread_source_candidate/conversate_name_tables_200004f4.c",
               G2 / "components/audio/uart_thread_source_candidate/conversate_ui_state_ram_20071368.c"]
    linker = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_name_tables_20261016.ld"
    record = {
        "status": "PASS_AUTHENTICATED_MAIN_CONVERSATE_NAME_TABLES_C",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "sources": [ref(path) for path in sources], "linker_script": ref(linker),
        "stock_payload_sha256": hashlib.sha256(payload).hexdigest(),
        "stock_decoded_low_ram_sha256": DECODED_SHA,
        "stock_matched_entries": matches,
        "unresolved_before": 133, "unresolved_after": 130,
        "removed_imports": sorted(removed), "new_imports": [],
        "fixed_ram_sections": {**previous["fixed_ram_sections"],
                               ".g2_conversate_ui_state_20071368":
                               {"address": hex(0x20071368), "size": 1, "type": "SHT_NOBITS"}},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Whole-image startup copy/relocation and UI-state cell initialization remain; source tables reproduce stock strings but not stock absolute pointer values.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sum(map(len, matches.values())), sha(output))


if __name__ == "__main__": main()

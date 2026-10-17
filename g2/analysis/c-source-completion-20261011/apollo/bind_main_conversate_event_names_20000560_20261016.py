#!/usr/bin/env python3
"""Reconstruct and bind authenticated Conversate UI event-name startup data."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from decode_main_low_ram_20261016 import PACKAGE, PAYLOAD_SHA, decode

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-event-names-20000560"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_event_names_20000560.c"
PRIOR = BASE / "main-conversate-anim-frames-20000bf4/candidate.o"
OBJECT = HERE / "names.o"
CANDIDATE = HERE / "candidate.o"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("authenticated Main payload changed")
    ram = decode()
    pointers = struct.unpack_from("<21I", ram, 0x560)
    strings = []
    for address in pointers:
        if not 0x438000 <= address < 0x7a0000:
            raise RuntimeError("event name outside payload")
        offset = address - 0x438000
        end = payload.index(0, offset, offset+80)
        data = payload[offset:end+1]
        if not data[:-1].startswith(b"CONVERSATE_UI_EVENT_") or not data[:-1].isascii():
            raise RuntimeError("event name content changed")
        strings.append(data)
    lines = ["/* Stock Conversate event names from Main startup RAM 0x20000560. */",
             "#include <stdint.h>"]
    for i, data in enumerate(strings):
        values = ", ".join(f"0x{x:02x}" for x in data)
        lines += [f"__attribute__((used, section(\".g2_conversate_event_name_{i:02d}\")))",
                  f"const char audio_conversate_event_name_bytes_{i:02d}[{len(data)}] = {{{values}}};"]
    lines += ["__attribute__((used, section(\".g2_conversate_event_names_20000560\")))",
              "const char *audio_conversate_ui_event_names_20000560[21] = {"]
    lines += [f"    audio_conversate_event_name_bytes_{i:02d}," for i in range(21)]
    lines += ["};", ""]
    SOURCE.write_text("\n".join(lines))
    HERE.mkdir(parents=True, exist_ok=True)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        symtab = elf.get_section_by_name(".symtab")
        table = elf.get_section_by_name(".g2_conversate_event_names_20000560")
        reloc = elf.get_section_by_name(".rel.g2_conversate_event_names_20000560")
        if table is None or table.data() != bytes(84) or reloc is None:
            raise RuntimeError("C event pointer table changed")
        if table["sh_flags"] & 1 != 1:
            raise RuntimeError("startup RAM pointer table is not writable")
        rows = list(reloc.iter_relocations())
        if len(rows) != 21:
            raise RuntimeError("C event pointer relocation count changed")
        for i, data in enumerate(strings):
            section = elf.get_section_by_name(f".g2_conversate_event_name_{i:02d}")
            if section is None or section.data() != data:
                raise RuntimeError(f"event name {i} bytes differ")
            row = rows[i]
            if row["r_offset"] != 4*i or row["r_info_type"] != 2 or \
               symtab.get_symbol(row["r_info_sym"]).name != f"audio_conversate_event_name_bytes_{i:02d}":
                raise RuntimeError(f"event name {i} relocation differs")
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CANDIDATE)], check=True)
    before, after = imports(PRIOR), imports(CANDIDATE)
    if len(before) != 129 or len(after) != 128 or before-after != {"audio_conversate_ui_event_names_20000560"} or after-before:
        raise RuntimeError("Main import frontier changed")
    record = {"status": "PASS_MAIN_CONVERSATE_EVENT_NAMES_DATA_INTEGRATION",
              "source": ref(SOURCE), "object": ref(OBJECT), "candidate_object": ref(CANDIDATE),
              "prior_candidate": ref(PRIOR), "stock_payload_sha256": PAYLOAD_SHA,
              "decoded_low_ram_sha256": hashlib.sha256(ram).hexdigest(),
              "stock_pointer_addresses": [hex(x) for x in pointers],
              "stock_string_sha256": [hashlib.sha256(x).hexdigest() for x in strings],
              "unresolved_before": 129, "unresolved_after": 128,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Other Main imports, exact final placement, whole-image source and hardware behavior remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()

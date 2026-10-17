#!/usr/bin/env python3
"""Generate and bind all eight authenticated Main locale pointer tables."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from decode_main_low_ram_20261016 import PACKAGE, PAYLOAD_SHA, decode

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261017"
HERE = BASE / "main-locale-data-20001588"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_locale_data_20001588.c"
CONSUMER = G2 / "components/audio/uart_thread_source_candidate/display_context_registry.c"
PRIOR = G2 / "build/c-firmware/20261016/main-conversate-event-names-20000560/candidate.o"
OBJECT = HERE / "locale-data.o"
CONSUMER_OBJECT = HERE / "context-registry-recheck.o"
CANDIDATE = HERE / "candidate.o"
NAMES = ("en", "de", "es", "fr", "it", "ja", "zh_cn", "zh_hk")
RAM_FIRST = 0x20001588
WORDS = 157
SPAN = WORDS * 4


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
    tables = {}
    for index, name in enumerate(NAMES):
        address = RAM_FIRST + index * SPAN
        tables[name] = struct.unpack_from("<157I", ram, address - 0x20000000)
    addresses = sorted({pointer for row in tables.values() for pointer in row if pointer})
    if len(addresses) != 1034:
        raise RuntimeError("locale string address census changed")
    strings = {}
    spans = []
    for address in addresses:
        if not 0x438000 <= address < 0x7a0000:
            raise RuntimeError("locale string pointer outside authenticated payload")
        offset = address - 0x438000
        end = payload.index(0, offset, offset + 1024) + 1
        strings[address] = payload[offset:end]
        spans.append((address, address + len(strings[address])))
    if any(next_start < end for (_, end), (next_start, _) in zip(spans, spans[1:])):
        raise RuntimeError("locale strings overlap; separate symbols would change identity")
    lines = ["/* Eight stock Main locale pointer tables from startup RAM 0x20001588. */",
             "#include <stdint.h>"]
    for address, data in strings.items():
        lines += [f"__attribute__((used, section(\".g2_locale_text_{address:06x}\")))",
                  f"const char audio_uart_locale_text_{address:06x}[{len(data)}] = {{"]
        for pos in range(0, len(data), 16):
            lines.append("    " + ", ".join(f"0x{value:02x}" for value in data[pos:pos+16]) + ",")
        lines.append("};")
    for name, row in tables.items():
        native = RAM_FIRST + NAMES.index(name) * SPAN
        lines += [f"__attribute__((used, section(\".g2_locale_data_{native:08x}\")))",
                  f"const char *audio_uart_locale_data_{name}[157] = {{"]
        for pointer in row:
            lines.append(f"    audio_uart_locale_text_{pointer:06x}," if pointer else "    0,")
        lines.append("};")
    lines.append("")
    SOURCE.write_text("\n".join(lines))
    HERE.mkdir(parents=True, exist_ok=True)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    consumer_source = CONSUMER.read_text()
    for name in NAMES:
        if f"extern const char *audio_uart_locale_data_{name}[157];" not in consumer_source:
            raise RuntimeError(f"locale consumer type for {name} changed")
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(CONSUMER), "-o", str(CONSUMER_OBJECT)], check=True)
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        symtab = elf.get_section_by_name(".symtab")
        for address, data in strings.items():
            section = elf.get_section_by_name(f".g2_locale_text_{address:06x}")
            if section is None or section.data() != data or section["sh_flags"] & 1:
                raise RuntimeError(f"locale string {address:x} differs")
        for index, (name, row) in enumerate(tables.items()):
            native = RAM_FIRST + index * SPAN
            section_name = f".g2_locale_data_{native:08x}"
            section = elf.get_section_by_name(section_name)
            reloc = elf.get_section_by_name(".rel" + section_name)
            if section is None or reloc is None or section["sh_size"] != SPAN or section["sh_flags"] & 1 != 1:
                raise RuntimeError(f"locale table {name} layout changed")
            relocations = list(reloc.iter_relocations())
            if len(relocations) != sum(pointer != 0 for pointer in row) or section.data() != bytes(SPAN):
                raise RuntimeError(f"locale table {name} relocation count changed")
            expected = [(i*4, f"audio_uart_locale_text_{pointer:06x}")
                        for i, pointer in enumerate(row) if pointer]
            actual = [(entry["r_offset"], symtab.get_symbol(entry["r_info_sym"]).name)
                      for entry in relocations]
            if actual != expected or any(entry["r_info_type"] != 2 for entry in relocations):
                raise RuntimeError(f"locale table {name} relocations differ")
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CANDIDATE)], check=True)
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_uart_locale_data_" + name for name in NAMES}
    if len(before) != 128 or len(after) != 120 or before-after != removed or after-before:
        raise RuntimeError("Main import frontier changed")
    record = {"status": "PASS_MAIN_EIGHT_LOCALE_TABLES_SOURCE_DATA_INTEGRATION",
              "source": ref(SOURCE), "object": ref(OBJECT), "candidate_object": ref(CANDIDATE),
              "consumer_source": ref(CONSUMER), "consumer_recheck_object": ref(CONSUMER_OBJECT),
              "prior_candidate": ref(PRIOR), "stock_payload_sha256": PAYLOAD_SHA,
              "decoded_low_ram_sha256": hashlib.sha256(ram).hexdigest(),
              "table_addresses": {name: hex(RAM_FIRST+i*SPAN) for i, name in enumerate(NAMES)},
              "pointers_per_table": WORDS, "distinct_stock_string_addresses": len(strings),
              "nonzero_pointers": sum(pointer != 0 for row in tables.values() for pointer in row),
              "unresolved_before": 128, "unresolved_after": 120,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Other Main imports, exact final placement, whole-image source and hardware behavior remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(strings), len(after), sha(receipt))


if __name__ == "__main__":
    main()

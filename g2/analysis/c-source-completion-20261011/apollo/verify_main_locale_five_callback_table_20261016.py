#!/usr/bin/env python3
"""Verify five C-relocated locale slots and their indirect call behavior."""
import hashlib
import importlib.util
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = G2 / "components/audio/uart_thread_source_candidate"
TABLE = HERE / "display_ring_locale_dispatch_five_callbacks_200044c0.c"
HEADER = HERE / "display_ring_locale_dispatch_table.h"
LOWER = HERE / "display_ring_locale_callbacks_4d4384.c"
CLASSIFY = HERE / "display_ring_locale_classify_callbacks_4d4368.c"
CONSUMER = HERE / "display_ring_locale_dispatch.c"
ERROR = HERE / "display_uart_error_cell.c"
LINKER = HERE / "display_ring_locale_dispatch_relocatable_200044c0.ld"
DECODER = G2 / "analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py"
ORACLE = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_locale_ascii_callbacks_20261016.py"
CLASSIFY_RECEIPT = G2 / "build/c-firmware/20261016/main-locale-classify-callbacks/receipt.json"
LOWER_RECEIPT = G2 / "build/c-firmware/20261016/main-locale-ascii-callbacks/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-locale-five-callback-table"
SLOTS = ((0x10, "audio_uart_locale_ascii_alpha_4d436e", 0x4d436e),
         (0x18, "audio_uart_locale_ascii_lowercase_4d4368", 0x4d4368),
         (0x20, "audio_uart_locale_ascii_space_4d4384", 0x4d4384),
         (0x24, "audio_uart_locale_ascii_uppercase_4d436c", 0x4d436c),
         (0x28, "audio_uart_locale_ascii_lower_4d4398", 0x4d4398))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    classify = json.loads(CLASSIFY_RECEIPT.read_text())
    lower = json.loads(LOWER_RECEIPT.read_text())
    if classify["status"] != "PASS_EXPERIMENTAL_MAIN_LOCALE_CLASSIFY_CALLBACKS_C" or \
            classify["comparisons"] != 801 or classify["source_sha256"] != sha(CLASSIFY) or \
            lower["status"] != "PASS_EXPERIMENTAL_MAIN_LOCALE_ASCII_CALLBACKS_C" or \
            lower["comparisons"] != 534 or lower["source_sha256"] != sha(LOWER):
        raise RuntimeError("locale callback proofs changed")
    decode_spec = importlib.util.spec_from_file_location("main_low_ram", DECODER)
    decoder = importlib.util.module_from_spec(decode_spec)
    decode_spec.loader.exec_module(decoder)
    original = decoder.decode()[0x44c0:0x44c0 + 44]
    oracle_spec = importlib.util.spec_from_file_location("locale_oracle", ORACLE)
    oracle = importlib.util.module_from_spec(oracle_spec)
    oracle_spec.loader.exec_module(oracle)
    payload = decoder.PACKAGE.read_bytes()[32:]
    OUT.mkdir(parents=True, exist_ok=True)
    flags = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
             "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
             "-Wextra", "-Werror", "-c"]
    objects = []
    for source in (TABLE, LOWER, CLASSIFY, CONSUMER, ERROR):
        obj = OUT / (source.stem + ".o")
        subprocess.run([*flags, str(source), "-o", str(obj)], check=True)
        objects.append(obj)
    table_obj = objects[0]
    relocation_lines = [line.strip() for line in subprocess.check_output(
        ["arm-none-eabi-objdump", "-r", str(table_obj)], text=True).splitlines()
        if "R_ARM_ABS32" in line]
    expected_relocations = [f"{offset:08x} R_ARM_ABS32       {name}"
                            for offset, name, _ in SLOTS]
    if relocation_lines != expected_relocations:
        raise RuntimeError("five locale callback relocations changed")
    raw_path = OUT / "locale-five-table-raw.bin"
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=.data.opencfw.ring.locale_dispatch",
                    str(table_obj), str(raw_path)], check=True)
    raw = raw_path.read_bytes()
    excluded = {i for offset, _, _ in SLOTS for i in range(offset, offset + 4)}
    if len(raw) != 44 or any(raw[i] != original[i] for i in range(44)
                             if i not in excluded):
        raise RuntimeError("noncallback locale bytes differ from stock")
    placed = OUT / "locale-five-table-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER),
                    str(table_obj), "-o", str(placed)], check=True)
    elf_path = OUT / "locale-five-table.elf"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-o", str(elf_path),
                    *(str(obj) for obj in objects)], check=True,
                   stderr=subprocess.DEVNULL)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {symbol.name: symbol["st_value"] for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        segments = [(segment["p_vaddr"], segment.data()) for segment in
                    elf.iter_segments() if segment["p_type"] == "PT_LOAD"]
    table_address = symbols["audio_uart_ring_locale_dispatch_200044c0"]
    def at(address, size):
        for start, data in segments:
            if start <= address and address + size <= start + len(data):
                return data[address-start:address-start+size]
        raise RuntimeError("linked locale table outside loadable segment")
    comparisons = 0
    for offset, name, stock in SLOTS:
        target = struct.unpack("<I", at(table_address + offset, 4))[0]
        if target != symbols[name]:
            raise RuntimeError("locale slot not relocated to C symbol: " + name)
        for value in (0, 8, 9, 13, 14, 0x20, 0x40, 0x41, 0x5a, 0x5b,
                      0x60, 0x61, 0x7a, 0x7b, 0x80, 0xffffffff):
            native = oracle.run((), payload, stock, value)
            compiled = oracle.run(segments, payload, target, value)
            if native != compiled:
                raise RuntimeError(f"indirect locale mismatch {name} {value:#x}")
            comparisons += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LOCALE_FIVE_CALLBACK_TABLE_C",
               "sources": {str(path.relative_to(ROOT)): sha(path) for path in
                           (TABLE, HEADER, LOWER, CLASSIFY, CONSUMER, ERROR, LINKER)},
               "decoder": str(DECODER.relative_to(ROOT)), "decoder_sha256": sha(DECODER),
               "prior_oracle": str(ORACLE.relative_to(ROOT)),
               "prior_oracle_sha256": sha(ORACLE),
               "lower_receipt": str(LOWER_RECEIPT.relative_to(ROOT)),
               "lower_receipt_sha256": sha(LOWER_RECEIPT),
               "classify_receipt": str(CLASSIFY_RECEIPT.relative_to(ROOT)),
               "classify_receipt_sha256": sha(CLASSIFY_RECEIPT),
               "objects": {str(path.relative_to(ROOT)): sha(path) for path in objects},
               "table_raw": str(raw_path.relative_to(ROOT)),
               "table_raw_sha256": sha(raw_path),
               "placed_object": str(placed.relative_to(ROOT)),
               "placed_sha256": sha(placed),
               "elf": str(elf_path.relative_to(ROOT)), "elf_sha256": sha(elf_path),
               "callback_relocations": expected_relocations,
               "selected_address": "0x200044c0", "selected_bytes": 44,
               "indirect_comparisons": comparisons,
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["All five function slots in the selected locale table are relocated to C leaves; 80 indirect stock/C cases pass. Two data pointer fields, full native table allocation and runtime mutation remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], comparisons, sha(path))


if __name__ == "__main__":
    main()

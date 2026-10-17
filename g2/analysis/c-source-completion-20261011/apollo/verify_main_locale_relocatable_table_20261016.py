#!/usr/bin/env python3
"""Check C locale table relocations and stock/C wrapper behavior."""
import hashlib
import importlib.util
import json
import random
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = G2 / "components/audio/uart_thread_source_candidate"
CONSUMER = HERE / "display_ring_locale_dispatch.c"
TABLE = HERE / "display_ring_locale_dispatch_relocatable_200044c0.c"
HEADER = HERE / "display_ring_locale_dispatch_table.h"
CALLBACKS = HERE / "display_ring_locale_callbacks_4d4384.c"
ERROR = HERE / "display_uart_error_cell.c"
LINKER = TABLE.with_suffix(".ld")
PACKAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
DECODER = G2 / "analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py"
CALLBACK_RECEIPT = G2 / "build/c-firmware/20261016/main-locale-ascii-callbacks/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-locale-relocatable-source"
FUNCTIONS = (("audio_uart_ring_locale_space_4d58ae", 0x4d58ae),
             ("audio_uart_ring_locale_lower_4d58c2", 0x4d58c2))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(payload, low_ram, segments, address, value):
    machine = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    machine.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    machine.mem_map(0x400000, 0x400000)
    machine.mem_write(0x438000, payload)
    machine.mem_map(0x100000, 0x100000)
    machine.mem_map(0x20000000, 0x100000)
    machine.mem_write(0x20000000, low_ram)
    for target, data in segments:
        machine.mem_write(target, data)
    machine.reg_write(A.UC_ARM_REG_R0, value)
    machine.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
    machine.reg_write(A.UC_ARM_REG_LR, 0x101ff1)
    machine.emu_start(address | 1, 0x101ff0, count=500)
    return machine.reg_read(A.UC_ARM_REG_R0)


def main():
    callback = json.loads(CALLBACK_RECEIPT.read_text())
    if callback["status"] != "PASS_EXPERIMENTAL_MAIN_LOCALE_ASCII_CALLBACKS_C" or \
            callback["source_sha256"] != sha(CALLBACKS) or callback["comparisons"] != 534:
        raise RuntimeError("C locale callback proof changed")
    spec = importlib.util.spec_from_file_location("low_ram", DECODER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    low_ram = module.decode()
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != module.PAYLOAD_SHA:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    flags = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
             "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
             "-Wextra", "-Werror", "-c"]
    objs = []
    for source in (CONSUMER, TABLE, CALLBACKS, ERROR):
        obj = OUT / (source.stem + ".o")
        subprocess.run([*flags, str(source), "-o", str(obj)], check=True)
        objs.append(obj)
    table_reloc = subprocess.check_output(["arm-none-eabi-objdump", "-r", str(objs[1])],
                                          text=True)
    lines = [line.strip() for line in table_reloc.splitlines()
             if "R_ARM_ABS32" in line]
    expected_reloc = ["00000020 R_ARM_ABS32       audio_uart_locale_ascii_space_4d4384",
                      "00000028 R_ARM_ABS32       audio_uart_locale_ascii_lower_4d4398"]
    if lines != expected_reloc:
        raise RuntimeError("locale table callback relocations changed")
    table_raw = OUT / "locale-table-raw.bin"
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=.data.opencfw.ring.locale_dispatch", str(objs[1]),
                    str(table_raw)], check=True)
    raw = table_raw.read_bytes()
    original = low_ram[0x44c0:0x44c0 + 44]
    if len(raw) != 44 or any(raw[i] != original[i] for i in range(44)
                             if i not in range(0x20, 0x24) and
                             i not in range(0x28, 0x2c)):
        raise RuntimeError("non-relocated locale table bytes differ from stock")
    placed = OUT / "locale-table-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER),
                    str(objs[1]), "-o", str(placed)], check=True)
    elf_path = OUT / "locale-relocatable.elf"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-o", str(elf_path),
                    *(str(obj) for obj in objs)], check=True,
                   stderr=subprocess.DEVNULL)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {symbol.name: symbol["st_value"] for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        segments = [(segment["p_vaddr"], segment.data()) for segment in
                    elf.iter_segments() if segment["p_type"] == "PT_LOAD"]
    values = sorted(set(range(0x80)) | {0x80, 0xff, 0x100, 0xffff, 0x10000,
                                         0x7fffffff, 0x80000000, 0xffffffe0,
                                         0xfffffff6, 0xfffffff7, 0xffffffff} |
                    {random.Random(0x4d58ae + i).getrandbits(32) for i in range(128)})
    comparisons = 0
    for name, stock in FUNCTIONS:
        if name not in symbols:
            raise RuntimeError("compiled locale wrapper missing: " + name)
        for value in values:
            native = run(payload, low_ram, (), stock, value)
            compiled = run(payload, low_ram, segments, symbols[name], value)
            if native != compiled:
                raise RuntimeError(f"locale wrapper mismatch {name} {value:#x}: "
                                   f"{native:#x} {compiled:#x}")
            comparisons += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LOCALE_RELOCATABLE_TABLE_C",
               "sources": {str(path.relative_to(ROOT)): sha(path) for path in
                           (CONSUMER, TABLE, HEADER, CALLBACKS, ERROR, LINKER)},
               "decoder": str(DECODER.relative_to(ROOT)), "decoder_sha256": sha(DECODER),
               "package": str(PACKAGE.relative_to(ROOT)), "package_sha256": sha(PACKAGE),
               "callback_receipt": str(CALLBACK_RECEIPT.relative_to(ROOT)),
               "callback_receipt_sha256": sha(CALLBACK_RECEIPT),
               "objects": {str(path.relative_to(ROOT)): sha(path) for path in objs},
               "table_raw": str(table_raw.relative_to(ROOT)),
               "table_raw_sha256": sha(table_raw),
               "placed_object": str(placed.relative_to(ROOT)),
               "placed_sha256": sha(placed),
               "elf": str(elf_path.relative_to(ROOT)), "elf_sha256": sha(elf_path),
               "callback_relocations": expected_reloc,
               "selected_address": "0x200044c0", "selected_bytes": 44,
               "inputs_per_wrapper": len(values), "comparisons": comparisons,
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Two accessed callback slots are C-relocated and wrapper decisions match stock in controlled emulation. Other stock pointer fields and runtime table mutation remain open.",
                          "Isolated placement and emulation do not establish startup copy, final image placement or hardware behavior."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], comparisons, sha(path))


if __name__ == "__main__":
    main()

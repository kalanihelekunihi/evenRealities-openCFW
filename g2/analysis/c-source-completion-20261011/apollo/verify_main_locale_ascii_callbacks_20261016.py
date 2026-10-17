#!/usr/bin/env python3
"""Compare stock Thumb locale callbacks with C across ASCII and 32-bit edges."""
import hashlib
import json
import random
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ring_locale_callbacks_4d4384.c"
PACKAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
DECODER = G2 / "analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py"
OUT = G2 / "build/c-firmware/20261016/main-locale-ascii-callbacks"
FUNCTIONS = (("audio_uart_locale_ascii_space_4d4384", 0x4d4384),
             ("audio_uart_locale_ascii_lower_4d4398", 0x4d4398))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(segments, payload, address, value):
    machine = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    machine.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    machine.mem_map(0x400000, 0x400000)
    machine.mem_write(0x438000, payload)
    machine.mem_map(0x100000, 0x100000)
    machine.mem_map(0x20000000, 0x100000)
    for target, data in segments:
        machine.mem_write(target, data)
    machine.reg_write(A.UC_ARM_REG_R0, value)
    machine.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
    machine.reg_write(A.UC_ARM_REG_LR, 0x101ff1)
    machine.emu_start(address | 1, 0x101ff0, count=100)
    return machine.reg_read(A.UC_ARM_REG_R0)


def main():
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo Main payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj, elf_path = OUT / "locale-ascii-callbacks.o", OUT / "locale-ascii-callbacks.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-o", str(elf_path),
                    str(obj)], check=True, stderr=subprocess.DEVNULL)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {item.name: item["st_value"] for item in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        segments = [(item["p_vaddr"], item.data()) for item in elf.iter_segments()
                    if item["p_type"] == "PT_LOAD"]
    values = sorted(set(range(0x80)) | {0x80, 0xff, 0x100, 0xffff, 0x10000,
                                         0x7fffffff, 0x80000000, 0xffffffe0,
                                         0xfffffff6, 0xfffffff7, 0xffffffff} |
                    {random.Random(0x4d4384 + i).getrandbits(32) for i in range(128)})
    comparisons = 0
    for name, stock in FUNCTIONS:
        if name not in symbols:
            raise RuntimeError("compiled callback missing: " + name)
        for value in values:
            native = run((), payload, stock, value)
            compiled = run(segments, payload, symbols[name], value)
            if native != compiled:
                raise RuntimeError(f"callback mismatch {name} {value:#x}: {native:#x} {compiled:#x}")
            comparisons += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LOCALE_ASCII_CALLBACKS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "package": str(PACKAGE.relative_to(ROOT)), "package_sha256": sha(PACKAGE),
               "decoder": str(DECODER.relative_to(ROOT)), "decoder_sha256": sha(DECODER),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "elf": str(elf_path.relative_to(ROOT)), "elf_sha256": sha(elf_path),
               "stock_addresses": {name: hex(address) for name, address in FUNCTIONS},
               "inputs_per_callback": len(values), "comparisons": comparisons,
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Controlled stock/C comparison covers ASCII, boundaries and deterministic 32-bit inputs for the two callback leaves. Locale table relocation and other callback slots remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], comparisons, sha(path))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare Terminal item line spacing 0x5ea2c2 with pinned Apollo stock."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_item_spacing_5ea2c2.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-item-spacing-5ea2c2"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = "#include <stdint.h>\nuint32_t audio_uart_ring_primary_head_cell;\n"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5eadbc-0x438000:0x5eadc0-0x438000], "little") != 0x200746dc:
        raise RuntimeError("Apollo stock payload or font cell changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "item-spacing-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "item-spacing-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_item_spacing_5ea2c2",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, line_height):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        cell = symbols["audio_uart_ring_primary_head_cell"] if compiled else 0x200746dc
        u.mem_write(cell, struct.pack("<I", 0x20003000))
        u.mem_write(0x2000300c, struct.pack("<I", line_height))
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_item_spacing_5ea2c2"] if compiled else 0x5ea2c2
        u.emu_start(entry | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(cell, 4))

    cases = 0
    for line_height in (0, 1, 27, 28, 29, 40, 0x7fffffff, 0xffffffff):
        stock = run(False, line_height)
        selected = run(True, line_height)
        if stock != selected:
            raise RuntimeError(f"item-spacing mismatch {line_height=}: {stock} vs {selected}")
        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_ITEM_SPACING_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "stock font-pointer cell and full 32-bit subtraction",
              "limits": ["Null or invalid font pointers fault in stock; final RAM placement remains open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

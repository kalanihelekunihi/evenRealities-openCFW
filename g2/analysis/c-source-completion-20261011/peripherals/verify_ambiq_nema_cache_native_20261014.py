#!/usr/bin/env python3
"""Compare stock Nema cache writes with the C body over bounded states."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_SP, UC_ARM_REG_LR

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/main/ambiq_gpu_blit_candidate_20261014/nema_cache.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
RESULT = Path(__file__).with_name("ambiq-nema-cache-native-results.json")
PAYLOAD = STOCK.read_bytes()[32:]
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

with tempfile.TemporaryDirectory(prefix="g2-nema-cache-") as folder:
    folder = Path(folder)
    stub = folder / "stub.s"
    stub.write_text(".syntax unified\n.thumb\n.bss\n"
                    ".global audio_uart_ambiq_unit_cell\n"
                    "audio_uart_ambiq_unit_cell: .space 4\n")
    image = folder / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-nostdlib", "-Wl,-Ttext=0x100000", str(SOURCE), str(stub),
                    "-o", str(image)], cwd=ROOT, check=True, capture_output=True)
    with image.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, enabled, words):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, PAYLOAD)
        cpu.mem_map(0x100000, 0x200000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                cpu.mem_write(address, data)
        cell = 0x20074efc if native else symbols["audio_uart_ambiq_unit_cell"]
        cpu.mem_write(cell, (0x20080000).to_bytes(4, "little"))
        cpu.mem_write(0x20080000, b"".join(x.to_bytes(4, "little") for x in words))
        cpu.reg_write(UC_ARM_REG_R0, enabled)
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        done = [False]

        def hook(uc, address, _size, _user):
            if address == 0x600000:
                done[0] = True
                uc.emu_stop()

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x4b1588 if native else symbols["display_driver_nema_cache_4b1588"]
        cpu.emu_start(entry | 1, 0, count=100)
        assert done[0], (native, enabled, words)
        return bytes(cpu.mem_read(0x20080000, 32))

    cases = 0
    for enabled, a, b, c, old in itertools.product(
        (0, 1, 0x100, 0xffffffff), (0, 1, 0x80000000),
        (0, 2, 0x10000000), (0, 4, 0x40000000), (0, 0x55555555)):
        words = [0xcccccccc] * 8
        words[3], words[4], words[5], words[6], words[7] = a, b, old, old, c
        assert run(True, enabled, words) == run(False, enabled, words), (enabled, words)
        cases += 1

body = PAYLOAD[0x4b1588 - 0x438000:0x4b15a6 - 0x438000]
receipt = {"status": "PASS_AMBIQ_NEMA_CACHE_NATIVE", "cases": cases,
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
           "native_body_start": "0x4b1588", "native_body_end_inclusive": "0x4b15a5",
           "native_body_sha256": hashlib.sha256(body).hexdigest(),
           "limits": ["Unit cell points to synthetic RAM; no concurrent GPU state or hardware execution tested"]}
RESULT.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)

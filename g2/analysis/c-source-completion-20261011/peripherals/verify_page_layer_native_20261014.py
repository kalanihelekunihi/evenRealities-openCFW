#!/usr/bin/env python3
"""Compare page layer bitfield update and ABI return with stock 0x44e3ca."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR,
                               UC_ARM_REG_PC)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/main/page_layer_candidate_20261014/page_layer.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
RESULT = Path(__file__).with_name("page-layer-native-results.json")
PAYLOAD = STOCK.read_bytes()[32:]
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

with tempfile.TemporaryDirectory(prefix="g2-page-layer-") as folder:
    folder = Path(folder)
    stub = folder / "stub.c"
    stub.write_text("#include <stdint.h>\nvolatile uint32_t sink;\n"
                    "__attribute__((noinline)) void audio_uart_lv_obj_setup_layer_43e1fa(uint32_t x)"
                    "{sink=x;}\n")
    image = folder / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-nostdlib", "-Wl,-Ttext=0x100000", str(SOURCE), str(stub),
                    "-o", str(image)], cwd=ROOT, check=True, capture_output=True)
    with image.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, layer, old, saved_r3):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, PAYLOAD)
        cpu.mem_map(0x100000, 0x200000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                cpu.mem_write(address, data)
        obj, inner = 0x20080000, 0x20081000
        cpu.mem_write(obj + 8, inner.to_bytes(4, "little"))
        cpu.mem_write(inner + 0x32, old.to_bytes(2, "little"))
        for reg, value in ((UC_ARM_REG_R0, obj), (UC_ARM_REG_R1, layer),
                           (UC_ARM_REG_R2, 0xdeadbeef), (UC_ARM_REG_R3, saved_r3),
                           (UC_ARM_REG_SP, 0x200ff000), (UC_ARM_REG_LR, 0x600001)):
            cpu.reg_write(reg, value)
        helper = 0x43e1fa if native else symbols["audio_uart_lv_obj_setup_layer_43e1fa"] & ~1
        events = []
        done = [False]

        def hook(uc, address, _size, _user):
            if address == 0x600000:
                done[0] = True
                uc.emu_stop()
            elif address == helper:
                events.append(uc.reg_read(UC_ARM_REG_R0))
                uc.reg_write(UC_ARM_REG_R0, 0)
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x44e3ca if native else symbols["audio_uart_page_44e3ca"]
        cpu.emu_start(entry | 1, 0, count=100)
        assert done[0], (native, layer, old)
        return events, cpu.reg_read(UC_ARM_REG_R0), bytes(cpu.mem_read(inner + 0x32, 2))

    cases = 0
    for layer, old, saved in itertools.product(
        (0, 1, 3, 7, 15, 16, 31, 0xff, 0x100, 0xffffffff),
        (0, 0x3c0, 0x1234, 0xffff, 0xfc3f, 0x0040, 0x00c0),
        (0, 0x12345678, 0xffffffff)):
        assert run(True, layer, old, saved) == run(False, layer, old, saved), (layer, old, saved)
        cases += 1

body = PAYLOAD[0x44e3ca-0x438000:0x44e3f8-0x438000]
receipt = {"status": "PASS_PAGE_LAYER_NATIVE", "cases": cases,
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
           "native_body_start": "0x44e3ca", "native_body_end_inclusive": "0x44e3f7",
           "native_body_sha256": hashlib.sha256(body).hexdigest(),
           "limits": ["Child object setup call entry-cut and compared as an argument event",
                      "Synthetic object and style RAM only; LVGL runtime integration unverified"]}
RESULT.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)

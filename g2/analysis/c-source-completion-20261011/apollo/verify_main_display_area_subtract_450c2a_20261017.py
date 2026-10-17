#!/usr/bin/env python3
"""Compare stock/C LVGL redraw-area subtraction over signed rectangles."""
import hashlib
import json
import random
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_area_subtract_450c2a.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-area-subtract-450c2a"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUTPUT, FIRST, SECOND = 0x20010000, 0x20011000, 0x20012000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "area-subtract.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_area_subtract_450c2a", str(obj), "-o", str(elf_path)],
                   check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, first, second):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data:
                    cpu.mem_write(start, data)
        cpu.mem_write(OUTPUT, bytes([0xa5]) * 64)
        cpu.mem_write(FIRST, struct.pack("<4i", *first))
        cpu.mem_write(SECOND, struct.pack("<4i", *second))
        for reg, value in ((A.UC_ARM_REG_R0, OUTPUT), (A.UC_ARM_REG_R1, FIRST),
                           (A.UC_ARM_REG_R2, SECOND), (A.UC_ARM_REG_SP, 0x200ff000),
                           (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        done = [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x450c2a if native else symbols["audio_uart_lv_area_subtract_450c2a"]
        cpu.emu_start(entry | 1, 0, count=5000)
        if not done[0]:
            raise RuntimeError(f"area subtraction did not return: {native} {first} {second}")
        return cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(OUTPUT, 64))

    cases = [((0, 0, 10, 10), (20, 20, 30, 30)),
             ((0, 0, 10, 10), (0, 0, 10, 10)),
             ((0, 0, 10, 10), (2, 2, 8, 8)),
             ((0, 0, 10, 10), (5, 5, 15, 15)),
             ((-10, -10, 10, 10), (-2, -2, 2, 2))]
    rng = random.Random(0x450c2a)
    for _ in range(995):
        areas = []
        for _ in range(2):
            x, y = rng.randrange(-50, 51), rng.randrange(-50, 51)
            areas.append((x, y, x + rng.randrange(0, 50), y + rng.randrange(0, 50)))
        cases.append(tuple(areas))
    for first, second in cases:
        stock, compiled = run(True, first, second), run(False, first, second)
        if stock != compiled:
            raise RuntimeError(f"area subtraction mismatch {first} {second}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_AREA_SUBTRACT_450C2A_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x450c2a..0x450d8a", "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()), "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Native area predicates, dimensions and byte copy execute from authenticated stock image.",
                         "Valid 0-49 width and height rectangles are covered; other Main source remains open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()

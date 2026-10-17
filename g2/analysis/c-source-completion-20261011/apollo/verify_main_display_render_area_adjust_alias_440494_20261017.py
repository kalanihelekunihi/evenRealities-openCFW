#!/usr/bin/env python3
"""Compare stock 0x440494 with the existing sourced body through its alias."""
import hashlib
import itertools
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
BASE = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = BASE / "display_render_area_adjust_alias_440494.c"
OWNER = BASE / "display_lv_scrollbar_clip.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-render-area-adjust-alias-440494"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
AREA, OBJECT, SPEC = 0x20010000, 0x20011000, 0x20012000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    alias_obj, owner_obj, elf_path = OUT / "alias.o", OUT / "owner.o", OUT / "oracle.elf"
    cc = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
          "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
          "-fno-builtin", "-c"]
    subprocess.run([*cc, str(SOURCE), "-o", str(alias_obj)], check=True)
    subprocess.run([*cc, str(OWNER), "-o", str(owner_obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_obj_adjust_area_440494",
                    "--defsym=audio_uart_lv_obj_has_parent_44dca2=0x44dca2",
                    "--defsym=audio_uart_lv_scrollbar_clip_child_440dda=0x440dda",
                    str(alias_obj), str(owner_obj), "-o", str(elf_path)],
                   check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, coordinates, flags, mode):
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
        cpu.mem_write(AREA, struct.pack("<4i", *coordinates))
        cpu.mem_write(OBJECT + 8, struct.pack("<I", SPEC))
        cpu.mem_write(SPEC + 0x32, struct.pack("<H", mode << 10))
        cpu.reg_write(A.UC_ARM_REG_R0, OBJECT)
        cpu.reg_write(A.UC_ARM_REG_R1, AREA)
        cpu.reg_write(A.UC_ARM_REG_R2, flags)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2, r3 = (machine.reg_read(x) for x in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if pc == 0x44dca2:
                events.append(("parent", r0))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            elif pc == 0x440dda:
                points = list(struct.unpack("<8i", machine.mem_read(r1, 32)))
                events.append(("child_clip", r0, r2, r3, tuple(points)))
                for index in range(0, 8, 2):
                    points[index] += 1
                    points[index + 1] += 2
                machine.mem_write(r1, struct.pack("<8i", *points))
            else:
                return
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x440494 if native else symbols["audio_uart_lv_obj_adjust_area_440494"]
        cpu.emu_start(entry | 1, 0, count=5000)
        assert done[0], (native, events)
        return events, struct.unpack("<4i", cpu.mem_read(AREA, 16))

    rng = random.Random(0x440494)
    regions = [(1, 2, 7, 9), (-10, -4, 5, 6), (0, 0, 0, 0)]
    for _ in range(13):
        x, y = rng.randrange(-50, 50), rng.randrange(-50, 50)
        regions.append((x, y, x + rng.randrange(0, 25), y + rng.randrange(0, 25)))
    cases = list(itertools.product(regions, (0, 1, 2, 3), (0, 2)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"area adjust mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_RENDER_AREA_ADJUST_ALIAS_440494_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x440494..0x4405d4 via existing 0x4403e6 owner",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "owner_source": str(OWNER.relative_to(ROOT)),
              "owner_source_sha256": sha(OWNER.read_bytes()),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Parent and child scrollbar clipping are controlled lower calls.",
                         "Object-scrollbar owner source is compiled with the alias for this oracle."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()

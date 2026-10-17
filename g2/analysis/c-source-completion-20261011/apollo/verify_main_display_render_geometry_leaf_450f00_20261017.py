#!/usr/bin/env python3
"""Direct stock/C oracle for LVGL area overlap and extra draw size."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_render_geometry_leaf_450f00.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-render-geometry-leaf-450f00"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
FIRST, SECOND, OBJECT, SPEC = 0x20010000, 0x20011000, 0x20012000, 0x20013000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "geometry-leaf.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_area_overlap_450f00", str(obj), "-o", str(elf_path)],
                   check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, operation, values):
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
        if operation == "overlap":
            first, second = values
            cpu.mem_write(FIRST, struct.pack("<4i", *first))
            cpu.mem_write(SECOND, struct.pack("<4i", *second))
            cpu.reg_write(A.UC_ARM_REG_R0, FIRST)
            cpu.reg_write(A.UC_ARM_REG_R1, SECOND)
            entry = 0x450f00 if native else symbols["audio_uart_lv_area_overlap_450f00"]
        else:
            linked, size = values
            cpu.mem_write(OBJECT + 8, struct.pack("<I", SPEC if linked else 0))
            cpu.mem_write(SPEC + 0x2c, struct.pack("<I", size))
            cpu.reg_write(A.UC_ARM_REG_R0, OBJECT)
            entry = 0x452dc8 if native else symbols["audio_uart_lv_obj_ext_draw_size_452dc8"]
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        done = [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start(entry | 1, 0, count=100)
        assert done[0], (native, operation, values)
        return cpu.reg_read(A.UC_ARM_REG_R0)

    regions = [(0, 0, 5, 5), (-5, -5, 0, 0), (4, 4, 10, 10),
               (6, 6, 7, 7), (0, 6, 5, 9), (-3, 2, -1, 4), (5, 5, 5, 5)]
    cases = [("overlap", pair) for pair in itertools.product(regions, regions)]
    rng = random.Random(0x450f00)
    for _ in range(100):
        x, y = rng.randrange(-30, 30), rng.randrange(-30, 30)
        z, w = rng.randrange(-30, 30), rng.randrange(-30, 30)
        cases.append(("overlap", ((x, y, x + rng.randrange(0, 15), y + rng.randrange(0, 15)),
                                  (z, w, z + rng.randrange(0, 15), w + rng.randrange(0, 15)))))
    cases.extend(("extra", (linked, size)) for linked, size in
                 itertools.product((False, True), (0, 1, 0x12345678, 0xffffffff)))
    for operation, values in cases:
        stock, compiled = run(True, operation, values), run(False, operation, values)
        if stock != compiled:
            raise RuntimeError(f"geometry leaf mismatch {operation} {values}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_RENDER_GEOMETRY_LEAF_450F00_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "overlap_cases": 149, "extra_size_cases": 8,
              "native_body": "0x450f00..0x450f28 plus 0x452dc8..0x452dd8",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Direct instruction execution checks the two leaf functions; callers and hardware are separate gates."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare stock/C refresh-area coalescing with randomized signed rectangles."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_refresh_collect_45377a.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-refresh-collect-45377a"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROOT_RAM, DISPLAY = 0x2006f548, 0x20010000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "refresh-collect.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_refresh_collect_45377a",
                    "--defsym=audio_uart_display_lv_root=0x2006f548",
                    "--defsym=audio_uart_lv_area_size_450b80=0x450b80",
                    "--defsym=audio_uart_lv_area_copy_4530fc=0x4530fc",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, rectangles, flags):
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
        cpu.mem_write(ROOT_RAM + 0x10, struct.pack("<I", DISPLAY))
        cpu.mem_write(DISPLAY + 0x260, struct.pack("<I", len(rectangles)))
        cpu.mem_write(DISPLAY + 0x40, bytes(0x220))
        for i, area in enumerate(rectangles):
            cpu.mem_write(DISPLAY + 0x40 + 16 * i, struct.pack("<4i", *area))
            cpu.mem_write(DISPLAY + 0x240 + i, bytes((flags[i],)))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        done = [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x45377a if native else symbols["audio_uart_lv_refresh_collect_45377a"]
        cpu.emu_start(entry | 1, 0, count=40000)
        if not done[0]:
            raise RuntimeError(f"refresh collect did not return: {native} {rectangles} {flags}")
        return bytes(cpu.mem_read(DISPLAY + 0x40, 0x220))

    rng = random.Random(0x45377a)
    cases = [([], []), ([(0, 0, 10, 10)], [0]),
             ([(0, 0, 10, 10), (5, 5, 12, 12)], [0, 0]),
             ([(0, 0, 10, 10), (30, 30, 40, 40)], [0, 0])]
    for _ in range(296):
        count = rng.randrange(0, 8)
        areas, flags = [], []
        for _ in range(count):
            x, y = rng.randrange(-30, 31), rng.randrange(-30, 31)
            areas.append((x, y, x + rng.randrange(0, 30), y + rng.randrange(0, 30)))
            flags.append(rng.randrange(0, 2))
        cases.append((areas, flags))
    for areas, flags in cases:
        stock, compiled = run(True, areas, flags), run(False, areas, flags)
        if stock != compiled:
            raise RuntimeError(f"refresh collect mismatch {areas} {flags}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_REFRESH_COLLECT_45377A_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x45377a..0x453838", "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()), "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Area size/copy helpers execute from authenticated stock image; cases cover 0-7 signed rectangles.",
                         "Other refresh passes and whole-image source remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()

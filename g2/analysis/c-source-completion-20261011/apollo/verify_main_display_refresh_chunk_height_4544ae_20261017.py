#!/usr/bin/env python3
"""Compare stock/C LVGL refresh stripe capacity and round callback behavior."""
import hashlib
import itertools
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_refresh_chunk_height_4544ae.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-refresh-chunk-height-4544ae"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROOT_RAM, DISPLAY, DRAW = 0x2006f548, 0x20010000, 0x20011000
LOWERS = {"audio_uart_font_bitmap_stride": 0x48aad8,
          "audio_uart_lv_display_event_44fdbe": 0x44fdbe,
          "audio_uart_lv_area_height_4515a4": 0x4515a4,
          "audio_uart_lvgl_log": 0x44d25c}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "chunk-height.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_refresh_chunk_height_4544ae",
                    "--defsym=audio_uart_display_lv_root=0x2006f548",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, width, height, format_value, capacity, stride, rounding):
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
        cpu.mem_write(DISPLAY + 0x24, struct.pack("<I", DRAW))
        cpu.mem_write(DISPLAY + 0x3c, bytes((format_value,)))
        cpu.mem_write(DRAW + 0xc, struct.pack("<I", capacity))
        for reg, value in ((A.UC_ARM_REG_R0, DISPLAY), (A.UC_ARM_REG_R1, width),
                           (A.UC_ARM_REG_R2, height), (A.UC_ARM_REG_SP, 0x200ff000),
                           (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        events, done = [], [False]

        def cstr(address):
            return bytes(cpu.mem_read(address, 160)).split(b"\0", 1)[0].decode("utf-8", "replace")

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2, r3 = (machine.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if pc == 0x48aad8:
                events.append(("stride", r0, r1))
                machine.reg_write(A.UC_ARM_REG_R0, stride)
            elif pc == 0x44fdbe:
                area = list(struct.unpack("<4i", machine.mem_read(r2, 16)))
                events.append(("round", r0, r1, tuple(area)))
                area[3] += rounding
                machine.mem_write(r2, struct.pack("<4i", *area))
                machine.reg_write(A.UC_ARM_REG_R0, 1)
            elif pc == 0x44d25c:
                events.append(("log", r0, cstr(r1), r2, cstr(r3),
                               cstr(word(machine.reg_read(A.UC_ARM_REG_SP)))))
            else:
                return
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x4544ae if native else symbols["audio_uart_lv_refresh_chunk_height_4544ae"]
        cpu.emu_start(entry | 1, 0, count=7000)
        if not done[0]:
            raise RuntimeError(f"chunk height did not return: {native} {(width,height,format_value,capacity,stride,rounding)}")
        return cpu.reg_read(A.UC_ARM_REG_R0), events

    cases = list(itertools.product((1, 13), (0, 1, 5, 10),
                                   (6, 7, 8, 9, 10, 11),
                                   (0, 32, 1024), (0, 1, 8), (0, 1, 2)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"chunk height mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_REFRESH_CHUNK_HEIGHT_4544AE_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x4544ae..0x454572", "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()), "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Stride, LVGL event and logging are controlled lower calls; native area-height helper executes from stock.",
                         "Width 1/13, height 0/1/5/10, formats 6-11, capacity 0/32/1024 and round increments 0-2 are covered."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()

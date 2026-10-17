#!/usr/bin/env python3
"""Compare stock/C LVGL refresh render-loop flags, stripes and call order."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_refresh_render_4539b6.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-refresh-render-4539b6"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROOT_RAM, DISPLAY = 0x2006f548, 0x20010000
LOWERS = {
    "audio_uart_lv_display_event_44fdbe": 0x44fdbe,
    "audio_uart_display_area_copy_439c04": 0x439c04,
    "audio_uart_lv_area_width_451598": 0x451598,
    "audio_uart_lv_area_height_4515a4": 0x4515a4,
    "audio_uart_lv_refresh_chunk_height_4544ae": 0x4544ae,
    "audio_uart_lv_refresh_area_453bce": 0x453bce,
    "audio_uart_lv_display_flush_454574": 0x454574,
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "refresh-render.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_refresh_render_4539b6",
                    "--defsym=audio_uart_display_lv_root=0x2006f548",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, mode, areas, flags, chunk, initial_flags):
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
        cpu.mem_write(DISPLAY + 0x260, struct.pack("<I", len(areas)))
        cpu.mem_write(DISPLAY + 0x38, struct.pack("<I", initial_flags))
        cpu.mem_write(DISPLAY + 0x39, bytes((mode,)))
        for index, area in enumerate(areas):
            cpu.mem_write(DISPLAY + 0x40 + index * 16, struct.pack("<4i", *area))
            cpu.mem_write(DISPLAY + 0x240 + index, bytes((flags[index],)))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2 = (machine.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if pc == 0x44fdbe:
                events.append(("event", r1, word(DISPLAY + 0x38)))
                machine.reg_write(A.UC_ARM_REG_R0, 1)
            elif pc == 0x4544ae:
                events.append(("chunk", r1, r2))
                machine.reg_write(A.UC_ARM_REG_R0, chunk)
            elif pc == 0x453bce:
                events.append(("area", struct.unpack("<4i", machine.mem_read(r0, 16)),
                               r1, word(DISPLAY + 0x38)))
            elif pc == 0x454574:
                events.append(("flush", r0, word(DISPLAY + 0x38)))
            else:
                return
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x4539b6 if native else symbols["audio_uart_lv_refresh_render_4539b6"]
        cpu.emu_start(entry | 1, 0, count=30000)
        if not done[0]:
            raise RuntimeError(f"refresh render did not return: {native} {mode} {areas} {flags} {chunk}")
        return word(DISPLAY + 0x38), events

    base = [(0, 0, 3, 5), (5, 2, 7, 4), (1, 1, 2, 2)]
    cases = []
    for count in range(4):
        for flags in itertools.product((0, 1), repeat=count):
            for mode in (0, 1, 2, 3):
                for chunk in (1, 2, 3, 7):
                    for initial in (0, 0x02000003):
                        cases.append((mode, base[:count], flags, chunk, initial))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"refresh render mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_REFRESH_RENDER_4539B6_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x4539b6..0x453b74", "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()), "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Render area, chunk height, display flush and event dispatch are controlled lower calls.",
                         "Mode 0-3, 0-3 areas and chunk sizes 1/2/3/7 are covered; nested render area remains open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()

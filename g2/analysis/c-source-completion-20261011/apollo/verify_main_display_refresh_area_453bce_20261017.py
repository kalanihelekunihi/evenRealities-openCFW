#!/usr/bin/env python3
"""Compare stock/C LVGL refresh-area call order and tile state."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_refresh_area_453bce.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-refresh-area-453bce"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROOT_RAM, DISPLAY, LAYER, DRAW = 0x2006f548, 0x20010000, 0x20011000, 0x20012000
AREA, CHILDREN, CALLBACK = 0x20013000, 0x20020000, 0x101800
LOWERS = {
    "audio_uart_display_area_copy_439c04": 0x439c04,
    "audio_uart_lv_layer_reshape_draw_buf_453b78": 0x453b78,
    "audio_uart_lv_display_width_44fa7e": 0x44fa7e,
    "audio_uart_lv_display_height_44faa8": 0x44faa8,
    "audio_uart_lv_area_height_4515a4": 0x4515a4,
    "audio_uart_lv_area_size_450b80": 0x450b80,
    "audio_uart_lv_color_bpp_440f44": 0x440f44,
    "audio_uart_lv_malloc": 0x44f718,
    "audio_uart_lv_heap_free": 0x44f758,
    "audio_uart_lv_area_set_450b5c": 0x450b5c,
    "audio_uart_lv_render_layer_init_4847c4": 0x4847c4,
    "audio_uart_lv_render_layer_453e10": 0x453e10,
    "audio_uart_lv_render_wait_484622": 0x484622,
    "audio_uart_lv_refresh_tasks_484548": 0x484548,
    "audio_uart_lvgl_log": 0x44d25c,
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "refresh-area.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_refresh_area_453bce",
                    "--defsym=audio_uart_display_lv_root=0x2006f548",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, mode, fmt, draw_size, divisor, callback, busy,
            allocation_ok=True):
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

        def write(address, value):
            cpu.mem_write(address, struct.pack("<I", value))

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def area(address):
            return struct.unpack("<4i", cpu.mem_read(address, 16))

        def tag(address):
            if CHILDREN <= address < CHILDREN + 0x400:
                return ("child", (address - CHILDREN) // 0x58,
                        (address - CHILDREN) % 0x58)
            if LAYER <= address < LAYER + 0x100:
                return ("layer", address - LAYER)
            if DISPLAY <= address < DISPLAY + 0x400:
                return ("display", address - DISPLAY)
            if address == AREA:
                return ("input", 0)
            if address >= 0x200fe000:
                return ("stack",)
            return ("addr", address)

        write(ROOT_RAM + 0x10, DISPLAY)
        write(DISPLAY + 0x24, DRAW)
        write(DISPLAY + 0x2ac, LAYER)
        write(DISPLAY + 0x2b4, CALLBACK | 1 if callback else 0)
        write(DISPLAY + 0x38, divisor << 17)
        cpu.mem_write(DISPLAY + 0x39, bytes((mode,)))
        write(DRAW + 8, 0x1234abcd)
        write(DRAW + 0xc, draw_size)
        cpu.mem_write(LAYER + 0x14, bytes((fmt,)))
        cpu.mem_write(AREA, struct.pack("<4i", 2, 4, 3, 7))
        cpu.reg_write(A.UC_ARM_REG_R0, AREA)
        cpu.reg_write(A.UC_ARM_REG_R1, 0x55)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done, waits = [], [False], [0]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2, r3 = (machine.reg_read(x) for x in
                               (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if pc == 0x439c04:
                events.append(("copy", tag(r0), tag(r1), r2, area(r1)))
                machine.mem_write(r0, bytes(machine.mem_read(r1, r2)))
            elif pc == 0x453b78:
                events.append(("reshape", tag(r0), r1, area(r0 + 4)))
            elif pc == 0x44fa7e:
                events.append(("width", tag(r0)))
                machine.reg_write(A.UC_ARM_REG_R0, 20)
            elif pc == 0x44faa8:
                events.append(("height", tag(r0)))
                machine.reg_write(A.UC_ARM_REG_R0, 10)
            elif pc == 0x4515a4:
                events.append(("area_height", tag(r0), area(r0)))
                machine.reg_write(A.UC_ARM_REG_R0, area(r0)[3] - area(r0)[1] + 1)
            elif pc == 0x450b80:
                events.append(("area_size", tag(r0), area(r0)))
                a = area(r0)
                machine.reg_write(A.UC_ARM_REG_R0, (a[2] - a[0] + 1) * (a[3] - a[1] + 1))
            elif pc == 0x440f44:
                events.append(("bpp", r0))
                machine.reg_write(A.UC_ARM_REG_R0, 16)
            elif pc == 0x44f718:
                events.append(("alloc", r0))
                machine.reg_write(A.UC_ARM_REG_R0, CHILDREN if allocation_ok else 0)
            elif pc == 0x44f758:
                events.append(("free", tag(r0)))
            elif pc == 0x450b5c:
                fifth = word(machine.reg_read(A.UC_ARM_REG_SP))
                events.append(("area_set", r1, r2, r3, fifth))
                machine.mem_write(r0, struct.pack("<4I", r1, r2, r3, fifth))
            elif pc == 0x4847c4:
                events.append(("init", tag(r0), r1, r2, area(r3)))
                for offset in (4, 0x18, 0x28):
                    machine.mem_write(r0 + offset, bytes(machine.mem_read(r3, 16)))
                machine.mem_write(r0 + 0x14, bytes((r2 & 255,)))
                write(r0 + 0x44, 1 if busy else 0)
            elif pc == 0x453e10:
                events.append(("render", tag(r0), area(r0 + 4), word(r0)))
            elif pc == 0x484622:
                events.append(("wait",))
                waits[0] += 1
                for i in range(4):
                    write(CHILDREN + i * 0x58 + 0x44, 0)
            elif pc == 0x484548:
                events.append(("tasks",))
            elif pc == CALLBACK:
                events.append(("callback", tag(r0), tag(r1)))
            elif pc == 0x44d25c:
                def cstr(address):
                    return bytes(machine.mem_read(address, 128)).split(b"\0")[0].decode()
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                words = struct.unpack("<III", machine.mem_read(sp, 12))
                events.append(("assert", r0, cstr(r1), r2, cstr(r3),
                               *(cstr(address) for address in words)))
                done[0] = True
                machine.emu_stop()
                return
            else:
                return
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x453bce if native else symbols["audio_uart_lv_refresh_area_453bce"]
        cpu.emu_start(entry | 1, 0, count=20000)
        if not done[0]:
            raise RuntimeError(f"refresh area did not return: {native} {(mode,fmt,draw_size,divisor,callback,busy)}")
        return (events, area(DISPLAY + 0x30c), area(LAYER + 4),
                area(LAYER + 0x18), area(LAYER + 0x28), word(LAYER + 0x40))

    cases = list(itertools.product((0, 1, 2, 3), (7, 11),
                                   (8, 20), (1, 2), (False, True), (False, True)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"refresh area mismatch {case}: {stock} != {compiled}")
    failure_cases = [(mode, 11, 8, 1, callback, False)
                     for mode in (0, 1, 2, 3) for callback in (False, True)]
    for case in failure_cases:
        stock, compiled = run(True, *case, False), run(False, *case, False)
        if stock != compiled:
            raise RuntimeError(f"refresh area failure mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_REFRESH_AREA_453BCE_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "cases": len(cases) + len(failure_cases),
              "success_cases": len(cases), "failure_cases": len(failure_cases),
              "native_body": "0x453bce..0x453e10 through return or allocation assertion log",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Memcpy, allocation, reshape, rendering, task waits and callbacks are controlled lower calls.",
                         "Failure cases stop at the assertion log; the deliberate fault loop and actual render scheduling remain separate gates."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(path.read_bytes()))


if __name__ == "__main__":
    main()

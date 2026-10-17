#!/usr/bin/env python3
"""Compare stock/C LVGL render-layer pass call order and clear area."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_render_layer_453e10.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-render-layer-453e10"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROOT_RAM, DISPLAY, LAYER, DRAW = 0x2006f548, 0x20010000, 0x20011000, 0x20012000
ACTIVE, PREVIOUS, BOTTOM, TOP, SYSTEM = (0x20020000, 0x20021000,
                                         0x20022000, 0x20023000, 0x20024000)
ACTIVE_COVER, PREVIOUS_COVER = 0x20020100, 0x20021100
LOWERS = {
    "audio_uart_lv_display_pre_refresh_454692": 0x454692,
    "audio_uart_lv_color_has_alpha_440fc4": 0x440fc4,
    "audio_uart_display_area_copy_439c04": 0x439c04,
    "audio_uart_ambiq_area_move_450bb2": 0x450bb2,
    "audio_uart_lv_draw_buf_clear_48ac40": 0x48ac40,
    "audio_uart_display_active_screen_get": 0x44fc62,
    "audio_uart_lv_display_bottom_layer_44fd38": 0x44fd38,
    "audio_uart_lv_display_top_layer_44fcbe": 0x44fcbe,
    "audio_uart_lv_display_system_layer_44fcfc": 0x44fcfc,
    "audio_uart_lv_render_find_cover_453f2e": 0x453f2e,
    "audio_uart_lv_render_object_chain_453fce": 0x453fce,
    "audio_uart_lvgl_log": 0x44d25c,
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "render-layer.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_render_layer_453e10",
                    "--defsym=audio_uart_display_lv_root=0x2006f548",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, alpha, previous, cover_active, cover_previous, reverse,
            second_buffer, null_reset=False):
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

        write(ROOT_RAM + 0x10, DISPLAY)
        write(DISPLAY + 0x20, DRAW if second_buffer else 0)
        write(DISPLAY + 0x2c4, ACTIVE)
        write(DISPLAY + 0x2cc, PREVIOUS if previous else 0)
        write(DISPLAY + 0x2c8, BOTTOM)
        write(DISPLAY + 0x2c0, TOP)
        write(DISPLAY + 0x2bc, SYSTEM)
        cpu.mem_write(DISPLAY + 0x2d8, bytes((1 if reverse else 0,)))
        cpu.mem_write(DISPLAY + 0x3c, bytes((7 if alpha else 11,)))
        cpu.mem_write(LAYER, bytes((0,)) * 0x58)
        write(LAYER, DRAW)
        cpu.mem_write(LAYER + 4, struct.pack("<4i", 3, 5, 13, 15))
        cpu.mem_write(LAYER + 0x18, struct.pack("<4i", 5, 7, 17, 19))
        write(LAYER + 0x39, 0xaabbccdd)
        cpu.reg_write(A.UC_ARM_REG_R0, 0 if null_reset else LAYER)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2 = (machine.reg_read(x) for x in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if pc == 0x454692:
                events.append(("pre", r0))
            elif pc == 0x440fc4:
                events.append(("alpha", r0))
                machine.reg_write(A.UC_ARM_REG_R0, 1 if alpha else 0)
            elif pc == 0x439c04:
                events.append(("copy", r1, r2, area(r1)))
                machine.mem_write(r0, bytes(machine.mem_read(r1, r2)))
            elif pc == 0x450bb2:
                events.append(("move", area(r0), struct.unpack("<i", struct.pack("<I", r1))[0],
                               struct.unpack("<i", struct.pack("<I", r2))[0]))
                a = area(r0)
                machine.mem_write(r0, struct.pack("<4I", *(n & 0xffffffff for n in
                    (a[0] + r1, a[1] + r2, a[2] + r1, a[3] + r2))))
            elif pc == 0x48ac40:
                events.append(("clear", r0, area(r1)))
            elif pc == 0x44fc62:
                events.append(("active", r0))
                machine.reg_write(A.UC_ARM_REG_R0, ACTIVE)
            elif pc == 0x44fd38:
                events.append(("bottom", r0))
                machine.reg_write(A.UC_ARM_REG_R0, BOTTOM)
            elif pc == 0x44fcbe:
                events.append(("top", r0))
                machine.reg_write(A.UC_ARM_REG_R0, TOP)
            elif pc == 0x44fcfc:
                events.append(("system", r0))
                machine.reg_write(A.UC_ARM_REG_R0, SYSTEM)
            elif pc == 0x453f2e:
                events.append(("find", r1, area(r0)))
                result = ACTIVE_COVER if r1 == ACTIVE and cover_active else (
                    PREVIOUS_COVER if r1 == PREVIOUS and cover_previous else 0)
                machine.reg_write(A.UC_ARM_REG_R0, result)
            elif pc == 0x453fce:
                events.append(("render", r0, r1))
            elif pc == 0x44d25c:
                def cstr(address):
                    return bytes(machine.mem_read(address, 128)).split(b"\0")[0].decode()
                r3 = machine.reg_read(A.UC_ARM_REG_R3)
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
        entry = (0x48471a if native else
                 symbols["audio_uart_lv_render_layer_reset_48471a"]) if null_reset else (
                 0x453e10 if native else symbols["audio_uart_lv_render_layer_453e10"])
        cpu.emu_start(entry | 1, 0, count=4000)
        assert done[0], (native, events)
        return events, word(LAYER + 0x38), word(LAYER + 0x39)

    cases = list(itertools.product((False, True), repeat=6))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"render layer mismatch {case}: {stock} != {compiled}")
    null_case = (False,) * 6
    stock, compiled = run(True, *null_case, True), run(False, *null_case, True)
    if stock != compiled:
        raise RuntimeError(f"render reset null mismatch: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_RENDER_LAYER_453E10_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases) + 1,
              "native_body": "0x453e10..0x453f2e plus 0x48471a..0x48475e",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Cover finder, object renderer, pre-refresh, buffer clear and display getters are controlled lower calls.",
                         "Null-layer reset stops at assertion log; deliberate fault loop is not executed."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(path.read_bytes()))


if __name__ == "__main__":
    main()

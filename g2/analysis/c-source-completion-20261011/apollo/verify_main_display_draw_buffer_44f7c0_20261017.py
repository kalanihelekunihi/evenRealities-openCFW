#!/usr/bin/env python3
"""Compare the stock LVGL display constructor with C under controlled callees."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_draw_buffer_44f7c0.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-draw-buffer-44f7c0"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROOT_RAM = 0x2006f548
DESC, LAYER, TIMER, THEME = 0x20010000, 0x20011000, 0x20012000, 0x20013000
LOWERS = {
    "audio_uart_lv_list_prepend_482b12": (0x482b12, "list"),
    "audio_uart_lv_malloc": (0x44f718, "malloc"),
    "audio_uart_lv_tick": (0x473482, "tick"),
    "audio_uart_lv_array_init_482b00": (0x482b00, "array"),
    "audio_uart_lv_timer_create_464466": (0x464466, "timer"),
    "audio_uart_page_instance_ready_48716c": (0x48716c, "ready"),
    "audio_uart_page_488290": (0x488290, "color"),
    "audio_uart_page_487022": (0x487022, "theme"),
    "audio_uart_page_43de82": (0x43de82, "object"),
    "audio_uart_lv_theme_refresh_44bc3a": (0x44bc3a, "refresh"),
    "audio_uart_page_43dfa4": (0x43dfa4, "flags"),
    "audio_uart_page_44e368": (0x44e368, "layout"),
    "audio_uart_page_invalidate_440656": (0x440656, "invalidate"),
    "audio_uart_lv_event_add_4500e4": (0x44fd80, "event"),
    "audio_uart_page_event_code_450286": (0x450286, "event_code"),
    "audio_uart_lv_timer_resume_46453e": (0x46453e, "resume"),
    "audio_uart_lvgl_log": (0x44d25c, "log"),
}
NATIVE_ONLY = {0x44f7b4: "zero_desc", 0x4846de: "init_layer",
               0x464574: "timer_update"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "draw-buffer.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    definitions = {name: address for name, (address, _) in LOWERS.items()}
    definitions.update(audio_uart_display_lv_root=ROOT_RAM,
                       audio_uart_display_lv_state=ROOT_RAM,
                       audio_uart_display_page_style=0x755610,
                       audio_uart_display_tick_45360c=0x45360c)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_display_draw_buffer",
                    *(f"--defsym={name}=0x{address:x}" for name, address in definitions.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, width, height, previous):
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
        cpu.mem_write(DESC, b"\xa5" * 0x31c)
        cpu.mem_write(LAYER, b"\xa5" * 0x58)
        cpu.mem_write(TIMER, struct.pack("<II", 100, 0))
        cpu.mem_write(ROOT_RAM + 0x14, struct.pack("<I", previous))
        sp = 0x200ff000
        for reg, value in ((A.UC_ARM_REG_R0, width), (A.UC_ARM_REG_R1, height),
                           (A.UC_ARM_REG_SP, sp), (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        kinds = {address: name for address, name in LOWERS.values()}
        if native:
            kinds.update(NATIVE_ONLY)
        events, done, objects = [], [False], [0]

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def write(address, value):
            cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = kinds.get(pc)
            if kind is None:
                return
            r0, r1, r2, r3 = (machine.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if kind == "zero_desc":
                machine.mem_write(r0, bytes(r1))
            elif kind == "init_layer":
                machine.mem_write(r0, bytes(0x58))
                machine.mem_write(r0 + 0x38, b"\xff")
            elif kind == "timer_update":
                write(r0 + 4, 0x1234 - word(r0) - 1)
            elif kind == "list":
                machine.reg_write(A.UC_ARM_REG_R0, DESC)
                events.append((kind, r0))
            elif kind == "malloc":
                machine.reg_write(A.UC_ARM_REG_R0, LAYER)
                events.append((kind, r0))
            elif kind == "tick":
                machine.reg_write(A.UC_ARM_REG_R0, 0x1234)
            elif kind == "array":
                write(r0, (r1 + 3) & ~3)
                write(r0 + 4, 0)
                write(r0 + 8, 0)
                events.append((kind, r0, r1))
            elif kind == "timer":
                machine.reg_write(A.UC_ARM_REG_R0, TIMER)
                events.append((kind, r1, r2))
            elif kind == "ready":
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind == "color":
                machine.reg_write(A.UC_ARM_REG_R0, 0x112233 if r0 else 0x445566)
                events.append((kind, r0))
            elif kind == "theme":
                machine.reg_write(A.UC_ARM_REG_R0, THEME)
                events.append((kind, r0, r1, r2, r3, word(machine.reg_read(A.UC_ARM_REG_SP))))
            elif kind == "object":
                machine.reg_write(A.UC_ARM_REG_R0, 0x20014000 + objects[0] * 0x100)
                objects[0] += 1
                events.append((kind, r0))
            elif kind in ("refresh", "flags", "layout", "invalidate"):
                events.append((kind, r0, r1 if kind in ("flags", "layout") else None))
            elif kind == "event":
                # Stock enters the tiny 0x44fd80 wrapper with a display;
                # the C provider calls its existing event-add callee directly.
                events.append((kind, r0 + 0x2e4 if native else r0, r2, r3))
            elif kind == "log":
                raise AssertionError("unexpected stock/C log")
            else:
                raise AssertionError(kind)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x44f7c0 if native else symbols["audio_uart_display_draw_buffer"]
        cpu.emu_start(entry | 1, 0, count=4000)
        if not done[0]:
            raise RuntimeError(f"draw-buffer did not return: {native} {width} {height}")
        return (cpu.reg_read(A.UC_ARM_REG_R0),
                bytes(cpu.mem_read(DESC, 0x31c)), bytes(cpu.mem_read(LAYER, 0x58)),
                word(ROOT_RAM + 0x14), bytes(cpu.mem_read(TIMER, 8)), events)

    cases = [(w, h, p) for w in (0, 1, 0x240, 0xffffffff)
             for h in (0, 1, 0x120, 0xffffffff)
             for p in (0, 0x20018000)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"draw-buffer mismatch {case}: {stock[0],stock[3:]} != {compiled[0],compiled[3:]}")
    receipt = {"status": "PASS_DIRECT_MAIN_DISPLAY_DRAW_BUFFER_44F7C0_C",
               "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
               "native_body": "0x44f7c0..0x44fa18",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
               "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path.read_bytes()),
               "source_complete": False, "flashable": False, "hardware_proof": False,
               "limits": ["Successful allocation path only; allocation, tick, timer, page and event callees are controlled.",
                          "The refresh timer callback at 0x45360c remains an unresolved source body."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()

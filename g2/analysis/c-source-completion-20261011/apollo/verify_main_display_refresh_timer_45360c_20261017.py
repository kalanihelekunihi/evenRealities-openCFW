#!/usr/bin/env python3
"""Compare the stock LVGL refresh timer and C body under controlled callees."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_refresh_timer_45360c.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-refresh-timer-45360c"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROOT_RAM, DISPLAY, TIMER, DRAW, NODE = 0x2006f548, 0x20010000, 0x20011000, 0x20012000, 0x20013000
LOWERS = {
    "audio_uart_display_current_44fa1a": (0x44fa1a, "current"),
    "audio_uart_lv_timer_pause": (0x46450c, "pause"),
    "audio_uart_lv_display_event_44fdbe": (0x44fdbe, "event"),
    "audio_uart_page_43f66c": (0x43f66c, "refresh"),
    "audio_uart_lv_refresh_collect_45377a": (0x45377a, "collect"),
    "audio_uart_lv_refresh_layout_45383c": (0x45383c, "layout"),
    "audio_uart_lv_refresh_render_4539b6": (0x4539b6, "render"),
    "audio_uart_font_path_node_append": (0x482bca, "append"),
    "audio_uart_display_area_copy_439c04": (0x439c04, "copy"),
    "audio_uart_lvgl_log": (0x44d25c, "log"),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "refresh-timer.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_display_tick_45360c",
                    "--defsym=audio_uart_display_lv_root=0x2006f548",
                    *(f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, case):
        use_timer, display_valid, draw_valid, panel_valid, count, flush, mode = case
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
            cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        write(TIMER + 0xc, DISPLAY if display_valid else 0)
        write(DISPLAY + 0x24, DRAW if draw_valid else 0)
        write(DRAW + 0x10, 0x2001a000 if draw_valid else 0)
        write(DRAW + 0xc, 0x2001b000 if draw_valid else 0)
        for offset, address in ((0x2c4, 0x20018000 if panel_valid else 0),
                                (0x2cc, 0x20018100), (0x2c8, 0x20018200),
                                (0x2c0, 0x20018300), (0x2bc, 0x20018400)):
            write(DISPLAY + offset, address)
        write(DISPLAY + 0x260, count)
        write(DISPLAY + 0x20, flush)
        cpu.mem_write(DISPLAY + 0x39, bytes((mode,)))
        cpu.mem_write(DISPLAY + 0x40, bytes(range(256)) * 2)
        cpu.mem_write(DISPLAY + 0x240, bytes((0, 1, 0, 1)) + bytes(28))
        sp = 0x200ff000
        for reg, value in ((A.UC_ARM_REG_R0, TIMER if use_timer else 0),
                           (A.UC_ARM_REG_SP, sp), (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        kinds = {address: name for address, name in LOWERS.values()}
        if native:
            kinds[0x45310e] = "clear"
        events, done, nodes = [], [False], [0]

        def cstr(address):
            return bytes(cpu.mem_read(address, 130)).split(b"\0", 1)[0].decode("utf-8", "replace")

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
            if kind == "current":
                machine.reg_write(A.UC_ARM_REG_R0, DISPLAY if display_valid else 0)
                events.append((kind,))
            elif kind == "pause":
                events.append((kind, r0))
            elif kind == "event":
                events.append((kind, r0, r1, r2))
                machine.reg_write(A.UC_ARM_REG_R0, 1)
            elif kind == "refresh":
                events.append((kind, r0))
            elif kind in ("collect", "layout", "render"):
                events.append((kind,))
            elif kind == "append":
                address = NODE + 0x20 * nodes[0]
                nodes[0] += 1
                machine.reg_write(A.UC_ARM_REG_R0, address)
                events.append((kind, r0))
            elif kind == "copy":
                machine.mem_write(r0, bytes(machine.mem_read(r1, r2)))
                events.append((kind, r0, r1, r2))
            elif kind == "clear":
                machine.mem_write(r0, bytes(r1))
            elif kind == "log":
                events.append((kind, r0, cstr(r1), r2, cstr(r3),
                               cstr(word(machine.reg_read(A.UC_ARM_REG_SP)))))
            else:
                raise AssertionError(kind)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x45360c if native else symbols["audio_uart_display_tick_45360c"]
        cpu.emu_start(entry | 1, 0, count=10000)
        if not done[0]:
            raise RuntimeError(f"refresh timer did not return: {native} {case}")
        return (word(ROOT_RAM + 0x10), word(DISPLAY + 0x260),
                bytes(cpu.mem_read(DISPLAY + 0x40, 0x220)),
                bytes(cpu.mem_read(NODE, 0x80)), events)

    cases = [(timer, display, draw, panel, count, flush, mode)
             for timer in (False, True) for display in (False, True)
             for draw in (False, True) for panel in (False, True)
             for count in (0, 2) for flush in (0, 1) for mode in (0, 1)]
    for case in cases:
        stock, compiled = run(True, case), run(False, case)
        if stock != compiled:
            raise RuntimeError(f"refresh timer mismatch {case}: {stock[1],stock[4]} != {compiled[1],compiled[4]}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_REFRESH_TIMER_45360C_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x45360c..0x453778", "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()), "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Refresh child passes, events, page refresh and list append are controlled callees.",
                         "Nested refresh collectors at 0x45377a, 0x45383c and 0x4539b6 remain unresolved."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()

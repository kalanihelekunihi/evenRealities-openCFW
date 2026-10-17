#!/usr/bin/env python3
"""Compare stock/C LVGL flush state, waits, events and driver callback."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_refresh_flush_454574.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-refresh-flush-454574"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROOT_RAM, DISPLAY, LAYER, DRAW = 0x2006f548, 0x20010000, 0x20011000, 0x20012000
CALLBACK, DATA, FIRST, SECOND = 0x101800, 0x20013000, 0x20014000, 0x20015000
LOWERS = {
    "audio_uart_lv_thread_sync_wait_4d46e8": 0x4d46e8,
    "audio_uart_lv_refresh_tasks_484548": 0x484548,
    "audio_uart_lv_display_pre_refresh_454692": 0x454692,
    "audio_uart_lv_display_event_44fdbe": 0x44fdbe,
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "refresh-flush.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_display_flush_454574",
                    "--defsym=audio_uart_display_lv_root=0x2006f548",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, busy, second, callback, flags, mode, selected_second):
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

        write(ROOT_RAM + 0x10, DISPLAY)
        write(DISPLAY + 0x2ac, LAYER)
        write(LAYER + 0x44, 1 if busy else 0)
        write(LAYER, DRAW)
        write(DRAW + 0x10, DATA)
        write(DISPLAY + 0x10, 10)
        write(DISPLAY + 0x14, 20)
        write(DISPLAY + 0x1c, FIRST)
        write(DISPLAY + 0x20, SECOND if second else 0)
        write(DISPLAY + 0x24, SECOND if selected_second else FIRST)
        write(DISPLAY + 0x28, CALLBACK | 1 if callback else 0)
        write(DISPLAY + 0x38, flags)
        cpu.mem_write(DISPLAY + 0x39, bytes((mode,)))
        cpu.mem_write(DISPLAY + 0x30c, struct.pack("<4i", 1, 2, 4, 5))
        cpu.reg_write(A.UC_ARM_REG_R0, DISPLAY)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def area(address):
            return struct.unpack("<4i", cpu.mem_read(address, 16))

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2 = (machine.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if pc == 0x4d46e8:
                events.append(("wait", r0))
                write(LAYER + 0x44, 0)
            elif pc == 0x484548:
                events.append(("tasks",))
            elif pc == 0x454692:
                events.append(("pre", r0))
            elif pc == 0x44fdbe:
                events.append(("event", r1, area(r2)))
                machine.reg_write(A.UC_ARM_REG_R0, 1)
            elif pc == CALLBACK:
                events.append(("callback", r0, area(r1), r2))
            else:
                return
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x454574 if native else symbols["audio_uart_lv_display_flush_454574"]
        cpu.emu_start(entry | 1, 0, count=4000)
        if not done[0]:
            raise RuntimeError(f"refresh flush did not return: {native} {(busy,second,callback,flags,mode,selected_second)}")
        return (word(DISPLAY + 0x24), word(DISPLAY + 0x30),
                word(DISPLAY + 0x34), word(LAYER + 0x44), events)

    cases = list(itertools.product((False, True), (False, True), (False, True),
                                   (0, 1, 2, 3), (0, 1, 2), (False, True)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"refresh flush mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_REFRESH_FLUSH_454574_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x454574..0x454610 plus 0x454648..0x454690",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Thread wait, refresh tasks, pre-refresh, event and driver callback are controlled lower calls.",
                         "Busy 0/1, dual-buffer 0/1, callback 0/1, flag 0-3 and modes 0-2 are covered."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()

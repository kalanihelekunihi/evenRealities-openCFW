#!/usr/bin/env python3
"""Direct stock/C replay of exit-prompt sender, logs, RAM writes and dispatch."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_message_send_58bfb2.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-ui-message-send-58bfb2"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_log_flags": (0x101010, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101020, 0x43d574, "extended"),
    "compressed_log_output": (0x101030, 0x43ce9e, "compact"),
    "audio_uart_lv_style_unlink_450500": (0x101040, 0x450500, "unlink"),
    "audio_conversate_exit_prompt_prepare_58bda8": (0x101050, 0x58bda8, "prepare"),
    "audio_conversate_exit_prompt_show_58bf12": (0x101060, 0x58bf12, "show"),
    "audio_terminal_fade_out_58c426": (0x101070, 0x58c426, "fade"),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_message_send_58bfb2",
                    "--section-start=.g2_conversate_exit_prompt_state_200745d0=0x200745d0",
                    "--section-start=.g2_conversate_exit_prompt_hold_20000be4=0x20000be4",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    assert symbols["audio_conversate_exit_prompt_state_200745d0"] == 0x200745d0
    assert symbols["audio_conversate_exit_prompt_hold_20000be4"] == 0x20000be4

    def run(native, app, message, event, animated, hold, flags):
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
        cpu.mem_write(0x200745d0, struct.pack("<III", 0xaaaa, 0xbbbb, 0xcccc))
        cpu.mem_write(0x20000be4, struct.pack("<I", 0xdddd))
        cpu.reg_write(A.UC_ARM_REG_R0, app)
        cpu.reg_write(A.UC_ARM_REG_R1, message)
        cpu.reg_write(A.UC_ARM_REG_R2, event)
        cpu.reg_write(A.UC_ARM_REG_R3, animated)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.mem_write(0x200ff000, struct.pack("<I", hold))
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def cstr(machine, pointer):
            return bytes(machine.mem_read(pointer, 170)).split(b"\0", 1)[0]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None:
                return
            r = [machine.reg_read(reg) for reg in (A.UC_ARM_REG_R0,
                 A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                line, fmt = struct.unpack("<II", machine.mem_read(sp, 8))
                tail = () if line == 0x50 else struct.unpack("<III", machine.mem_read(sp + 8, 12))
                events.append((kind, r[0], cstr(machine, r[1]),
                               cstr(machine, r[2]), cstr(machine, r[3]),
                               line, cstr(machine, fmt), *tail))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind == "compact":
                tail = () if r[0] == 0x04000000 else (r[3], *struct.unpack("<II", machine.mem_read(sp, 8)))
                events.append((kind, r[0], cstr(machine, r[1]),
                               cstr(machine, r[2]), *tail))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind == "fade":
                callback = "show" if r[2] in (0x58bf13, 0x101061) else hex(r[2])
                events.append((kind, r[0], r[1], callback))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind in ("prepare", "show"):
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            else:
                events.append((kind, r[0], r[1]))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x58bfb2 if native else symbols["audio_conversate_ui_message_send_58bfb2"]
        cpu.emu_start(entry | 1, 0, count=300)
        if not done[0]:
            raise RuntimeError("message sender did not return")
        return (events, cpu.reg_read(A.UC_ARM_REG_R0),
                bytes(cpu.mem_read(0x200745d0, 12)),
                bytes(cpu.mem_read(0x20000be4, 4)))

    cases = [(app, msg, event, animated, hold, flags)
             for app in (0, 1, 0x20001000)
             for msg in (0, 0x20002000)
             for event in (0, 11)
             for animated in (0, 1, 256)
             for hold in (0, 1000)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"message sender mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_UI_MESSAGE_SEND_58BFB2_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x58bfb2..0x58c0b5",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "ram_cells": {"state": "0x200745d0..0x200745db", "hold": "0x20000be4..0x20000be7"},
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Log transport, LVGL unlink, prompt prepare/show and fade-out are controlled lower boundaries.",
                         "RAM placement is proven only in the isolated oracle link."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()

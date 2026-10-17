#!/usr/bin/env python3
"""Compare session-switch event and root-hide leaves with stock Apollo."""
import hashlib
import itertools
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_switch_helpers_20261016.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-switch-result-5ed758"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    obj = OUT / "switch-helpers-oracle.o"
    elf = OUT / "switch-helpers-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    "--defsym=audio_terminal_ui_state_base=0x2006e0d0",
                    "--defsym=audio_terminal_ui_event_5e5484=0x5e5485",
                    "--defsym=audio_uart_page_43dfa4=0x43dfa5",
                    str(obj), "-o", str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open("rb") as f:
        e = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   e.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, kind, value):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(0x2006e0d0, struct.pack("<I", value))
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, value)
        trace = []

        def hook(cpu, pc, size, _):
            if pc not in (0x5e5484, 0x43dfa4):
                return
            count = 3 if pc == 0x5e5484 else 2
            trace.append((pc, *(cpu.reg_read(r) for r in
                                (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                 A.UC_ARM_REG_R2)[:count])))
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        if kind == "event":
            native, symbol = 0x5ed1ec, "audio_terminal_session_switch_event_5ed1ec"
        else:
            native, symbol = 0x5ed1d6, "audio_terminal_session_root_hide_5ed1d6"
        u.emu_start((symbols[symbol] if compiled else native) | 1,
                    0x600000, count=70)
        return trace

    cases = 0
    for kind, value in itertools.product(("event", "hide"),
                                         (0, 1, 0xffff, 0x20090000, 0xffffffff)):
        stock, candidate = run(False, kind, value), run(True, kind, value)
        if stock != candidate:
            raise RuntimeError(f"session-switch helper mismatch {kind} {value}: {stock!r} {candidate!r}")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_SWITCH_HELPERS_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf),
               "cases": cases, "scope": "Event 4/session/0 forwarding and conditional root-hide call",
               "limits": ["Lower event and LVGL effects are isolated; full image and hardware remain open."]}
    path = OUT / "helpers-oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

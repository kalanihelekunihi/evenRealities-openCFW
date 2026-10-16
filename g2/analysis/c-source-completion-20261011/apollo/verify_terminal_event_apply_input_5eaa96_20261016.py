#!/usr/bin/env python3
"""Bounded stock comparison for Terminal input application 0x5eaa96."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_event_apply_input_5eaa96.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-event-apply-input-5eaa96"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void audio_terminal_event_refresh_view_5ea992(void){}
void audio_terminal_display_status_44ea04(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_terminal_view_position_5ea926(uint32_t a){(void)a;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "apply-input-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "apply-input-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_event_apply_input_5eaa96",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    names = ("audio_terminal_event_refresh_view_5ea992", "audio_terminal_display_status_44ea04",
             "audio_terminal_view_position_5ea926")
    stock_addresses = (0x5ea992, 0x44ea04, 0x5ea926)

    def run(compiled, input_kind, root, flag, position):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes((0x5a,)) * 0x2a0)
        u.mem_write(state + 4, struct.pack("<I", root))
        input_addr = 0 if input_kind == 0 else 0x20003000
        u.mem_write(0x20003000, bytes((1 if input_kind == 2 else 0, flag, 0, 0)) +
                    struct.pack("<I", position))
        cuts = {(symbols[name] if compiled else address) & ~1: index
                for index, (name, address) in enumerate(zip(names, stock_addresses))}
        trace = []
        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            args = tuple(cpu.reg_read(reg) for reg in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            trace.append((index, () if index == 0 else args[:1] if index == 2 else args))
            cpu.reg_write(A.UC_ARM_REG_R0, 0xdeadbeef)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, input_addr)
        entry = symbols["audio_terminal_event_apply_input_5eaa96"] if compiled else 0x5eaa96
        u.emu_start(entry | 1, 0x600000, count=10000)
        return bytes(u.mem_read(state, 0x2a0)), trace

    cases = 0
    for input_kind in (0, 1, 2):
        for root in (0, 0x20002000):
            for flag in (0, 1, 0xff):
                for position in (0, 0x12345678):
                    stock = run(False, input_kind, root, flag, position)
                    selected = run(True, input_kind, root, flag, position)
                    if stock != selected:
                        raise RuntimeError(f"apply-input mismatch {input_kind=} {root=} "
                                           f"{flag=} {position=}: {stock[1]} vs {selected[1]}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_EVENT_APPLY_INPUT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "input/root guards, flag state write and lower-call trace",
              "limits": ["View-refresh and display child effects and shared RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

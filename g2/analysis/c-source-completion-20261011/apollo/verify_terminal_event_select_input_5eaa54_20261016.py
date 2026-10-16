#!/usr/bin/env python3
"""Bounded stock comparison for Terminal input selector 0x5eaa54."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_event_select_input_5eaa54.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-event-select-input-5eaa54"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
uint32_t audio_uart_lv_obj_y_44e498(uint32_t a){(void)a;return 0;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "select-input-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "select-input-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_event_select_input_5eaa54",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, input_kind, outputs, root, flag):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state + 4, struct.pack("<I", root))
        u.mem_write(state + 0x28c, bytes((flag,)))
        input_addr = 0 if input_kind == 0 else 0x20003000
        u.mem_write(0x20003000, bytes((1 if input_kind == 2 else 0, 7, 0, 0)) +
                    struct.pack("<I", 0x12345678))
        u.mem_write(0x20004000, b"\xaa" * 8)
        calls = []
        cut = (symbols["audio_uart_lv_obj_y_44e498"] if compiled else 0x44e498) & ~1
        def hook(cpu, pc, size, _):
            if pc == cut:
                calls.append(cpu.reg_read(A.UC_ARM_REG_R0))
                cpu.reg_write(A.UC_ARM_REG_R0, 0x3456)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, input_addr)
        u.reg_write(A.UC_ARM_REG_R1, 0x20004000 if outputs else 0)
        u.reg_write(A.UC_ARM_REG_R2, 0x20004004 if outputs else 0)
        entry = symbols["audio_terminal_event_select_input_5eaa54"] if compiled else 0x5eaa54
        u.emu_start(entry | 1, 0x600000, count=10000)
        return bytes(u.mem_read(0x20004000, 8)), calls

    cases = 0
    for input_kind in (0, 1, 2):
        for outputs in (False, True):
            for root in (0, 0x20002000):
                for flag in (0, 1, 0xff):
                    stock = run(False, input_kind, outputs, root, flag)
                    selected = run(True, input_kind, outputs, root, flag)
                    if stock != selected:
                        raise RuntimeError(f"input-selector mismatch {input_kind=} {outputs=} "
                                           f"{root=} {flag=}: {stock} vs {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_EVENT_SELECT_INPUT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "input/output pointer guards, stock values and lower-call trace",
              "limits": ["LVGL scroll child effect and shared RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

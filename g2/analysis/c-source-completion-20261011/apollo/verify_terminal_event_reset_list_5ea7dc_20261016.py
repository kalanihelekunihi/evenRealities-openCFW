#!/usr/bin/env python3
"""Compare bounded Terminal list reset with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_event_reset_list_5ea7dc.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-event-reset-list-5ea7dc"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void audio_lv_object_flag_43ded4(uint32_t a,uint32_t b){(void)a;(void)b;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5eb28c-0x438000:0x5eb290-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Apollo stock payload or Terminal base changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "reset-list-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "reset-list-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_event_reset_list_5ea7dc",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, mask, fill):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes((fill,)) * 0x2a0)
        for index in range(12):
            val = 0x20002000 + index * 16 if mask & (1 << index) else 0
            u.mem_write(state + 0xc + index * 4, struct.pack("<I", val))
        cut = (symbols["audio_lv_object_flag_43ded4"] if compiled else 0x43ded4) & ~1
        calls = []
        def hook(cpu, pc, size, _):
            if pc == cut:
                calls.append((cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)))
                cpu.reg_write(A.UC_ARM_REG_R0, 0xdeadbeef)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_event_reset_list_5ea7dc"] if compiled else 0x5ea7dc
        u.emu_start(entry | 1, 0x600000, count=10000)
        return bytes(u.mem_read(state, 0x2a0)), calls

    masks = [0, 0xfff, 0x555, 0xaaa] + [1 << n for n in range(12)]
    cases = 0
    for mask in masks:
        for fill in (0, 0x5a, 0xff):
            if run(False, mask, fill) != run(True, mask, fill):
                raise RuntimeError(f"reset-list mismatch {mask=:#x} {fill=:#x}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_EVENT_RESET_LIST_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "12 object guards, lower-call trace and 0x2a0-byte Terminal RAM",
              "limits": ["LVGL object flag child effects and shared RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

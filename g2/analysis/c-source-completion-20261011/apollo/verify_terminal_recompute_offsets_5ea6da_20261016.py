#!/usr/bin/env python3
"""Compare Terminal offset recomputation with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_recompute_offsets_5ea6da.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-recompute-offsets-5ea6da"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
uint32_t audio_terminal_resource_597324(void){return 0;}
void audio_lv_object_size_call_43f4c0(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "offsets-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "offsets-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_recompute_offsets_5ea6da",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, resource, count, first, child, fill):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes((fill,)) * 0x2a0)
        u.mem_write(state + 8, struct.pack("<I", child))
        for i, height in enumerate((0x12, 0x34, 0x56, 0x78)):
            u.mem_write(state + 0x3c + i * 2, struct.pack("<H", height))
        u.mem_write(0x20009500, struct.pack("<H", count))
        cuts = {(symbols["audio_terminal_resource_597324"] if compiled else 0x597324) & ~1: 0,
                (symbols["audio_lv_object_size_call_43f4c0"] if compiled else 0x43f4c0) & ~1: 1}
        trace = []
        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            if index == 0:
                trace.append(("resource",))
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000 if resource else 0)
            else:
                trace.append(("size", *(cpu.reg_read(reg) for reg in
                                       (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, first)
        entry = symbols["audio_terminal_recompute_offsets_5ea6da"] if compiled else 0x5ea6da
        u.emu_start(entry | 1, 0x600000, count=10000)
        return bytes(u.mem_read(state, 0x2a0)), trace

    cases = 0
    for resource in (0, 1):
        for count in (0, 1, 2, 4):
            for first in (0, 1, 2, 5):
                for child in (0, 0x20002000):
                    for fill in (0, 0x5a):
                        stock = run(False, resource, count, first, child, fill)
                        selected = run(True, resource, count, first, child, fill)
                        if stock != selected:
                            raise RuntimeError(f"offset mismatch {resource=} {count=} "
                                               f"{first=} {child=} {fill=}: "
                                               f"{stock[1]} vs {selected[1]}")
                        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_RECOMPUTE_OFFSETS_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "resource/first/count/child guards, full 0x2a0-byte RAM and child-call trace",
              "limits": ["Counts beyond the observed 64-slot layout, LVGL size effects and placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

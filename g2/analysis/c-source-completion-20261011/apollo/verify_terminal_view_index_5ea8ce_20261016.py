#!/usr/bin/env python3
"""Bounded stock comparison for Terminal viewport start-index 0x5ea8ce."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_view_index_5ea8ce.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-view-index-5ea8ce"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint32_t audio_terminal_resource_597324(void){return 0;}
uint32_t audio_terminal_position_index_5ea868(uint32_t a){(void)a;return 0;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "view-index-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "view-index-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_view_index_5ea8ce",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, resource, count, returned):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(0x20009500, struct.pack("<H", count))
        cuts = {(symbols["audio_terminal_resource_597324"] if compiled else 0x597324) & ~1: 0,
                (symbols["audio_terminal_position_index_5ea868"] if compiled else 0x5ea868) & ~1: 1}
        trace = []
        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            trace.append((index,) if index == 0 else (index, cpu.reg_read(A.UC_ARM_REG_R0)))
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000 if resource else 0 if index == 0 else returned)
            if index == 1:
                cpu.reg_write(A.UC_ARM_REG_R0, returned)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, 0x12345678)
        entry = symbols["audio_terminal_view_index_5ea8ce"] if compiled else 0x5ea8ce
        u.emu_start(entry | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace

    cases = 0
    for resource in (0, 1):
        for count in (0, 1, 12, 13, 20, 64):
            for returned in (0, 1, 2, 3, 10, 64, 0x10003):
                stock = run(False, resource, count, returned)
                selected = run(True, resource, count, returned)
                if stock != selected:
                    raise RuntimeError(f"view-index mismatch {resource=} {count=} {returned=}: "
                                       f"{stock} vs {selected}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_VIEW_INDEX_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "resource/count guard, centered start, 12-row cap and lower-call trace",
              "limits": ["Position-index child effect and full Terminal resource placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

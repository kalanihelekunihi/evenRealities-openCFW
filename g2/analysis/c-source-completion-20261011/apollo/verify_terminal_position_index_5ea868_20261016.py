#!/usr/bin/env python3
"""Compare Terminal position binary search with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_position_index_5ea868.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-position-index-5ea868"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
uint32_t audio_terminal_resource_597324(void){return 0;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "position-index-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "position-index-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_position_index_5ea868",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, resource, count, position, layout):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes((0x5a,)) * 0x2a0)
        for index in range(64):
            offset = (index * 10 if layout == 0 else index * 10 + 5 if layout == 1
                      else (index // 2) * 10)
            u.mem_write(state + 0xbc + index * 4, struct.pack("<I", offset))
        u.mem_write(0x20009500, struct.pack("<H", count))
        cut = (symbols["audio_terminal_resource_597324"] if compiled else 0x597324) & ~1
        trace = []
        def hook(cpu, pc, size, _):
            if pc == cut:
                trace.append("resource")
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000 if resource else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, position & 0xffffffff)
        entry = symbols["audio_terminal_position_index_5ea868"] if compiled else 0x5ea868
        u.emu_start(entry | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace, bytes(u.mem_read(state, 0x2a0))

    cases = 0
    for resource in (0, 1):
        for count in (0, 1, 2, 5, 64):
            for position in (-10, -1, 0, 1, 5, 9, 10, 19, 20, 639, 1000):
                for layout in (0, 1, 2):
                    stock = run(False, resource, count, position, layout)
                    selected = run(True, resource, count, position, layout)
                    if stock != selected:
                        raise RuntimeError(f"position-index mismatch {resource=} {count=} "
                                           f"{position=} {layout=}: {stock[:2]} vs {selected[:2]}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_POSITION_INDEX_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "signed position clamp, resource/count guards and 64-slot offset search",
              "limits": ["Count above 64 and final shared RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

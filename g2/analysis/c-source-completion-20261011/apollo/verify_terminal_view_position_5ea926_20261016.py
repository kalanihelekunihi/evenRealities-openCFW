#!/usr/bin/env python3
"""Bounded stock comparison for Terminal view-position decision 0x5ea926."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_view_position_5ea926.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-view-position-5ea926"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
uint32_t audio_terminal_resource_597324(void){return 0;}
uint32_t audio_terminal_view_index_5ea8ce(uint32_t a){(void)a;return 0;}
void audio_terminal_view_select_5ea810(uint32_t a){(void)a;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "view-position-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "view-position-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_view_position_5ea926",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    names = ("audio_terminal_resource_597324", "audio_terminal_view_index_5ea8ce",
             "audio_terminal_view_select_5ea810")
    stock_addresses = (0x597324, 0x5ea8ce, 0x5ea810)

    def run(compiled, child, resource, count, flag, selected_index, new_index):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes((0x5a,)) * 0x2a0)
        u.mem_write(state + 8, struct.pack("<I", child))
        u.mem_write(state + 0x1c0, struct.pack("<H", selected_index))
        u.mem_write(state + 0x1c2, bytes((flag,)))
        u.mem_write(0x20009500, struct.pack("<H", count))
        cuts = {(symbols[name] if compiled else address) & ~1: index
                for index, (name, address) in enumerate(zip(names, stock_addresses))}
        trace = []
        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            trace.append((index,) if index == 0 else (index, r0))
            if index == 0:
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000 if resource else 0)
            elif index == 1:
                cpu.reg_write(A.UC_ARM_REG_R0, new_index)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, 0x12345678)
        entry = symbols["audio_terminal_view_position_5ea926"] if compiled else 0x5ea926
        u.emu_start(entry | 1, 0x600000, count=10000)
        return bytes(u.mem_read(state, 0x2a0)), trace

    cases = 0
    for child in (0, 0x20002000):
        for resource in (0, 1):
            for count in (0, 1, 3):
                for flag in (0, 1):
                    for selected_index in (0, 1, 0xffff):
                        for new_index in (1, 0x10001):
                            stock = run(False, child, resource, count, flag, selected_index, new_index)
                            selected = run(True, child, resource, count, flag, selected_index, new_index)
                            if stock != selected:
                                raise RuntimeError(f"view-position mismatch {child=} {resource=} "
                                                   f"{count=} {flag=} {selected_index=} "
                                                   f"{new_index=}: {stock[1]} vs {selected[1]}")
                            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_VIEW_POSITION_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "child/resource/count/selection guards, full Terminal RAM and lower-call trace",
              "limits": ["View-index/select child effects and final shared RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

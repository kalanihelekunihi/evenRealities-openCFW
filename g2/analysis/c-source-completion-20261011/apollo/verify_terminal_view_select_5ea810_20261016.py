#!/usr/bin/env python3
"""Compare Terminal 12-row view selection with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_view_select_5ea810.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-view-select-5ea810"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
uint32_t audio_terminal_resource_597324(void){return 0;}
void audio_lv_object_flag_43ded4(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_terminal_view_row_5ea768(uint32_t a,uint32_t b){(void)a;(void)b;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "view-select-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "view-select-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_view_select_5ea810",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    names = ("audio_terminal_resource_597324", "audio_lv_object_flag_43ded4",
             "audio_terminal_view_row_5ea768")
    stock_addresses = (0x597324, 0x43ded4, 0x5ea768)

    def run(compiled, resource, count, first, mask, fill):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes((fill,)) * 0x2a0)
        for slot in range(12):
            object = 0x20003000 + slot * 16 if mask & (1 << slot) else 0
            u.mem_write(state + 0xc + slot * 4, struct.pack("<I", object))
        u.mem_write(0x20009500, struct.pack("<H", count))
        cuts = {(symbols[name] if compiled else address) & ~1: index
                for index, (name, address) in enumerate(zip(names, stock_addresses))}
        trace = []
        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            r1 = cpu.reg_read(A.UC_ARM_REG_R1)
            trace.append((index,) if index == 0 else (index, r0, r1))
            if index == 0:
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000 if resource else 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, first)
        entry = symbols["audio_terminal_view_select_5ea810"] if compiled else 0x5ea810
        u.emu_start(entry | 1, 0x600000, count=10000)
        return bytes(u.mem_read(state, 0x2a0)), trace

    cases = 0
    for resource in (0, 1):
        for count in (0, 1, 5, 12, 20):
            for first in (0, 4, 0xffff):
                for mask in (0, 0xfff, 0x555, 0xaaa):
                    for fill in (0, 0x5a):
                        stock = run(False, resource, count, first, mask, fill)
                        selected = run(True, resource, count, first, mask, fill)
                        if stock != selected:
                            raise RuntimeError(f"view-select mismatch {resource=} {count=} "
                                               f"{first=} {mask=:#x} {fill=}: "
                                               f"{stock[1]} vs {selected[1]}")
                        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_VIEW_SELECT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "12 object-slot guards, count/index bounds, selection RAM and lower-call trace",
              "limits": ["LVGL object-flag and row child effects plus final RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare Terminal item text-height 0x5ea67a with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_item_height_5ea67a.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-item-height-5ea67a"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint32_t audio_uart_ring_primary_head_cell;
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
int32_t audio_terminal_item_spacing_5ea2c2(void){return 0;}
void audio_uart_page_event_calculate_489546(void*a,const char*b,const void*c,int32_t d,int32_t e,int32_t f,uint32_t g)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "item-height-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "item-height-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_item_height_5ea67a",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    names = ("audio_uart_buffer_zero", "audio_terminal_item_spacing_5ea2c2",
             "audio_uart_page_event_calculate_489546")
    stock_addresses = (0x43c0e4, 0x5ea2c2, 0x489546)

    def run(compiled, kind, font, measured_height, spacing):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_uart_ring_primary_head_cell"] if compiled else 0x200746dc
        u.mem_write(state, struct.pack("<I", 0x20004000 if font else 0))
        item = 0 if kind == 0 else 0x20003000
        u.mem_write(0x20003000, b"\x00\x00" + bytes((0x41 if kind == 2 else 0,)) + b"\x00")
        cuts = {(symbols[name] if compiled else address) & ~1: index
                for index, (name, address) in enumerate(zip(names, stock_addresses))}
        trace = []
        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            regs = tuple(cpu.reg_read(reg) for reg in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if index == 0:
                trace.append((index, regs[1:3]))
                cpu.mem_write(regs[0], bytes((regs[2] & 0xff,)) * regs[1])
            elif index == 1:
                trace.append((index,))
                cpu.reg_write(A.UC_ARM_REG_R0, spacing & 0xffffffff)
            else:
                sp = cpu.reg_read(A.UC_ARM_REG_SP)
                extra = struct.unpack("<III", bytes(cpu.mem_read(sp, 12)))
                trace.append((index, regs[1:], extra))
                cpu.mem_write(regs[0] + 4, struct.pack("<I", measured_height & 0xffffffff))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, item)
        entry = symbols["audio_terminal_item_height_5ea67a"] if compiled else 0x5ea67a
        u.emu_start(entry | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace

    cases = 0
    for kind in (0, 1, 2):
        for font in (0, 1):
            for measured_height in (-1, 0, 27, 28, 29, 55, 56, 83):
                for spacing in (0, 4):
                    stock = run(False, kind, font, measured_height, spacing)
                    selected = run(True, kind, font, measured_height, spacing)
                    if stock != selected:
                        raise RuntimeError(f"item-height mismatch {kind=} {font=} "
                                           f"{measured_height=} {spacing=}: {stock} vs {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_ITEM_HEIGHT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "item/font guards, seven-argument text-measure ABI and 28-pixel rounding",
              "limits": ["Text measurement and spacing child effects plus final RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

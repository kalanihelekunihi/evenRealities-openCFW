#!/usr/bin/env python3
"""Compare all stock LV font range modes with compiled C lookup."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_font_lookup_4b2774.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-font-lookup-4b2774"
SHIM = '''#include <stdint.h>
void *audio_uart_lv_font_pair_search_52a284(const void*k,const void*b,uint32_t n,uint32_t z,void*c){return 0;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def put16(cpu, addr, value): cpu.mem_write(addr, (value & 0xffff).to_bytes(2, "little"))
def put32(cpu, addr, value): cpu.mem_write(addr, (value & 0xffffffff).to_bytes(4, "little"))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if hashlib.sha256(blob[0x4b2774-0x438000:0x4b28ee-0x438000]).hexdigest() != \
            "c2b7461f40b74e64e4056382a8f1c7fa9c02f6d07fae9615c1228221e4763546":
        raise RuntimeError("LV glyph lookup native span changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_font_lookup_4b2774",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def cpu_new():
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000); cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for addr, data in segments: cpu.mem_write(addr, data)
            cpu.mem_map(0x20000000, 0x400000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            return cpu
        def run(compiled, mode, cp, map_value, hit, second):
            cpu = cpu_new()
            font, state, ranges = 0x20010000, 0x20012000, 0x20013000
            glyph_list, map_base = 0x20014000, 0x20015000
            put32(cpu, font+0x18, state)
            put32(cpu, state+8, ranges)
            put16(cpu, state+0x12, 2 if second else 1)
            put32(cpu, ranges, 0x40)
            put16(cpu, ranges+4, 4)
            put16(cpu, ranges+6, 10)
            put32(cpu, ranges+8, glyph_list)
            put32(cpu, ranges+12, map_base)
            put16(cpu, ranges+0x10, 3)
            cpu.mem_write(ranges+0x12, bytes([mode]))
            cpu.mem_write(map_base, bytes([map_value])*8)
            put16(cpu, map_base+2, 7)
            put32(cpu, ranges+0x14, 0x42)
            put16(cpu, ranges+0x18, 4)
            put16(cpu, ranges+0x1a, 20)
            cpu.mem_write(ranges+0x26, bytes([2]))
            search = ((syms["audio_uart_lv_font_pair_search_52a284"] if compiled else 0x52a284) & ~1)
            cmp_addr = ((syms["audio_uart_lv_font_u16_compare_4b29d0"]
                         if compiled else 0x4b29d0) & ~1)
            trace = []
            def hook(cpu, address, size, _):
                if address != search: return
                key = cpu.reg_read(A.UC_ARM_REG_R0)
                base, count, stride = (cpu.reg_read(reg) for reg in
                                       (A.UC_ARM_REG_R1, A.UC_ARM_REG_R2,
                                        A.UC_ARM_REG_R3))
                callback = int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP), 4),
                                          "little") & ~1
                trace.append((int.from_bytes(cpu.mem_read(key, 2), "little"),
                              base, count, stride, callback == cmp_addr))
                cpu.reg_write(A.UC_ARM_REG_R0, glyph_list+2 if hit else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, font)
            cpu.reg_write(A.UC_ARM_REG_R1, cp)
            cpu.emu_start((syms["audio_uart_lv_font_lookup_4b2774"] if compiled
                           else 0x4b2774) | 1, 0x600000, count=100000)
            return trace, cpu.reg_read(A.UC_ARM_REG_R0)
        cases = list(itertools.product((0, 1, 2, 3, 4), (0, 0x40, 0x41, 0x43, 0x44),
                                       (0, 2), (0, 1), (0, 1)))
        for case in cases:
            stock, source = run(False, *case), run(True, *case)
            if stock != source: raise AssertionError((case, stock, source))
        cmp_cases = 0
        for a, b in itertools.product((0, 1, 255, 65535), (0, 2, 255, 65535)):
            results = []
            for compiled in (False, True):
                cpu = cpu_new(); key, entry = 0x20018000, 0x20018020
                put16(cpu, key, a); put16(cpu, entry, b)
                cpu.reg_write(A.UC_ARM_REG_R0, key)
                cpu.reg_write(A.UC_ARM_REG_R1, entry)
                cpu.emu_start((syms["audio_uart_lv_font_u16_compare_4b29d0"] if compiled
                               else 0x4b29d0) | 1, 0x600000, count=1000)
                results.append(cpu.reg_read(A.UC_ARM_REG_R0))
            if results[0] != results[1]: raise AssertionError((a, b, results))
            cmp_cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_FONT_LOOKUP_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x4b2774..0x4b28ed",
               "lookup_cases": len(cases), "comparator_cases": cmp_cases,
               "limits": ["Binary search controlled at call boundary; range modes and results match stock.",
                          "Actual font ranges and glyph bitmap callback remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), cmp_cases)

if __name__ == "__main__": main()

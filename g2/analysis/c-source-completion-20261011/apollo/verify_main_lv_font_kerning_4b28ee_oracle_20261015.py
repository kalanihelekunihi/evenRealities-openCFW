#!/usr/bin/env python3
"""Compare stock and C LV kerning branches and pair comparators."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_font_kerning_4b28ee.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-font-kerning-4b28ee"
SHIM = '''#include <stdint.h>
void *audio_uart_lv_font_pair_search_52a284(const void*k,const void*b,uint32_t n,uint32_t z,void*c){return 0;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def put32(cpu, address, value): cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))
def word(cpu, address): return int.from_bytes(cpu.mem_read(address, 4), "little")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if hashlib.sha256(blob[0x4b28ee-0x438000:0x4b29a0-0x438000]).hexdigest() != \
            "55e08acaa01da6bcae2e802276f49e6195176ea5d7dfbea219c1c108d6d7bb00":
        raise RuntimeError("kerning native span changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_font_kerning_4b28ee",
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
        def run(compiled, mode, hit, value, left_class, right_class):
            cpu = cpu_new()
            font, state, pairs = 0x20010000, 0x20012000, 0x20013000
            base, values, lc, rc = 0x20014000, 0x20015000, 0x20016000, 0x20017000
            put32(cpu, font+0x18, state)
            put32(cpu, state+0xc, pairs)
            cpu.mem_write(state+0x12, (0x2000 if mode == 2 else 0).to_bytes(2, "little"))
            put32(cpu, pairs, base if mode < 2 else values)
            put32(cpu, pairs+4, values if mode < 2 else lc)
            put32(cpu, pairs+8, ((mode << 30) | 3) if mode < 2 else rc)
            cpu.mem_write(pairs+0xd, bytes([4]))
            cpu.mem_write(values+1, bytes([value & 0xff]))
            cpu.mem_write(values+4, bytes([value & 0xff]))
            cpu.mem_write(lc+1, bytes([left_class]))
            cpu.mem_write(rc+2, bytes([right_class]))
            search = ((syms["audio_uart_lv_font_pair_search_52a284"] if compiled else 0x52a284) & ~1)
            cmp8 = ((syms["audio_uart_lv_font_pair_cmp_u8_4b29a0"] if compiled else 0x4b29a0) & ~1)
            cmp16 = ((syms["audio_uart_lv_font_pair_cmp_u16_4b29b8"] if compiled else 0x4b29b8) & ~1)
            trace = []
            def hook(cpu, address, size, _):
                if address != search: return
                key = cpu.reg_read(A.UC_ARM_REG_R0)
                r1, r2, r3 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                callback = word(cpu, cpu.reg_read(A.UC_ARM_REG_SP)) & ~1
                label = "u8" if callback == cmp8 else "u16" if callback == cmp16 else hex(callback)
                trace.append((word(cpu, key), word(cpu, key+4), r1, r2, r3, label))
                cpu.reg_write(A.UC_ARM_REG_R0, base + r3 if hit else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            for reg, arg in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2),
                                (font, 1, 2)):
                cpu.reg_write(reg, arg)
            cpu.emu_start((syms["audio_uart_lv_font_kerning_4b28ee"] if compiled
                           else 0x4b28ee) | 1, 0x600000, count=100000)
            return trace, cpu.reg_read(A.UC_ARM_REG_R0)
        cases = list(itertools.product((0, 1, 2), (0, 1), (-7, 5), (0, 2), (0, 3)))
        for case in cases:
            stock, source = run(False, *case), run(True, *case)
            if stock != source: raise AssertionError((case, stock, source))
        def compare(compiled, bits, key, entry):
            cpu = cpu_new()
            address = 0x20018000
            cpu.mem_write(address, key[0].to_bytes(4, "little") + key[1].to_bytes(4, "little"))
            cpu.mem_write(address+0x20, bytes(entry))
            cpu.reg_write(A.UC_ARM_REG_R0, address)
            cpu.reg_write(A.UC_ARM_REG_R1, address+0x20)
            native = 0x4b29a0 if bits == 8 else 0x4b29b8
            symbol = "audio_uart_lv_font_pair_cmp_u8_4b29a0" if bits == 8 else \
                     "audio_uart_lv_font_pair_cmp_u16_4b29b8"
            cpu.emu_start((syms[symbol] if compiled else native) | 1, 0x600000, count=10000)
            return cpu.reg_read(A.UC_ARM_REG_R0)
        cmp_cases = 0
        for bits, a, b, ea, eb in itertools.product((8, 16), (0, 1, 256),
                                                     (0, 3, 65535), (0, 1, 255), (0, 2)):
            entry = ((ea & 0xff, eb & 0xff) if bits == 8 else
                     ((ea & 0xff), (ea >> 8) & 0xff, (eb & 0xff), (eb >> 8) & 0xff))
            stock, source = compare(False, bits, (a, b), entry), compare(True, bits, (a, b), entry)
            if stock != source: raise AssertionError((bits, a, b, ea, eb, stock, source))
            cmp_cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_FONT_KERNING_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x4b28ee..0x4b29cf",
               "kerning_cases": len(cases), "comparator_cases": cmp_cases,
               "limits": ["Binary-search helper controlled; actual pair search remains lower import.",
                          "Class tables and pair values are controlled memory, not full font payload."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), cmp_cases)

if __name__ == "__main__": main()

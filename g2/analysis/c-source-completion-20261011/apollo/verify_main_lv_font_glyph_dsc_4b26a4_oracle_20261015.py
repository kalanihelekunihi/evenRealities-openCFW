#!/usr/bin/env python3
"""Compare stock and C LV glyph descriptor callback branches."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_font_glyph_dsc_4b26a4.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-font-glyph-dsc-4b26a4"
LOWER = {"lookup": (0x4b2774, "audio_uart_lv_font_lookup_4b2774"),
         "kern": (0x4b28ee, "audio_uart_lv_font_kerning_4b28ee")}
SHIM = '''#include <stdint.h>
int32_t audio_uart_lv_font_lookup_4b2774(const void*f,uint32_t c){return 0;}
int8_t audio_uart_lv_font_kerning_4b28ee(const void*f,int32_t a,int32_t b){return 0;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def put32(cpu, address, value): cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if hashlib.sha256(blob[0x4b26a4-0x438000:0x4b2774-0x438000]).hexdigest() != \
            "301b0a9e61088b24044ab76678f4e9e94c6498a4f4f8a11fb7700cfd5bb6314c":
        raise RuntimeError("glyph descriptor native span changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_font_glyph_dsc_4b26a4",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, case):
            cp, glyph, next_glyph, kern_flag, kern, scale, flags = case
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000); cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for addr, data in segments: cpu.mem_write(addr, data)
            cpu.mem_map(0x20000000, 0x400000)
            font, out, state, table = 0x20010000, 0x20011000, 0x20012000, 0x20013000
            put32(cpu, font+0x18, state)
            put32(cpu, state+4, table)
            put32(cpu, state+0xc, kern_flag)
            cpu.mem_write(state+0x10, scale.to_bytes(2, "little") + flags.to_bytes(2, "little"))
            entry = table + 2*16
            put32(cpu, entry+4, 0x85)
            cpu.mem_write(entry+8, bytes.fromhex("0a0014000300fdff"))
            cpu.mem_write(out, bytes([0xa5])*32)
            addresses = {((syms[symbol] if compiled else native_addr) & ~1): kind
                         for kind, (native_addr, symbol) in LOWER.items()}
            trace = []
            lookup_count = 0
            def hook(cpu, address, size, _):
                nonlocal lookup_count
                kind = addresses.get(address)
                if not kind: return
                r0, r1, r2 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if kind == "lookup":
                    trace.append((kind, r0, r1))
                    result = glyph if lookup_count == 0 else next_glyph
                    lookup_count += 1
                else:
                    trace.append((kind, r0, r1, r2))
                    result = kern & 0xffffffff
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3),
                                  (font, out, cp, 0x42)):
                cpu.reg_write(reg, value)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.emu_start((syms["audio_uart_lv_font_glyph_dsc_4b26a4"] if compiled
                           else 0x4b26a4) | 1, 0x600000, count=100000)
            return trace, bytes(cpu.mem_read(out, 32)), cpu.reg_read(A.UC_ARM_REG_R0)
        cases = list(itertools.product((9, 0x41), (0, 2), (0, 3), (0, 1),
                                       (-3, 5), (16, 31), (0, 0xc600)))
        for case in cases:
            stock, source = run(False, case), run(True, case)
            if stock != source: raise AssertionError((case, stock, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_FONT_GLYPH_DSC_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x4b26a4..0x4b2773",
               "cases": len(cases),
               "limits": ["Glyph lookup and kerning helpers controlled; complete font data and bitmap output open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()

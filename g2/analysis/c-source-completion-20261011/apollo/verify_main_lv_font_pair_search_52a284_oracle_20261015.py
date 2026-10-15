#!/usr/bin/env python3
"""Compare stock and C binary-search midpoint and result behavior."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_font_pair_search_52a284.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-font-pair-search-52a284"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if hashlib.sha256(blob[0x52a284-0x438000:0x52a2d6-0x438000]).hexdigest() != \
            "8a27eb0c4a96a669ef6fc1b193f9f2a2a3314c06807b95ad402748340d4852ca":
        raise RuntimeError("binary-search native span changed")
    with tempfile.TemporaryDirectory() as td:
        elf = Path(td) / "oracle.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_font_pair_search_52a284",
                        str(SOURCE), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, count, target, stride):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000); cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for addr, data in segments: cpu.mem_write(addr, data)
            cpu.mem_map(0x20000000, 0x400000)
            base, key, callback = 0x20014000, 0x20016000, 0x20018000
            cpu.mem_write(callback, bytes.fromhex("7047"))
            cpu.mem_write(key, (target & 0xffffffff).to_bytes(4, "little"))
            for index in range(12):
                cpu.mem_write(base+index*stride, (2*index).to_bytes(4, "little"))
            trace = []
            def hook(cpu, address, size, _):
                if address != callback: return
                lhs = int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_R0), 4),
                                     "little", signed=True)
                entry = cpu.reg_read(A.UC_ARM_REG_R1)
                rhs = int.from_bytes(cpu.mem_read(entry, 4), "little", signed=True)
                trace.append((entry-base)//stride)
                result = -1 if lhs < rhs else 1 if lhs > rhs else 0
                cpu.reg_write(A.UC_ARM_REG_R0, result & 0xffffffff)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            for reg, arg in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                 A.UC_ARM_REG_R2, A.UC_ARM_REG_R3),
                                (key, base, count, stride)):
                cpu.reg_write(reg, arg)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.mem_write(0x203ff000, (callback | 1).to_bytes(4, "little"))
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.emu_start((syms["audio_uart_lv_font_pair_search_52a284"] if compiled
                           else 0x52a284) | 1, 0x600000, count=100000)
            return trace, cpu.reg_read(A.UC_ARM_REG_R0)
        cases = list(itertools.product(range(11), (-1, 0, 1, 2, 3, 4, 5, 7, 10, 17, 18),
                                       (4, 8)))
        for case in cases:
            stock, source = run(False, *case), run(True, *case)
            if stock != source: raise AssertionError((case, stock, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_FONT_PAIR_SEARCH_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x52a284..0x52a2d5",
               "cases": len(cases),
               "limits": ["Comparator controlled; binary search call order and result match stock."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()

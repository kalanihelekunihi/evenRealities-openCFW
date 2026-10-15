#!/usr/bin/env python3
"""Compare stock and C graphics target register calls."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_graphics_target_4b1516.c"
OUT = G2 / "build/c-firmware/20261015/main-display-graphics-target-4b1516"
SHIM = '#include <stdint.h>\nvoid audio_uart_nema_child_514846(uint32_t a,uint32_t b){}\n'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if hashlib.sha256(blob[0x4b1516-0x438000:0x4b1548-0x438000]).hexdigest() != \
            "7617c194fca1b385a05d28257ebf08ae3aef67c558cdbab830706a5fcc45245a":
        raise RuntimeError("graphics target span changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_display_graphics_target_4b1516",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, case):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000); cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for addr, data in segments: cpu.mem_write(addr, data)
            cpu.mem_map(0x20000000, 0x400000)
            child = (syms["audio_uart_nema_child_514846"] if compiled else 0x514846) & ~1
            trace = []
            def hook(cpu, address, size, _):
                if address != child: return
                trace.append((cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3), case):
                cpu.reg_write(reg, value)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.emu_start((syms["audio_uart_display_graphics_target_4b1516"] if compiled
                           else 0x4b1516) | 1, 0x600000, count=10000)
            return trace
        coords = (0, 1, 0xffffffff, 0x80000000, 0x7fffffff)
        sizes = (0, 1, 0x120, 0xffff)
        cases = list(itertools.product(coords, coords, sizes, sizes))
        for case in cases:
            stock, source = run(False, case), run(True, case)
            if stock != source: raise AssertionError((case, stock, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_GRAPHICS_TARGET_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x4b1516..0x4b1547",
               "cases": len(cases),
               "limits": ["NEMA register child controlled; live GPU register state remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()

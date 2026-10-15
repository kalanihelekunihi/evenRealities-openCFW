#!/usr/bin/env python3
"""Compare Apollo input-event frame and dispatch sequence with compiled C."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_input_event_453002.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-input-event-453002"
SHIM = '''#include <stdint.h>
void *audio_uart_lv_basic_box_clear_454746(void *p,uint32_t v,uint32_t n){return p;}
uint32_t audio_uart_lv_event_list_dispatch_44ffe6(void *p,void *e,uint32_t mode){return 1;}
'''
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_input_event_453002",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, code, target, first, second):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            inp = 0x20010000
            cuts = {
                (syms["audio_uart_lv_basic_box_clear_454746"] & ~1) if compiled else 0x452ed0: "clear",
                (syms["audio_uart_lv_event_list_dispatch_44ffe6"] & ~1) if compiled else 0x44ffe6: "dispatch",
            }
            trace = []
            def hook(cpu, address, size, user):
                kind = cuts.get(address)
                if kind is None: return
                r0, r1, r2 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if kind == "clear":
                    n = r1 if not compiled else r2
                    if n != 28: raise AssertionError((kind, n))
                    cpu.mem_write(r0, bytes(28))
                    trace.append((kind, n))
                    result = r0
                else:
                    frame = tuple(int.from_bytes(cpu.mem_read(r1 + i * 4, 4), "little") for i in range(7))
                    trace.append((kind, r0 - inp, frame, r2))
                    result = first if r2 == 1 else second
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, inp)
            u.reg_write(A.UC_ARM_REG_R1, code)
            u.reg_write(A.UC_ARM_REG_R2, target)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms["audio_uart_lv_input_event_453002"] if compiled else 0x453002) | 1,
                        0x600000, count=10000)
            return trace, u.reg_read(A.UC_ARM_REG_R0) & 0xff
        cases = list(itertools.product((0, 1, 0x17, 0x12345678),
                                       (0, 0x20011000, 0xffffffff), (0, 1, 2, 0xff), (0, 1, 2)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_INPUT_EVENT_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x453002..0x453051",
               "cases": len(cases),
               "limits": ["Frame zero helper and event-list dispatch controlled; callback side effects remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()

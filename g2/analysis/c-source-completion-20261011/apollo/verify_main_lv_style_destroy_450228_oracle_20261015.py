#!/usr/bin/env python3
"""Compare stock event-list destruction and invalidation with compiled C."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_style_destroy_450228.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-style-destroy-450228"
SHIM = '''#include <stdint.h>
uint32_t audio_uart_lv_event_count_450388(void *p){return 0;}
void *audio_uart_lv_event_slot_450390(void *p,uint32_t i){return 0;}
void audio_uart_lv_event_compact_450346(void *p){}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,... ){}
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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_style_destroy_450228",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, count, flag, bits):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            lst, slots = 0x20010000, 0x20011000
            descriptors = [0x20012000 + i * 0x100 for i in range(count)]
            u.mem_write(lst + 0x14, bytes([flag]))
            for i, item in enumerate(descriptors):
                u.mem_write(slots + i * 4, item.to_bytes(4, "little"))
                u.mem_write(item + 8, bits.to_bytes(4, "little"))
            trace = []
            cuts = {
                (syms["audio_uart_lv_event_count_450388"] & ~1) if compiled else 0x450388: "count",
                (syms["audio_uart_lv_event_slot_450390"] & ~1) if compiled else 0x450390: "slot",
                (syms["audio_uart_lv_event_compact_450346"] & ~1) if compiled else 0x450346: "compact",
            }
            def hook(cpu, address, size, user):
                kind = cuts.get(address)
                if kind is None: return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                if r0 != lst: raise AssertionError((kind, hex(r0)))
                if kind == "count": trace.append((kind,)); result = count
                elif kind == "slot": trace.append((kind, r1)); result = slots + r1 * 4
                else: trace.append((kind,)); result = 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, lst)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms["audio_uart_lv_style_destroy_450228"] if compiled else 0x450228) | 1,
                        0x600000, count=100000)
            values = [int.from_bytes(u.mem_read(item + 8, 4), "little") for item in descriptors]
            return trace, u.mem_read(lst + 0x14, 1)[0], values
        cases = list(itertools.product(range(4), (0, 1, 2, 0x80), (0, 1, 0x10000, 0xffffffff)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_STYLE_DESTROY_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_spans": ["0x450228..0x450285", "0x45036c..0x45037d"],
               "cases": len(cases),
               "limits": ["Count, slot, and compaction helpers controlled; allocator effects absent.",
                          "Null-list assertion and log strings not compared."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()

#!/usr/bin/env python3
"""Compare Apollo display flush lock branches with compiled C."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_flush_lock_47381e.c"
OUT = G2 / "build/c-firmware/20261015/main-display-flush-lock-47381e"
LOWER = {
    "take": (0x441c44, "xQueueSemaphoreTake"),
    "send": (0x4417ee, "audio_uart_queue_send"),
    "give_isr": (0x441a42, "xQueueGiveFromISR"),
    "isr": (0x442228, "audio_uart_display_in_isr_442228"),
    "log": (0x44d25c, "audio_uart_lvgl_log"),
}
SHIM = '''#include <stdint.h>
void *audio_uart_display_lock;
int32_t xQueueSemaphoreTake(void*p,uint32_t n){return 1;}
int32_t audio_uart_queue_send(void*p,const void*q,uint32_t a,uint32_t b){return 1;}
int32_t xQueueGiveFromISR(void*p,int32_t*q){return 1;}
uint32_t audio_uart_display_in_isr_442228(void){return 0;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,... ){}
'''
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if int.from_bytes(blob[0x47390c-0x438000:0x473910-0x438000], "little") != 0x200746bc:
        raise RuntimeError("display lock literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_display_flush_begin_47381e",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, entry, locked, take_result, isr_result):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            mutex = 0x20010000
            cell = syms["audio_uart_display_lock"] if compiled else 0x200746bc
            u.mem_write(cell, (mutex if locked else 0).to_bytes(4, "little"))
            cuts = {(syms[name] & ~1) if compiled else address: kind
                    for kind, (address, name) in LOWER.items()}
            trace = []
            def label(value): return "mutex" if value == mutex else "null" if value == 0 else hex(value)
            def hook(cpu, address, size, user):
                kind = cuts.get(address)
                if kind is None: return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if kind == "log": trace.append((kind, r0, r2))
                elif kind == "isr": trace.append((kind,))
                elif kind == "take": trace.append((kind, label(r0), r1))
                elif kind == "send": trace.append((kind, label(r0), r1, r2, r3))
                else: trace.append((kind, label(r0), r1))
                result = take_result if kind == "take" else isr_result if kind == "isr" else 1
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            native, name = (0x47381e, "audio_uart_display_flush_begin_47381e") if entry == "begin" else \
                           (0x47386a, "audio_uart_display_flush_end_47386a")
            u.emu_start((syms[name] if compiled else native) | 1, 0x600000, count=10000)
            return trace
        cases = list(itertools.product(("begin", "end"), (False, True), (0, 1), (0, 1)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_LOCK_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest,
               "native_spans": ["0x47381e..0x473869", "0x47386a..0x4738a7"],
               "native_lock_cell": "0x200746bc", "cases": len(cases),
               "limits": ["Queue semaphore, send, ISR give, ISR query and log calls controlled.",
                          "Log string pointers and live queue timing remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()

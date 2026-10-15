#!/usr/bin/env python3
"""Compare stock and C display-manager queue message and failure branches."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_flush_view_474066.c"
OUT = G2 / "build/c-firmware/20261015/main-display-flush-view-474066"
LOWER = {
    "zero": (0x43c0e4, "audio_uart_buffer_zero"),
    "queue": (0x449abe, "audio_cmsis_queue_put"),
    "flags": (0x43d0ce, "audio_log_level"),
    "extended": (0x43d574, "audio_log_extended"),
    "compact": (0x43ce9e, "compressed_log_output"),
}
SHIM = '''#include <stdint.h>
volatile uint32_t audio_uart_display_manager_queue_cell;
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){}
int32_t audio_cmsis_queue_put(void*p,const void*q,uint8_t priority,uint32_t timeout){return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,... ){}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,... ){return 0;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def word(cpu, addr): return int.from_bytes(cpu.mem_read(addr, 4), "little")
def cstr(cpu, addr):
    data = bytes(cpu.mem_read(addr, 256))
    return data[:data.index(0)].decode("latin1")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if hashlib.sha256(blob[0x474066-0x438000:0x474100-0x438000]).hexdigest() != \
            "f492a194d31e12a8093b74b119b18dfb7479579689af8d66e38577c38f4e5fc6":
        raise RuntimeError("display view span changed")
    if int.from_bytes(blob[0x4742f8-0x438000:0x4742fc-0x438000], "little") != 0x20000658:
        raise RuntimeError("display manager RAM literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_display_flush_view_474066",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, payload, queue_status, flags):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000); cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for addr, data in segments: cpu.mem_write(addr, data)
            cpu.mem_map(0x20000000, 0x400000)
            queue_cell = (syms["audio_uart_display_manager_queue_cell"]
                          if compiled else 0x20000664)
            cpu.mem_write(queue_cell, (0x20012340).to_bytes(4, "little"))
            addresses = {((syms[symbol] if compiled else native_addr) & ~1): kind
                         for kind, (native_addr, symbol) in LOWER.items()}
            trace = []
            flag_index = 0
            def hook(cpu, address, size, _):
                nonlocal flag_index
                kind = addresses.get(address)
                if not kind: return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                result = 0
                if kind == "zero":
                    trace.append((kind, r1, r2))
                    cpu.mem_write(r0, bytes([r2 & 0xff]) * r1)
                elif kind == "queue":
                    trace.append((kind, r0, bytes(cpu.mem_read(r1, 36)), r2, r3))
                    result = queue_status & 0xffffffff
                elif kind == "flags":
                    trace.append((kind,))
                    result = flags[min(flag_index, len(flags)-1)]
                    flag_index += 1
                elif kind == "extended":
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    trace.append((kind, r0, cstr(cpu, r1), cstr(cpu, r2),
                                  cstr(cpu, r3), word(cpu, sp), cstr(cpu, word(cpu, sp+4))))
                else:
                    trace.append((kind, r0, cstr(cpu, r1), cstr(cpu, r2)))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3), payload[:4]):
                cpu.reg_write(reg, value)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.mem_write(0x203ff000, payload[4].to_bytes(4, "little") +
                          payload[5].to_bytes(4, "little"))
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.emu_start((syms["audio_uart_display_flush_view_474066"] if compiled
                           else 0x474066) | 1, 0x600000, count=100000)
            return trace, cpu.reg_read(A.UC_ARM_REG_R0)
        payloads = ((0, 0, 0, 0, 0x240, 0x120),
                    (1, 2, 3, 4, 5, 6),
                    (0xffffffff, 0x80000000, 0x12345678, 0, 0, 7))
        outcomes = ((0, (0, 0, 0)), (-1, (0, 0, 0)),
                    (-1, (2, 0, 0)), (-1, (0, 1, 0)),
                    (-1, (0, 0, 4)), (-1, (2, 1, 4)))
        cases = list(itertools.product(payloads, outcomes))
        for payload, (status, flags) in cases:
            stock, source = run(False, payload, status, flags), run(True, payload, status, flags)
            if stock != source: raise AssertionError((payload, status, flags, stock, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_VIEW_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x474066..0x4740ff",
               "native_queue_cell": "0x20000664", "cases": len(cases),
               "limits": ["Queue, logger and zero helper controlled; live queue delivery open.",
                          "Absolute RAM queue cell requires source layout and startup proof."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()

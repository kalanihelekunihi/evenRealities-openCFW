#!/usr/bin/env python3
"""Compare Apollo display transfer branches with compiled C."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_flush_transfer_47366c.c"
OUT = G2 / "build/c-firmware/20261015/main-display-flush-transfer-47366c"
LOWER = {
    "copy": (0x439c04, "audio_uart_display_area_copy_439c04"),
    "width": (0x451598, "audio_uart_lv_area_width_451598"),
    "height": (0x4515a4, "audio_uart_lv_area_height_4515a4"),
    "bind": (0x4b092a, "audio_uart_ambiq_bind_buffer_4b092a"),
    "transfer": (0x5fa13c, "audio_uart_display_frame_transfer_5fa13c"),
    "blend": (0x4b075e, "audio_uart_ambiq_blend_clear_4b075e"),
    "submit": (0x4b0c8a, "audio_uart_ambiq_submit_4b0c8a"),
}
SHIM = '''#include <stdint.h>
void *audio_uart_display_instance;
void *audio_uart_display_area_copy_439c04(void*p,const void*q,uint32_t n){return p;}
int32_t audio_uart_lv_area_width_451598(const void*p){return 1;}
int32_t audio_uart_lv_area_height_4515a4(const void*p){return 1;}
uint32_t audio_uart_ambiq_bind_buffer_4b092a(void*p,const void*q,uint32_t n){return 1;}
void audio_uart_display_frame_transfer_5fa13c(const void*p,const void*q,uint32_t w,uint32_t h){}
void audio_uart_ambiq_blend_clear_4b075e(void*p){}
uint32_t audio_uart_ambiq_submit_4b0c8a(uint32_t n){return 0;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,... ){}
'''
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    source_area = int.from_bytes(blob[0x4738f4-0x438000:0x4738f8-0x438000], "little")
    if source_area != 0x786260 or blob[source_area-0x438000:source_area-0x438000+16] != \
            bytes.fromhex("00000000000000003f0200001f010000"):
        raise RuntimeError("stock display area changed")
    if int.from_bytes(blob[0x4738f8-0x438000:0x4738fc-0x438000], "little") != 0x200746b8:
        raise RuntimeError("display instance literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_display_flush_transfer_47366c",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, width, height, bound, sync):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            instance, pixels, output = 0x20010000, 0x20011000, 0x20012000
            cell = syms["audio_uart_display_instance"] if compiled else 0x200746b8
            u.mem_write(cell, instance.to_bytes(4, "little"))
            u.mem_write(instance + 0x10, output.to_bytes(4, "little"))
            cuts = {(syms[name] & ~1) if compiled else address: kind
                    for kind, (address, name) in LOWER.items()}
            trace = []
            def label(value):
                return {instance: "instance", pixels: "pixels", output: "output",
                        0: "null"}.get(value, hex(value))
            def hook(cpu, address, size, user):
                kind = cuts.get(address)
                if kind is None: return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if kind == "copy":
                    content = bytes(cpu.mem_read(r1, r2))
                    trace.append((kind, content, r2))
                    cpu.mem_write(r0, content)
                    result = r0
                elif kind in ("width", "height"):
                    trace.append((kind, tuple(cpu.mem_read(r0, 16))))
                    result = width if kind == "width" else height
                elif kind == "bind":
                    trace.append((kind, label(r0), tuple(cpu.mem_read(r1, 16)), r2))
                    result = bound
                elif kind == "transfer":
                    trace.append((kind, label(r0), label(r1), r2, r3))
                    result = 0
                elif kind == "blend":
                    trace.append((kind, label(r0)))
                    result = 0
                else:
                    trace.append((kind, r0))
                    result = 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, 0)
            u.reg_write(A.UC_ARM_REG_R1, pixels)
            u.reg_write(A.UC_ARM_REG_R2, sync)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms["audio_uart_display_flush_transfer_47366c"] if compiled else 0x47366c) | 1,
                        0x600000, count=100000)
            return trace
        cases = list(itertools.product((0, 1, 100), (0, 1, 100), (0, 1), (0, 1, 3)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_TRANSFER_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x47366c..0x4736f3",
               "native_full_area": "0x786260", "cases": len(cases),
               "limits": ["Area, bind, frame transfer, and submit helpers controlled; live panel DMA remains open.",
                          "Invalid display-index fatal path not exercised."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()

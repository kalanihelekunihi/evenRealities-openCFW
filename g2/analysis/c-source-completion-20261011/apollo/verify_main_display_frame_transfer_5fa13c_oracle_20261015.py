#!/usr/bin/env python3
"""Compare stock and compiled display frame-transfer call traces."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_frame_transfer_5fa13c.c"
OUT = G2 / "build/c-firmware/20261015/main-display-frame-transfer-5fa13c"
LOWER = {
    "texture": (0x4b1298, "audio_uart_nema_bind_tex_4b1298"),
    "target": (0x4b1516, "audio_uart_display_graphics_target_4b1516"),
    "identity": (0x561810, "audio_uart_nema_matrix_identity_561810"),
    "matrix": (0x5226e8, "audio_uart_nema_matrix_upload_5226e8"),
    "blend": (0x513924, "audio_uart_display_graphics_blend_513924"),
    "color": (0x4b146c, "audio_uart_ambiq_texture_color_4b146c"),
    "rectangle": (0x522ae0, "audio_uart_nema_mask_rectangle_522ae0"),
    "alpha": (0x513e2e, "audio_uart_ambiq_image_alpha_513e2e"),
    "finish": (0x4b1548, "audio_uart_display_graphics_finish_4b1548"),
}
SHIM = '''#include <stdint.h>
void audio_uart_nema_bind_tex_4b1298(uint32_t a,const void*b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g){}
void audio_uart_display_graphics_target_4b1516(uint32_t a,uint32_t b,uint32_t c,uint32_t d){}
void audio_uart_nema_matrix_identity_561810(void*p){}
void audio_uart_nema_matrix_upload_5226e8(const void*p){}
void audio_uart_display_graphics_blend_513924(uint32_t a,uint32_t b,uint32_t c,uint32_t d){}
void audio_uart_ambiq_texture_color_4b146c(uint32_t a){}
void audio_uart_nema_mask_rectangle_522ae0(uint32_t a,uint32_t b,uint32_t c,uint32_t d){}
void audio_uart_ambiq_image_alpha_513e2e(uint32_t a){}
void audio_uart_display_graphics_finish_4b1548(void){}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def word(cpu, addr): return int.from_bytes(cpu.mem_read(addr, 4), "little")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    native = blob[0x5fa13c-0x438000:0x5fa216-0x438000]
    if hashlib.sha256(native).hexdigest() != "1c197f083b5cf027f687d8a64232ea0ef9c0d8a87c0024406d2cfe6c402a2953":
        raise RuntimeError("frame-transfer span changed")
    if blob[0x5fa218-0x438000:0x5fa21c-0x438000] != bytes.fromhex("01010010"):
        raise RuntimeError("second pass literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_display_frame_transfer_5fa13c",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, width, height):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000); cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for addr, data in segments: cpu.mem_write(addr, data)
            cpu.mem_map(0x20000000, 0x400000)
            addresses = {((syms[symbol] if compiled else native_addr) & ~1): kind
                         for kind, (native_addr, symbol) in LOWER.items()}
            trace = []
            def hook(cpu, address, size, _):
                kind = addresses.get(address)
                if not kind: return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if kind == "texture":
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    trace.append((kind, r0, r1, r2, r3,
                                  word(cpu, sp), word(cpu, sp+4), word(cpu, sp+8)))
                elif kind == "identity":
                    trace.append((kind,))
                    cpu.mem_write(r0, bytes(36))
                elif kind == "matrix":
                    trace.append((kind, word(cpu, r0), word(cpu, r0+8)))
                elif kind == "finish":
                    trace.append((kind,))
                elif kind in ("color", "alpha"):
                    trace.append((kind, r0))
                else:
                    trace.append((kind, r0, r1, r2, r3))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20010000)
            cpu.reg_write(A.UC_ARM_REG_R1, 0x20020000)
            cpu.reg_write(A.UC_ARM_REG_R2, width)
            cpu.reg_write(A.UC_ARM_REG_R3, height)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.emu_start((syms["audio_uart_display_frame_transfer_5fa13c"] if compiled else
                           0x5fa13c) | 1, 0x600000, count=100000)
            return trace, cpu.reg_read(A.UC_ARM_REG_R0)
        cases = list(itertools.product((0, 1, 2, 3, 4, 576, 0xfffffffe),
                                       (0, 1, 288, 0xffffffff)))
        for case in cases:
            stock, source = run(False, *case), run(True, *case)
            if stock != source: raise AssertionError((case, stock, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_FRAME_TRANSFER_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest,
               "native_span": "0x5fa13c..0x5fa215", "cases": len(cases),
               "limits": ["Graphics calls controlled at entry; live GPU state and frame output open.",
                          "Matrix helper writes deterministic zero defaults for call-trace comparison."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()

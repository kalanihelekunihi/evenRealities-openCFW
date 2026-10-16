#!/usr/bin/env python3
"""Compare label draw descriptor style initialization with native Apollo."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SRC = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_label_dsc_init_452988.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-label-dsc-init-452988"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
WRAPPERS = {0x4525b2: 0x59, 0x452592: 0x58, 0x4525c8: 0x5b,
            0x4525d2: 0x5c, 0x4525dc: 0x5d, 0x4525be: 0x5a,
            0x4525e8: 0x5e}
SHIM = '''#include <stdint.h>
__attribute__((noinline)) uint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c)
{(void)a;(void)b;(void)c;return 0;}
__attribute__((noinline)) uint32_t audio_uart_lv_draw_task_opacity_452df0(void*a,uint32_t b,void*c)
{(void)a;(void)b;(void)c;return 0;}
__attribute__((noinline)) uint32_t audio_uart_lv_draw_rgb_mix_452e22(void*a,uint32_t b,void*c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;return 0;}
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != PAYLOAD_SHA:
        raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_draw_label_dsc_init_452988",
                        str(SRC), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, opacity, layer_opacity, part, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            page, descriptor = 0x20011000, 0x20012000
            cpu.mem_write(page, bytes(0x100))
            cpu.mem_write(descriptor, bytes([seed]) * 0x100)
            style = syms["audio_uart_lv_style_property_44bdea"] & ~1
            layer = (syms["audio_uart_lv_draw_task_opacity_452df0"] if compiled else 0x452df0) & ~1
            color = (syms["audio_uart_lv_draw_rgb_mix_452e22"] if compiled else 0x452e22) & ~1
            values = {0x59: opacity, 0x58: 0x10203040, 0x5b: 2,
                      0x5c: 3, 0x5d: 5, 0x5a: 0x20015000, 0x5e: 2}
            trace = []

            def hook(cpu, address, size, _):
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                r2 = cpu.reg_read(A.UC_ARM_REG_R2)
                r3 = cpu.reg_read(A.UC_ARM_REG_R3)
                if address == layer:
                    trace.append(("layer", r0, r1, r2))
                    result = layer_opacity
                elif address == color:
                    trace.append(("color", r0, r1, r2, r3))
                    result = 0x11223344
                elif compiled and address == style:
                    trace.append(("style", r0, r1, r2))
                    result = values[r2]
                elif not compiled and address in WRAPPERS:
                    prop = WRAPPERS[address]
                    trace.append(("style", r0, r1, prop))
                    result = values[prop]
                else:
                    return
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, page)
            cpu.reg_write(A.UC_ARM_REG_R1, part)
            cpu.reg_write(A.UC_ARM_REG_R2, descriptor)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_lv_draw_label_dsc_init_452988"] if compiled else 0x452988
            cpu.emu_start(entry | 1, 0x600000, count=10000)
            return trace, bytes(cpu.mem_read(descriptor, 0x60))

        cases = list(itertools.product((0, 2, 3, 128, 255),
                                       (0, 1, 128, 252, 253, 255),
                                       (0, 0x40000), (0, 0xa5)))
        for case in cases:
            stock, source = run(False, *case), run(True, *case)
            if stock != source:
                raise AssertionError((case, stock, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_LABEL_DSC_INIT_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": digest,
               "upstream": "third-party/upstream/lvgl/src/core/lv_obj_draw.c",
               "native_span": "0x452988..0x452a4b", "cases": len(cases),
               "limits": ["Layer opacity and color mixing are controlled children.",
                          "Full style inheritance and rendering remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))


if __name__ == "__main__":
    main()

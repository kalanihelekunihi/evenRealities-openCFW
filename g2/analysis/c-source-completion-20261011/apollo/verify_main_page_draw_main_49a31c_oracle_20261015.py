#!/usr/bin/env python3
"""Compare Apollo LVGL label draw_main branch and descriptor behavior."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/display_page_draw_main_49a31c.c"
OUT = G2 / "build/c-firmware/20261015/main-page-draw-main-49a31c"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = {
    "layer": (0x451960, "audio_uart_lv_event_layer_451960"),
    "coords": (0x43feca, "audio_uart_lv_obj_content_coords_43feca"),
    "flags": (0x49abea, "audio_uart_page_layout_flags_49abea"),
    "descriptor_init": (0x489f5e, "audio_uart_lv_image_descriptor_init_489f5e"),
    "height": (0x4515a4, "audio_uart_lv_area_height_4515a4"),
    "width": (0x451598, "audio_uart_lv_area_width_451598"),
    "style_init": (0x452988, "audio_uart_lv_draw_label_dsc_init_452988"),
    "measure": (0x489546, "audio_uart_page_event_calculate_489546"),
    "intersect": (0x450bcc, "audio_uart_lv_area_intersect_450bcc"),
    "scroll": (0x44e4aa, "audio_uart_lv_scroll_top_44e4aa"),
    "move": (0x450bb2, "audio_uart_ambiq_area_move_450bb2"),
    "draw": (0x489fe0, "audio_uart_lv_draw_label_489fe0"),
    "advance": (0x4d57f4, "audio_uart_font_glyph_advance_4d57f4"),
}
STYLE = {
    0x4993a0: 0x58, 0x499392: 0x1c, 0x4993de: 0x61,
    0x4993f6: 0x60, 0x4993ec: 0x5f,
}
SHIM = "#include <stdint.h>\n#include <stddef.h>\n" + "\n".join(
    f"__attribute__((noinline)) uint32_t {name}(void*a,void*b,void*c,void*d)"
    "{(void)a;(void)b;(void)c;(void)d;return 0;}"
    for _, name in CALLS.values()) + "\n" + '''
__attribute__((noinline)) uint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c)
{(void)a;(void)b;(void)c;return 0;}
void __aeabi_memclr4(void *p, size_t n) {unsigned char *b=p;while(n--)*b++=0;}
'''


def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))


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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_event_dispatch_49a31c",
                        str(SRC), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, case):
            mode, align, measured_width, measured_height, area_height, selected, visible = case
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            event, page, layer, font, string = (0x20011000, 0x20012000, 0x20013000,
                                                 0x20014000, 0x20015000)
            cpu.mem_write(event, bytes(0x100))
            cpu.mem_write(page, bytes(0x100))
            cpu.mem_write(layer, bytes(0x100))
            cpu.mem_write(font, bytes(0x100))
            cpu.mem_write(string, b"hello world\0")
            put(cpu, event, page)
            put(cpu, page + 0x2c, string)
            put(cpu, page + 0x20, 22)
            put(cpu, page + 0x54, 7)
            put(cpu, page + 0x58, 9)
            put(cpu, page + 0x44, 1 if selected else 0xffff)
            put(cpu, page + 0x48, 2 if selected else 0xffff)
            cpu.mem_write(page + 0x5c, bytes([mode]))
            put(cpu, font + 0xc, 12)
            for i in range(4):
                put(cpu, layer + 0x18 + 4 * i, 100 + i)
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            style_target = syms["audio_uart_lv_style_property_44bdea"] & ~1
            trace = []

            def hook(cpu, address, size, _):
                if compiled and address == style_target:
                    prop = cpu.reg_read(A.UC_ARM_REG_R2)
                    trace.append(("style", cpu.reg_read(A.UC_ARM_REG_R1), prop))
                    cpu.reg_write(A.UC_ARM_REG_R0, {0x58: 0x102030,
                        0x1c: 0x405060, 0x61: 0x708090, 0x60: 0xa0,
                        0x5f: 2}.get(prop, 0))
                    cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
                    return
                if not compiled and address in STYLE:
                    prop = STYLE[address]
                    trace.append(("style", cpu.reg_read(A.UC_ARM_REG_R1), prop))
                    cpu.reg_write(A.UC_ARM_REG_R0, {0x58: 0x102030,
                        0x1c: 0x405060, 0x61: 0x708090, 0x60: 0xa0,
                        0x5f: 2}[prop])
                    cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
                    return
                key = targets.get(address)
                if key is None:
                    return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                r2 = cpu.reg_read(A.UC_ARM_REG_R2)
                r3 = cpu.reg_read(A.UC_ARM_REG_R3)
                result = 0
                if key == "layer":
                    trace.append((key, r0))
                    result = layer
                elif key == "coords":
                    trace.append((key, r0, "area"))
                    for i, value in enumerate((0, 0, 29, area_height - 1)):
                        put(cpu, r1 + 4 * i, value)
                elif key == "flags":
                    trace.append((key, r0))
                    result = 3
                elif key == "descriptor_init":
                    trace.append((key, "descriptor"))
                    cpu.mem_write(r0, bytes(0x64))
                    put(cpu, r0 + 0x20, font)
                    put(cpu, r0 + 0x28, 2)
                    put(cpu, r0 + 0x2c, 3)
                    cpu.mem_write(r0 + 0x51, bytes([align]))
                elif key in ("height", "width"):
                    trace.append((key, "area"))
                    result = area_height if key == "height" else 30
                elif key == "style_init":
                    trace.append((key, r0, r1, "descriptor"))
                elif key == "measure":
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    args = tuple(int.from_bytes(cpu.mem_read(sp + i, 4), "little")
                                 for i in (0, 4, 8))
                    trace.append((key, r1, r2, r3, *args))
                    put(cpu, r0, measured_width)
                    put(cpu, r0 + 4, measured_height)
                elif key == "intersect":
                    trace.append((key, "area", "layer_clip"))
                    for i, value in enumerate((1, 2, 20, 21)):
                        put(cpu, r0 + 4 * i, value)
                    result = 1 if visible else 0
                elif key == "scroll":
                    trace.append((key, r0))
                    result = 5
                elif key == "move":
                    trace.append((key, r1, r2))
                elif key == "draw":
                    trace.append((key, r0, bytes(cpu.mem_read(r1, 0x64)),
                                  bytes(cpu.mem_read(r2, 16)),
                                  bytes(cpu.mem_read(layer + 0x18, 16))))
                elif key == "advance":
                    trace.append((key, r0, r1, r2))
                    result = 4
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, event)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_event_dispatch_49a31c"] if compiled else 0x49a31c
            cpu.emu_start(entry | 1, 0x600000, count=50000)
            return trace, bytes(cpu.mem_read(layer + 0x18, 16))

        cases = list(itertools.product((0, 2, 3, 4, 5), (1, 2, 3),
                                       (20, 50), (20, 50), (30, 1050),
                                       (False, True), (False, True)))
        for case in cases:
            stock, source = run(False, case), run(True, case)
            if stock != source:
                raise AssertionError((case, stock, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_DRAW_MAIN_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": digest,
               "upstream": "third-party/upstream/lvgl/src/widgets/label/lv_label.c",
               "native_span": "0x49a31c..0x49a5bf", "cases": len(cases),
               "limits": ["Style initializer and final draw routine are controlled child calls.",
                          "Descriptor snapshots are compared at each draw; hardware rendering remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare LVGL image cover and draw branches with pinned Apollo stock."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_image_draw_498ec0.c"
OUT = G2 / "build/c-firmware/20261016/main-lv-image-draw-498ec0"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OBJECT, EVENT, INFO, LAYER, TEST_AREA = (0x20001000, 0x20002000,
                                         0x20003000, 0x20004000, 0x20005000)
CALLS = (("audio_uart_page_event_code_450286", 0x450286),
         ("audio_uart_lv_color_has_alpha_440fc4", 0x440fc4),
         ("audio_uart_lv_image_style_opa_498634", 0x498634),
         ("audio_uart_lv_area_contains_450f28", 0x450f28),
         ("audio_uart_lv_image_get_pivot_498b82", 0x498b82),
         ("audio_uart_lv_obj_width_43fd9e", 0x43fd9e),
         ("audio_uart_lv_obj_height_43fdda", 0x43fdda),
         ("audio_uart_ambiq_transform_area_488cda", 0x488cda),
         ("audio_uart_lv_event_layer_451960", 0x451960),
         ("audio_uart_ambiq_image_options_init_488918", 0x488918),
         ("audio_uart_lv_obj_init_draw_image_452a34", 0x452a34),
         ("audio_uart_display_area_copy_439c04", 0x439c04),
         ("audio_uart_lv_image_style_radius_49865e", 0x49865e),
         ("audio_uart_lv_area_set_450b5c", 0x450b5c),
         ("audio_uart_lv_area_transform_451082", 0x451082),
         ("audio_uart_lv_area_intersect_450bcc", 0x450bcc),
         ("audio_uart_ambiq_area_move_450bb2", 0x450bb2),
         ("audio_uart_lv_draw_image_488a38", 0x488a38),
         ("audio_uart_lv_image_descriptor_init_489f5e", 0x489f5e),
         ("audio_uart_lv_draw_label_dsc_init_452988", 0x452988),
         ("audio_uart_lv_draw_label_489fe0", 0x489fe0),
         ("audio_uart_lvgl_log", 0x44d25c))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display-lv-image-draw-oracle.o"
    elf = OUT / "display-lv-image-draw-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    defs = [f"--defsym={name}=0x{address | 1:x}" for name, address in CALLS]
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", *defs, str(obj),
                    "-o", str(elf)], check=True)
    with elf.open("rb") as stream:
        e = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symtab = e.get_section_by_name(".symtab")
        symbols = {s.name: s["st_value"] for s in symtab.iter_symbols()}
    return elf, segments, symbols


def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    elf, segments, symbols = build()
    cuts = {address: i for i, (_, address) in enumerate(CALLS)}

    def run(compiled, code, kind, rotation, scale, align, source,
            cover, alpha, opa, contained, width, height):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(OBJECT, bytes(((i * 7 + 19) & 255 for i in range(0x60))))
        put = lambda address, value: u.mem_write(address, struct.pack("<I", value & 0xffffffff))
        put(OBJECT + 0x14, 12)
        put(OBJECT + 0x18, 23)
        put(OBJECT + 0x1c, 111)
        put(OBJECT + 0x20, 83)
        put(OBJECT + 0x2c, source)
        put(OBJECT + 0x30, 0)
        put(OBJECT + 0x34, 3)
        put(OBJECT + 0x38, 5)
        put(OBJECT + 0x3c, width)
        put(OBJECT + 0x40, height)
        put(OBJECT + 0x44, rotation)
        put(OBJECT + 0x48, scale)
        put(OBJECT + 0x4c, scale)
        put(OBJECT + 0x58, kind | (align << 8))
        put(EVENT, OBJECT)
        put(EVENT + 0x10, INFO)
        put(INFO, cover)
        put(INFO + 4, TEST_AREA)
        u.mem_write(TEST_AREA, struct.pack("<4i", 5, 8, 40, 50))
        u.mem_write(LAYER + 0x18, struct.pack("<4i", 0, 0, 128, 64))
        trace = []

        def signed(value):
            return value if value < 0x80000000 else value - 0x100000000

        def area(cpu, address):
            return struct.unpack("<4i", bytes(cpu.mem_read(address, 16)))

        def cstring(cpu, address):
            return bytes(cpu.mem_read(address, 170)).split(b"\0", 1)[0]

        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            a, b, c, d = (cpu.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                           A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            ret = 0
            if i == 0:
                trace.append(("code", a)); ret = code
            elif i == 1:
                trace.append(("alpha-format", a)); ret = alpha
            elif i == 2:
                trace.append(("opacity", a, b)); ret = opa
            elif i == 3:
                trace.append(("contains", area(cpu, a), area(cpu, b), c))
                ret = contained
            elif i == 4:
                trace.append(("pivot", a)); cpu.mem_write(b, struct.pack("<2i", 7, 9))
            elif i == 5:
                trace.append(("width", a)); ret = width
            elif i == 6:
                trace.append(("height", a)); ret = height
            elif i == 7:
                sx, sy, pivot = struct.unpack("<3I", bytes(cpu.mem_read(sp, 12)))
                trace.append(("transform", b, c, d, sx, sy,
                              struct.unpack("<2i", bytes(cpu.mem_read(pivot, 8)))))
                cpu.mem_write(a, struct.pack("<4i", -3, -4, b + 2, c + 3))
            elif i == 8:
                trace.append(("layer", a)); ret = LAYER
            elif i == 9:
                trace.append(("image-init",)); cpu.mem_write(a, bytes([0x55]) * 0x70)
            elif i == 10:
                trace.append(("image-style", a, b))
            elif i == 11:
                trace.append(("copy", c, area(cpu, b)))
                cpu.mem_write(a, bytes(cpu.mem_read(b, c)))
            elif i == 12:
                trace.append(("radius", a, b)); ret = 4
            elif i == 13:
                fifth = struct.unpack("<I", bytes(cpu.mem_read(sp, 4)))[0]
                trace.append(("set", b, c, d, fifth))
                cpu.mem_write(a, struct.pack("<4I", b, c, d, fifth))
            elif i == 14:
                x, y = struct.unpack("<2I", bytes(cpu.mem_read(sp, 8)))
                trace.append(("align", area(cpu, a), area(cpu, b), c, x, y))
                cpu.mem_write(b, struct.pack("<4i", 2, 4, 42, 44))
            elif i == 15:
                trace.append(("intersect", area(cpu, b), area(cpu, c)))
                cpu.mem_write(a, struct.pack("<4i", 10, 11, 60, 50)); ret = 1
            elif i == 16:
                trace.append(("move", area(cpu, a), signed(b), signed(c)))
                x1, y1, x2, y2 = area(cpu, a)
                cpu.mem_write(a, struct.pack("<4i", x1 + signed(b), y1 + signed(c),
                                             x2 + signed(b), y2 + signed(c)))
            elif i == 17:
                descriptor = bytes(cpu.mem_read(b, 0x70))
                trace.append(("draw-image", a, area(cpu, c),
                              struct.unpack_from("<I", descriptor, 0x10)[0],
                              struct.unpack_from("<I", descriptor, 0x1c)[0],
                              struct.unpack_from("<I", descriptor, 0x2c)[0],
                              struct.unpack_from("<3I", descriptor, 0x30),
                              struct.unpack_from("<2i", descriptor, 0x44),
                              struct.unpack_from("<H", descriptor, 0x50)[0],
                              struct.unpack_from("<4i", descriptor, 0x58),
                              struct.unpack_from("<I", descriptor, 0x68)[0]))
            elif i == 18:
                trace.append(("label-init",)); cpu.mem_write(a, bytes([0x33]) * 100)
            elif i == 19:
                trace.append(("label-style", a, b))
            elif i == 20:
                descriptor = bytes(cpu.mem_read(b, 100))
                trace.append(("draw-label", a, area(cpu, c),
                              struct.unpack_from("<I", descriptor, 0x10)[0],
                              struct.unpack_from("<I", descriptor, 0x1c)[0]))
            else:
                message = struct.unpack("<I", bytes(cpu.mem_read(sp, 4)))[0]
                trace.append(("log", a, cstring(cpu, b), c,
                              cstring(cpu, d), cstring(cpu, message)))
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, EVENT)
        entry = symbols["audio_uart_lv_image_draw_498ec0"] if compiled else 0x498ec0
        u.emu_start(entry | 1, 0x600000, count=10000)
        return trace, bytes(u.mem_read(INFO, 8)), bytes(u.mem_read(LAYER + 0x18, 16))

    cases = 0
    cover_cases = []
    for kind in (0, 1, 2, 3):
        for rotation, scale in ((0, 0x100), (1, 0x100), (0, 0x80)):
            for cover, alpha, opa, contained in ((0, 0, 255, 1),
                                                  (2, 0, 255, 1),
                                                  (0, 1, 255, 1),
                                                  (0, 0, 200, 1),
                                                  (0, 0, 255, 0)):
                cover_cases.append((0x1a, kind, rotation, scale, 0,
                                    0x20006000, cover, alpha, opa,
                                    contained, 40, 30))
    for case in cover_cases:
        stock, selected = run(False, *case), run(True, *case)
        if stock != selected:
            raise RuntimeError(f"image cover mismatch {case}: {stock[0]} != {selected[0]}; info_equal={stock[1] == selected[1]}; clip_equal={stock[2] == selected[2]}")
        cases += 1
    draw_cases = []
    for kind in (0, 1, 2, 3):
        for align in (0, 9, 10, 12, 13):
            for source in (0, 0x20006000):
                for width, height, scale in ((40, 30, 0x100), (0, 30, 0x100),
                                             (40, 0, 0x100), (40, 30, 0)):
                    draw_cases.append((0x1d, kind, 0, scale, align, source,
                                       0, 0, 255, 1, width, height))
    for case in draw_cases:
        stock, selected = run(False, *case), run(True, *case)
        if stock != selected:
            raise RuntimeError(f"image draw mismatch {case}: {stock[0]} != {selected[0]}; info_equal={stock[1] == selected[1]}; clip_equal={stock[2] == selected[2]}")
        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_DRAW_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "cover_cases": len(cover_cases), "draw_cases": len(draw_cases),
              "scope": "Cover-check and draw-main control, lower-call order, descriptor fields and info/clip effects",
              "limits": ["Real lower draw effects, tile arithmetic edge values and hardware rendering outside bounded oracle."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Bounded native comparison for the LVGL letter-position source candidate."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc, UcError
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SRC = G2 / "components/audio/uart_thread_source_candidate/display_page_text_window_499a5c.c"
OUT = G2 / "build/c-firmware/20261015/main-page-text-window-499a5c"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = {
    "pad_left": (0x499388, "audio_uart_page_pad_left_499388"),
    "pad_top": (0x49937e, "audio_uart_page_pad_top_49937e"),
    "coords": (0x43feca, "audio_uart_lv_obj_content_coords_43feca"),
    "text_ptr": (0x4997f8, "audio_uart_page_text_pointer_4997f8"),
    "width": (0x451598, "audio_uart_lv_area_width_451598"),
    "height": (0x4515a4, "audio_uart_lv_area_height_4515a4"),
    "font": (0x4993c0, "audio_uart_page_metric_4993c0"),
    "line_space": (0x4993d4, "audio_uart_page_metric_4993d4"),
    "letter_space": (0x4993ca, "audio_uart_page_metric_4993ca"),
    "flags": (0x49abea, "audio_uart_page_layout_flags_49abea"),
    "next_line": (0x4897fc, "audio_uart_text_line_length_4897fc"),
    "previous": (0x489dbc, "audio_uart_text_utf8_previous_489dbc"),
    "align_class": (0x44c448, "audio_uart_page_text_align_class_44c448"),
    "align": (0x49ac4a, "audio_uart_page_text_align_49ac4a"),
    "glyph_next": (0x489b3c, "audio_uart_text_next_glyph_489b3c"),
    "hash": (0x489652, "audio_uart_text_hash_state_489652"),
    "advance": (0x4d57f4, "audio_uart_font_glyph_advance_4d57f4"),
    "count": (0x489e4a, "audio_uart_text_utf8_count_to_bytes_489e4a"),
    "style_property": (0x44bdea, "audio_uart_lv_style_property_44bdea"),
}
SHIM = "#include <stdint.h>\n" + "\n".join(
    f"__attribute__((noinline)) uint32_t {name}(void*a,void*b,void*c,void*d)"
    "{(void)a;(void)b;(void)c;(void)d;return 0;}"
    for key, (_, name) in CALLS.items() if key not in ("pad_left", "pad_top")) + \
    "\n__attribute__((noinline)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...){(void)a;(void)b;(void)c;(void)d;(void)e;}\n"


def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != PAYLOAD_SHA:
        raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim = Path(td) / "shim.c"
        elf = Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_text_window_499a5c",
                        str(SRC), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, mode, x, y, max_height, flags, fatal_kind=None):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            page, position, string, font = 0x20011000, 0x20012000, 0x20013000, 0x20014000
            cpu.mem_write(page, bytes(0x100))
            cpu.mem_write(page + 0x5c, bytes([mode]))
            cpu.mem_write(string, b"abcde\0")
            put(cpu, page + 0x2c, string)
            put(cpu, position, x)
            put(cpu, position + 4, y)
            put(cpu, font + 0xc, 12)
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            if compiled:
                for key in ("pad_left", "pad_top"):
                    targets[syms[CALLS[key][1]] & ~1] = key
            trace = []
            log_target = (syms["audio_uart_lvgl_log"] if compiled else 0x44d25c) & ~1

            def read_string(cpu, address):
                return bytes(cpu.mem_read(address, 256)).split(b"\0", 1)[0].decode("ascii")

            def hook(cpu, address, size, _):
                if address == log_target:
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    args = [int.from_bytes(cpu.mem_read(sp + i, 4), "little")
                            for i in (0, 4, 8)]
                    trace.append(("fatal_log", cpu.reg_read(A.UC_ARM_REG_R0),
                                  read_string(cpu, cpu.reg_read(A.UC_ARM_REG_R1)),
                                  cpu.reg_read(A.UC_ARM_REG_R2),
                                  read_string(cpu, cpu.reg_read(A.UC_ARM_REG_R3)),
                                  *(read_string(cpu, value) for value in args)))
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
                if key in ("pad_left", "pad_top"):
                    trace.append(("style_property", r0, r1,
                                  0x12 if key == "pad_left" else 0x10))
                elif key == "coords":
                    trace.append((key, r0))
                    cpu.mem_write(r1, bytes(16))
                elif key == "text_ptr":
                    trace.append((key, r0))
                    result = string
                elif key in ("width", "height"):
                    trace.append((key, "area"))
                    result = 30 if key == "width" else max_height
                elif key in ("font", "line_space", "letter_space"):
                    trace.append((key, r0, r1))
                    result = {"font": font, "line_space": 3, "letter_space": 2}[key]
                elif key == "flags":
                    trace.append((key, r0))
                    result = flags
                elif key == "next_line":
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    stack_args = tuple(int.from_bytes(cpu.mem_read(sp + offset, 4),
                                                      "little")
                                       for offset in (0, 4, 8))
                    trace.append((key, r0 - string, r1, r2, r3, *stack_args))
                    result = max(0, 5 - (r0 - string))
                elif key == "previous":
                    offset = int.from_bytes(cpu.mem_read(r1, 4), "little")
                    trace.append((key, r0, offset))
                    put(cpu, r1, offset - 1)
                    result = ord("e")
                elif key == "align_class":
                    trace.append((key, r0, r1, r2))
                elif key == "align":
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    stack_args = tuple(int.from_bytes(cpu.mem_read(sp + offset, 4),
                                                      "little")
                                       for offset in (0, 4, 8, 12))
                    trace.append((key, r1, r2 - string, r3,
                                  stack_args[0], stack_args[1], "area",
                                  stack_args[3]))
                elif key == "glyph_next":
                    offset = int.from_bytes(cpu.mem_read(r3, 4), "little")
                    trace.append((key, r0 - string, offset))
                    put(cpu, r1, ord("a") + offset)
                    put(cpu, r2, ord("b") + offset)
                    put(cpu, r3, offset + 1)
                elif key == "advance":
                    trace.append((key, r0, r1, r2))
                    result = 5
                elif key == "count":
                    trace.append((key, r0 - string, r1))
                    result = r1
                elif key == "hash":
                    trace.append((key, r1))
                elif key == "style_property":
                    trace.append((key, r0, r1, r2))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0 if fatal_kind == "page" else page)
            cpu.reg_write(A.UC_ARM_REG_R1, 0 if fatal_kind == "position" else position)
            cpu.reg_write(A.UC_ARM_REG_R2, 0)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_text_window_499a5c"] if compiled else 0x499a5c
            try:
                cpu.emu_start(entry | 1, 0x600000, count=100000)
            except UcError as error:
                if fatal_kind is None or "WRITE_UNMAPPED" not in str(error):
                    raise
                return trace, "fault"
            if fatal_kind is not None:
                raise AssertionError(("fatal path did not fault", fatal_kind, trace))
            return trace, cpu.reg_read(A.UC_ARM_REG_R0)

        cases = list(itertools.product((0, 1), (0, 5, 25), (0, 40), (15, 50), (0, 8)))
        for case in cases:
            stock = run(False, *case)
            source = run(True, *case)
            if stock != source:
                raise AssertionError((case, stock, source))
        for kind in ("page", "position"):
            stock = run(False, 0, 0, 0, 15, 0, kind)
            source = run(True, 0, 0, 0, 15, 0, kind)
            if stock != source:
                raise AssertionError((kind, stock, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_WINDOW_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": digest, "native_span": "0x499a5c..0x499c9d",
               "upstream": "third-party/upstream/lvgl/src/widgets/label/lv_label.c",
               "cases": len(cases) + 2,
               "limits": ["Controlled child calls and ASCII text only; bidi and native placement remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases) + 2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare the source-owned default label-layout path with native Apollo."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/display_page_layout_update_49a602.c"
OUT = G2 / "build/c-firmware/20261015/main-page-layout-update-49a602"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = {
    "geometry": 0x43feca,
    "width": 0x451598,
    "metric_font": 0x4993c0,
    "metric_other": 0x4993d4,
    "metric_spacing": 0x4993ca,
    "flags": 0x49abea,
    "prepare": 0x49aacc,
    "measure": 0x489546,
    "finish": 0x43ffa0,
    "invalidate": 0x440656,
    "style": 0x499402,
    "duration_style": 0x49940c,
    "duration_default": 0x4505a2,
    "anim_init": 0x4503d6,
    "anim_set": 0x4506ce,
    "anim_find": 0x450566,
    "anim_limit": 0x4506fc,
    "anim_copy": 0x49a5c0,
    "anim_start": 0x450408,
    "anim_delete": 0x450500,
    "height": 0x4515a4,
    "font_count": 0x4d57f4,
    "utf8_count": 0x489e6e,
    "utf8_length": 0x454768,
    "text_window": 0x499a5c,
    "utf8_bytes": 0x489e14,
    "utf8_previous": 0x489dbc,
    "event_finish": 0x49ab06,
}
NAMES = {
    "geometry": "audio_uart_lv_obj_content_coords_43feca",
    "width": "audio_uart_lv_area_width_451598",
    "metric_font": "audio_uart_page_metric_4993c0",
    "metric_other": "audio_uart_page_metric_4993d4",
    "metric_spacing": "audio_uart_page_metric_4993ca",
    "flags": "audio_uart_page_layout_flags_49abea",
    "prepare": "audio_uart_page_event_prepare_49aacc",
    "measure": "audio_uart_page_event_calculate_489546",
    "finish": "audio_uart_page_relayout_43ffa0",
    "invalidate": "audio_uart_page_invalidate_440656",
    "style": "audio_uart_page_metric_499402",
    "duration_style": "audio_uart_page_metric_49940c",
    "duration_default": "audio_uart_lv_anim_duration_clamp_4505a2",
    "anim_init": "audio_uart_lv_anim_init_4503d6",
    "anim_set": "audio_uart_lv_anim_values_4506ce",
    "anim_find": "audio_uart_page_lv_anim_lookup_450566",
    "anim_limit": "audio_uart_lv_anim_speed_to_time_4506fc",
    "anim_copy": "audio_uart_page_layout_copy_anim_49a5c0",
    "anim_start": "audio_uart_lv_anim_start_450408",
    "anim_delete": "audio_uart_lv_style_unlink_450500",
    "height": "audio_uart_lv_area_height_4515a4",
    "font_count": "audio_uart_font_glyph_advance_4d57f4",
    "utf8_count": "audio_uart_text_utf8_count_489e6e",
    "utf8_length": "audio_uart_lv_string_length_454768",
    "text_window": "audio_uart_page_text_window_499a5c",
    "utf8_bytes": "audio_uart_text_utf8_bytes_for_count_489e14",
    "utf8_previous": "audio_uart_text_utf8_previous_489dbc",
    "event_finish": "audio_uart_page_event_finish_49ab06",
}
SHIM = "#include <stdint.h>\n" + "\n".join(
    f"__attribute__((noinline)) uint32_t {name}(void*a,void*b,void*c,void*d)"
    "{(void)a;(void)b;(void)c;(void)d;return 0;}"
    for name in NAMES.values()
)


def put(cpu, addr, value):
    cpu.mem_write(addr, (value & 0xffffffff).to_bytes(4, "little"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != PAYLOAD_SHA:
        raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        elf = Path(td) / "oracle.elf"
        shim = Path(td) / "shim.c"
        shim.write_text(SHIM)
        subprocess.run([
            "clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
            "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
            "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_layout_update_49a602",
            str(SRC), str(shim), "-o", str(elf),
        ], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, mode, text_present, high_bits, geometry_width=123,
                geometry_height=80, measured_width=40, measured_height=20,
                styled_duration=250, old_offset=0, old_reverse=False,
                style_present=False, utf8_count=6, utf8_length=12,
                initial_bytes=8):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                cpu.mem_write(addr, data)
            cpu.mem_map(0x20000000, 0x400000)
            page = 0x20011000
            cpu.mem_write(page, bytes([0xa5]) * 0x100)
            cpu.mem_write(page + 0x5c, bytes([mode | high_bits]))
            put(cpu, page + 0x2c, 0x20013000 if text_present else 0)
            cpu.mem_write(0x20013000, b"label\0")
            put(cpu, 0x2001400c, 12)
            put(cpu, 0x20015034, old_offset)
            cpu.mem_write(0x2001505c, bytes([2 if old_reverse else 0]))
            cpu.mem_write(0x20016000, bytes(0x60))
            calls = {((syms[NAMES[key]] if compiled else addr) & ~1): key
                     for key, addr in CALLS.items()}
            trace = []

            def hook(cpu, address, size, _):
                key = calls.get(address)
                if key is None:
                    return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                r2 = cpu.reg_read(A.UC_ARM_REG_R2)
                r3 = cpu.reg_read(A.UC_ARM_REG_R3)
                if key in ("metric_font", "metric_other", "metric_spacing",
                           "style", "duration_style"):
                    trace.append((key, r0, r1))
                elif key == "measure":
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    stack_args = tuple(int.from_bytes(cpu.mem_read(sp + offset, 4),
                                                      "little")
                                       for offset in (0, 4, 8))
                    trace.append((key, r1, r2, r3, *stack_args))
                elif key in ("width", "height"):
                    trace.append((key, "stack"))
                elif key == "geometry":
                    trace.append((key, r0, "stack"))
                    put(cpu, r1, 0x12345678)
                elif key == "anim_init":
                    trace.append((key, "stack"))
                    cpu.mem_write(r0, bytes(0x60))
                elif key == "anim_set":
                    trace.append((key, r1, r2))
                elif key == "anim_find":
                    trace.append((key, r0, r1))
                elif key == "anim_limit":
                    trace.append((key, r0, r1, r2))
                elif key in ("anim_start", "anim_copy"):
                    trace.append((key, bytes(cpu.mem_read(r0, 0x60))))
                elif key in ("anim_delete",):
                    trace.append((key, r0, r1))
                elif key == "duration_default":
                    trace.append((key, r0, r1, r2))
                elif key == "font_count":
                    trace.append((key, r0, r1, r2))
                elif key == "text_window":
                    trace.append((key, r0, tuple(int.from_bytes(cpu.mem_read(r1 + i, 4), "little", signed=True)
                                                  for i in (0, 4)), r2))
                elif key == "utf8_bytes":
                    trace.append((key, r0, r1))
                elif key == "utf8_previous":
                    value = int.from_bytes(cpu.mem_read(r1, 4), "little")
                    trace.append((key, r0, value))
                    put(cpu, r1, value - 1)
                elif key == "event_finish":
                    trace.append((key, r0, r1))
                else:
                    trace.append((key, r0))
                if key == "measure":
                    put(cpu, r0, measured_width)
                    put(cpu, r0 + 4, measured_height)
                cpu.reg_write(A.UC_ARM_REG_R0, {
                    "width": geometry_width, "height": geometry_height,
                    "metric_font": 0x20014000, "metric_other": 33,
                    "metric_spacing": 22, "flags": 3,
                    "style": 0x20016000 if style_present else 0,
                    "duration_style": styled_duration,
                    "duration_default": 300,
                    "font_count": 2,
                    "anim_find": 0x20015000 if old_offset or old_reverse else 0,
                    "anim_limit": -15 & 0xffffffff,
                    "utf8_count": utf8_count,
                    "utf8_length": utf8_length,
                    "text_window": 4,
                    "utf8_bytes": initial_bytes,
                }.get(key, 0))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, page)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_layout_update_49a602"] if compiled else 0x49a602
            cpu.emu_start(entry | 1, 0x600000, count=50000)
            return trace, bytes(cpu.mem_read(page, 0x80))

        cases = [(mode, present, high, 123, 80, 40, 20, 250, 0, False, False)
                 for mode, present, high in itertools.product(
                     (0, 4, 5, 15), (False, True), (0, 0x10, 0x60))]
        cases += [(mode, True, high, width, height, mw, mh, duration, old, reverse, style)
                  for mode, high, width, height, mw, mh, duration, old, reverse, style in itertools.product(
                      (2, 3),
                      (0, 0x40), (30, 100), (30, 100), (20, 120),
                      (20, 120), (0, 250), (0, -5), (False, True), (False, True))]
        cases += [(1, True, 0, 80, height, 40, measured, 250, 0, False, False,
                   count, length, initial)
                  for height, measured, count, length, initial in itertools.product(
                      (30, 100), (20, 120), (2, 6), (6, 12), (4, 12))]
        for case in cases:
            stock = run(False, *case)
            source = run(True, *case)
            if stock != source:
                raise AssertionError((case, stock[0], source[0],
                                      [(i, stock[1][i], source[1][i])
                                       for i in range(0x80) if stock[1][i] != source[1][i]]))
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_PAGE_LAYOUT_UPDATE_ORACLE",
        "source": str(SRC.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "official_payload_sha256": digest,
        "native_entry": "0x49a602", "cases": len(cases),
        "limits": ["Native child calls, including 0x499a5c and UTF-8 traversal callbacks, are controlled stubs.",
                   "The full import is not yet bound, and device behavior remains open."],
    }
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))


if __name__ == "__main__":
    main()

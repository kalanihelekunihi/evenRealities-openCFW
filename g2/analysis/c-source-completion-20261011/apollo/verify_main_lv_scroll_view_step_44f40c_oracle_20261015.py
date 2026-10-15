#!/usr/bin/env python3
"""Compare native and C scroll-to-view step with controlled lower providers."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_scroll_view_step_44f40c.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-scroll-view-step-44f40c"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWER = {
    "parent": (0x44dca2, "audio_uart_lv_obj_parent_44dca2"),
    "flag": (0x43e0e0, "audio_uart_lv_obj_has_flag_43e0e0"),
    "dir": (0x44e442, "audio_uart_lv_get_scroll_dir_44e442"),
    "property": (0x44bdea, "audio_uart_lv_style_property_44bdea"),
    "pad_top": (0x44e230, "audio_uart_lv_style_raw_pad_top_44e230"),
    "pad_bottom": (0x44e23a, "audio_uart_lv_style_raw_pad_bottom_44e23a"),
    "pad_left": (0x44e244, "audio_uart_lv_style_raw_pad_left_44e244"),
    "pad_right": (0x44e24e, "audio_uart_lv_style_raw_pad_right_44e24e"),
    "scroll_top": (0x44e4aa, "audio_uart_lv_scroll_top_44e4aa"),
    "scroll_bottom": (0x44e4bc, "audio_uart_lv_scroll_bottom_44e4bc"),
    "scroll_left": (0x44e586, "audio_uart_lv_scroll_left_44e586"),
    "scroll_right": (0x44e67a, "audio_uart_lv_scroll_right_44e67a"),
    "height": (0x43fdda, "audio_uart_lv_obj_height_43fdda"),
    "width": (0x43fd9e, "audio_uart_lv_obj_width_43fd9e"),
    "area_height": (0x4515a4, "audio_uart_lv_area_height_4515a4"),
    "area_width": (0x451598, "audio_uart_lv_area_width_451598"),
    "unlink": (0x450500, "audio_uart_lv_style_unlink_450500"),
    "dispatch": (0x44e884, "audio_uart_lv_scroll_dispatch_44e884"),
}
SHIM = """#include <stdint.h>
void *audio_uart_lv_obj_parent_44dca2(void *x){(void)x;return 0;}
uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *x,uint32_t y){(void)x;(void)y;return 0;}
uint32_t audio_uart_lv_get_scroll_dir_44e442(void *x){(void)x;return 0;}
uint32_t audio_uart_lv_style_property_44bdea(void *x,uint32_t y,uint32_t z)
{(void)x;(void)y;(void)z;return 0;}
int32_t audio_uart_lv_style_raw_pad_top_44e230(void *x,uint32_t y)
{(void)x;(void)y;return 0;}
int32_t audio_uart_lv_style_raw_pad_bottom_44e23a(void *x,uint32_t y)
{(void)x;(void)y;return 0;}
int32_t audio_uart_lv_style_raw_pad_left_44e244(void *x,uint32_t y)
{(void)x;(void)y;return 0;}
int32_t audio_uart_lv_style_raw_pad_right_44e24e(void *x,uint32_t y)
{(void)x;(void)y;return 0;}
int32_t audio_uart_lv_scroll_top_44e4aa(void *x){(void)x;return 0;}
int32_t audio_uart_lv_scroll_bottom_44e4bc(void *x){(void)x;return 0;}
int32_t audio_uart_lv_scroll_left_44e586(void *x){(void)x;return 0;}
int32_t audio_uart_lv_scroll_right_44e67a(void *x){(void)x;return 0;}
int32_t audio_uart_lv_obj_height_43fdda(void *x){(void)x;return 0;}
int32_t audio_uart_lv_obj_width_43fd9e(void *x){(void)x;return 0;}
int32_t audio_uart_lv_area_height_4515a4(const int32_t *x){(void)x;return 0;}
int32_t audio_uart_lv_area_width_451598(const int32_t *x){(void)x;return 0;}
uint32_t audio_uart_lv_style_unlink_450500(void *x,void *y){(void)x;(void)y;return 0;}
void audio_uart_lv_scroll_anim_x_44f3b8(void *x,int32_t y){(void)x;(void)y;}
void audio_uart_lv_scroll_anim_y_44f3d4(void *x,int32_t y){(void)x;(void)y;}
void audio_uart_lv_scroll_dispatch_44e884(void *x,int32_t y,int32_t z,uint32_t a)
{(void)x;(void)y;(void)z;(void)a;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))


def rect(cpu, address, values):
    for i, value in enumerate(values):
        put(cpu, address + 4 * i, value)


def signed(value):
    return value if value < 0x80000000 else value - 0x100000000


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as temporary:
        elf = Path(temporary) / "step.elf"
        shim = Path(temporary) / "shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_scroll_view_step_44f40c",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        names = {parts[2]: int(parts[0], 16)
                 for line in subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                 if len(parts := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(part["p_vaddr"], part.data())
                        for part in ELFFile(stream).iter_segments() if part["p_type"] == "PT_LOAD"]

        def run(compiled, flagged, vmode, hmode, dirs, area, own, initial, animate):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, payload)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            obj, parent, spec, requested, offset = (
                0x20010000, 0x20011000, 0x20012000, 0x20013000, 0x20014000)
            cpu.mem_write(obj, bytes(0x80))
            cpu.mem_write(parent, bytes(0x80))
            cpu.mem_write(spec, bytes(0x80))
            put(cpu, parent + 8, spec)
            rect(cpu, parent + 0x14, (0, 0, 99, 99))
            rect(cpu, obj + 0x14, own)
            rect(cpu, requested, area)
            rect(cpu, offset, initial)
            cpu.mem_write(spec + 0x32, ((vmode << 4) | (hmode << 2)).to_bytes(2, "little"))
            hooks = {native & ~1: key for key, (native, _) in LOWER.items()}
            if compiled:
                hooks = {names[source] & ~1: key for key, (_, source) in LOWER.items()}
            trace = []

            def hook(uc, address, size, unused):
                key = hooks.get(address)
                if key is None:
                    return
                r0, r1, r2, r3 = (uc.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if key == "parent":
                    trace.append((key, r0))
                    result = parent
                elif key == "flag":
                    trace.append((key, r0, r1))
                    result = int(flagged)
                elif key == "dir":
                    trace.append((key, r0))
                    result = dirs
                elif key == "property":
                    trace.append((key, r0, r1, r2))
                    result = {0x30: 2, 0x34: 0x0f}[r2]
                elif key.startswith("pad_"):
                    trace.append((key, r0, r1))
                    result = {"pad_top": 3, "pad_bottom": 4,
                              "pad_left": 5, "pad_right": 6}[key]
                elif key.startswith("scroll_"):
                    trace.append((key, r0))
                    result = 20
                elif key in ("width", "height"):
                    trace.append((key, r0))
                    result = 100
                elif key in ("area_width", "area_height"):
                    vals = [signed(int.from_bytes(uc.mem_read(r0 + i * 4, 4), "little"))
                            for i in range(4)]
                    result = (vals[2] - vals[0] + 1) if key == "area_width" else \
                        (vals[3] - vals[1] + 1)
                    trace.append((key, r0))
                elif key == "unlink":
                    trace.append((key, r0))
                    result = 0
                elif key == "dispatch":
                    trace.append((key, r0, signed(r1), signed(r2), r3 & 0xff))
                    result = 0
                else:
                    raise AssertionError(key)
                uc.reg_write(A.UC_ARM_REG_R0, result & 0xffffffff)
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, requested)
            cpu.reg_write(A.UC_ARM_REG_R1, obj)
            cpu.reg_write(A.UC_ARM_REG_R2, offset)
            cpu.reg_write(A.UC_ARM_REG_R3, animate)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = names["audio_uart_lv_scroll_view_step_44f40c"] if compiled else 0x44f40c
            try:
                cpu.emu_start(entry | 1, 0x600000, count=100000)
            except Exception as error:
                raise RuntimeError((compiled, flagged, vmode, hmode, dirs,
                                    hex(cpu.reg_read(A.UC_ARM_REG_PC)), trace)) from error
            return trace, bytes(cpu.mem_read(offset, 8)), bytes(cpu.mem_read(obj, 0x80))

        cases = [(False, 0, 0, 15, (10, 10, 20, 20), (10, 10, 20, 20), (0, 0), 0)]
        for vmode in range(4):
            for hmode in range(4):
                cases.append((True, vmode, hmode, 15,
                              (-10, -15, 30, 45), (-5, -8, 40, 50), (2, -3), 1))
        for dirs in (0, 1, 2, 4, 8, 15):
            cases.append((True, 0, 0, dirs,
                          (-20, 80, 130, 160), (-5, -8, 40, 50), (0, 0), 0))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                first = next(((i, a, b) for i, (a, b) in enumerate(zip(native[0], source[0]))
                              if a != b), None)
                raise AssertionError((case, first, len(native[0]), len(source[0]),
                                      native[1] == source[1], native[2] == source[2]))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_SCROLL_VIEW_STEP_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x44f40c..0x44f703", "cases": len(cases),
               "limits": ["Alignment modes, direction masks and offset writes native-compared with controlled style and scroll providers.",
                          "Live LVGL geometry, animation cancellation and dispatch remain lower-provider behavior."]}
    path = OUT / "oracle.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(path))


if __name__ == "__main__":
    main()

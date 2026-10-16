#!/usr/bin/env python3
"""Compare all LVGL image event branches with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_image_event_498c9c.c"
OUT = G2 / "build/c-firmware/20261016/main-lv-image-event-498c9c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OBJECT, EVENT, PARAM, POINT = 0x20001000, 0x20002000, 0x20003000, 0x20004000
CALLS = (("audio_uart_page_event_code_450286", 0x450286),
         ("audio_uart_lv_object_event_base_4516f8", 0x4516f8),
         ("audio_uart_lv_image_get_pivot_498b82", 0x498b82),
         ("audio_uart_page_498680", 0x498680),
         ("audio_uart_lv_refresh_draw_452d42", 0x452d42),
         ("audio_uart_lv_image_update_align_4992cc", 0x4992cc),
         ("audio_uart_lv_obj_width_43fd9e", 0x43fd9e),
         ("audio_uart_lv_obj_height_43fdda", 0x43fdda),
         ("audio_uart_ambiq_transform_area_488cda", 0x488cda),
         ("audio_uart_lv_get_click_area_4408b0", 0x4408b0),
         ("audio_uart_lv_round_corner_450dd4", 0x450dd4),
         ("audio_uart_lv_image_draw_498ec0", 0x498ec0))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "lv-image-event-oracle-stub.c"
    stub.write_text("#include <stdint.h>\n"
                    "const uint8_t audio_uart_image_class_756108[36]={0};\n"
                    "__attribute__((noinline,used)) uint32_t audio_uart_page_event_code_450286(const void*a){(void)a;return 0;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_uart_lv_object_event_base_4516f8(const void*a,void*b){(void)a;(void)b;return 0;}\n"
                    "__attribute__((noinline,used)) void audio_uart_lv_image_get_pivot_498b82(void*a,void*b){(void)a;(void)b;}\n"
                    "__attribute__((noinline,used)) void audio_uart_page_498680(void*a,const void*b){(void)a;(void)b;}\n"
                    "__attribute__((noinline,used)) void audio_uart_lv_refresh_draw_452d42(void*a){(void)a;}\n"
                    "__attribute__((noinline,used)) void audio_uart_lv_image_update_align_4992cc(void*a){(void)a;}\n"
                    "__attribute__((noinline,used)) int32_t audio_uart_lv_obj_width_43fd9e(void*a){(void)a;return 0;}\n"
                    "__attribute__((noinline,used)) int32_t audio_uart_lv_obj_height_43fdda(void*a){(void)a;return 0;}\n"
                    "__attribute__((noinline,used)) void audio_uart_ambiq_transform_area_488cda(void*a,int32_t b,int32_t c,int32_t d,int32_t e,int32_t f,const void*g){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;}\n"
                    "__attribute__((noinline,used)) void audio_uart_lv_get_click_area_4408b0(void*a,void*b){(void)a;(void)b;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_uart_lv_round_corner_450dd4(const int32_t*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\n"
                    "__attribute__((noinline,used)) void audio_uart_lv_image_draw_498ec0(void*a){(void)a;}\n")
    elf = OUT / "lv-image-event-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_image_event_498c9c",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, code, base_result, source_type, transformed,
            exact_size, param_value):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(OBJECT, bytes(((i * 11 + 3) & 255 for i in range(0x60))))
        put = lambda addr, value: u.mem_write(addr, struct.pack("<I", value & 0xffffffff))
        put(OBJECT + 0x2c, 0x20005000)
        put(OBJECT + 0x3c, 100 if exact_size else 101)
        put(OBJECT + 0x40, 60)
        put(OBJECT + 0x44, 17 if transformed else 0)
        put(OBJECT + 0x48, 0x100)
        put(OBJECT + 0x4c, 0x100)
        put(OBJECT + 0x50, 50)
        put(OBJECT + 0x54, 30)
        put(OBJECT + 0x58, source_type | (0xb00 if code == 0x31 else 0))
        put(OBJECT + 0x14, 12)
        put(OBJECT + 0x18, 25)
        put(EVENT, OBJECT)
        put(EVENT + 0x10, PARAM)
        put(PARAM, POINT if code == 0x16 else param_value)
        put(PARAM + 4, 0x77777777)
        u.mem_write(POINT, struct.pack("<2i", 27, 38))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address) in enumerate(CALLS)}
        class_pointer = symbols["audio_uart_image_class_756108"] if compiled else 0x756108
        trace = []

        def words(cpu, address, count):
            return struct.unpack("<" + "i" * count,
                                 bytes(cpu.mem_read(address, count * 4)))

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
                trace.append(("code", a))
                ret = code
            elif i == 1:
                trace.append(("base", "image-class" if a == class_pointer else a, b))
                ret = base_result
            elif i == 2:
                trace.append(("pivot", a))
                cpu.mem_write(b, struct.pack("<2i", 7, 9))
            elif i == 3:
                trace.append(("source", a, b))
            elif i == 4:
                trace.append(("refresh", a))
            elif i == 5:
                trace.append(("align", a))
            elif i == 6:
                trace.append(("width", a))
                ret = 100
            elif i == 7:
                trace.append(("height", a))
                ret = 60
            elif i == 8:
                sx, sy, pivot_ptr = struct.unpack("<3I", bytes(cpu.mem_read(sp, 12)))
                trace.append(("transform", b, c, d, sx, sy, words(cpu, pivot_ptr, 2)))
                cpu.mem_write(a, struct.pack("<4i", -10, -20, b + 10, c + 20))
            elif i == 9:
                trace.append(("click", a))
                cpu.mem_write(b, struct.pack("<4i", 0, 0, 100, 60))
            elif i == 10:
                trace.append(("hit", words(cpu, a, 4), b, c))
                ret = 1
            else:
                trace.append(("draw", a))
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, class_pointer)
        u.reg_write(A.UC_ARM_REG_R1, EVENT)
        entry = symbols["audio_uart_lv_image_event_498c9c"] if compiled else 0x498c9c
        u.emu_start(entry | 1, 0x600000, count=10000)
        return trace, bytes(u.mem_read(OBJECT, 0x60)), bytes(u.mem_read(PARAM, 8))

    cases = 0
    for code in (0x32, 0x1b, 0x31, 0x16, 0x34, 0x1d, 0x20, 0x1a, 0x77):
        for base_result in (0, 1):
            for source_type in (0, 2, 3):
                for transformed in (False, True):
                    for exact_size in (False, True):
                        for param_value in (0, 15):
                            case = (code, base_result, source_type, transformed,
                                    exact_size, param_value)
                            stock, selected = run(False, *case), run(True, *case)
                            if stock != selected:
                                raise RuntimeError(f"image event mismatch {case}: {stock[0]} != {selected[0]}; object_equal={stock[1] == selected[1]}; param_equal={stock[2] == selected[2]}")
                            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_EVENT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "All event code branches with controlled lower-call traces and state",
              "limits": ["Lower effects, arbitrary transforms and malformed event pointers outside bounded oracle; draw helper remains open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))


if __name__ == "__main__":
    main()

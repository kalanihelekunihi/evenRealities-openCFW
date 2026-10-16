#!/usr/bin/env python3
"""Compare LVGL image constructor and destroyer with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_image_lifecycle_498bd0.c"
OUT = G2 / "build/c-firmware/20261016/main-lv-image-lifecycle-498bd0"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OBJECT = 0x20001000
CALLS = (("audio_uart_lv_obj_width_43fd9e", 0x43fd9e),
         ("audio_uart_lv_obj_height_43fdda", 0x43fdda),
         ("audio_lv_object_clear_flag_43dfa4", 0x43dfa4),
         ("audio_lv_object_call_43ded4", 0x43ded4),
         ("audio_uart_lv_heap_free", 0x44f758))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "lv-image-lifecycle-oracle-stub.c"
    stub.write_text("#include <stdint.h>\n"
                    "const uint8_t audio_uart_image_class_756108[36]={0};\n"
                    "__attribute__((noinline,used)) int32_t audio_uart_lv_obj_width_43fd9e(void*a){(void)a;return 0;}\n"
                    "__attribute__((noinline,used)) int32_t audio_uart_lv_obj_height_43fdda(void*a){(void)a;return 0;}\n"
                    "__attribute__((noinline,used)) void audio_lv_object_clear_flag_43dfa4(uint32_t a,uint32_t b){(void)a;(void)b;}\n"
                    "__attribute__((noinline,used)) void audio_lv_object_call_43ded4(uint32_t a,uint32_t b){(void)a;(void)b;}\n"
                    "__attribute__((noinline,used)) void audio_uart_lv_heap_free(void*a){(void)a;}\n")
    elf = OUT / "lv-image-lifecycle-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_image_ctor_498bd0",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, kind, flags, source_pointer, width, height):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(OBJECT, bytes(((i * 13 + 7) & 255 for i in range(0x60))))
        u.mem_write(OBJECT + 0x2c, struct.pack("<I", source_pointer))
        u.mem_write(OBJECT + 0x58, struct.pack("<I", flags))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address) in enumerate(CALLS)}
        trace = []

        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            a, b = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
            trace.append((i, a, b) if i in (2, 3) else (i, a))
            ret = width if i == 0 else height if i == 1 else 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, 0x20008000)
        u.reg_write(A.UC_ARM_REG_R1, OBJECT)
        name = f"audio_uart_lv_image_{kind}_{'498bd0' if kind == 'ctor' else '498c6c'}"
        entry = symbols[name] if compiled else (0x498bd0 if kind == "ctor" else 0x498c6c)
        u.emu_start(entry | 1, 0x600000, count=2000)
        state = bytearray(u.mem_read(OBJECT, 0x60))
        if kind == "ctor":
            if state[0x50:0x54] != struct.pack("<I", 0x20000032) or \
                    state[0x54:0x58] != struct.pack("<I", 0x20000032):
                raise RuntimeError("image constructor encoded 50 percent pivot changed")
        return trace, bytes(state)

    cases = 0
    for kind in ("ctor", "dtor"):
        for flags in (0, 1, 2, 3, 0x80, 0x900, 0xfeedcafe):
            for pointer in (0, 0x20003000):
                for width, height in ((0, 0), (320, 240), (0xffffffff, 0x80000000)):
                    case = (kind, flags, pointer, width, height)
                    stock, selected = run(False, *case), run(True, *case)
                    if stock != selected:
                        raise RuntimeError(f"image lifecycle mismatch {case}: {stock[0]} != {selected[0]}; state_equal={stock[1] == selected[1]}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_LIFECYCLE_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Image constructor state, dimensions, flags and destructor ownership branches",
              "limits": ["LVGL geometry, flag and heap effects isolated; image event callback remains open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))


if __name__ == "__main__":
    main()

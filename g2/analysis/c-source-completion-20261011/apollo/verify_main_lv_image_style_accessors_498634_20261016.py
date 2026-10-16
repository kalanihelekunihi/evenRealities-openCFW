#!/usr/bin/env python3
"""Compare LVGL image style opacity and radius wrappers with stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_image_style_accessors_498634.c"
OUT = G2 / "build/c-firmware/20261016/main-lv-image-style-accessors-498634"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "image-style-accessors-oracle-stub.c"
    stub.write_text("#include <stdint.h>\n"
                    "__attribute__((noinline,used)) uint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\n")
    elf = OUT / "image-style-accessors-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_image_style_opa_498634",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, kind, object, part, value):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        cut = (symbols["audio_uart_lv_style_property_44bdea"] if compiled else 0x44bdea) & ~1
        trace = []

        def hook(cpu, pc, size, _):
            if pc != cut:
                return
            trace.append(tuple(cpu.reg_read(reg) for reg in
                               (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                A.UC_ARM_REG_R2)))
            cpu.reg_write(A.UC_ARM_REG_R0, value)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, object)
        u.reg_write(A.UC_ARM_REG_R1, part)
        name = "audio_uart_lv_image_style_opa_498634" if kind == "opa" else "audio_uart_lv_image_style_radius_49865e"
        entry = symbols[name] if compiled else (0x498634 if kind == "opa" else 0x49865e)
        u.emu_start(entry | 1, 0x600000, count=1000)
        return trace, u.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for kind in ("opa", "radius"):
        for object in (0, 0x20001000, 0x20002000):
            for part in (0, 0x40000, 0xffffffff):
                for value in (0, 1, 0xff, 0x12345678, 0xffffffff):
                    case = (kind, object, part, value)
                    stock, selected = run(False, *case), run(True, *case)
                    if stock != selected:
                        raise RuntimeError(f"image style mismatch {case}: {stock} != {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_STYLE_ACCESSORS_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Opacity truncation, radius return, property IDs, object and part forwarding",
              "limits": ["Style-property provider effects isolated; final placement remains open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))


if __name__ == "__main__":
    main()

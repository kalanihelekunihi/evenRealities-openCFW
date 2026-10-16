#!/usr/bin/env python3
"""Compare LVGL click-area copy and padding with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_click_area_4408b0.c"
OUT = G2 / "build/c-firmware/20261016/main-lv-click-area-4408b0"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OBJECT, SPECIAL, AREA = 0x20001000, 0x20002000, 0x20003000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "lv-click-area-oracle-stub.c"
    stub.write_text("#include <stdint.h>\n"
                    "__attribute__((noinline,used)) void audio_uart_lv_area_copy_43ee94(void*a,const void*b){(void)a;(void)b;}\n"
                    "__attribute__((noinline,used)) void audio_uart_lv_area_expand_450b98(void*a,int32_t b,int32_t c){(void)a;(void)b;(void)c;}\n")
    elf = OUT / "lv-click-area-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_get_click_area_4408b0",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, coords, has_special, pad):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(OBJECT + 8, struct.pack("<I", SPECIAL if has_special else 0))
        u.mem_write(OBJECT + 0x14, struct.pack("<4i", *coords))
        u.mem_write(SPECIAL + 0x28, struct.pack("<i", pad))
        u.mem_write(AREA, bytes(16))
        cuts = {(symbols["audio_uart_lv_area_copy_43ee94"] if compiled else 0x43ee94) & ~1: 0,
                (symbols["audio_uart_lv_area_expand_450b98"] if compiled else 0x450b98) & ~1: 1}
        trace = []

        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            a, b, c = (cpu.reg_read(reg) for reg in
                       (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if i == 0:
                trace.append(("copy", a, b))
                cpu.mem_write(a, bytes(cpu.mem_read(b, 16)))
            else:
                trace.append(("expand", a, b, c))
                x1, y1, x2, y2 = struct.unpack("<4i", bytes(cpu.mem_read(a, 16)))
                signed = lambda x: x if x < 0x80000000 else x - 0x100000000
                cpu.mem_write(a, struct.pack("<4i", signed((x1 - b) & 0xffffffff),
                                             signed((y1 - c) & 0xffffffff),
                                             signed((x2 + b) & 0xffffffff),
                                             signed((y2 + c) & 0xffffffff)))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, OBJECT)
        u.reg_write(A.UC_ARM_REG_R1, AREA)
        entry = symbols["audio_uart_lv_get_click_area_4408b0"] if compiled else 0x4408b0
        u.emu_start(entry | 1, 0x600000, count=1000)
        return trace, bytes(u.mem_read(AREA, 16))

    cases = 0
    for coords in ((0, 0, 0, 0), (10, 20, 40, 60), (-100, 25, 50, 120)):
        for has_special in (False, True):
            for pad in (-8, -1, 0, 1, 5, 0x7fff):
                case = (coords, has_special, pad)
                stock, selected = run(False, *case), run(True, *case)
                if stock != selected:
                    raise RuntimeError(f"click area mismatch {case}: {stock} != {selected}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_MAIN_LV_CLICK_AREA_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Object coordinates, optional special click pad and two lower calls",
              "limits": ["Area helpers isolated and concurrent object changes outside bounded oracle."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))


if __name__ == "__main__":
    main()

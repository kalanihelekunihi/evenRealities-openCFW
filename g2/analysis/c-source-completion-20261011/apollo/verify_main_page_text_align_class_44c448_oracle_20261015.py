#!/usr/bin/env python3
"""Compare text align resolver with native LVGL wrappers."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/display_page_text_align_class_44c448.c"
OUT = G2 / "build/c-firmware/20261015/main-page-text-align-class-44c448"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM = "#include <stdint.h>\n__attribute__((noinline)) uint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\n"


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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_text_align_class_44c448",
                        str(SRC), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, align, direction):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                cpu.mem_write(addr, data)
            cpu.mem_map(0x20000000, 0x400000)
            cpu.mem_write(0x20011000, bytes(0x100))
            cpu.mem_write(0x20013000, b"hello\0")
            trace = []
            getters = {0x44b8ac: (0x5e, align), 0x44b8f6: (0x27, direction)}
            style = syms["audio_uart_lv_style_property_44bdea"] & ~1

            def hook(cpu, address, size, _):
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                r2 = cpu.reg_read(A.UC_ARM_REG_R2)
                if compiled and address == style:
                    trace.append((r0, r1, r2))
                    result = align if r2 == 0x5e else direction
                elif not compiled and address in getters:
                    prop, result = getters[address]
                    trace.append((r0, r1, prop))
                else:
                    return
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            for reg, value in ((A.UC_ARM_REG_R0, 0x20011000),
                               (A.UC_ARM_REG_R1, 0),
                               (A.UC_ARM_REG_R2, 0x20013000),
                               (A.UC_ARM_REG_SP, 0x203ff000),
                               (A.UC_ARM_REG_LR, 0x600001)):
                cpu.reg_write(reg, value)
            entry = syms["audio_uart_page_text_align_class_44c448"] if compiled else 0x44c448
            cpu.emu_start(entry | 1, 0x600000, count=10000)
            return trace, cpu.reg_read(A.UC_ARM_REG_R0) & 0xff

        cases = list(itertools.product((0, 1, 2, 3, 255), repeat=2))
        for case in cases:
            stock, source = run(False, *case), run(True, *case)
            if stock != source:
                raise AssertionError((case, stock, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_ALIGN_CLASS_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": digest,
               "native_spans": ["0x44c448..0x44c46f", "0x44b8ac", "0x44b8f6", "0x44b7b4"],
               "cases": len(cases),
               "limits": ["Style getters are controlled; unrelated bidi configurations are not covered."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))


if __name__ == "__main__":
    main()

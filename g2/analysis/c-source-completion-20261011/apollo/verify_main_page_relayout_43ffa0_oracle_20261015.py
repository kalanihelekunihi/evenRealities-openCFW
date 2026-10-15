#!/usr/bin/env python3
"""Native/C relayout branch and style-query comparison."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_relayout_43ffa0.c"
OUT = G2 / "build/c-firmware/20261015/main-page-relayout-43ffa0"
LOWER = {"width": (0x43eea6, "audio_uart_lv_style_width_43eea6"),
         "height": (0x43eec4, "audio_uart_lv_style_height_43eec4"),
         "mark": (0x43f648, "audio_uart_lv_mark_layout_43f648")}
SHIM = '''#include <stdint.h>
int32_t audio_uart_lv_style_width_43eea6(void*a,uint32_t b){return 0;}
int32_t audio_uart_lv_style_height_43eec4(void*a,uint32_t b){return 0;}
void audio_uart_lv_mark_layout_43f648(void*a){}
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "test.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_relayout_43ffa0",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, width, height, object_value):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            cuts = {(syms[symbol] & ~1) if compiled else addr: op
                    for op, (addr, symbol) in LOWER.items()}
            trace = []

            def hook(cpu, address, size, unused):
                op = cuts.get(address)
                if op is None:
                    return
                r0, r1 = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
                trace.append((op, r0, r1 if op != "mark" else None))
                if op in ("width", "height"):
                    cpu.reg_write(A.UC_ARM_REG_R0, width if op == "width" else height)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, object_value)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_relayout_43ffa0"] if compiled else 0x43ffa0
            u.emu_start(entry | 1, 0x600000, count=10000)
            return u.reg_read(A.UC_ARM_REG_R0), trace

        values = (0, 1, 0x3fffffff, 0xffffffff)
        cases = 0
        for width, height, object_value in itertools.product(values, values,
                                                              (0, 0x20010000)):
            native, source = run(False, width, height, object_value), run(True, width, height, object_value)
            if native != source:
                raise AssertionError((width, height, object_value, native, source))
            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_RELAYOUT_43FFA0_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": digest, "native_span": "0x43ffa0..0x43ffcf",
               "cases": cases,
               "limits": ["Three lower style/layout calls are controlled at native boundaries.",
                          "Return and call arguments are compared; hardware display remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases)


if __name__ == "__main__":
    main()

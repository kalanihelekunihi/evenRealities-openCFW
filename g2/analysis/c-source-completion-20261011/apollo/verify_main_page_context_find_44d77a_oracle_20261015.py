#!/usr/bin/env python3
"""Compare Apollo input-to-page lookup with compiled C."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_context_find_44d77a.c"
OUT = G2 / "build/c-firmware/20261015/main-page-context-find-44d77a"
SHIM = "void *audio_uart_lv_input_next_452edc(void *p){return 0;}\n"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_context_find_44d77a",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, kinds, match_index):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            page, inputs = 0x20010000, [0x20012000, 0x20012100, 0x20012200]
            for index, addr in enumerate(inputs[:len(kinds)]):
                data = bytearray(0xc0)
                data[0] = kinds[index]
                data[0xb8:0xbc] = (page if index == match_index else page+4).to_bytes(4, "little")
                u.mem_write(addr, bytes(data))
            cut = (syms["audio_uart_lv_input_next_452edc"] & ~1) if compiled else 0x452edc
            trace = []

            def hook(cpu, address, size, unused):
                if address != cut:
                    return
                arg = cpu.reg_read(A.UC_ARM_REG_R0)
                trace.append(arg)
                index = inputs.index(arg)+1 if arg in inputs else 0
                cpu.reg_write(A.UC_ARM_REG_R0, inputs[index] if index < len(kinds) else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, page)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_context_find_44d77a"] if compiled else 0x44d77a
            u.emu_start(entry | 1, 0x600000, count=100000)
            return u.reg_read(A.UC_ARM_REG_R0), trace

        cases = []
        for length in range(4):
            for kinds in itertools.product((0, 1, 2), repeat=length):
                for match_index in range(-1, length):
                    cases.append((kinds, match_index))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_CONTEXT_FIND_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x44d77a..0x44d7b5",
               "cases": len(cases),
               "limits": ["LVGL input iterator is controlled; return and iterator trace are compared.",
                          "Input layout beyond type byte and page pointer at +0xb8 is not validated."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))


if __name__ == "__main__":
    main()

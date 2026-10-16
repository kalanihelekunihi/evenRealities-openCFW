#!/usr/bin/env python3
"""Compare the Terminal theme wrapper's four calls to pinned stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_theme_5e47cc.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-theme-5e47cc"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = [(0x44122a, "audio_uart_page_44122a"),
         (0x441238, "audio_uart_page_441238"),
         (0x44120e, "audio_uart_page_44120e"),
         (0x44121c, "audio_uart_page_44121c")]
STUB = """#include <stdint.h>
#define V3(n) void n(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
V3(audio_uart_page_44122a)
V3(audio_uart_page_441238)
V3(audio_uart_page_44120e)
V3(audio_uart_page_44121c)
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "theme-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "theme-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_theme_5e47cc",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, values):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        cuts = {((symbols[name] & ~1) if compiled else address): name
                for address, name in CALLS}
        trace = []
        def hook(cpu, pc, size, _):
            name = cuts.get(pc)
            if name is None:
                return
            trace.append((name, *(cpu.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2), values):
            u.reg_write(reg, value)
        entry = symbols["audio_terminal_ui_theme_5e47cc"] if compiled else 0x5e47cc
        u.emu_start(entry|1, 0x600000, count=10000)
        return trace

    cases = 0
    for values in ((0, 0, 0), (0x20041000, 0, 0),
                   (0x20042000, 0xff, 0), (0x20043000, 0x12345678, 0xffffffff)):
        stock, selected = run(False, values), run(True, values)
        if stock != selected:
            raise RuntimeError(f"Terminal theme mismatch {values}: {stock} vs {selected}")
        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_THEME_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "four ordered LVGL setter calls and argument tuples",
              "limits": ["LVGL setter effects, object lifetime, concurrency and hardware behavior remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

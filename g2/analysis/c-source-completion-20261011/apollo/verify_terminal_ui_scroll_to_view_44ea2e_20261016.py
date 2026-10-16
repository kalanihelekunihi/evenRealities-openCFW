#!/usr/bin/env python3
"""Compare LVGL one-step scroll-to-view wrapper to stock call cuts."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_scroll_to_view_44ea2e.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-scroll-to-view-44ea2e"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
void audio_uart_page_43f66c(void*a){(void)a;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_lv_scroll_view_step_44f40c(void*a,void*b,void*c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "scroll-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "scroll-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_scroll_to_view_44ea2e",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, object_value, animation):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        update = (symbols["audio_uart_page_43f66c"] if compiled else 0x43f66c)&~1
        zero = (symbols["audio_uart_buffer_zero"] if compiled else 0x43bb00)&~1
        step = (symbols["audio_uart_lv_scroll_view_step_44f40c"] if compiled else 0x44f40c)&~1
        trace = []
        def hook(cpu, pc, size, _):
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if pc == update:
                trace.append(("update", r0))
            elif pc == zero:
                length, value = (r1, r2) if compiled else (r2, r1)
                trace.append(("zero", length, value))
                cpu.mem_write(r0, bytes((value & 0xff,))*length)
            elif pc == step:
                trace.append(("step", r0 == object_value+0x14,
                              r1 == object_value, bytes(cpu.mem_read(r2, 8)).hex(), r3))
            else:
                return
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, object_value)
        u.reg_write(A.UC_ARM_REG_R1, animation)
        entry = symbols["audio_terminal_ui_scroll_to_view_44ea2e"] if compiled else 0x44ea2e
        u.emu_start(entry|1, 0x600000, count=10000)
        return trace

    cases = 0
    for obj in (0x20041000, 0x20042000, 0x20043000):
        for animation in (0, 1, 0xff, 0x100, 0x101, 0xffffffff):
            stock, selected = run(False, obj, animation), run(True, obj, animation)
            if stock != selected:
                raise RuntimeError(f"scroll wrapper mismatch {obj=} {animation=}: "
                                   f"{stock} vs {selected}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_SCROLL_TO_VIEW_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "layout update, 8-byte zero and scroll-step argument order",
              "limits": ["LVGL layout and scroll-step effects, object lifetime and hardware remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

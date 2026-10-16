#!/usr/bin/env python3
"""Compare Terminal UI start call order and root assignment against stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_start_5e716c.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-start-5e716c"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = [(0x43de82, "audio_uart_page_43de82", 1),
         (0x43dfa4, "audio_uart_page_43dfa4", 2),
         (0x43f4c0, "audio_uart_page_43f4c0", 3),
         (0x43f09a, "audio_uart_page_43f09a", 3),
         (0x44104c, "audio_uart_page_44104c", 1),
         (0x44127e, "audio_uart_page_44127e", 3),
         (0x44129e, "audio_uart_page_44129e", 3),
         (0x44131c, "audio_uart_page_44131c", 3),
         (0x44133a, "audio_uart_page_44133a", 3),
         (0x441378, "audio_uart_page_441378", 3),
         (0x441386, "audio_uart_page_441386", 3),
         (0x44146a, "audio_uart_page_44146a", 3),
         (0x5e47cc, "audio_terminal_ui_theme_5e47cc", 3),
         (0x441246, "audio_uart_page_441246", 3),
         (0x58966c, "audio_terminal_list_anim_init_58966c", 0)]
STUB = """#include <stdint.h>
uint32_t audio_terminal_display_queue_handle;
uint32_t audio_uart_page_43de82(uint32_t a){return a;}
uint32_t audio_uart_page_44104c(uint32_t a){return a;}
#define V2(n) void n(uint32_t a,uint32_t b){(void)a;(void)b;}
#define V3(n) void n(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
V2(audio_uart_page_43dfa4)
V3(audio_uart_page_43f4c0)
V3(audio_uart_page_43f09a)
V3(audio_uart_page_44127e)
V3(audio_uart_page_44129e)
V3(audio_uart_page_44131c)
V3(audio_uart_page_44133a)
V3(audio_uart_page_441378)
V3(audio_uart_page_441386)
V3(audio_uart_page_44146a)
V3(audio_terminal_ui_theme_5e47cc)
V3(audio_uart_page_441246)
void audio_terminal_list_anim_init_58966c(void){}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e7b70-0x438000:0x5e7b74-0x438000], "little") != 0x20074a90:
        raise RuntimeError("Terminal start stock pointer changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "start-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "start-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_start_5e716c",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    stock_cuts = {address: (name, count) for address, name, count in CALLS}
    compiled_cuts = {symbols[name] & ~1: (name, count) for _, name, count in CALLS}

    def run(compiled, root, color):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        queue = symbols["audio_terminal_display_queue_handle"] if compiled else 0x20074a90
        u.mem_write(queue, struct.pack("<I", 0xa5a5a5a5))
        cuts = compiled_cuts if compiled else stock_cuts
        trace = []
        def hook(cpu, pc, size, _):
            cut = cuts.get(pc)
            if cut is None:
                return
            name, count = cut
            values = tuple(cpu.reg_read(reg) for reg in
                           (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            trace.append((name, *values[:count]))
            if name == "audio_uart_page_43de82":
                cpu.reg_write(A.UC_ARM_REG_R0, root)
            elif name == "audio_uart_page_44104c":
                cpu.reg_write(A.UC_ARM_REG_R0, color)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, 0)
        entry = symbols["audio_terminal_ui_start_5e716c"] if compiled else 0x5e716c
        u.emu_start(entry|1, 0x600000, count=20000)
        return trace, int.from_bytes(u.mem_read(queue, 4), "little")

    cases = 0
    for root in (0, 0x20041000, 0x20042000):
        for color in (0, 0xffffff, 0x123456):
            stock, selected = run(False, root, color), run(True, root, color)
            if stock != selected:
                raise RuntimeError(f"Terminal start mismatch {root=} {color=}: "
                                   f"{stock} vs {selected}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_START_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "root assignment and 15 lower-call argument/order traces",
              "limits": ["LVGL lower-call effects, root RAM final placement, concurrent UI and hardware behavior remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

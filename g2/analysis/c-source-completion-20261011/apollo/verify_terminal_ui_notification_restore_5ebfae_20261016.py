#!/usr/bin/env python3
"""Compare Terminal notification restore's conditional lower calls."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_notification_restore_5ebfae.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-notification-restore-5ebfae"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
const char *audio_uart_page_49942e(uint8_t*a,const char*b){(void)a;(void)b;return 0;}
void audio_terminal_ui_scroll_to_view_44ea2e(void*a,uint32_t b){(void)a;(void)b;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5ec2e4-0x438000:0x5ec2e8-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Terminal notification state pointer changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "restore-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "restore-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_notification_restore_5ebfae",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, label, pane, scroll, record):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        base = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(base, b"\xa5"*0x2a0)
        for off, value in ((0x1fc, label), (0x1f4, pane), (0x200, scroll)):
            u.mem_write(base+off, struct.pack("<I", value))
        label_set = (symbols["audio_uart_page_49942e"] if compiled else 0x49942e)&~1
        scroll_to = (symbols["audio_terminal_ui_scroll_to_view_44ea2e"] if compiled else 0x44ea2e)&~1
        trace = []
        def hook(cpu, pc, size, _):
            if pc == label_set:
                trace.append(("label", cpu.reg_read(A.UC_ARM_REG_R0),
                              cpu.reg_read(A.UC_ARM_REG_R1)))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            elif pc == scroll_to:
                trace.append(("scroll", cpu.reg_read(A.UC_ARM_REG_R0),
                              cpu.reg_read(A.UC_ARM_REG_R1)))
            else:
                return
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, record)
        entry = symbols["audio_terminal_ui_notification_restore_5ebfae"] if compiled else 0x5ebfae
        u.emu_start(entry|1, 0x600000, count=10000)
        return trace, bytes(u.mem_read(base, 0x2a0)).hex()

    cases = 0
    for label in (0, 0x20041000):
        for pane in (0, 0x20042000):
            for scroll in (0, 0x20043000):
                for record in (0, 0x20044000, 0xdeadbeef):
                    stock = run(False, label, pane, scroll, record)
                    selected = run(True, label, pane, scroll, record)
                    if stock != selected:
                        raise RuntimeError(f"restore mismatch {label=} {pane=} {scroll=} "
                                           f"{record=}: {stock[0]} vs {selected[0]}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_NOTIFICATION_RESTORE_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "label, pane and scroll branches with argument and state comparison",
              "limits": ["Lower label/scroll effects, shared Terminal RAM allocation and hardware remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

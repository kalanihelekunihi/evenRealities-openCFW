#!/usr/bin/env python3
"""Compare Terminal query-dismiss FSM action with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_dismiss_query_5e68b4.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-dismiss-query-5e68b4"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void audio_td_dismiss_query_notification(uint32_t a){(void)a;}
int32_t audio_terminal_ui_restore_query_5e6620(uint32_t a){(void)a;return 0;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e7268-0x438000:0x5e726c-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Apollo stock payload or Terminal state base changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "dismiss-query-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "dismiss-query-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e68b4",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, old_state, event_payload, session, child_result):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state+0x288, struct.pack("<I", session))
        dismiss = (symbols["audio_td_dismiss_query_notification"] if compiled else 0x5974d4)&~1
        restore = (symbols["audio_terminal_ui_restore_query_5e6620"] if compiled else 0x5e6620)&~1
        trace = []

        def hook(cpu, pc, size, _):
            if pc == dismiss:
                trace.append(("dismiss", cpu.reg_read(A.UC_ARM_REG_R0)))
            elif pc == restore:
                trace.append(("restore", cpu.reg_read(A.UC_ARM_REG_R0)))
                cpu.reg_write(A.UC_ARM_REG_R0, child_result)
            else:
                return
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old_state)
        u.reg_write(A.UC_ARM_REG_R1, event_payload)
        entry = symbols["audio_terminal_ui_action_5e68b4"] if compiled else 0x5e68b4
        u.emu_start(entry|1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace

    cases = 0
    for old_state in (0, 4, 12, 0x100, 0xffffffff):
        for event_payload in (0, 1, 2, 0xffffffff):
            for session in (0, 0x12345678):
                for child_result in (0, 1, 13, 0xffffffff):
                    stock = run(False, old_state, event_payload, session, child_result)
                    selected = run(True, old_state, event_payload, session, child_result)
                    if stock != selected:
                        raise RuntimeError(f"dismiss action mismatch {old_state=:#x} "
                                           f"{event_payload=:#x} {session=:#x} {child_result=:#x}: "
                                           f"{stock} vs {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_DISMISS_QUERY_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "R1 payload branch, stock session field, byte-width old state and child return propagation",
              "limits": ["Query-restore child effect and final shared Terminal RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

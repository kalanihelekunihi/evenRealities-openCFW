#!/usr/bin/env python3
"""Compare Terminal FSM status action and payload helpers with pinned stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_status_5e7022.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-status-5e7022"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void audio_terminal_display_status_44ea04(uint32_t a,uint32_t b,uint32_t c)
{(void)a;(void)b;(void)c;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e7268-0x438000:0x5e726c-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Apollo stock payload or Terminal state base changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "status-action-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "status-action-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e7022",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, entry, payload, object_value, old_state):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state+4, struct.pack("<I", object_value))
        u.mem_write(state+0x28c, b"\x7f")
        display = (symbols["audio_terminal_display_status_44ea04"] if compiled else 0x44ea04)&~1
        trace = []

        def hook(cpu, pc, size, _):
            if pc != display:
                return
            trace.append((cpu.reg_read(A.UC_ARM_REG_R0),
                          cpu.reg_read(A.UC_ARM_REG_R1),
                          cpu.reg_read(A.UC_ARM_REG_R2)))
            cpu.reg_write(A.UC_ARM_REG_R0, 0xdeadbeef)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old_state if entry[1] == 0x5e7022 else payload)
        u.reg_write(A.UC_ARM_REG_R1, payload)
        u.emu_start((symbols[entry[0]] if compiled else entry[1])|1,
                    0x600000, count=10000)
        return (u.reg_read(A.UC_ARM_REG_R0),
                u.mem_read(state+0x28c, 1)[0], trace)

    values = (0, 1, 0x7fff, 0x8000, 0x10000, 0x7fffffff,
              0x80000000, 0x80001234, 0xffffffff)
    cases = 0
    for entry in (("audio_terminal_status_low_5e4f10", 0x5e4f10),
                  ("audio_terminal_status_high_5e4f14", 0x5e4f14)):
        for payload in values:
            stock = run(False, entry, payload, 0, 0)
            selected = run(True, entry, payload, 0, 0)
            if stock != selected:
                raise RuntimeError(f"status helper mismatch {entry[0]} {payload=:#x}: "
                                   f"{stock} vs {selected}")
            cases += 1
    entry = ("audio_terminal_ui_action_5e7022", 0x5e7022)
    for payload in values:
        for object_value in (0, 0x20002000):
            for old_state in (0, 12, 0xffffffff):
                stock = run(False, entry, payload, object_value, old_state)
                selected = run(True, entry, payload, object_value, old_state)
                if stock != selected:
                    raise RuntimeError(f"status action mismatch {payload=:#x} "
                                       f"{object_value=:#x} {old_state=:#x}: {stock} vs {selected}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_STATUS_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "two payload helpers plus FSM action guard, state byte, display call and return",
              "limits": ["Display child effect and final shared Terminal RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

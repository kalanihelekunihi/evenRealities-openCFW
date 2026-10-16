#!/usr/bin/env python3
"""Compare the two payload-consuming Terminal FSM actions with pinned stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_payload_5e6400.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-payload-5e6400"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ENTRIES = [(0x5e6400, "audio_terminal_ui_action_5e6400", 0x5e4a6e,
            "audio_terminal_control_flags_5e4a6e"),
           (0x5e6410, "audio_terminal_ui_action_5e6410", 0x5e48b8,
            "audio_terminal_elapsed_text_5e48b8")]
STUB = """#include <stdint.h>
void audio_terminal_control_flags_5e4a6e(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_terminal_elapsed_text_5e48b8(uint32_t a){(void)a;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "payload-action-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "payload-action-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e6400",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, entry, old_state, value):
        stock_entry, name, stock_lower, lower_name = entry
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        lower = (symbols[lower_name] if compiled else stock_lower) & ~1
        trace = []

        def hook(cpu, pc, size, _):
            if pc != lower:
                return
            args = (cpu.reg_read(A.UC_ARM_REG_R0),)
            if stock_entry == 0x5e6400:
                args += (cpu.reg_read(A.UC_ARM_REG_R1),)
            trace.append(args)
            cpu.reg_write(A.UC_ARM_REG_R0, 0xdeadbeef)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old_state)
        u.reg_write(A.UC_ARM_REG_R1, value)
        u.emu_start((symbols[name] if compiled else stock_entry)|1,
                    0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace

    cases = 0
    for entry in ENTRIES:
        for state in (0, 5, 12):
            for value in (0, 1, 0xf, 0x10, 0x3c, 0xff, 0x12345678, 0xffffffff):
                stock = run(False, entry, state, value)
                selected = run(True, entry, state, value)
                if stock != selected:
                    raise RuntimeError(f"payload action mismatch {entry[1]} {state=} "
                                       f"{value=:#x}: {stock} vs {selected}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_PAYLOAD_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "two FSM actions with old-state and event-payload variation; exact lower-call arguments and return",
              "limits": ["Control-flags and elapsed-text child effects remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

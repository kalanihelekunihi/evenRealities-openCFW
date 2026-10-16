#!/usr/bin/env python3
"""Compare two Terminal FSM reset actions with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_reset_pair_5e5290.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-reset-pair-5e5290"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void audio_terminal_reset_first_5e51ba(uint32_t a){(void)a;}
void audio_terminal_reset_mode_5eae2c(uint32_t a){(void)a;}
void audio_terminal_reset_display_5e4c84(uint32_t a){(void)a;}
void audio_terminal_reset_subtree_5ea342(void){}
void audio_lv_object_call_43ded4(uint32_t a,uint32_t b){(void)a;(void)b;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e5dd8-0x438000:0x5e5ddc-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Apollo stock payload or Terminal state base changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "reset-pair-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "reset-pair-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e5290",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, entry, old_state, payload, object_value):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state+0x1cc, struct.pack("<I", object_value))
        names = ("audio_terminal_reset_first_5e51ba", "audio_terminal_reset_mode_5eae2c",
                 "audio_terminal_reset_display_5e4c84", "audio_terminal_reset_subtree_5ea342",
                 "audio_lv_object_call_43ded4")
        stock = (0x5e51ba, 0x5eae2c, 0x5e4c84, 0x5ea342, 0x43ded4)
        cuts = {(symbols[name] if compiled else address)&~1: index
                for index, (name, address) in enumerate(zip(names, stock))}
        trace = []

        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            r1 = cpu.reg_read(A.UC_ARM_REG_R1)
            trace.append((index,) if index == 3 else
                         ((index, r0, r1) if index == 4 else (index, r0)))
            cpu.reg_write(A.UC_ARM_REG_R0, 0xdeadbeef)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old_state)
        u.reg_write(A.UC_ARM_REG_R1, payload)
        name, address = entry
        u.emu_start((symbols[name] if compiled else address)|1,
                    0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace

    cases = 0
    for entry in (("audio_terminal_ui_action_5e5290", 0x5e5290),
                  ("audio_terminal_ui_action_5e5386", 0x5e5386)):
        for old_state in (0, 12, 0x100, 0xffffffff):
            for payload in (0, 0x12345678):
                for object_value in (0, 0x20002000):
                    stock = run(False, entry, old_state, payload, object_value)
                    selected = run(True, entry, old_state, payload, object_value)
                    if stock != selected:
                        raise RuntimeError(f"reset pair mismatch {entry[0]} {old_state=:#x} "
                                           f"{payload=:#x} {object_value=:#x}: {stock} vs {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_RESET_PAIR_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "two FSM actions, byte-width old state, child call order, object guard and return",
              "limits": ["Four reset children, LVGL effect and final shared Terminal RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare two Terminal reset children with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_reset_mode_display_20261016.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-reset-mode-display"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void audio_terminal_mode_set_5eae1e(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_lv_object_call_43ded4(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_lv_obj_invalidate_43dfa4(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_terminal_processing_prepare_5ea30c(void){}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e53b4-0x438000:0x5e53b8-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Apollo payload or Terminal state base changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "reset-mode-display-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "reset-mode-display-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_reset_display_5e4c84",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, entry, value, object_value, flag):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state+4, struct.pack("<I", object_value))
        u.mem_write(state+0x27e, bytes((flag,)))
        names = ("audio_terminal_mode_set_5eae1e", "audio_lv_object_call_43ded4",
                 "audio_lv_obj_invalidate_43dfa4", "audio_terminal_processing_prepare_5ea30c")
        stock = (0x5eae1e, 0x43ded4, 0x43dfa4, 0x5ea30c)
        cuts = {(symbols[name] if compiled else address)&~1: index
                for index, (name, address) in enumerate(zip(names, stock))}
        trace = []

        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            trace.append((index,) if index == 3 else
                         (index, cpu.reg_read(A.UC_ARM_REG_R0),
                          cpu.reg_read(A.UC_ARM_REG_R1)))
            cpu.reg_write(A.UC_ARM_REG_R0, 0xdeadbeef)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, value)
        name, address = entry
        u.emu_start((symbols[name] if compiled else address)|1, 0x600000, count=10000)
        return trace

    cases = 0
    for mode in (0, 1, 4, 0xff, 0x100, 0x12345678, 0xffffffff):
        stock = run(False, ("audio_terminal_reset_mode_5eae2c", 0x5eae2c), mode, 0, 0)
        selected = run(True, ("audio_terminal_reset_mode_5eae2c", 0x5eae2c), mode, 0, 0)
        if stock != selected:
            raise RuntimeError(f"reset mode mismatch {mode=:#x}: {stock} vs {selected}")
        cases += 1
    for mode in (0, 1, 0x100, 0xffffffff):
        for object_value in (0, 1, 0x20002000):
            for flag in (0, 1):
                stock = run(False, ("audio_terminal_reset_display_5e4c84", 0x5e4c84),
                            mode, object_value, flag)
                selected = run(True, ("audio_terminal_reset_display_5e4c84", 0x5e4c84),
                               mode, object_value, flag)
                if stock != selected:
                    raise RuntimeError(f"reset display mismatch {mode=:#x} "
                                       f"{object_value=:#x} {flag=}: {stock} vs {selected}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_RESET_MODE_DISPLAY_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "mode byte forwarding, display object/flag branches and lower-call order",
              "limits": ["Mode-set and LVGL lower-call effects remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

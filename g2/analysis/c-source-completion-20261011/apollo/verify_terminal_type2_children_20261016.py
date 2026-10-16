#!/usr/bin/env python3
"""Bounded stock/compiled comparison for Terminal type-two helpers."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_type2_children_20261016.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-type2-children"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_td_state[0xa1dc];
uint8_t audio_terminal_ui_state_base[0x2a0];
__attribute__((noinline,used)) uint32_t audio_td_ring_index_wrap(void *p,uint16_t i){(void)p;(void)i;return 0;}
__attribute__((noinline,used)) void audio_uart_compiler_move_439710(void *a,const void *b,uint32_t n){(void)a;(void)b;(void)n;}
__attribute__((noinline,used)) uint32_t audio_terminal_item_59737c(uint32_t i){(void)i;return 0;}
__attribute__((noinline,used)) uint32_t audio_terminal_item_height_5ea67a(uint32_t i){(void)i;return 0;}
__attribute__((noinline,used)) void audio_terminal_recompute_offsets_5ea6da(uint32_t i){(void)i;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "type2-children-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "type2-children-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_last_record_597350",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    calls = {"audio_td_ring_index_wrap": 0x5970a8,
             "audio_uart_compiler_move_439710": 0x439710,
             "audio_terminal_item_59737c": 0x59737c,
             "audio_terminal_item_height_5ea67a": 0x5ea67a,
             "audio_terminal_recompute_offsets_5ea6da": 0x5ea6da}

    def run(compiled, function, count, physical, item, height, pattern):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x200000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        ring = symbols["audio_td_state"] + 0x1054 if compiled else 0x20110d74
        u.mem_write(state, bytes(((i + pattern) & 255 for i in range(0x2a0))))
        u.mem_write(ring + 0x8500, struct.pack("<H", count))
        trace = []
        cuts = {((symbols[name] if compiled else stock) & ~1): name
                for name, stock in calls.items()}
        def hook(cpu, pc, size, _):
            name = cuts.get(pc)
            if name is None:
                return
            if name == "audio_td_ring_index_wrap":
                trace.append((name, cpu.reg_read(A.UC_ARM_REG_R0) - ring,
                              cpu.reg_read(A.UC_ARM_REG_R1)))
                cpu.reg_write(A.UC_ARM_REG_R0, physical)
            elif name == "audio_uart_compiler_move_439710":
                dst, src, length = (cpu.reg_read(r) for r in
                                    (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                trace.append((name, dst - state, src - state, length))
                cpu.mem_write(dst, bytes(cpu.mem_read(src, length)))
            elif name == "audio_terminal_item_59737c":
                trace.append((name, cpu.reg_read(A.UC_ARM_REG_R0)))
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20004000 if item else 0)
            elif name == "audio_terminal_item_height_5ea67a":
                trace.append((name, cpu.reg_read(A.UC_ARM_REG_R0)))
                cpu.reg_write(A.UC_ARM_REG_R0, height)
            else:
                trace.append((name, cpu.reg_read(A.UC_ARM_REG_R0)))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x201ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        name = "audio_terminal_last_record_597350" if function == "last" else "audio_terminal_list_rollover_5eab8e"
        stock = 0x597350 if function == "last" else 0x5eab8e
        u.emu_start((symbols[name] if compiled else stock) | 1, 0x600000, count=10000)
        result = u.reg_read(A.UC_ARM_REG_R0)
        return (result - ring if result else 0, trace) if function == "last" else (bytes(u.mem_read(state, 0x2a0)), trace)

    cases = 0
    for count in (0, 1, 2, 63, 64, 65535):
        for physical in (0, 1, 31, 63):
            a = run(False, "last", count, physical, False, 0, 0)
            b = run(True, "last", count, physical, False, 0, 0)
            if a != b:
                raise RuntimeError(f"last-record mismatch {count=} {physical=}: {a} != {b}")
            cases += 1
    for item in (False, True):
        for height in (0, 1, 28, 65535):
            for pattern in (0, 31, 255):
                a = run(False, "rollover", 0, 0, item, height, pattern)
                b = run(True, "rollover", 0, 0, item, height, pattern)
                if a != b:
                    raise RuntimeError(f"rollover mismatch {item=} {height=} {pattern=}: {a[1]} != {b[1]}")
                cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_TERMINAL_TYPE2_CHILDREN_C_ORACLE",
               "cases": cases, "source_sha256": sha(SOURCE),
               "stock_payload_sha256": PIN, "source_complete": False,
               "limits": ["Lower-call effects and final RAM placement remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()

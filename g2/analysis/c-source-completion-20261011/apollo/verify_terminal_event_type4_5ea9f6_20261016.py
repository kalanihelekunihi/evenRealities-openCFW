#!/usr/bin/env python3
"""Compare Terminal type-four event reset with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_event_type4_5ea9f6.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-event-type4-5ea9f6"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_lv_object_size_call_43f4c0(uint32_t a,uint32_t b,uint32_t c)
{(void)a;(void)b;(void)c;}
void audio_terminal_event_reset_list_5ea7dc(void){}
void audio_terminal_display_status_44ea04(uint32_t a,uint32_t b,uint32_t c)
{(void)a;(void)b;(void)c;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5eb28c-0x438000:0x5eb290-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Apollo stock payload or Terminal state base changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "type4-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "type4-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_event_type4_5ea9f6",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, root, child, fill):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes((fill,))*0x2a0)
        u.mem_write(state+4, struct.pack("<I", root))
        u.mem_write(state+8, struct.pack("<I", child))
        names = ("audio_uart_buffer_zero", "audio_lv_object_size_call_43f4c0",
                 "audio_terminal_event_reset_list_5ea7dc",
                 "audio_terminal_display_status_44ea04")
        stock = (0x43c0e4, 0x43f4c0, 0x5ea7dc, 0x44ea04)
        cuts = {(symbols[name] if compiled else address)&~1: index
                for index, (name, address) in enumerate(zip(names, stock))}
        trace = []

        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            r1 = cpu.reg_read(A.UC_ARM_REG_R1)
            r2 = cpu.reg_read(A.UC_ARM_REG_R2)
            if index == 0:
                trace.append(("zero", r0-state, r1, r2))
                cpu.mem_write(r0, bytes((r2 & 0xff,))*r1)
            elif index == 1:
                trace.append(("size", r0, r1, r2))
            elif index == 2:
                trace.append(("list",))
            else:
                trace.append(("display", r0, r1, r2))
            cpu.reg_write(A.UC_ARM_REG_R0, 0xdeadbeef)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_event_type4_5ea9f6"] if compiled else 0x5ea9f6
        u.emu_start(entry|1, 0x600000, count=10000)
        return bytes(u.mem_read(state, 0x2a0)).hex(), trace

    cases = 0
    for root in (0, 0x20002000):
        for child in (0, 0x20003000):
            for fill in (0, 0x5a, 0xff):
                stock = run(False, root, child, fill)
                selected = run(True, root, child, fill)
                if stock != selected:
                    raise RuntimeError(f"type4 mismatch {root=:#x} {child=:#x} "
                                       f"{fill=:#x}: {stock[1]} vs {selected[1]}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_EVENT_TYPE4_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "two exact zero extents, state writes, child/root guards and lower-call order",
              "limits": ["List-reset and LVGL child effects and shared RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

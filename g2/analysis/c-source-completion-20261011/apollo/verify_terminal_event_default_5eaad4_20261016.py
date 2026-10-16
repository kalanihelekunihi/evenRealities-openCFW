#!/usr/bin/env python3
"""Bounded stock comparison for Terminal default event 0x5eaad4."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_event_default_5eaad4.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-event-default-5eaad4"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void audio_terminal_event_select_input_5eaa54(const uint8_t*a,uint32_t*b,uint8_t*c){(void)a;(void)b;(void)c;}
void audio_terminal_event_type4_5ea9f6(void){}
uint32_t audio_terminal_resource_597324(void){return 0;}
uint32_t audio_terminal_item_59737c(uint32_t a){(void)a;return 0;}
uint32_t audio_terminal_item_height_5ea67a(uint32_t a){(void)a;return 0;}
void audio_terminal_recompute_offsets_5ea6da(uint32_t a){(void)a;}
void audio_terminal_event_apply_input_5eaa96(const uint8_t*a){(void)a;}
void audio_terminal_event_refresh_view_5ea992(void){}
void audio_terminal_display_status_44ea04(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_terminal_view_position_5ea926(uint32_t a){(void)a;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5eb28c-0x438000:0x5eb290-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Apollo stock payload or Terminal base changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "default-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "default-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_event_default_5eaad4",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    names = ("audio_terminal_event_select_input_5eaa54", "audio_terminal_event_type4_5ea9f6",
             "audio_terminal_resource_597324", "audio_terminal_item_59737c",
             "audio_terminal_item_height_5ea67a", "audio_terminal_recompute_offsets_5ea6da",
             "audio_terminal_event_apply_input_5eaa96", "audio_terminal_event_refresh_view_5ea992",
             "audio_terminal_display_status_44ea04", "audio_terminal_view_position_5ea926")
    stock_addresses = (0x5eaa54, 0x5ea9f6, 0x597324, 0x59737c, 0x5ea67a,
                       0x5ea6da, 0x5eaa96, 0x5ea992, 0x44ea04, 0x5ea926)

    def run(compiled, root, count, input_kind, flag, fill):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes((fill,)) * 0x2a0)
        u.mem_write(state + 4, struct.pack("<I", root))
        u.mem_write(0x20009500, struct.pack("<H", count))
        input_addr = 0 if input_kind == 0 else 0x20003000
        u.mem_write(0x20003000, bytes((1 if input_kind == 2 else 0, flag, 0, 0)) +
                    struct.pack("<I", 0x1234))
        cuts = {(symbols[name] if compiled else address) & ~1: index
                for index, (name, address) in enumerate(zip(names, stock_addresses))}
        trace = []
        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            r0, r1, r2 = (cpu.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if index == 0:
                trace.append((index, r0))
                cpu.mem_write(r1, struct.pack("<I", 0x456))
                cpu.mem_write(r2, bytes((flag,)))
            elif index in (1, 7):
                trace.append((index,))
            elif index == 2:
                trace.append((index,))
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            elif index == 3:
                trace.append((index, r0))
                cpu.reg_write(A.UC_ARM_REG_R0, 0 if r0 & 1 else 0x20005000 + r0 * 8)
            elif index == 4:
                trace.append((index, r0))
                cpu.reg_write(A.UC_ARM_REG_R0, 0x30)
            elif index in (5, 6, 9):
                trace.append((index, r0))
            else:
                trace.append((index, r0, r1, r2))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, input_addr)
        entry = symbols["audio_terminal_event_default_5eaad4"] if compiled else 0x5eaad4
        u.emu_start(entry | 1, 0x600000, count=10000)
        return bytes(u.mem_read(state, 0x2a0)), trace

    cases = 0
    for root in (0, 0x20002000):
        for count in (0, 1, 2, 3):
            for input_kind in (0, 1, 2):
                for flag in (0, 1):
                    for fill in (0, 0x5a):
                        stock = run(False, root, count, input_kind, flag, fill)
                        selected = run(True, root, count, input_kind, flag, fill)
                        if stock != selected:
                            raise RuntimeError(f"default mismatch {root=} {count=} "
                                               f"{input_kind=} {flag=} {fill=}: "
                                               f"{stock[1]} vs {selected[1]}")
                        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_EVENT_DEFAULT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "root/count/item/payload/flag guards, height RAM and lower-call trace",
              "limits": ["Lower-call effects, full item range and shared RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

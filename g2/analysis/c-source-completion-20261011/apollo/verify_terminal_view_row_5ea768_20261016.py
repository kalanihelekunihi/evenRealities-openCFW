#!/usr/bin/env python3
"""Compare Terminal row update 0x5ea768 with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_view_row_5ea768.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-view-row-5ea768"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
uint32_t audio_terminal_item_59737c(uint32_t a){(void)a;return 0;}
void audio_lv_object_flag_43ded4(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_lv_object_position_43f09a(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_lv_object_size_call_43f4c0(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_terminal_row_bind_5ea564(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_lv_object_clear_flag_43dfa4(uint32_t a,uint32_t b){(void)a;(void)b;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "view-row-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "view-row-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_view_row_5ea768",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    names = ("audio_terminal_item_59737c", "audio_lv_object_flag_43ded4",
             "audio_lv_object_position_43f09a", "audio_lv_object_size_call_43f4c0",
             "audio_terminal_row_bind_5ea564", "audio_lv_object_clear_flag_43dfa4")
    stock_addresses = (0x59737c, 0x43ded4, 0x43f09a, 0x43f4c0, 0x5ea564, 0x43dfa4)

    def run(compiled, slot, object_present, item_present, index, height):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes((0x5a,)) * 0x2a0)
        for x in range(12):
            obj = 0x20003000 + x * 16 if object_present else 0
            u.mem_write(state + 0xc + x * 4, struct.pack("<I", obj))
        u.mem_write(state + 0xbc + index * 4, struct.pack("<I", 0x12345678))
        u.mem_write(state + 0x3c + index * 2, struct.pack("<H", height))
        cuts = {(symbols[name] if compiled else address) & ~1: child
                for child, (name, address) in enumerate(zip(names, stock_addresses))}
        trace = []
        def hook(cpu, pc, size, _):
            child = cuts.get(pc)
            if child is None:
                return
            args = tuple(cpu.reg_read(reg) for reg in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            trace.append((child, args[:1] if child == 0 else args[:2] if child in (1, 5) else args))
            if child == 0:
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20005000 if item_present else 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, slot)
        u.reg_write(A.UC_ARM_REG_R1, index)
        entry = symbols["audio_terminal_view_row_5ea768"] if compiled else 0x5ea768
        u.emu_start(entry | 1, 0x600000, count=10000)
        return bytes(u.mem_read(state, 0x2a0)), trace

    cases = 0
    for slot in (0, 1, 11, 12, 0xffff):
        for object_present in (False, True):
            for item_present in (False, True):
                for index in (0, 1, 11, 63):
                    for height in (0, 27, 28, 50):
                        stock = run(False, slot, object_present, item_present, index, height)
                        selected = run(True, slot, object_present, item_present, index, height)
                        if stock != selected:
                            raise RuntimeError(f"row mismatch {slot=} {object_present=} "
                                               f"{item_present=} {index=} {height=}: "
                                               f"{stock[1]} vs {selected[1]}")
                        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_VIEW_ROW_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "slot/object/item guards, offset/height lookup and lower-call trace",
              "limits": ["LVGL and row-bind lower effects plus final RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()

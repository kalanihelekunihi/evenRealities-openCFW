#!/usr/bin/env python3
"""Compare Terminal query-indicator offset and layout with pinned stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_query_indicator_5eb322.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-query-indicator-5eb322"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_terminal_query_count_5eb30c", 0x5eb30c),
         ("audio_lv_child_44dce2", 0x44dce2),
         ("audio_uart_lv_obj_y_43fce0", 0x43fce0),
         ("audio_uart_lv_obj_x_43fc70", 0x43fc70),
         ("audio_lv_object_flag_43ded4", 0x43ded4),
         ("audio_lv_object_clear_flag_43dfa4", 0x43dfa4),
         ("audio_lv_object_position_43f09a", 0x43f09a))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "query-indicator-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\nuint32_t audio_uart_ring_secondary_head_cell;\n"
                    "__attribute__((noinline,used)) uint32_t audio_terminal_query_count_5eb30c(void){return 0;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_lv_child_44dce2(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n"
                    "__attribute__((noinline,used)) int32_t audio_uart_lv_obj_y_43fce0(void*a){(void)a;return 0;}\n"
                    "__attribute__((noinline,used)) int32_t audio_uart_lv_obj_x_43fc70(void*a){(void)a;return 0;}\n"
                    "__attribute__((noinline,used)) void audio_lv_object_flag_43ded4(uint32_t a,uint32_t b){(void)a;(void)b;}\n"
                    "__attribute__((noinline,used)) void audio_lv_object_clear_flag_43dfa4(uint32_t a,uint32_t b){(void)a;(void)b;}\n"
                    "__attribute__((noinline,used)) void audio_lv_object_position_43f09a(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\n")
    elf = OUT / "query-indicator-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_query_indicator_5eb322",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, entry, present, list_present, indicator_present,
            browsing, focus, count, child_present, font_height):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes(((i + focus) & 255 for i in range(0x2a0))))
        u.mem_write(state + 0x21c, struct.pack("<I", 0x20009000 if list_present else 0))
        u.mem_write(state + 0x220, struct.pack("<I", 0x20009100 if indicator_present else 0))
        u.mem_write(state + 0x279, bytes([focus]))
        u.mem_write(state + 0x27c, bytes([browsing]))
        cell = symbols["audio_uart_ring_secondary_head_cell"] if compiled else 0x200746e0
        u.mem_write(cell, struct.pack("<I", 0x20003000))
        u.mem_write(0x2000300c, struct.pack("<i", font_height))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address) in enumerate(CALLS)}
        trace = []
        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            r1 = cpu.reg_read(A.UC_ARM_REG_R1)
            r2 = cpu.reg_read(A.UC_ARM_REG_R2)
            if i == 0:
                trace.append(("count",))
                ret = count
            elif i == 1:
                trace.append(("child", r0, r1))
                ret = 0x20009200 if child_present else 0
            elif i == 2:
                trace.append(("y", r0))
                ret = 13 if r0 == 0x20009000 else 9
            elif i == 3:
                trace.append(("x", r0))
                ret = 38
            elif i == 4:
                trace.append(("hide", r0, r1))
                ret = 0
            elif i == 5:
                trace.append(("show", r0, r1))
                ret = 0
            else:
                trace.append(("position", r0, r1, r2))
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        if entry == "offset":
            symbol, stock = "audio_terminal_query_indicator_offset_5eb2ee", 0x5eb2ee
        else:
            symbol, stock = "audio_terminal_query_indicator_5eb322", 0x5eb322
            u.reg_write(A.UC_ARM_REG_R0, state if present else 0)
        u.emu_start((symbols[symbol] if compiled else stock) | 1, 0x600000, count=10000)
        return (u.reg_read(A.UC_ARM_REG_R0) if entry == "offset" else None,
                trace, bytes(u.mem_read(state, 0x2a0)))
    cases = 0
    for height in (-5, 0, 16, 17, 24, 31, 100):
        args = "offset", 1, 1, 1, 0, 0, 2, 1, height
        if run(False, *args) != run(True, *args):
            raise RuntimeError(f"offset mismatch {height}")
        cases += 1
    for present in (0, 1):
        for list_present in (0, 1):
            for indicator_present in (0, 1):
                for browsing in (0, 1):
                    for focus, count in ((0, 0), (0, 1), (1, 1), (1, 2), (255, 255)):
                        for child_present in (0, 1):
                            for height in (12, 24, 31):
                                args = "indicator", present, list_present, indicator_present, browsing, focus, count, child_present, height
                                stock = run(False, *args)
                                candidate = run(True, *args)
                                if stock != candidate:
                                    raise RuntimeError(f"indicator mismatch {args}: {stock[:2]} != {candidate[:2]}; state_equal={stock[2] == candidate[2]}")
                                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_QUERY_INDICATOR_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Font offset, guard, focus count, child lookup, hide/show, position and unchanged state",
              "limits": ["LVGL lower effects isolated; font-pointer validity and final placement remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()

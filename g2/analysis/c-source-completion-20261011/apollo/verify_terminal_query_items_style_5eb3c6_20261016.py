#!/usr/bin/env python3
"""Compare Terminal query count and item styling with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_query_items_style_5eb3c6.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-query-items-style-5eb3c6"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_td_session_struct_ptr", 0x59731e),
         ("audio_lv_child_44dce2", 0x44dce2),
         ("audio_lv_color_44104c", 0x44104c),
         ("audio_lv_style_color_44140e", 0x44140e),
         ("audio_terminal_query_indicator_5eb322", 0x5eb322))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "query-items-style-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n"
                    "__attribute__((noinline,used)) uint8_t *audio_td_session_struct_ptr(void){return 0;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_lv_child_44dce2(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_lv_color_44104c(uint32_t a){return a;}\n"
                    "__attribute__((noinline,used)) void audio_lv_style_color_44140e(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_query_indicator_5eb322(uint32_t a){(void)a;}\n")
    elf = OUT / "query-items-style-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_query_items_style_5eb3c6",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, entry, count, session_present, list_present, focus, browsing, child_mode):
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
        u.mem_write(state + 0x279, bytes([focus]))
        u.mem_write(state + 0x27c, bytes([browsing]))
        session = 0x20002000
        u.mem_write(session + 0x406, struct.pack("<H", count))
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
                trace.append(("session",))
                ret = session if session_present else 0
            elif i == 1:
                trace.append(("child", r0, r1))
                ret = 0 if child_mode == 2 or (child_mode == 1 and r1 % 2 == 0) else 0x20010000 + r1
            elif i == 2:
                trace.append(("color", r0))
                ret = r0 ^ 0x13579b
            elif i == 3:
                trace.append(("style", r0, r1, r2))
                ret = 0
            else:
                trace.append(("indicator", "state" if r0 == state else r0))
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        if entry == "style":
            u.reg_write(A.UC_ARM_REG_R0, state)
            symbol, stock = "audio_terminal_query_items_style_5eb3c6", 0x5eb3c6
        else:
            symbol, stock = "audio_terminal_query_count_5eb30c", 0x5eb30c
        u.emu_start((symbols[symbol] if compiled else stock) | 1, 0x600000, count=100000)
        return (u.reg_read(A.UC_ARM_REG_R0) if entry == "count" else None,
                trace, bytes(u.mem_read(state, 0x2a0)))
    cases = 0
    for count in (0, 1, 2, 3, 8, 255):
        for present in (0, 1):
            args = "count", count, present, 1, 0, 0, 0
            if run(False, *args) != run(True, *args):
                raise RuntimeError(f"count mismatch {args}")
            cases += 1
    for count in (0, 1, 2, 3, 8, 255):
        for session_present in (0, 1):
            for list_present in (0, 1):
                for focus in (0, 1, 7):
                    for browsing in (0, 1):
                        for child_mode in (0, 1, 2):
                            args = "style", count, session_present, list_present, focus, browsing, child_mode
                            stock = run(False, *args)
                            candidate = run(True, *args)
                            if stock != candidate:
                                raise RuntimeError(f"style mismatch {args}: {stock[:2]} != {candidate[:2]}; state_equal={stock[2] == candidate[2]}")
                            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_QUERY_ITEMS_STYLE_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Count getter, list guard, item loop, child/color/style calls, indicator call and unchanged state",
              "limits": ["Indicator child and LVGL lower effects isolated; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()

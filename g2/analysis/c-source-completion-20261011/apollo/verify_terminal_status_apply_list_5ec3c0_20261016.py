#!/usr/bin/env python3
"""Compare Terminal interrupt-confirm list style and indicator layout with stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_status_apply_list_5ec3c0.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-status-apply-list-5ec3c0"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_lv_child_44dce2", 0x44dce2, 2),
         ("audio_uart_page_44104c", 0x44104c, 1),
         ("audio_uart_page_44140e", 0x44140e, 3),
         ("audio_uart_lv_obj_x_43fc70", 0x43fc70, 1),
         ("audio_uart_lv_obj_y_43fce0", 0x43fce0, 1),
         ("audio_lv_object_position_43f09a", 0x43f09a, 3),
         ("audio_uart_page_43dfa4", 0x43dfa4, 2))
ENTRIES = (("audio_terminal_status_apply_list_5ec3c0", 0x5ec3c0),
           ("audio_terminal_status_apply_list_position_5ec34e", 0x5ec34e))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "list-style-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint32_t audio_uart_ring_secondary_head_cell;\n" +
                    "\n".join(f"__attribute__((noinline,used)) uint32_t {name}"
                              "(uint32_t a,uint32_t b,uint32_t c)"
                              "{(void)a;(void)b;(void)c;return 0;}"
                              for name, _, _ in CALLS) + "\n")
    elf = OUT / "list-style-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_status_apply_list_5ec3c0",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, entry, mask, selected, height, x, y):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = 0x20008000 if mask & 1 else 0
        if state:
            u.mem_write(state, bytes(0x2a0))
            u.mem_write(state + 0x238, struct.pack("<I", 0x20009000 if mask & 2 else 0))
            u.mem_write(state + 0x23c, struct.pack("<I", 0x20009100 if mask & 4 else 0))
            u.mem_write(state + 0x278, bytes([selected]))
        font = 0x20012000
        u.mem_write(font + 12, struct.pack("<I", height))
        cell = symbols["audio_uart_ring_secondary_head_cell"] if compiled else 0x200746e0
        u.mem_write(cell, struct.pack("<I", font))
        cuts = {(symbols[name] if compiled else address) & ~1: (i, name, arity)
                for i, (name, address, arity) in enumerate(CALLS)}
        trace = []
        def hook(cpu, pc, size, _):
            item = cuts.get(pc)
            if item is None:
                return
            i, name, arity = item
            args = tuple(cpu.reg_read(r) for r in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            trace.append((name, *args[:arity]))
            if i == 0:
                ret = 0x2000a000 + args[1] * 0x100 if mask & (8 << args[1]) else 0
            elif i == 1:
                ret = args[0] ^ 0x005a3c18
            elif i == 3:
                ret = x & 0xffffffff
            elif i == 4:
                ret = y & 0xffffffff
            else:
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, state)
        name, stock_entry = ENTRIES[entry]
        u.emu_start((symbols[name] if compiled else stock_entry) | 1, 0x600000, count=10000)
        return trace, bytes(u.mem_read(state, 0x2a0)) if state else b""
    cases = 0
    for entry in range(2):
        for mask in range(32):
            for selected in (0, 1, 2):
                for height in (0, 16, 17, 31):
                    for x, y in ((0, 0), (40, 80)):
                        args = entry, mask, selected, height, x, y
                        stock = run(False, *args)
                        candidate = run(True, *args)
                        if stock != candidate:
                            raise RuntimeError(f"list style mismatch {args}: {stock[0]} != {candidate[0]}")
                        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_STATUS_APPLY_LIST_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Both stock entries, object/child guards, colors, font offset and indicator placement",
              "limits": ["Font pointer initialization and LVGL lower effects remain open; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare Terminal query-layout guard and publication with stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_query_layout_5ebb96.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-query-layout-5ebb96"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_terminal_query_items_style_5eb3c6", 0x5eb3c6),
         ("audio_terminal_status_publish_5e5498", 0x5e5498))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "query-layout-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n"
                    "__attribute__((noinline,used)) void audio_terminal_query_items_style_5eb3c6(uint32_t a){(void)a;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_status_publish_5e5498(uint32_t a,uint32_t b){(void)a;(void)b;}\n")
    elf = OUT / "query-layout-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_query_layout_5ebb96",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, mask, index, seed):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes(((i + seed) & 255 for i in range(0x2a0))))
        for i, off in enumerate((0x214, 0x21c, 0x220)):
            u.mem_write(state + off, struct.pack("<I", (0x20009000 + i * 0x100) if mask & (1 << i) else 0))
        u.mem_write(state + 0x279, bytes([index]))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address) in enumerate(CALLS)}
        trace = []
        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            r1 = cpu.reg_read(A.UC_ARM_REG_R1)
            if i == 0:
                trace.append(("style", "state" if r0 == state else r0))
            else:
                trace.append(("publish", r0, r1))
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.emu_start((symbols["audio_terminal_query_layout_5ebb96"] if compiled else 0x5ebb96) | 1,
                    0x600000, count=10000)
        return trace, bytes(u.mem_read(state, 0x2a0))
    cases = 0
    for mask in range(8):
        for index in (0, 1, 0x7f, 0xff):
            for seed in (0, 0xa5):
                args = mask, index, seed
                stock = run(False, *args)
                candidate = run(True, *args)
                if stock != candidate:
                    raise RuntimeError(f"query-layout mismatch {args}: {stock[0]} != {candidate[0]}; state_equal={stock[1] == candidate[1]}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_QUERY_LAYOUT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Three-object guard, item-style call, focus publication and unchanged state",
              "limits": ["Item-style and publication lower effects isolated; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()

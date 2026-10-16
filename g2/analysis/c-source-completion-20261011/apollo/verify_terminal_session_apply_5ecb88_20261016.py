#!/usr/bin/env python3
"""Compare Terminal direct session selection application against stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_apply_5ecb88.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-apply-5ecb88"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_terminal_session_count_5eca48", 0x5eca48),
         ("audio_terminal_session_row_style_5ecb08", 0x5ecb08))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "session-apply-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n"
                    "__attribute__((noinline,used)) uint32_t audio_terminal_session_count_5eca48(void){return 0;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_session_row_style_5ecb08(uint32_t a,uint32_t b){(void)a;(void)b;}\n")
    elf = OUT / "session-apply-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_session_apply_5ecb88",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, index, count, special, pattern):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes(((i + pattern) & 255 for i in range(0x2a0))))
        for row in range(11):
            value = (0x20009000 + row * 0x100) if row == 0 and special or row > 0 and (pattern == 1 or (pattern == 2 and row % 2 == 0)) else 0
            u.mem_write(state + 0x248 + row * 4, struct.pack("<I", value))
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
                trace.append(("count",))
                ret = count
            else:
                trace.append(("style", r0, r1 & 255))
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, index & 0xffffffff)
        u.emu_start((symbols["audio_terminal_session_apply_5ecb88"] if compiled else 0x5ecb88) | 1,
                    0x600000, count=10000)
        return trace, bytes(u.mem_read(state, 0x2a0))
    cases = 0
    for index in (-2, -1, 0, 1, 9, 10, 0x10000, 0xffff8000):
        for count in (0, 1, 3, 10):
            for special in (0, 1):
                for pattern in (0, 1, 2):
                    args = index, count, special, pattern
                    stock = run(False, *args)
                    selected = run(True, *args)
                    if stock != selected:
                        raise RuntimeError(f"session-apply mismatch {args}: {stock[0]} != {selected[0]}; state_equal={stock[1] == selected[1]}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_SESSION_APPLY_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Special row, bounded row loop, signed selected index and state update",
              "limits": ["Row-style child effects isolated; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()

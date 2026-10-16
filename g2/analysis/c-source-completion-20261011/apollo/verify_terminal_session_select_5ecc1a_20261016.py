#!/usr/bin/env python3
"""Compare Terminal session selection and lookup helpers against stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_select_5ecc1a.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-select-5ecc1a"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_td_active_session", 0x59732a),
         ("audio_terminal_session_animate_5896fc", 0x5896fc),
         ("audio_terminal_session_apply_5ecb88", 0x5ecb88),
         ("audio_terminal_session_focus_5ecbea", 0x5ecbea))
ENTRY = {"count": ("audio_terminal_session_count_5eca48", 0x5eca48),
         "valid": ("audio_terminal_session_valid_5eca64", 0x5eca64),
         "object": ("audio_terminal_session_object_5ecb52", 0x5ecb52),
         "select": ("audio_terminal_session_select_5ecc1a", 0x5ecc1a)}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "session-select-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n"
                    "__attribute__((noinline,used)) uint8_t *audio_td_active_session(void){return 0;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_terminal_session_animate_5896fc(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_session_apply_5ecb88(int32_t a){(void)a;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_session_focus_5ecbea(int32_t a){(void)a;}\n")
    elf = OUT / "session-select-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_session_select_5ecc1a",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, entry, index, prior, active_count, active_present, pattern, animate):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes(((i + pattern) & 255 for i in range(0x2a0))))
        for i in range(11):
            value = (0x2000a000 + i * 0x100) if pattern == 1 or (pattern == 2 and i % 2 == 0) else 0
            u.mem_write(state + 0x248 + i * 4, struct.pack("<I", value))
        u.mem_write(state + 0x27a, struct.pack("<h", prior))
        active = 0x20002000
        u.mem_write(active + 8, struct.pack("<I", active_count))
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
                trace.append(("active",))
                ret = active if active_present else 0
            elif i == 1:
                trace.append(("animate", r0, r1, r2))
                ret = animate
            elif i == 2:
                trace.append(("apply", r0))
                ret = 0
            else:
                trace.append(("focus", r0))
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, index & 0xffffffff)
        symbol, stock = ENTRY[entry]
        u.emu_start((symbols[symbol] if compiled else stock) | 1, 0x600000, count=10000)
        return (u.reg_read(A.UC_ARM_REG_R0) if entry != "select" else None,
                trace, bytes(u.mem_read(state, 0x2a0)))
    cases = 0
    def check(args):
        nonlocal cases
        stock = run(False, *args)
        candidate = run(True, *args)
        if stock != candidate:
            raise RuntimeError(f"session-select mismatch {args}: {stock[:2]} != {candidate[:2]}; state_equal={stock[2] == candidate[2]}")
        cases += 1
    for active_count in (0, 1, 3, 10, 11, 0xffffffff):
        for present in (0, 1):
            check(("count", 0, 0, active_count, present, 0, 0))
    for index in (-2, -1, 0, 1, 9, 10, 0x10000, 0xffff8000):
        for active_count in (0, 1, 3, 11):
            for present in (0, 1):
                check(("valid", index, 0, active_count, present, 0, 0))
                check(("object", index, 0, active_count, present, 1, 0))
    for prior in (-1, 0, 2):
        for index in (-2, -1, 0, 1, 2, 10):
            for active_count in (0, 3, 11):
                for pattern in (0, 1, 2):
                    for animate in (0, 1, 0x100):
                        check(("select", index, prior, active_count, 1, pattern, animate))
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_SESSION_SELECT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Count cap, signed validity/object lookup and selection animation/fallback decisions",
              "limits": ["Animation, direct-apply and focus child effects isolated; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()

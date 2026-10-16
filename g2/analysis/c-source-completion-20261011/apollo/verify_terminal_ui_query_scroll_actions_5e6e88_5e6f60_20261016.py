#!/usr/bin/env python3
"""Compare paired Terminal query-scroll actions against pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_query_scroll_actions_5e6e88_5e6f60.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-query-scroll-actions-5e6e88-5e6f60"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_terminal_display_status_44ea04", 0x44ea04),
         ("audio_terminal_query_layout_5ebb96", 0x5ebb96),
         ("audio_log_flags", 0x43d0ce),
         ("audio_log_extended", 0x43d574),
         ("compressed_log_output", 0x43ce9e))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "query-scroll-actions-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n"
                    "__attribute__((noinline,used)) void audio_terminal_display_status_44ea04(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_query_layout_5ebb96(void){}\n"
                    "__attribute__((noinline,used)) uint32_t audio_log_flags(void){return 0;}\n"
                    "__attribute__((noinline,used)) void audio_log_extended"
                    "(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)"
                    "{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\n"
                    "__attribute__((noinline,used)) uint32_t compressed_log_output"
                    "(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\n")
    elf = OUT / "query-scroll-actions-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e6e88",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, action, old, payload, present, flags, seed):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes(((i + seed) & 255 for i in range(0x2a0))))
        u.mem_write(state + 0x214, struct.pack("<I", 0x20009000 if present else 0))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address) in enumerate(CALLS)}
        trace = []
        def cstring(cpu, address):
            data = bytes(cpu.mem_read(address, 200))
            return data[:data.index(0)]
        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            regs = [cpu.reg_read(r) for r in
                    (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                     A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            if i == 0:
                trace.append(("scroll", *regs[:3]))
                ret = 0
            elif i == 1:
                trace.append(("layout",))
                ret = 0
            elif i == 2:
                trace.append(("flags",))
                ret = flags
            elif i == 3:
                stack = struct.unpack("<6I", bytes(cpu.mem_read(sp, 24)))
                trace.append(("extended", regs[0], cstring(cpu, regs[1]),
                              cstring(cpu, regs[2]), cstring(cpu, regs[3]),
                              stack[0], cstring(cpu, stack[1]), *stack[2:6]))
                ret = 0
            else:
                stack = struct.unpack("<3I", bytes(cpu.mem_read(sp, 12)))
                trace.append(("compact", regs[0], cstring(cpu, regs[1]),
                              cstring(cpu, regs[2]), regs[3], *stack))
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old)
        u.reg_write(A.UC_ARM_REG_R1, payload)
        entry = symbols[f"audio_terminal_ui_action_{action:x}"] if compiled else action
        u.emu_start(entry | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace, bytes(u.mem_read(state, 0x2a0))
    payloads = [0, 1, 0xffff, 0x10000000, 0x20000000, 0x40000000,
                0x80000000, 0x70001234, 0xf000abcd, 0xffffffff]
    cases = 0
    for action in (0x5e6e88, 0x5e6f60):
        for old in (0, 0x12345678):
            for payload in payloads:
                for present in (0, 1):
                    for flags in (0, 1, 2, 4, 5, 7):
                        for seed in (0, 0xa5):
                            args = action, old, payload, present, flags, seed
                            stock = run(False, *args)
                            candidate = run(True, *args)
                            if stock != candidate:
                                raise RuntimeError(f"query-scroll mismatch {args}: {stock[:2]} != {candidate[:2]}; state_equal={stock[2] == candidate[2]}")
                            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_TERMINAL_QUERY_SCROLL_ACTIONS_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
               "scope": "Both actions, packed fields, null guard, state updates, scroll/layout calls, enabled logs",
               "limits": ["Query layout, LVGL and logger lower effects isolated; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()

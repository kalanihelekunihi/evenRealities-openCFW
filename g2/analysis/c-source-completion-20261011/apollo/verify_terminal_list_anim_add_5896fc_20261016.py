#!/usr/bin/env python3
"""Compare Terminal animation elapsed, timeout and queue insertion with stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_list_anim_add_5896fc.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-list-anim-add-5896fc"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("g2_flashdb_candidate_tick", 0x4490cc),
         ("audio_terminal_list_anim_init_58966c", 0x58966c),
         ("audio_terminal_list_anim_process_58956e", 0x58956e),
         ("audio_log_flags", 0x43d0ce),
         ("audio_log_extended", 0x43d574),
         ("compressed_log_output", 0x43ce9e))
ENTRIES = {"elapsed": ("audio_terminal_list_anim_elapsed_5893f0", 0x5893f0),
           "poll": ("audio_terminal_list_anim_timeout_poll_5893fe", 0x5893fe),
           "add": ("audio_terminal_session_animate_5896fc", 0x5896fc)}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "list-anim-add-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_list_anim_state_base[0xd0];\n"
                    "__attribute__((noinline,used)) uint32_t g2_flashdb_candidate_tick(void){return 0;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_list_anim_init_58966c(void){}\n"
                    "__attribute__((noinline,used)) void audio_terminal_list_anim_process_58956e(void){}\n"
                    "__attribute__((noinline,used)) uint32_t audio_log_flags(void){return 0;}\n"
                    "__attribute__((noinline,used)) void audio_log_extended"
                    "(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)"
                    "{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\n"
                    "__attribute__((noinline,used)) uint32_t compressed_log_output"
                    "(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\n")
    elf = OUT / "list-anim-add-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_session_animate_5896fc",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, entry, old, new, duration, running, timeout, start,
            pending, tail, flags):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_list_anim_state_base"] if compiled else 0x20070ea8
        u.mem_write(state, bytes(((i * 7 + tail) & 255 for i in range(0xd0))))
        u.mem_write(state + 0xc1, bytes([tail]))
        u.mem_write(state + 0xc2, bytes([pending]))
        u.mem_write(state + 0xc3, bytes([running]))
        u.mem_write(state + 0xc4, bytes([3]))
        u.mem_write(state + 0xc8, struct.pack("<I", start))
        u.mem_write(state + 0xcc, struct.pack("<I", timeout))
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
                trace.append(("tick",))
                ret = 0x12345678
            elif i == 1:
                trace.append(("init",))
                cpu.mem_write(state, bytes(0xd0))
                ret = 0
            elif i == 2:
                trace.append(("process",))
                ret = 0
            elif i == 3:
                trace.append(("flags",))
                ret = flags
            elif i == 4:
                stack = struct.unpack("<5I", bytes(cpu.mem_read(sp, 20)))
                msg = cstring(cpu, stack[1])
                args = stack[2:5] if b"elapsed=" in msg else ()
                trace.append(("extended", regs[0], cstring(cpu, regs[1]),
                              cstring(cpu, regs[2]), cstring(cpu, regs[3]),
                              stack[0], msg, *args))
                ret = 0
            else:
                msg = cstring(cpu, regs[1])
                args = (regs[3], *struct.unpack("<2I", bytes(cpu.mem_read(sp, 8)))) if b"elapsed=" in msg else ()
                trace.append(("compact", regs[0], msg,
                              cstring(cpu, regs[2]), *args))
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old)
        u.reg_write(A.UC_ARM_REG_R1, new)
        u.reg_write(A.UC_ARM_REG_R2, duration)
        symbol, stock = ENTRIES[entry]
        u.emu_start((symbols[symbol] if compiled else stock) | 1,
                    0x600000, count=10000)
        return (u.reg_read(A.UC_ARM_REG_R0) if entry != "poll" else None,
                trace, bytes(u.mem_read(state, 0xd0)))
    cases = 0
    def check(args):
        nonlocal cases
        stock = run(False, *args)
        selected = run(True, *args)
        if stock != selected:
            raise RuntimeError(f"list-anim mismatch {args}: {stock[:2]} != {selected[:2]}; state_equal={stock[2] == selected[2]}")
        cases += 1
    for start in (0, 1, 0x12345600, 0xfffffffe):
        check(("elapsed", start, 0, 0, 0, 0, 0, 0, 0, 0))
    for running in (0, 1):
        for timeout in (0, 10, 200):
            for start in (0x12345600, 0x12345670):
                for flags in (0, 1, 2, 4, 7):
                    check(("poll", 0, 0, 0, running, timeout, start, 2, 0, flags))
    for pending in (0, 15, 16):
        for old, new in ((0, 0), (0x20001000, 0), (0, 0x20002000), (0x20001000, 0x20002000)):
            for running in (0, 1):
                for tail in (0, 15):
                    for flags in (0, 1, 2, 4, 7):
                        check(("add", old, new, 200, running, 0, 0, pending, tail, flags))
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_LIST_ANIM_ADD_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Elapsed tick, timeout recovery and enabled logs, queue capacity and insertion, process call",
              "limits": ["Queue processor and real logging/timer effects isolated; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()

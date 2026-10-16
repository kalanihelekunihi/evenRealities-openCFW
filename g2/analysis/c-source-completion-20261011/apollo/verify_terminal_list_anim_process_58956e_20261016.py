#!/usr/bin/env python3
"""Compare Terminal animation queue processor and completion callback with stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_list_anim_process_58956e.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-list-anim-process-58956e"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("g2_flashdb_candidate_tick", 0x4490cc),
         ("audio_terminal_list_anim_old_start_58c6c4", 0x58c6c4),
         ("audio_terminal_list_anim_new_start_58c622", 0x58c622),
         ("audio_terminal_list_anim_new_prepare_5894d6", 0x5894d6),
         ("audio_log_flags", 0x43d0ce),
         ("audio_log_extended", 0x43d574),
         ("compressed_log_output", 0x43ce9e))
ENTRIES = {"process": ("audio_terminal_list_anim_process_58956e", 0x58956e),
           "finish": ("audio_terminal_list_anim_finish_58949e", 0x58949e)}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "list-anim-process-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_list_anim_state_base[0xd0];\n"
                    "__attribute__((noinline,used)) uint32_t g2_flashdb_candidate_tick(void){return 0;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_list_anim_old_start_58c6c4(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_list_anim_new_start_58c622(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_list_anim_new_prepare_5894d6(uint32_t a){(void)a;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_log_flags(void){return 0;}\n"
                    "__attribute__((noinline,used)) void audio_log_extended"
                    "(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)"
                    "{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\n"
                    "__attribute__((noinline,used)) uint32_t compressed_log_output"
                    "(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\n")
    elf = OUT / "list-anim-process-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_list_anim_process_58956e",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, entry, pending, busy, active, head, old, new, duration,
            second, flags):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_list_anim_state_base"] if compiled else 0x20070ea8
        u.mem_write(state, bytes(((i * 7 + head) & 255 for i in range(0xd0))))
        u.mem_write(state + 0xc0, bytes([head]))
        u.mem_write(state + 0xc2, bytes([pending]))
        u.mem_write(state + 0xc3, bytes([busy]))
        u.mem_write(state + 0xc4, bytes([active]))
        u.mem_write(state + 0xc8, struct.pack("<I", 0x11223344))
        u.mem_write(state + 0xcc, struct.pack("<I", 300))
        u.mem_write(state + head * 12, struct.pack("<3I", old, new, duration))
        if second:
            u.mem_write(state + ((head + 1) % 16) * 12, struct.pack("<3I", 0x20003000, 0, 50))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address) in enumerate(CALLS)}
        finish = symbols["audio_terminal_list_anim_finish_58949e"] if compiled else 0x58949e
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
            elif i in (1, 2):
                callback = "finish" if (regs[2] & ~1) == (finish & ~1) else regs[2]
                trace.append(("old" if i == 1 else "new", regs[0], regs[1], callback))
                ret = 0
            elif i == 3:
                trace.append(("prepare", regs[0]))
                ret = 0
            elif i == 4:
                trace.append(("flags",))
                ret = flags
            elif i == 5:
                line, message = struct.unpack("<2I", bytes(cpu.mem_read(sp, 8)))
                trace.append(("extended", regs[0], cstring(cpu, regs[1]),
                              cstring(cpu, regs[2]), cstring(cpu, regs[3]),
                              line, cstring(cpu, message)))
                ret = 0
            else:
                trace.append(("compact", regs[0], cstring(cpu, regs[1]),
                              cstring(cpu, regs[2])))
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        symbol, stock = ENTRIES[entry]
        u.emu_start((symbols[symbol] if compiled else stock) | 1,
                    0x600000, count=10000)
        return trace, bytes(u.mem_read(state, 0xd0))
    cases = 0
    def check(args):
        nonlocal cases
        stock = run(False, *args)
        selected = run(True, *args)
        if stock != selected:
            raise RuntimeError(f"list-anim process mismatch {args}: {stock[0]} != {selected[0]}; state_equal={stock[1] == selected[1]}")
        cases += 1
    for pending in (0, 1, 2):
        for busy in (0, 1):
            for head in (0, 15):
                for old, new in ((0, 0), (0x20001000, 0), (0, 0x20002000),
                                 (0x20001000, 0x20002000)):
                    for duration in (0, 50):
                        for flags in (0, 2, 7):
                            check(("process", pending, busy, 0, head, old, new, duration, pending == 2, flags))
    for active in (0, 1, 2):
        for pending in (0, 1):
            for busy in (0, 1):
                for flags in (0, 2):
                    check(("finish", pending, busy, active, 0, 0x20001000, 0, 50, False, flags))
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_LIST_ANIM_PROCESS_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Queue guards, dequeue, null skip recursion, timing/active state, animation callbacks and finish",
              "limits": ["Old/new animation and new-object preparation lower effects isolated; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()

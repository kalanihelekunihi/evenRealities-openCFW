#!/usr/bin/env python3
"""Compare Terminal overlay-focus wrapper and packet builder with stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_status_publish_5e5498_5cf134.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-status-publish-5e5498-5cf134"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_log_flags", 0x43d0ce),
         ("audio_log_extended", 0x43d574),
         ("compressed_log_output", 0x43ce9e),
         ("audio_terminal_send_message_5ce7c4", 0x5ce7c4))
ENTRIES = (("audio_terminal_status_publish_5e5498", 0x5e5498),
           ("audio_terminal_pb_overlay_focus_5cf134", 0x5cf134))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "publish-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_message_sequence;\n"
                    "__attribute__((noinline,used)) uint32_t audio_log_flags(void){return 0;}\n"
                    "__attribute__((noinline,used)) void audio_log_extended"
                    "(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)"
                    "{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\n"
                    "__attribute__((noinline,used)) uint32_t compressed_log_output"
                    "(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_terminal_send_message_5ce7c4"
                    "(uint32_t a,uint32_t b,const void*c,uint32_t d,uint32_t e)"
                    "{(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\n")
    elf = OUT / "publish-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_status_publish_5e5498",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, entry, overlay, focused, sequence, flags):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        cell = symbols["audio_terminal_message_sequence"] if compiled else 0x20074fff
        u.mem_write(cell, bytes([sequence]))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address) in enumerate(CALLS)}
        trace = []
        def cstring(cpu, address):
            data = bytes(cpu.mem_read(address, 200))
            return data[:data.index(0)]
        def hook(cpu, pc, size, _):
            if not compiled and pc == 0x43c0e4:
                dest = cpu.reg_read(A.UC_ARM_REG_R0)
                count = cpu.reg_read(A.UC_ARM_REG_R1)
                fill = cpu.reg_read(A.UC_ARM_REG_R2) & 255
                assert count == 8 and fill == 0
                cpu.mem_write(dest, bytes(count))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
                return
            i = cuts.get(pc)
            if i is None:
                return
            regs = [cpu.reg_read(r) for r in
                    (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                     A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            if i == 0:
                trace.append(("flags",))
                ret = flags
            elif i == 1:
                stack = struct.unpack("<5I", bytes(cpu.mem_read(sp, 20)))
                trace.append(("extended", regs[0], cstring(cpu, regs[1]),
                              cstring(cpu, regs[2]), cstring(cpu, regs[3]),
                              stack[0], cstring(cpu, stack[1]), *stack[2:]))
                ret = 0
            elif i == 2:
                stack = struct.unpack("<2I", bytes(cpu.mem_read(sp, 8)))
                trace.append(("compact", regs[0], cstring(cpu, regs[1]),
                              cstring(cpu, regs[2]), regs[3], *stack))
                ret = 0
            else:
                notify = struct.unpack("<I", bytes(cpu.mem_read(sp, 4)))[0]
                trace.append(("send", regs[0], regs[1],
                              bytes(cpu.mem_read(regs[2], 8)), regs[3], notify))
                ret = 0x12345678
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, overlay)
        u.reg_write(A.UC_ARM_REG_R1, focused)
        name, stock_entry = ENTRIES[entry]
        u.emu_start((symbols[name] if compiled else stock_entry) | 1, 0x600000, count=10000)
        return trace, bytes(u.mem_read(cell, 1))
    cases = 0
    for entry in range(2):
        for overlay in (0, 1, 2, 0x1234):
            for focused in (0, 1, 0x12345678, 0xffffffff):
                for sequence in (0, 1, 0xff):
                    for flags in (0, 1, 2, 4, 7):
                        args = entry, overlay, focused, sequence, flags
                        stock = run(False, *args)
                        selected = run(True, *args)
                        if stock != selected:
                            raise RuntimeError(f"publish mismatch {args}: {stock[0]} != {selected[0]}")
                        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_STATUS_PUBLISH_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Both stock entries, exact packet bytes, sequence, enabled logging and send arguments",
              "limits": ["Real send and logger lower effects, sequence initialization and final placement remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()

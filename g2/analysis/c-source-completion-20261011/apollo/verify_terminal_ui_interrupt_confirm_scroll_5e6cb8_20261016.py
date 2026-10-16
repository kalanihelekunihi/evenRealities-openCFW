#!/usr/bin/env python3
"""Compare Terminal interrupt-confirm scroll action and toggle child with stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_interrupt_confirm_scroll_5e6cb8.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-interrupt-confirm-scroll-5e6cb8"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_terminal_toggle_view_5ec73c", 0x5ec73c),
         ("audio_terminal_status_apply_list_5ec3c0", 0x5ec3c0),
         ("audio_terminal_status_publish_5e5498", 0x5e5498),
         ("audio_log_flags", 0x43d0ce),
         ("audio_log_extended", 0x43d574),
         ("compressed_log_output", 0x43ce9e))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "interrupt-confirm-scroll-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n"
                    "__attribute__((noinline,used)) void audio_terminal_status_apply_list_5ec3c0"
                    "(uint32_t a){(void)a;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_status_publish_5e5498"
                    "(uint32_t a,uint32_t b){(void)a;(void)b;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_log_flags(void){return 0;}\n"
                    "__attribute__((noinline,used)) void audio_log_extended"
                    "(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)"
                    "{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\n"
                    "__attribute__((noinline,used)) uint32_t compressed_log_output"
                    "(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\n")
    elf = OUT / "interrupt-confirm-scroll-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e6cb8",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, entry, present, status, old, payload, flags):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes(0x2a0))
        for i, offset in enumerate((0x230, 0x238, 0x23c)):
            u.mem_write(state + offset, struct.pack("<I", 0x20009000 + i * 0x100 if present & (1 << i) else 0))
        u.mem_write(state + 0x278, bytes([status]))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address) in enumerate(CALLS)}
        trace = []
        def cstring(cpu, address):
            data = bytes(cpu.mem_read(address, 200))
            return data[:data.index(0)]
        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None or (entry == 1 and i == 0):
                return
            regs = [cpu.reg_read(r) for r in
                    (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                     A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            if i == 0:
                trace.append(("toggle",))
                ret = 0
            elif i == 1:
                assert regs[0] == state
                trace.append(("layout",))
                ret = 0
            elif i == 2:
                trace.append(("publish", regs[0], regs[1]))
                ret = 0
            elif i == 3:
                trace.append(("flags",))
                ret = flags
            elif i == 4:
                stack = struct.unpack("<4I", bytes(cpu.mem_read(sp, 16)))
                trace.append(("extended", regs[0], cstring(cpu, regs[1]),
                              cstring(cpu, regs[2]), cstring(cpu, regs[3]),
                              stack[0], cstring(cpu, stack[1]), stack[2], stack[3]))
                ret = 0
            else:
                selection = struct.unpack("<I", bytes(cpu.mem_read(sp, 4)))[0]
                trace.append(("compact", regs[0], cstring(cpu, regs[1]),
                              cstring(cpu, regs[2]), regs[3], selection))
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old)
        u.reg_write(A.UC_ARM_REG_R1, payload)
        name, stock_entry = (("audio_terminal_ui_action_5e6cb8", 0x5e6cb8),
                             ("audio_terminal_toggle_view_5ec73c", 0x5ec73c))[entry]
        u.emu_start((symbols[name] if compiled else stock_entry) | 1, 0x600000, count=10000)
        return trace, bytes(u.mem_read(state, 0x2a0))
    cases = 0
    for entry in (0, 1):
        for present in range(8):
            for status in (0, 1, 2):
                for old in (0, 0x1234):
                    for payload in (0, 1, 2, 0x101):
                        for flags in (0, 1, 2, 4, 7):
                            args = entry, present, status, old, payload, flags
                            stock = run(False, *args)
                            selected = run(True, *args)
                            if stock != selected:
                                raise RuntimeError(f"interrupt-confirm mismatch {args}: {stock[0]} != {selected[0]}")
                            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_INTERRUPT_CONFIRM_SCROLL_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Both stock entries, state guards, selection writes, layout/publish and enabled logging",
              "limits": ["List layout child and logger lower effects remain open; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()

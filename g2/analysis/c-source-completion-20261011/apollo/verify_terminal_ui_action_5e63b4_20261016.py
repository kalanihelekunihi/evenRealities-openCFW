#!/usr/bin/env python3
"""Compare Terminal event-word action with pinned stock, including message bytes."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_5e63b4.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e63b4"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "action-5e63b4-oracle-stub.c"
    stub.write_text("#include <stdint.h>\n"
                    "__attribute__((noinline,used)) void audio_terminal_event_emit_5eadd4"
                    "(uint32_t a,uint32_t b,const void*c){(void)a;(void)b;(void)c;}\n")
    elf = OUT / "action-5e63b4-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e63b4",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    def run(compiled, old, payload):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(0x200fef00, b"\xa5" * 0x100)
        emit = (symbols["audio_terminal_event_emit_5eadd4"] if compiled else 0x5eadd4) & ~1
        trace = []
        def hook(cpu, pc, size, _):
            if not compiled and pc == 0x43c0e4:
                dest = cpu.reg_read(A.UC_ARM_REG_R0)
                count = cpu.reg_read(A.UC_ARM_REG_R1)
                fill = cpu.reg_read(A.UC_ARM_REG_R2) & 255
                assert count == 8 and fill == 0
                cpu.mem_write(dest, bytes([fill]) * count)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            elif pc == emit:
                kind = cpu.reg_read(A.UC_ARM_REG_R0)
                event = cpu.reg_read(A.UC_ARM_REG_R1)
                message = cpu.reg_read(A.UC_ARM_REG_R2)
                trace.append((kind, event, bytes(cpu.mem_read(message, 8))))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old)
        u.reg_write(A.UC_ARM_REG_R1, payload)
        entry = symbols["audio_terminal_ui_action_5e63b4"] if compiled else 0x5e63b4
        u.emu_start(entry | 1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace
    payloads = [0, 1, 0xffff, 0x00100000, 0x00f00000, 0x01000000,
                0x3f100000, 0x40000000, 0x7fffffff, 0x80000000,
                0xdeadbeef, 0xffffffff]
    cases = 0
    for old in (0, 1, 0x1234, 0xffffffff):
        for payload in payloads:
            stock = run(False, old, payload)
            selected = run(True, old, payload)
            if stock != selected:
                raise RuntimeError(f"action 5e63b4 mismatch {old:#x} {payload:#x}: {stock} != {selected}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_5E63B4_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Packed event fields, exact eight-byte message, call guard and return",
              "limits": ["Emitter lower effects and final placement remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))

if __name__ == "__main__":
    main()

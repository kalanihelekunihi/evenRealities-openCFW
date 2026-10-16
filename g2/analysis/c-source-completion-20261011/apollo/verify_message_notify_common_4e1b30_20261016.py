#!/usr/bin/env python3
"""Compare MessageNotify 0x4e1b30 with its C body under controlled children."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
                               UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/message_notify_common_4e1b30.c"
OUT = G2 / "build/c-firmware/20261016/main-message-notify-common"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = '''#include <stdint.h>
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_system_alert_command_45a8ee(uint32_t a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t audio_message_notify_frame_process_4d6ba8(const void*a,uint16_t b){(void)a;(void)b;return 0;}
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(payload, segments, symbols, compiled, command, data, length, value, flags):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x20000000, 0x100000)
    for address, content in segments:
        cpu.mem_write(address, content)
    state = (symbols["audio_message_notify_startup_state_20074fe5"]
             if compiled else 0x20074fe5)
    cpu.mem_write(state, b"\x39")
    pointer = 0x20007000
    cpu.mem_write(pointer, data)
    cpu.reg_write(UC_ARM_REG_R0, command)
    cpu.reg_write(UC_ARM_REG_R1, pointer)
    cpu.reg_write(UC_ARM_REG_R2, length)
    cpu.reg_write(UC_ARM_REG_R3, value)
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    native = {0x43d0ce: "flags", 0x43d574: "extended",
              0x43ce9e: "compact", 0x43c0e4: "zero",
              0x45a8ee: "alert", 0x4d6ba8: "frame"}
    named = {"audio_log_flags": "flags", "audio_log_extended": "extended",
             "compressed_log_output": "compact", "audio_uart_buffer_zero": "zero",
             "audio_system_alert_command_45a8ee": "alert",
             "audio_message_notify_frame_process_4d6ba8": "frame"}
    hooks = ({symbols[name] & ~1: kind for name, kind in named.items()}
             if compiled else native)
    calls = []

    def cstr(address):
        if not address:
            return ""
        out = bytearray()
        for offset in range(256):
            b = cpu.mem_read(address + offset, 1)[0]
            if not b:
                break
            out.append(b)
        return out.decode("latin1")

    def hook(machine, pc, size, unused):
        kind = hooks.get(pc)
        if kind is None:
            return
        a, b, c, d = (machine.reg_read(r) for r in
                      (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
        if kind == "flags":
            calls.append((kind,))
            result = flags
        elif kind == "extended":
            calls.append((kind, a, cstr(b), cstr(c), cstr(d),
                          int.from_bytes(machine.mem_read(machine.reg_read(UC_ARM_REG_SP), 4), "little")))
            result = 0
        elif kind == "compact":
            calls.append((kind, a, cstr(b), cstr(c), d))
            result = 0
        elif kind == "frame":
            calls.append((kind, b))
            result = 0
        elif kind == "zero":
            calls.append((kind, b, c))
            machine.mem_write(a, bytes([c & 255]) * b)
            result = a
        elif kind == "alert":
            calls.append((kind, a, c, d, bytes(machine.mem_read(b, c))))
            result = 0
        else:
            raise AssertionError(kind)
        machine.reg_write(UC_ARM_REG_R0, result)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = symbols["audio_uart_registry_callback_4e1b30"] if compiled else 0x4e1b30
    cpu.emu_start(entry | 1, 0x600000, count=2500)
    return cpu.reg_read(UC_ARM_REG_R0), cpu.mem_read(state, 1), calls


def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "message-notify-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "message-notify-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_registry_callback_4e1b30",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for command, first, second, length, value, flags in itertools.product(
            (0, 1, 5, 255), (0, 1, 2), (0, 2, 4, 5, 0x82),
            (0, 1, 6, 65537), (0, 0x12345678), (0, 1, 2, 4, 7)):
        data = bytes((first, second, 0x12, 0x34, 0x56, 0x78, 0x9a, 0xbc))
        args = (command, data, length, value, flags)
        stock = run(payload, segments, symbols, False, *args)
        actual = run(payload, segments, symbols, True, *args)
        if stock != actual:
            raise RuntimeError(f"MessageNotify mismatch {args}: {stock!r} != {actual!r}")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MESSAGE_NOTIFY_COMMON_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf_path),
               "cases": cases,
               "scope": "command dispatch, startup state, request bytes, child arguments and logging branches",
               "limits": ["Frame decoder 0x4d6ba8 and final RAM placement remain open.",
                          "No full-image or hardware proof."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

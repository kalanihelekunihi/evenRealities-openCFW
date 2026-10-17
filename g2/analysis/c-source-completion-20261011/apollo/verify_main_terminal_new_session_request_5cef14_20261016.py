#!/usr/bin/env python3
"""Compare new-session request packet encoder's stock/C call contract."""
import hashlib
import itertools
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_new_session_request_encode_5cef14.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-new-session-request-5cef14"
SEQ = 0x20074fff
CALLS = {"audio_uart_buffer_zero": 0x43c0e4,
         "audio_log_flags": 0x43d0ce,
         "audio_log_extended": 0x43d574,
         "compressed_log_output": 0x43ce9e,
         "audio_terminal_send_message_5ce7c4": 0x5ce7c4}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "new-session-request-oracle.o"
    elf = OUT / "new-session-request-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defs = {"audio_terminal_message_sequence": SEQ}
    defs.update({name: address | 1 for name, address in CALLS.items()})
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    *(f"--defsym={name}=0x{address:x}" for name, address in defs.items()),
                    str(obj), "-o", str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open("rb") as f:
        e = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbol = next(s["st_value"] for s in
                      e.get_section_by_name(".symtab").iter_symbols()
                      if s.name == "audio_terminal_new_session_request_5cef14")

    def run(compiled, host, sequence, flags):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(SEQ, bytes((sequence,)))
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, host)
        trace = []
        flag_index = 0

        def cstr(cpu, ptr):
            return bytes(cpu.mem_read(ptr, 180)).split(b"\0", 1)[0]

        def hook(cpu, pc, size, _):
            nonlocal flag_index
            if pc not in CALLS.values():
                return
            r = [cpu.reg_read(reg) for reg in
                 (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                  A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            result = 0
            if pc == 0x43c0e4:
                trace.append(("zero", r[1], r[2]))
                cpu.mem_write(r[0], bytes((r[2] & 255,)) * r[1])
                result = r[0]
            elif pc == 0x43d0ce:
                trace.append(("flags", flag_index))
                result = flags[min(flag_index, len(flags) - 1)]
                flag_index += 1
            elif pc == 0x43d574:
                line, message, magic, sent_host = struct.unpack("<IIII", cpu.mem_read(sp, 16))
                trace.append(("extended", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]),
                              cstr(cpu, r[3]), line, cstr(cpu, message), magic, sent_host))
            elif pc == 0x43ce9e:
                sent_host = struct.unpack("<I", cpu.mem_read(sp, 4))[0]
                trace.append(("compact", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]),
                              r[3], sent_host))
            else:
                fifth = struct.unpack("<I", cpu.mem_read(sp, 4))[0]
                trace.append(("send", r[0], r[1], bytes(cpu.mem_read(r[2], 4)),
                              r[3], fifth))
                result = 0x1234
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start((symbol if compiled else 0x5cef14) | 1,
                    0x600000, count=260)
        return trace, u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(SEQ, 1))

    cases = 0
    for args in itertools.product((0, 1, 0x12345678, 0xffffffff),
                                  (0, 1, 255),
                                  ((0, 0, 0), (2, 0, 0),
                                   (0, 1, 0), (0, 0, 4), (2, 1, 4))):
        stock, candidate = run(False, *args), run(True, *args)
        if stock != candidate:
            print("mismatch", args, stock, candidate)
            raise RuntimeError("new-session request mismatch")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_NEW_SESSION_REQUEST_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf),
               "cases": cases,
               "scope": "Four-byte host packet, sequence wrap, enabled logs, send arguments and return",
               "limits": ["Lower packet transport/logger effects isolated; selector action and final image/hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

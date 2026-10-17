#!/usr/bin/env python3
"""Compare query-notification activation with pinned stock Apollo."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_query_notification_activate_5e66d8.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-query-notification-activate-5e66d8"
STATE, ACTIVE = 0x2006e0d0, 0x20080000
CALLS = {
    "audio_terminal_counter_b_get_5973dc": (0x5973dc, 0),
    "audio_td_active_session": (0x59732a, 0),
    "audio_td_host_counter_get_5973d4": (0x5973d4, 0),
    "audio_td_dismiss_query_notification": (0x5974d4, 1),
    "audio_terminal_ui_restore_query_5e6620": (0x5e6620, 1),
    "audio_terminal_ui_stop_service_e_5ec9c0": (0x5ec9c0, 0),
    "audio_terminal_ui_action_5e583c": (0x5e583c, 2),
    "audio_terminal_ui_event_5e5484": (0x5e5484, 3),
    "audio_terminal_reset_ancillary_5e65f8": (0x5e65f8, 0),
    "audio_terminal_session_switch_request_5cee8c": (0x5cee8c, 2),
    "audio_log_flags": (0x43d0ce, 0),
    "audio_log_extended": (0x43d574, 0),
    "compressed_log_output": (0x43ce9e, 0),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj, elf = OUT / "activate-oracle.o", OUT / "activate-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defs = {name: address | 1 for name, (address, _) in CALLS.items()}
    defs["audio_terminal_ui_state_base"] = STATE
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    *(f"--defsym={name}=0x{address:x}" for name, address in defs.items()),
                    str(obj), "-o", str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open("rb") as f:
        e = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbol = next(s["st_value"] for s in
                      e.get_section_by_name(".symtab").iter_symbols()
                      if s.name == "audio_terminal_ui_action_5e66d8")
    by_address = {address: (name, argc) for name, (address, argc) in CALLS.items()}

    def run(compiled, old, target, current, host, active, hit, flags):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        initial = bytearray(0x2a0)
        initial[0x27f] = 0x71
        initial[0x288:0x28c] = struct.pack("<I", target)
        u.mem_write(STATE, bytes(initial))
        records = bytearray(0x400)
        records[8:12] = struct.pack("<I", 3)
        for i, value in enumerate((0x1111, target if hit else 0x2222, 0x3333)):
            records[0x9c+i*0x90:0xa0+i*0x90] = struct.pack("<I", value)
        u.mem_write(ACTIVE, bytes(records))
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old)
        u.reg_write(A.UC_ARM_REG_R1, 0xdeadbeef)
        trace = []
        flag_index = 0

        def cstr(cpu, ptr):
            return bytes(cpu.mem_read(ptr, 190)).split(b"\0", 1)[0]

        def hook(cpu, pc, size, _):
            nonlocal flag_index
            if pc not in by_address:
                return
            name, argc = by_address[pc]
            r = [cpu.reg_read(reg) for reg in
                 (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                  A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            result = 0
            if name == "audio_log_flags":
                trace.append(("flags", flag_index))
                result = flags[min(flag_index, len(flags)-1)]
                flag_index += 1
            elif name == "audio_log_extended":
                line, message = struct.unpack("<II", cpu.mem_read(sp, 8))
                count = 3 if line == 0x627 else int(line in (0x619, 0x62d))
                values = struct.unpack("<" + "I" * count,
                                       cpu.mem_read(sp+8, count*4)) if count else ()
                trace.append(("extended", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]),
                              cstr(cpu, r[3]), line, cstr(cpu, message), values))
            elif name == "compressed_log_output":
                count = 3 if r[0] == 0x08c00000 else int(r[0] == 0x0c400000)
                values = ((r[3],) + struct.unpack("<" + "I" * (count-1),
                           cpu.mem_read(sp, (count-1)*4))) if count else ()
                trace.append(("compact", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]), values))
            else:
                trace.append((name, tuple(r[:argc])))
            if name == "audio_terminal_counter_b_get_5973dc":
                result = current
            elif name == "audio_td_active_session":
                result = ACTIVE if active else 0
            elif name == "audio_td_host_counter_get_5973d4":
                result = host
            elif name == "audio_terminal_ui_restore_query_5e6620":
                result = 13
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start((symbol if compiled else 0x5e66d8) | 1, 0x600000, count=1500)
        return trace, bytes(u.mem_read(STATE, 0x2a0)), u.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for args in itertools.product((2, 10, 0x10a), (0, 0x1234),
                                  (0x1234, 0x5678), (0, 0x9999),
                                  (0, 1), (0, 1),
                                  ((0, 0, 0), (2, 0, 0),
                                   (0, 1, 0), (0, 0, 4), (2, 1, 4))):
        stock, candidate = run(False, *args), run(True, *args)
        if stock != candidate:
            for n, (a, b) in enumerate(itertools.zip_longest(stock[0], candidate[0])):
                if a != b:
                    print("first call mismatch", args, n, a, b)
                    break
            if stock[1] != candidate[1]:
                print("state differs", args)
            print("return", stock[2], candidate[2])
            raise RuntimeError("query-notification activation mismatch")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_NOTIFICATION_ACTIVATE_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
               "scope": "No target, current, unavailable and switch-request paths, record lookup, enabled logs",
               "limits": ["Calls are isolated; full image and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

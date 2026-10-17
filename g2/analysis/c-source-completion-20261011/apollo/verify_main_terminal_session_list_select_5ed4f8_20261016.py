#!/usr/bin/env python3
"""Compare all selector command branches against stock Apollo call/state contract."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_session_list_select_5ed4f8.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-list-select-5ed4f8"
STATE = 0x2006e0d0
CALLS = {
    "audio_terminal_session_command_5eca3e": (0x5eca3e, 1),
    "audio_terminal_session_index_i16_5eca44": (0x5eca44, 1),
    "audio_td_active_session": (0x59732a, 0),
    "audio_terminal_session_valid_5eca64": (0x5eca64, 1),
    "audio_terminal_session_switch_event_5ed1ec": (0x5ed1ec, 1),
    "audio_terminal_ui_stop_service_a_5eceb2": (0x5eceb2, 0),
    "audio_terminal_session_root_hide_5ed1d6": (0x5ed1d6, 0),
    "audio_terminal_request_display": (0x5e43d2, 2),
    "audio_terminal_session_switch_request_5cee8c": (0x5cee8c, 2),
    "audio_uart_page_43ded4": (0x43ded4, 2),
    "audio_terminal_session_pending_prompt_5ece4c": (0x5ece4c, 1),
    "audio_td_has_active_session": (0x5973b2, 0),
    "audio_td_host_counter_get_5973d4": (0x5973d4, 0),
    "audio_terminal_new_session_request_5cef14": (0x5cef14, 1),
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
    obj = OUT / "select-oracle.o"
    elf = OUT / "select-oracle.elf"
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
                      if s.name == "audio_terminal_ui_action_5ed4f8")
    by_address = {address: (name, argc) for name, (address, argc) in CALLS.items()}

    def run(compiled, mode, index, active, valid, has_active, root, flags):
        payload = ((mode & 255) << 16) | (index & 0xffff)
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(STATE, bytes((i * 7 + 11) & 255 for i in range(0x2a0)))
        u.mem_write(STATE + 4, struct.pack("<I", root))
        u.mem_write(0x20080000, bytes(0x400))
        u.mem_write(0x20080000, struct.pack("<I", 0x77777777))
        for i in range(3):
            u.mem_write(0x2008009c + i * 0x90, struct.pack("<I", 0x111000 + i))
            u.mem_write(0x20080122 + i * 0x90, bytes((i + 1,)))
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, 11)
        u.reg_write(A.UC_ARM_REG_R1, payload)
        trace = []
        flag_index = 0
        host_index = 0

        def cstr(cpu, ptr):
            return bytes(cpu.mem_read(ptr, 190)).split(b"\0", 1)[0]

        def hook(cpu, pc, size, _):
            nonlocal flag_index, host_index
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
                result = flags[min(flag_index, len(flags) - 1)]
                flag_index += 1
            elif name == "audio_log_extended":
                line, message = struct.unpack("<II", cpu.mem_read(sp, 8))
                n = 2 if line in (0x20f, 0x21b, 0x22c) else 1
                values = struct.unpack("<" + "I" * n, cpu.mem_read(sp + 8, n * 4))
                trace.append(("extended", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]),
                              cstr(cpu, r[3]), line, cstr(cpu, message), values))
            elif name == "compressed_log_output":
                n = 2 if r[0] in (0x0c800000, 0x08800000) else 1
                values = (r[3],) + struct.unpack("<" + "I" * (n - 1),
                                                 cpu.mem_read(sp, 4 * (n - 1)))
                trace.append(("compact", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]), values))
            elif name == "audio_terminal_session_pending_prompt_5ece4c":
                trace.append((name, cstr(cpu, r[0])))
            else:
                trace.append((name, tuple(r[:argc])))
            if name == "audio_terminal_session_command_5eca3e":
                result = mode & 255
            elif name == "audio_terminal_session_index_i16_5eca44":
                result = index & 0xffffffff
            elif name == "audio_td_active_session":
                result = 0x20080000 if active else 0
            elif name == "audio_terminal_session_valid_5eca64":
                result = valid
            elif name == "audio_td_has_active_session":
                result = has_active
            elif name == "audio_td_host_counter_get_5973d4":
                result = 0x888000 + host_index
                host_index += 1
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start((symbol if compiled else 0x5ed4f8) | 1,
                    0x600000, count=1500)
        return trace, bytes(u.mem_read(STATE, 0x2a0)), u.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for args in itertools.product((0, 1, 2, 3, 4, 0x101),
                                  (-1, 0, 2), (0, 1), (0, 1), (0, 1),
                                  (0, 0x20090000),
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
            raise RuntimeError("selector command action mismatch")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_LIST_SELECT_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf),
               "cases": cases,
               "scope": "All four selector command modes, active/valid gates, pending state, enabled logs and return",
               "limits": ["Lower packet/UI/logger effects are isolated; full image and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

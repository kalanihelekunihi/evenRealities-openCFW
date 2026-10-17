#!/usr/bin/env python3
"""Compare the session-id-change FSM action with pinned stock Apollo bytes."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_session_id_changed_5e5580.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-id-changed-5e5580"
STATE = 0x2006e0d0
CALLS = {
    "audio_ux_get_system_ble_status": (0x47d8ce, 0),
    "audio_terminal_runtime_event_from_ble": (0x5e50ea, 1),
    "audio_terminal_ui_stop_service_a_5eceb2": (0x5eceb2, 0),
    "audio_terminal_ui_stop_service_b_5ec268": (0x5ec268, 0),
    "audio_terminal_ui_stop_service_c_5ebbc6": (0x5ebbc6, 0),
    "audio_terminal_ui_stop_service_d_5ec770": (0x5ec770, 0),
    "audio_terminal_ui_stop_service_e_5ec9c0": (0x5ec9c0, 0),
    "audio_terminal_reset_mode_5eae2c": (0x5eae2c, 1),
    "audio_terminal_reset_ancillary_5e65f8": (0x5e65f8, 0),
    "audio_terminal_ui_event_5e5484": (0x5e5484, 3),
    "audio_terminal_ui_action_5e583c": (0x5e583c, 2),
    "audio_terminal_ui_action_5e522e": (0x5e522e, 2),
    "audio_terminal_ui_action_5e5290": (0x5e5290, 2),
    "audio_terminal_ui_action_5e52c2": (0x5e52c2, 2),
    "audio_terminal_ui_action_5e6548": (0x5e6548, 2),
    "audio_terminal_ui_action_5e641c": (0x5e641c, 2),
    "audio_terminal_ui_action_5e57c6": (0x5e57c6, 2),
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
    obj, elf = OUT / "session-id-oracle.o", OUT / "session-id-oracle.elf"
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
                      if s.name == "audio_terminal_ui_action_5e5580")
    by_address = {address: (name, argc) for name, (address, argc) in CALLS.items()}

    def run(compiled, old, payload, event, pending, session, flags):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        initial = bytearray(0x2a0)
        initial[0x27e] = 0xab
        initial[0x27f] = pending
        initial[0x288:0x28c] = struct.pack("<I", session)
        u.mem_write(STATE, bytes(initial))
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old)
        u.reg_write(A.UC_ARM_REG_R1, payload)
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
                count = int(line in (0x3bb, 0x3bf))
                values = struct.unpack("<" + "I" * count,
                                       cpu.mem_read(sp+8, count*4)) if count else ()
                trace.append(("extended", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]),
                              cstr(cpu, r[3]), line, cstr(cpu, message), values))
            elif name == "compressed_log_output":
                values = (r[3],) if r[0] == 0x0c400000 else ()
                trace.append(("compact", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]), values))
            else:
                trace.append((name, tuple(r[:argc])))
            if name == "audio_ux_get_system_ble_status":
                result = 17
            elif name == "audio_terminal_runtime_event_from_ble":
                result = event
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start((symbol if compiled else 0x5e5580) | 1, 0x600000, count=1500)
        return trace, bytes(u.mem_read(STATE, 0x2a0)), u.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for args in itertools.product((3, 10, 1, 0x103), (0x1234, 0x4321),
                                  (0, 2, 3, 4, 6, 7, 22, 0x107), (0, 1),
                                  (0x1234,),
                                  ((0, 0, 0), (2, 0, 0), (0, 1, 0),
                                   (0, 0, 4), (2, 1, 4))):
        stock, candidate = run(False, *args), run(True, *args)
        if stock != candidate:
            for n, (a, b) in enumerate(itertools.zip_longest(stock[0], candidate[0])):
                if a != b:
                    print("first call mismatch", args, n, a, b)
                    break
            if stock[1] != candidate[1]:
                print("state differs", args)
            print("return", stock[2], candidate[2])
            raise RuntimeError("session-id-change action mismatch")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_ID_CHANGED_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
               "scope": "Blocked, active-session, reset and all event dispatch branches with enabled logs",
               "limits": ["Calls are isolated; full image and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

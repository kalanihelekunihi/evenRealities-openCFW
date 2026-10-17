#!/usr/bin/env python3
"""Compare query-reply FSM action with pinned Apollo stock call and state contract."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_query_reply_5e69a0.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-query-reply-5e69a0"
STATE, SESSION = 0x2006e0d0, 0x20080000
CALLS = {
    "audio_td_session_struct_ptr": (0x59731e, 0),
    "audio_terminal_reset_display_5e4c84": (0x5e4c84, 1),
    "audio_terminal_query_reply_send_5ced38": (0x5ced38, 1),
    "audio_terminal_ui_stop_service_c_5ebbc6": (0x5ebbc6, 0),
    "audio_td_session_struct_clear": (0x597124, 0),
    "audio_uart_page_43dfa4": (0x43dfa4, 2),
    "audio_terminal_processing_prepare_5ea30c": (0x5ea30c, 0),
    "audio_terminal_set_label_style_5e482a": (0x5e482a, 4),
    "audio_terminal_select_output_mode_5ea2a8": (0x5ea2a8, 1),
    "audio_uart_page_49942e": (0x49942e, 2),
    "audio_terminal_elapsed_refresh_5e4902": (0x5e4902, 0),
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
    obj, elf = OUT / "query-reply-oracle.o", OUT / "query-reply-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defs = {name: address | 1 for name, (address, _) in CALLS.items()}
    defs.update(audio_terminal_ui_state_base=STATE,
                audio_terminal_output_style_20003f80=0x20003f80,
                audio_terminal_output_payload_20074a94=0x20074a94,
                audio_terminal_output_active_2007502c=0x2007502c,
                audio_terminal_output_mode_2007502d=0x2007502d)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    *(f"--defsym={name}=0x{address:x}" for name, address in defs.items()),
                    str(obj), "-o", str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open("rb") as f:
        e = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbol = next(s["st_value"] for s in
                      e.get_section_by_name(".symtab").iter_symbols()
                      if s.name == "audio_terminal_ui_action_5e69a0")
    by_address = {address: (name, argc) for name, (address, argc) in CALLS.items()}

    def run(compiled, payload, count, widgets, session_present, flags):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        initial = bytearray(0x2a0)
        initial[0x28c] = 0x65
        if widgets:
            for offset, value in ((0x1cc, 0x20090000), (0x1d0, 0x20090020),
                                  (0x1d4, 0x20090040), (0x1dc, 0x20090060)):
                initial[offset:offset+4] = struct.pack("<I", value)
        u.mem_write(STATE, bytes(initial))
        records = bytearray(0x1000)
        records[0:4] = struct.pack("<I", 0x12345678)
        records[0x406:0x408] = struct.pack("<H", count)
        for i in range(3):
            records[0x408+i*0x88:0x40c+i*0x88] = struct.pack("<I", 0xabcdef00+i)
        u.mem_write(SESSION, bytes(records))
        u.mem_write(0x20074a94, struct.pack("<I", 0xbabababa))
        u.mem_write(0x2007502c, bytes((0x41, 0x42)))
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, 7)
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
                values = struct.unpack("<III", cpu.mem_read(sp+8, 12))
                trace.append(("extended", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]),
                              cstr(cpu, r[3]), line, cstr(cpu, message), values))
            elif name == "compressed_log_output":
                values = (r[3],) + struct.unpack("<II", cpu.mem_read(sp, 8))
                trace.append(("compact", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]), values))
            elif name == "audio_terminal_query_reply_send_5ced38":
                trace.append((name, struct.unpack("<II", cpu.mem_read(r[0], 8))))
            elif name == "audio_uart_page_49942e":
                trace.append((name, r[0], cstr(cpu, r[1])))
            else:
                trace.append((name, tuple(r[:argc])))
            if name == "audio_td_session_struct_ptr":
                result = SESSION if session_present else 0
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start((symbol if compiled else 0x5e69a0) | 1, 0x600000, count=1500)
        return (trace, bytes(u.mem_read(STATE, 0x2a0)),
                bytes(u.mem_read(0x20074a94, 4)),
                bytes(u.mem_read(0x2007502c, 2)), u.reg_read(A.UC_ARM_REG_R0))

    cases = 0
    payloads = (0, 1, 2, 0x80000101, 0x80000202, 0x00000102)
    for args in itertools.product(payloads, (0, 2, 3), (0, 1), (0, 1),
                                  ((0, 0, 0), (2, 0, 0), (0, 1, 0),
                                   (0, 0, 4), (2, 1, 4))):
        stock, candidate = run(False, *args), run(True, *args)
        if stock != candidate:
            for n, (a, b) in enumerate(itertools.zip_longest(stock[0], candidate[0])):
                if a != b:
                    print("first call mismatch", args, n, a, b)
                    break
            for n in range(1, len(stock)):
                if stock[n] != candidate[n]:
                    print("field differs", args, n, stock[n], candidate[n])
            raise RuntimeError("query-reply action mismatch")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_REPLY_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
               "scope": "Query index, packet, output flags, widget gate, enabled logging and state cells",
               "limits": ["Packet sender and UI effects isolated; whole image and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

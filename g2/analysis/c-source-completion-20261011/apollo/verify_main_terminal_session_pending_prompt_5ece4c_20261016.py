#!/usr/bin/env python3
"""Compare pending selector prompt's widget gate and state with stock Apollo."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_pending_prompt_5ece4c.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-pending-prompt-5ece4c"
STATE = 0x2006e0d0
CALLS = {
    "audio_terminal_ui_stop_service_a_5eceb2": 0x5eceb2,
    "audio_terminal_session_root_hide_5ed1d6": 0x5ed1d6,
    "audio_terminal_processing_prepare_5ea30c": 0x5ea30c,
    "audio_uart_page_43dfa4": 0x43dfa4,
    "audio_terminal_image_set_5e47fe": 0x5e47fe,
    "audio_uart_page_49942e": 0x49942e,
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "pending-prompt-oracle.o"
    elf = OUT / "pending-prompt-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defs = {name: address | 1 for name, address in CALLS.items()}
    defs.update(audio_terminal_ui_state_base=STATE,
                audio_terminal_asset_7733a8=0x7733a8)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    *(f"--defsym={name}=0x{address:x}" for name, address in defs.items()),
                    str(obj), "-o", str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open("rb") as f:
        e = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbol = next(s["st_value"] for s in
                      e.get_section_by_name(".symtab").iter_symbols()
                      if s.name == "audio_terminal_session_pending_prompt_5ece4c")
    by_address = {address: name for name, address in CALLS.items()}

    def run(compiled, missing, message):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(STATE, bytes((i * 7 + 11) & 255 for i in range(0x2a0)))
        for i, offset in enumerate((0x1cc, 0x1d0, 0x1d4, 0x1dc)):
            u.mem_write(STATE + offset,
                        struct.pack("<I", 0 if i == missing else 0x20090000 + i * 0x1000))
        u.mem_write(0x20081000, message + b"\0")
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, 0x20081000)
        trace = []

        def cstr(cpu, ptr):
            return bytes(cpu.mem_read(ptr, 100)).split(b"\0", 1)[0]

        def hook(cpu, pc, size, _):
            if pc not in by_address:
                return
            r = [cpu.reg_read(reg) for reg in
                 (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1)]
            if pc == 0x43dfa4 or pc == 0x5e47fe:
                trace.append((pc, r[0], r[1]))
            elif pc == 0x49942e:
                trace.append((pc, r[0], cstr(cpu, r[1])))
            else:
                trace.append((pc,))
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start((symbol if compiled else 0x5ece4c) | 1,
                    0x600000, count=220)
        return trace, bytes(u.mem_read(STATE, 0x2a0))

    cases = 0
    for missing, message in itertools.product((-1, 0, 1, 2, 3),
                                              (b"", b" ", b"Pending")):
        stock, candidate = run(False, missing, message), run(True, missing, message)
        if stock != candidate:
            print("mismatch", missing, message, stock[0], candidate[0])
            raise RuntimeError("pending prompt mismatch")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_PENDING_PROMPT_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf),
               "cases": cases,
               "scope": "Four-widget gate, call order, label bytes and pending flag",
               "limits": ["Lower LVGL effects and selector action remain open; full image/hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

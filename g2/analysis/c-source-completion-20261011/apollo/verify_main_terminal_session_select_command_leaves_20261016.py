#!/usr/bin/env python3
"""Compare selector command and TD host-counter C leaves with stock Apollo."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_select_command_leaves_20261016.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-select-command-leaves"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "command-leaves-oracle.o"
    elf = OUT / "command-leaves-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    "--defsym=audio_td_state=0x2010fd20", str(obj), "-o", str(elf)],
                   check=True, stderr=subprocess.DEVNULL)
    with elf.open("rb") as f:
        e = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   e.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, kind, value):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x200000)
        u.mem_write(0x20119280, struct.pack("<I", value))
        u.reg_write(A.UC_ARM_REG_SP, 0x201ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, value)
        if kind == "command":
            native, name = 0x5eca3e, "audio_terminal_session_command_5eca3e"
        else:
            native, name = 0x5973d4, "audio_td_host_counter_get_5973d4"
        u.emu_start((symbols[name] if compiled else native) | 1,
                    0x600000, count=40)
        return u.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    values = (0, 1, 0xffff, 0x10000, 0x20000, 0x30000,
              0xff0000, 0x12345678, 0x80000000, 0xffffffff)
    for kind in ("command", "host"):
        for value in values:
            stock, candidate = run(False, kind, value), run(True, kind, value)
            if stock != candidate:
                raise RuntimeError(f"command leaf mismatch {kind} {value}: {stock} {candidate}")
            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_SELECT_COMMAND_LEAVES_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf),
               "cases": cases,
               "scope": "Payload bits 16-23 and TD host counter at observed RAM 0x20119280",
               "limits": ["Selector command action, packet encoders, final RAM placement and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

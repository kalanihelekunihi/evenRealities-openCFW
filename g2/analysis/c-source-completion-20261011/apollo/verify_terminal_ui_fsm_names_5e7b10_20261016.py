#!/usr/bin/env python3
"""Compare Terminal FSM name lookup over full byte input domains."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_fsm_names_5e7b10.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-fsm-names-5e7b10"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOOKUPS = [(0x5e7b10, "audio_terminal_ui_state_name_5e7b10",
            "audio_terminal_ui_state_names", 0x20003ea4, 13, "UNKNOWN_STATE"),
           (0x5e7b2a, "audio_terminal_ui_event_name_5e7b2a",
            "audio_terminal_ui_event_names", 0x20003edc, 40, "UNKNOWN_EVENT")]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e7e60-0x438000:0x5e7e64-0x438000], "little") != 0x20003ea4 or \
            int.from_bytes(blob[0x5e7e68-0x438000:0x5e7e6c-0x438000], "little") != 0x20003edc:
        raise RuntimeError("Terminal FSM name pointers changed")
    OUT.mkdir(parents=True, exist_ok=True)
    elf = OUT / "names-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_state_name_5e7b10",
                    str(SOURCE), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, lookup, value, pattern):
        address, name, array, stock_ram, count, unknown = lookup
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for segment_address, data in segments:
            u.mem_write(segment_address, data)
        u.mem_map(0x20000000, 0x100000)
        ram = symbols[array] if compiled else stock_ram
        values = [0x20040000 + ((i+pattern*count)*16) for i in range(count)]
        u.mem_write(ram, b"".join(struct.pack("<I", v) for v in values))
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, value)
        entry = symbols[name] if compiled else address
        u.emu_start(entry|1, 0x600000, count=1000)
        pointer = u.reg_read(A.UC_ARM_REG_R0)
        if (value & 0xff) < count:
            return pointer, bytes(u.mem_read(ram, count*4)).hex()
        result = bytearray()
        for i in range(40):
            c = u.mem_read(pointer+i, 1)[0]
            if c == 0:
                break
            result.append(c)
        return result.decode(), bytes(u.mem_read(ram, count*4)).hex()

    cases = 0
    for lookup in LOOKUPS:
        for pattern in (0, 1):
            for value in range(256):
                for candidate in (value, value | 0x100):
                    stock = run(False, lookup, candidate, pattern)
                    selected = run(True, lookup, candidate, pattern)
                    if stock != selected:
                        raise RuntimeError(f"FSM name mismatch {lookup[1]} {candidate=} "
                                           f"{pattern=}: {stock} vs {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_FSM_NAMES_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "both byte domains, high-bit truncation, pointer slots and fallback strings",
              "limits": ["State/event name RAM startup and actual string population remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

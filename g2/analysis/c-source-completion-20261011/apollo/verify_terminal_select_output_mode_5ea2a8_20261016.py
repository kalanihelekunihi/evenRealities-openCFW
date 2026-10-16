#!/usr/bin/env python3
"""Compare Terminal output phrase hash and selector with pinned stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_select_output_mode_5ea2a8.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-select-output-mode-5ea2a8"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
TABLE = 0x74f3fc
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void audio_lv_anim_start_49942e(uint32_t a,const void*b){(void)a;(void)b;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    for literal, value in ((0x5eadac, 0x7feb352d), (0x5eadb0, 0x846ca68b),
                           (0x5eadb4, 0x2006e0d0), (0x5eadb8, TABLE)):
        if int.from_bytes(blob[literal-0x438000:literal-0x438000+4], "little") != value:
            raise RuntimeError(f"Terminal output selector literal {literal:#x} changed")
    expected = ["Architecting...", "Cogitating...", "Computing...", "Exploring...",
                "Planning...", "Generating...", "Inferring...", "Pondering...",
                "Processing...", "Thinking..."]
    for i, phrase in enumerate(expected):
        pointer = int.from_bytes(blob[TABLE-0x438000+i*4:TABLE-0x438000+i*4+4], "little")
        actual = blob[pointer-0x438000:pointer-0x438000+64].split(b"\0")[0].decode()
        if actual != phrase:
            raise RuntimeError(f"Terminal output phrase {i} changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "output-mode-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "output-mode-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_select_output_mode_5ea2a8",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, entry, payload, object_value):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state+0x1d4, struct.pack("<I", object_value))
        anim = (symbols["audio_lv_anim_start_49942e"] if compiled else 0x49942e)&~1
        trace = []

        def cstring(addr):
            out = bytearray()
            for i in range(64):
                ch = u.mem_read(addr+i, 1)[0]
                if ch == 0:
                    return out.decode("ascii")
                out.append(ch)
            raise RuntimeError("unterminated output phrase")

        def hook(cpu, pc, size, _):
            if pc != anim:
                return
            trace.append((cpu.reg_read(A.UC_ARM_REG_R0),
                          cstring(cpu.reg_read(A.UC_ARM_REG_R1))))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, payload)
        name, address = entry
        u.emu_start((symbols[name] if compiled else address)|1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace

    values = [0, 1, 2, 9, 10, 0x12345678, 0x7fffffff, 0xffffffff]
    values += [((i * 0x9e3779b1) & 0xffffffff) for i in range(40)]
    cases = 0
    for payload in values:
        stock = run(False, ("audio_terminal_output_hash_5ea256", 0x5ea256), payload, 0)
        selected = run(True, ("audio_terminal_output_hash_5ea256", 0x5ea256), payload, 0)
        if stock != selected:
            raise RuntimeError(f"output hash mismatch {payload=:#x}: {stock} vs {selected}")
        cases += 1
    for entry in (("audio_terminal_select_output_mode_core_5ea270", 0x5ea270),
                  ("audio_terminal_select_output_mode_5ea2a8", 0x5ea2a8)):
        for payload in values:
            for object_value in (0, 0x20002000):
                stock = run(False, entry, payload, object_value)
                selected = run(True, entry, payload, object_value)
                if stock != selected:
                    raise RuntimeError(f"output selector mismatch {entry[0]} "
                                       f"{payload=:#x} {object_value=:#x}: {stock} vs {selected}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_SELECT_OUTPUT_MODE_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "stock_phrase_table": "0x74f3fc", "phrases": expected,
              "scope": "hash, selector core and wrapper across 48 payloads, null/non-null object, exact phrase and return",
              "limits": ["LVGL text effect and final shared Terminal RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()

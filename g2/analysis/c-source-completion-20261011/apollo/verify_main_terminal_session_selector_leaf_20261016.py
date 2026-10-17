#!/usr/bin/env python3
"""Bounded stock/C comparison for Apollo selector spacing and row text."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_selector_leaf_20261016.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-selector-leaf"
MARGINS = (0x44122a, 0x441238, 0x44120e, 0x44121c)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "selector-leaf-oracle.o"
    elf = OUT / "selector-leaf-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defs = {f"audio_uart_page_{a:x}": a | 1 for a in MARGINS}
    defs["g2_audio_dump_snprintf"] = 0x44b729
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    *(f"--defsym={k}=0x{v:x}" for k, v in defs.items()),
                    str(obj), "-o", str(elf)], check=True)
    with elf.open("rb") as f:
        e = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   e.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, kind, source, capacity, object_, value, selector):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        trace = []
        if kind == "margin":
            u.reg_write(A.UC_ARM_REG_R0, object_)
            u.reg_write(A.UC_ARM_REG_R1, value)
            u.reg_write(A.UC_ARM_REG_R2, selector)
            native = 0x5eca00
            symbol = "audio_terminal_session_four_margins_5eca00"
        else:
            u.mem_write(0x20082000, b"?" * 70)
            if source is not None:
                u.mem_write(0x20081000, source)
            u.reg_write(A.UC_ARM_REG_R0, 0 if object_ == 0 else 0x20082000)
            u.reg_write(A.UC_ARM_REG_R1, capacity)
            u.reg_write(A.UC_ARM_REG_R2, 0 if source is None else 0x20081000)
            native = 0x5ecc74
            symbol = "audio_terminal_session_row_text_5ecc74"

        def hook(cpu, pc, size, _):
            if pc in MARGINS:
                trace.append((pc, *(cpu.reg_read(r) for r in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))))
            elif pc == 0x439be4:
                dest, src, length = (cpu.reg_read(r) for r in
                                     (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                cpu.mem_write(dest, bytes(cpu.mem_read(src, length)))
            elif pc == 0x44b728:
                dest = cpu.reg_read(A.UC_ARM_REG_R0)
                cap = cpu.reg_read(A.UC_ARM_REG_R1)
                fmt = cpu.reg_read(A.UC_ARM_REG_R2)
                raw = bytes(cpu.mem_read(fmt, 24)).split(b"\0", 1)[0]
                ident = cpu.reg_read(A.UC_ARM_REG_R3)
                trace.append((pc, cap, raw, ident))
                result = ("Session %lu" % ident).encode()[:max(0, cap - 1)]
                cpu.mem_write(dest, result + b"\0")
            else:
                return
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start((symbols[symbol] if compiled else native) | 1,
                    0x600000, count=300)
        data = bytes(u.mem_read(0x20082000, 70)) if kind == "row" else b""
        return trace, data

    cases = 0
    for object_, value, selector in itertools.product(
            (0, 0x20090000), (0, 1, 0x102), (0, 3)):
        args = ("margin", None, 0, object_, value, selector)
        if run(False, *args) != run(True, *args):
            raise RuntimeError(f"selector margin mismatch {args}")
        cases += 1
    for source, capacity, dest in itertools.product(
            (None, b"\x39\x30\x00\x00\x00\x00" + b"x" * 70,
             b"\x2a\x00\x00\x00\x05\x00hello" + b"z" * 70,
             b"\x2a\x00\x00\x00\x42\x00" + b"a" * 70),
            (0, 1, 4, 64), (0, 1)):
        args = ("row", source, capacity, dest, 0, 0)
        stock = run(False, *args)
        candidate = run(True, *args)
        if stock != candidate:
            raise RuntimeError(f"selector row mismatch {args}: {stock!r} {candidate!r}")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_SELECTOR_LEAF_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf),
               "cases": cases, "scope": "Margin forwarding and bounded row text, including empty-name formatting",
               "limits": ["Formatter lower effects are mocked; selector rebuild and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

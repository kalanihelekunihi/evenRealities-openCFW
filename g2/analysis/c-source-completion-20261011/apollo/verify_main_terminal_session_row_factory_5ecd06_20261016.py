#!/usr/bin/env python3
"""Compare Apollo selector row factory C with stock call order and return."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_row_factory_5ecd06.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-row-factory-5ecd06"
CALLS = {
    "audio_uart_page_43de82": (0x43de82, 1),
    "audio_uart_page_43f4c0": (0x43f4c0, 3),
    "audio_uart_page_48ba78": (0x48ba78, 2),
    "audio_uart_page_48ba92": (0x48ba92, 4),
    "audio_uart_page_43dfa4": (0x43dfa4, 2),
    "audio_uart_page_44129e": (0x44129e, 3),
    "audio_uart_page_44131c": (0x44131c, 3),
    "audio_uart_page_44132a": (0x44132a, 3),
    "audio_uart_page_44104c": (0x44104c, 1),
    "audio_uart_page_4412ec": (0x4412ec, 3),
    "audio_uart_page_44130c": (0x44130c, 3),
    "audio_uart_page_44146a": (0x44146a, 3),
    "audio_uart_page_44120e": (0x44120e, 3),
    "audio_uart_page_44121c": (0x44121c, 3),
    "audio_uart_page_44122a": (0x44122a, 3),
    "audio_uart_page_441238": (0x441238, 3),
    "audio_uart_page_441254": (0x441254, 3),
    "audio_terminal_voice_anim_create_597e90": (0x597e90, 1),
    "audio_terminal_session_row_icon_5eccc2": (0x5eccc2, 3),
    "audio_uart_page_44127e": (0x44127e, 3),
    "audio_uart_page_4413ce": (0x4413ce, 3),
    "audio_uart_page_499416": (0x499416, 1),
    "audio_uart_page_49942e": (0x49942e, 2),
    "audio_uart_page_441180": (0x441180, 3),
    "audio_uart_page_4411aa": (0x4411aa, 3),
    "audio_uart_page_layout_499678": (0x499678, 2),
    "audio_uart_page_44140e": (0x44140e, 3),
    "audio_uart_page_44143e": (0x44143e, 3),
    "audio_uart_page_44145a": (0x44145a, 3),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "row-factory-oracle.o"
    elf = OUT / "row-factory-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defs = {name: address | 1 for name, (address, _) in CALLS.items()}
    defs["audio_uart_ring_secondary_head_cell"] = 0x200746dc
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    *(f"--defsym={name}=0x{address:x}" for name, address in defs.items()),
                    str(obj), "-o", str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open("rb") as f:
        e = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbol = next(s["st_value"] for s in
                      e.get_section_by_name(".symtab").iter_symbols()
                      if s.name == "audio_terminal_session_row_factory_5ecd06")
    by_address = {address: (name, argc) for name, (address, argc) in CALLS.items()}

    def run(compiled, kind, mode, name):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(0x200746dc, (0x123abc).to_bytes(4, "little"))
        u.mem_write(0x20081000, name + b"\0")
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        for register, value in ((A.UC_ARM_REG_R0, 0x20090000),
                                (A.UC_ARM_REG_R1, 0x20081000),
                                (A.UC_ARM_REG_R2, kind),
                                (A.UC_ARM_REG_R3, mode)):
            u.reg_write(register, value)
        trace = []

        def hook(cpu, pc, size, _):
            if pc not in by_address:
                return
            call, argc = by_address[pc]
            args = tuple(cpu.reg_read(r) for r in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                          A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)[:argc])
            trace.append((call, args))
            result = 0
            if call == "audio_uart_page_43de82":
                result = 0x20092000
            elif call == "audio_terminal_voice_anim_create_597e90":
                result = 0x20093000
            elif call == "audio_uart_page_499416":
                result = 0x20094000
            elif call == "audio_uart_page_44104c":
                result = 0x12345678
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start((symbol if compiled else 0x5ecd06) | 1,
                    0x600000, count=900)
        return trace, u.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for kind, mode, name in itertools.product((0, 1, 0x101),
                                              (0, 1, 2, 3, 0x101),
                                              (b"", b"New Session", b"Row 1")):
        args = (kind, mode, name)
        stock, candidate = run(False, *args), run(True, *args)
        if stock != candidate:
            for n, (a, b) in enumerate(itertools.zip_longest(stock[0], candidate[0])):
                if a != b:
                    print("first call mismatch", args, n, a, b)
                    break
            print("return", stock[1], candidate[1])
            raise RuntimeError("selector row factory mismatch")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_ROW_FACTORY_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf),
               "cases": cases,
               "scope": "Selector row construction call order, icon choice forwarding, and row return",
               "limits": ["Lower LVGL and row icon effects are mocked; full image and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

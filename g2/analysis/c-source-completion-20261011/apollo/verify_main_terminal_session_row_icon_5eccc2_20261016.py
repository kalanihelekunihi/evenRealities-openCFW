#!/usr/bin/env python3
"""Bounded stock/C oracle for selector row icon choice and source-owned icon."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_row_icon_5eccc2.c"
ASSET = G2 / "components/audio/uart_thread_source_candidate/terminal_session_icon_773060.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-row-icon-5eccc2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    pixels = blob[0x6ce9b8-0x438000:0x6ce9b8-0x438000+256]
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    for source in (SOURCE, ASSET):
        obj = OUT / (source.stem + "-oracle.o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    elf = OUT / "row-icon-oracle.elf"
    defs = {"audio_terminal_query_image_770890": 0x770890,
            "audio_terminal_asset_7733a8": 0x7733a8,
            "audio_terminal_output_style_20003f80": 0x20003f80,
            "audio_terminal_image_set_5e47fe": 0x5e47ff,
            "audio_terminal_set_label_style_5e482a": 0x5e482b}
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    *(f"--defsym={k}=0x{v:x}" for k, v in defs.items()),
                    *(str(o) for o in objects), "-o", str(elf)],
                   check=True, stderr=subprocess.DEVNULL)
    with elf.open("rb") as f:
        e = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   e.get_section_by_name(".symtab").iter_symbols()}
    icon = symbols["audio_terminal_session_icon_773060"]

    def run(compiled, image, kind, mode):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        for register, value in ((A.UC_ARM_REG_R0, image),
                                (A.UC_ARM_REG_R1, kind),
                                (A.UC_ARM_REG_R2, mode)):
            u.reg_write(register, value)
        trace = []

        def hook(cpu, pc, size, _):
            if pc not in (0x5e47fe, 0x5e482a):
                return
            args = tuple(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,
                          A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if pc == 0x5e47fe:
                descriptor = args[1]
                if descriptor in (0x773060, icon):
                    header = bytes(cpu.mem_read(descriptor, 16))
                    data_ptr = int.from_bytes(cpu.mem_read(descriptor + 16, 4), "little")
                    data = bytes(cpu.mem_read(data_ptr, 256))
                    assert header == bytes.fromhex("19060000100010001000000000010000")
                    assert data == pixels
                    args = (args[0], "session icon")
                else:
                    args = (args[0], descriptor)
            trace.append((pc, args if pc == 0x5e47fe else args))
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start((symbols["audio_terminal_session_row_icon_5eccc2"]
                     if compiled else 0x5eccc2) | 1, 0x600000, count=100)
        return trace

    cases = 0
    for image, kind, mode in itertools.product((0, 0x20090000),
                                               (0, 1, 0x100, 0x101),
                                               (0, 1, 2, 3, 0x101)):
        args = (image, kind, mode)
        stock, candidate = run(False, *args), run(True, *args)
        if stock != candidate:
            raise RuntimeError(f"row icon mismatch {args}: {stock!r} {candidate!r}")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_ROW_ICON_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "asset": str(ASSET.relative_to(ROOT)), "asset_sha256": sha(ASSET),
               "asset_pixels_sha256": hashlib.sha256(pixels).hexdigest(),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf),
               "cases": cases,
               "scope": "Four image/style selection branches and exact 16x16 session icon",
               "limits": ["Lower image/style effects, final asset placement and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()

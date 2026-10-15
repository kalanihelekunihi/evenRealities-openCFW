#!/usr/bin/env python3
"""Bind native-observed two-byte minimum UART product mode state."""
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/uart_product_mode_state.c"
USER = G2 / "components/audio/uart_thread_source_candidate/command_mode.c"
BASE = G2 / "build/c-firmware/20261014/main-radio-gpio-callback/apollo-main-radio-gpio-callback.o"
OUT = G2 / "build/c-firmware/20261014/main-uart-product-mode-state"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_audio_uart_command_mode.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    with NATIVE.open("rb") as stream:
        elf = ELFFile(stream)
        segment = next(item for item in elf.iter_segments() if item["p_type"] == "PT_LOAD")
        image = segment.data()
        base = segment["p_vaddr"]
        if struct.unpack_from("<I", image, 0x4abea0-base)[0] != 0x200038f0:
            raise RuntimeError("native UART product mode pointer changed")
        if image[0x4abe60-base:0x4abe66-base] != bytes.fromhex("0f48 4078 7047"):
            raise RuntimeError("native UART product getter byte load changed")
    if "g2_uart_product_mode_state[1]" not in USER.read_text():
        raise RuntimeError("UART product mode consumer changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "uart_product_mode_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbol = next(item for item in elf.get_section_by_name(".symtab").iter_symbols()
                      if item.name == "g2_uart_product_mode_state")
        section = elf.get_section(symbol["st_shndx"])
        if symbol["st_size"] != 2 or section.name != ".g2_ram_200038f0" or section["sh_size"] != 2:
            raise RuntimeError("compiled product mode minimum span changed")
    if names(obj, "-g", "--defined-only") != {"g2_uart_product_mode_state"} or names(obj, "-u"):
        raise RuntimeError("compiled UART product mode symbol set changed")
    before = names(BASE, "-u")
    if "g2_uart_product_mode_state" not in before:
        raise RuntimeError("Main UART product mode import changed")
    linked = OUT / "apollo-main-uart-product-mode-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before-after != {"g2_uart_product_mode_state"} or after-before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    result = subprocess.run([sys.executable, str(ORACLE)], check=True,
                            capture_output=True, text=True)
    if result.stdout.strip() != "PASS_AUDIO_UART_COMMAND_MODE 256":
        raise RuntimeError("UART command mode native oracle changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_UART_PRODUCT_MODE_STATE_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_pointer_literal": "0x4abea0", "native_ram": "0x200038f0",
        "observed_minimum_bytes": 2,
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
        "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
        "oracle_output": result.stdout.strip(),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Only two observed bytes are allocated; full generated object extent and startup values remain open.",
                   "Final RAM placement, full image and hardware behavior remain unproved."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

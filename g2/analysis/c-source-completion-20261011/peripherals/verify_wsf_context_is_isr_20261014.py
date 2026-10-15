#!/usr/bin/env python3
"""Compare the full stock IPSR predicate with compiled C in M-class emulation."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_IPSR, UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/foundation/wsf_radio/context_is_isr.c"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
OBJECT = OUT / "wsf-context-is-isr-verifier.o"
ELF = OUT / "wsf-context-is-isr-verifier.elf"
RECEIPT = OUT / "wsf-context-is-isr-native-comparison.json"
ENTRY = 0x442228
STOP = 0x20001000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(entry, native, segments, ipsr):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x442000, 0x1000)
    cpu.mem_write(ENTRY, native)
    cpu.mem_map(0x100000, 0x1000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x10000)
    cpu.reg_write(UC_ARM_REG_SP, 0x2000f000)
    cpu.reg_write(UC_ARM_REG_LR, STOP | 1)
    cpu.reg_write(UC_ARM_REG_IPSR, ipsr)
    cpu.emu_start(entry | 1, STOP, count=1000)
    assert cpu.reg_read(UC_ARM_REG_PC) == STOP
    assert cpu.reg_read(UC_ARM_REG_IPSR) == ipsr
    return cpu.reg_read(UC_ARM_REG_R0)


def main():
    blob = STOCK.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
    offset = 32 + ENTRY - 0x438000
    native = blob[offset:offset + 16]
    assert native.hex() == "eff30580002801d1002000e001207047"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-Wall", "-Wextra", "-Werror", "-O2",
                    "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", str(OBJECT), "-o", str(ELF)], check=True)
    with ELF.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        symbol = next(s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()
                      if s.name == "opencfw_wsf_context_is_isr")
    cases = [0, 1, 2, 3, 15, 16, 31, 32, 63, 127, 255]
    for ipsr in cases:
        expected = 0 if ipsr == 0 else 1
        assert run(ENTRY, native, segments, ipsr) == expected
        assert run(symbol, native, segments, ipsr) == expected
    receipt = {
        "status": "PASS_BOUNDED_NATIVE_WSF_CONTEXT_IS_ISR_C",
        "stock_blob_sha256": sha(STOCK), "stock_entry": hex(ENTRY),
        "stock_entry_bytes": native.hex(), "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha(SOURCE), "cases": cases,
        "source_elf_sha256": sha(ELF), "whole_image_complete": False,
        "hardware_proof": False,
        "limits": ["IPSR values 0..255 are sampled; all M-class exception IDs and hardware transition timing are not exercised.",
                   "Final linkage and exception-context integration remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(RECEIPT))


if __name__ == "__main__":
    main()

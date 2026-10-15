#!/usr/bin/env python3
"""Oracle-test native page style forwarding and compose its C provider."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/page_font_style_44143e.c"
USER = G2 / "components/audio/uart_thread_source_candidate/system_alert_page_update_4d30ba.c"
BASE = G2 / "build/c-firmware/20261014/main-thread-runtime-cells/apollo-main-thread-runtime-cells.o"
OUT = G2 / "build/c-firmware/20261014/main-page-font-style"
NAME = "audio_uart_page_44143e"
CALLEE = "audio_uart_page_style_apply_44be4c"
NATIVE_ENTRY = 0x44143e
NATIVE_CALLEE = 0x44be4c
NATIVE_BYTES = bytes.fromhex("80b513000a005a210af001fd01bd")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def get_segments(path):
    with path.open("rb") as stream:
        elf = ELFFile(stream)
        return [(seg["p_vaddr"], seg.data()) for seg in elf.iter_segments()
                if seg["p_type"] == "PT_LOAD"]


def call_args(segments, entry, callee, args):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    for address, data in segments:
        start = address & ~0xfff
        end = (address + len(data) + 0xfff) & ~0xfff
        cpu.mem_map(start, end - start)
        cpu.mem_write(address, data)
    cpu.mem_map(0x101000, 0x1000)
    cpu.mem_write(0x101000, b"\x70\x47")
    cpu.mem_map(0x20000000, 0x10000)
    cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
    cpu.reg_write(A.UC_ARM_REG_LR, 0x101ff1)
    for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2), args):
        cpu.reg_write(reg, value)
    seen = []

    def hook(uc, pc, _size, _user):
        if pc == callee:
            seen.append(tuple(uc.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)))
            uc.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start(entry | 1, 0, count=40)
    if len(seen) != 1:
        raise RuntimeError(f"callee not reached: {entry:#x}, {args}")
    return seen[0]


def main():
    raw = NATIVE.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("native ELF format changed")
    phoff = struct.unpack_from("<I", raw, 28)[0]
    kind, offset, vaddr, _, filesz, _, _, _ = struct.unpack_from("<IIIIIIII", raw, phoff)
    if kind != 1 or not vaddr <= NATIVE_ENTRY < vaddr + filesz - len(NATIVE_BYTES):
        raise RuntimeError("native page wrapper unmapped")
    if raw[offset + NATIVE_ENTRY - vaddr:offset + NATIVE_ENTRY - vaddr + len(NATIVE_BYTES)] != NATIVE_BYTES:
        raise RuntimeError("native page wrapper bytes changed")
    if NAME not in USER.read_text():
        raise RuntimeError("page style user changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "page_font_style_44143e.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {NAME} or names(obj, "-u") != {CALLEE}:
        raise RuntimeError("C page wrapper symbol contract changed")
    oracle_elf = OUT / "page_font_style_oracle.elf"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000",
                    f"--defsym={CALLEE}=0x101001", str(obj), "-o", str(oracle_elf)], check=True)
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", str(oracle_elf)], text=True)
    entry = next(int(line.split()[0], 16) for line in output.splitlines()
                 if line.split()[-1] == NAME)
    cases = [(0x20010000 + i * 0x20, value, selector) for i, (value, selector) in
             enumerate(((0, 0), (1, 0), (0xffffffff, 0), (0x200746e0, 0),
                         (0x12345678, 1), (0x3fffffff, 0xffffffff),
                         (0xaaaaaaaa, 0x55555555), (0xdeadbeef, 0x7f),
                         (0x80000000, 0x10000), (0x18, 3),
                         (0x5a, 0x80000000), (0x00010000, 0x1234)))]
    native_segments = get_segments(NATIVE)
    c_segments = get_segments(oracle_elf)
    for args in cases:
        old = call_args(native_segments, NATIVE_ENTRY, NATIVE_CALLEE, args)
        new = call_args(c_segments, entry, 0x101000, args)
        if old != new or old != (args[0], 0x5a, args[1], args[2]):
            raise RuntimeError(f"page style argument mismatch: {args}, {old}, {new}")
    before = names(BASE, "-u")
    if NAME not in before or CALLEE in before:
        raise RuntimeError("Apollo Main page style imports changed")
    linked = OUT / "apollo-main-page-font-style.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {NAME} or after - before:
        raise RuntimeError(f"unexpected page style import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_PAGE_FONT_STYLE_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entry": hex(NATIVE_ENTRY), "native_callee": hex(NATIVE_CALLEE),
        "native_wrapper_bytes_hex": NATIVE_BYTES.hex(), "oracle_cases": len(cases),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "oracle_elf": str(oracle_elf.relative_to(ROOT)), "oracle_elf_sha256": sha(oracle_elf),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Oracle compares wrapper call arguments, not downstream style effects.",
                   "Full-image placement and hardware behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

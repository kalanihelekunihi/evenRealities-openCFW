#!/usr/bin/env python3
"""Compile bounded native-backed Apollo case status function and byte cells."""
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/case_status_source.c"
USERS = [G2 / "components/audio/uart_thread_source_candidate/display_status.c"]
BASE = G2 / "build/c-firmware/20261014/main-hub-send-queue/apollo-main-hub-send-queue.o"
OUT = G2 / "build/c-firmware/20261014/main-case-status"
ORACLE_SCRIPT = Path(__file__).with_name("verify_main_case_status_oracle_20261014.py")
RAM = {
    "audio_uart_case_status_disabled": (0x20075012, 0x4acb00, 1),
    "audio_uart_case_sensor_a": (0x2007418f, 0x4acdd0, 1),
    "audio_uart_case_sensor_b": (0x2007418e, 0x4acdd0, 1),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    rows = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in rows.splitlines() if row.strip()}


def section_sizes(path):
    raw = path.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("compiled object ELF format changed")
    shoff = struct.unpack_from("<I", raw, 32)[0]
    shentsize, shnum = struct.unpack_from("<HH", raw, 46)
    sections = [struct.unpack_from("<IIIIIIIIII", raw, shoff + i * shentsize)
                for i in range(shnum)]
    strings = sections[struct.unpack_from("<H", raw, 50)[0]]
    result = {}
    for section in sections:
        start = strings[4] + section[0]
        name = raw[start:raw.index(b"\0", start)].decode()
        if name.startswith(".g2_ram_"):
            result[name] = section[5]
    return result


def main():
    raw = NATIVE.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("native ELF format changed")
    phoff = struct.unpack_from("<I", raw, 28)[0]
    kind, offset, vaddr, _, filesz, _, _, _ = struct.unpack_from("<IIIIIIII", raw, phoff)
    if kind != 1:
        raise RuntimeError("native load segment changed")
    source = SOURCE.read_text()
    users = "\n".join(path.read_text() for path in USERS)
    for name, (address, literal, _) in RAM.items():
        if not vaddr <= literal <= vaddr + filesz - 4:
            raise RuntimeError(f"unmapped native literal: {literal:#x}")
        found = struct.unpack_from("<I", raw, offset + literal - vaddr)[0]
        expected = address if literal == 0x4acb00 else 0x20074188
        if found != expected or f".g2_ram_{address:08x}" not in source:
            raise RuntimeError(f"case status RAM contract changed: {name} {found:#x}")
    if "audio_uart_case_status" not in USERS[0].read_text():
        raise RuntimeError("case status user changed")
    native_bytes = raw[offset + 0x4acad0 - vaddr:offset + 0x4acaf8 - vaddr]
    if len(native_bytes) != 40 or native_bytes[:2] != bytes.fromhex("80b5"):
        raise RuntimeError("native case status function span changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "case_status_source.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    resolved = set(RAM) | {"audio_uart_case_status"}
    if names(obj, "-g", "--defined-only") != resolved or names(obj, "-u"):
        raise RuntimeError("C case status symbol set changed")
    expected = {f".g2_ram_{address:08x}": size for address, _, size in RAM.values()}
    if section_sizes(obj) != expected:
        raise RuntimeError("C case status section sizes changed")
    before = names(BASE, "-u")
    if "audio_uart_case_status" not in before:
        raise RuntimeError("Apollo Main case status import changed")
    linked = OUT / "apollo-main-case-status.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"audio_uart_case_status"} or after - before:
        raise RuntimeError(f"unexpected case status import delta: {before-after}, {after-before}")
    subprocess.run([sys.executable, str(ORACLE_SCRIPT)], check=True,
                   capture_output=True, text=True)
    oracle_path = OUT / "oracle.json"
    oracle = json.loads(oracle_path.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_CASE_STATUS_NATIVE_ORACLE" or oracle["case_count"] != 27:
        raise RuntimeError("case status native oracle changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_CASE_STATUS_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_ram": {name: {"ram": hex(address), "literal": hex(literal), "bytes": size}
                       for name, (address, literal, size) in RAM.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(path.relative_to(ROOT)): sha(path) for path in USERS},
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "oracle_script": str(ORACLE_SCRIPT.relative_to(ROOT)), "oracle_script_sha256": sha(ORACLE_SCRIPT),
        "oracle": str(oracle_path.relative_to(ROOT)), "oracle_sha256": sha(oracle_path),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Case status byte startup values and final RAM placement remain open.",
                   "Whole-image and hardware behavior remain unproved."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

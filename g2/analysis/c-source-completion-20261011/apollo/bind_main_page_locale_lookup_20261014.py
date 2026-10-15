#!/usr/bin/env python3
"""Compare native/C locale search with controlled RAM table and comparator."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/page_locale_lookup_460050.c"
USER = G2 / "components/audio/uart_thread_source_candidate/system_alert_page_update_4d30ba.c"
BASE = G2 / "build/c-firmware/20261014/main-page-font-style/apollo-main-page-font-style.o"
OUT = G2 / "build/c-firmware/20261014/main-page-locale-lookup"
COMPARATOR = "audio_uart_font_path_compare"
NATIVE_BYTES = {
    0x460050: bytes.fromhex("f8b504000d001600002700e07f1c380080b2b0420bda2100380080b255f820000cf02cfd0028f1d1bfb2380001e04ff6ff70f2bd"),
    0x460084: bytes.fromhex("80b59d222649fff7e1ff02bd"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def segments(path):
    with path.open("rb") as stream:
        elf = ELFFile(stream)
        return [(seg["p_vaddr"], seg.data()) for seg in elf.iter_segments()
                if seg["p_type"] == "PT_LOAD"]


def run(image, entry, comparator, count, match, wrapper):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    for address, data in image:
        start = address & ~0xfff
        end = (address + len(data) + 0xfff) & ~0xfff
        cpu.mem_map(start, end - start)
        cpu.mem_write(address, data)
    cpu.mem_map(0x101000, 0x2000)
    cpu.mem_write(0x101000, b"\x70\x47")
    cpu.mem_write(0x101ff0, b"\x70\x47")
    cpu.mem_map(0x20000000, 0x10000)
    table = 0x20002928
    key = 0x20008000
    for i in range(157):
        cpu.mem_write(table + i * 4, struct.pack("<I", 0x20009000 + i * 4))
    cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
    cpu.reg_write(A.UC_ARM_REG_LR, 0x101ff1)
    cpu.reg_write(A.UC_ARM_REG_R0, key)
    if not wrapper:
        cpu.reg_write(A.UC_ARM_REG_R1, table)
        cpu.reg_write(A.UC_ARM_REG_R2, count)
    seen = []
    returned = []

    def hook(uc, pc, _size, _user):
        if pc == comparator:
            candidate = uc.reg_read(A.UC_ARM_REG_R0)
            query = uc.reg_read(A.UC_ARM_REG_R1)
            seen.append((candidate, query))
            target = 0x20009000 + match * 4 if match >= 0 else -1
            uc.reg_write(A.UC_ARM_REG_R0, 0 if candidate == target else 1)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
        elif pc == 0x101ff0:
            returned.append(uc.reg_read(A.UC_ARM_REG_R0))
            uc.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start(entry | 1, 0, count=4000)
    if len(returned) != 1:
        raise RuntimeError(f"locale search did not return: {entry:#x}, {count}, {match}")
    return returned[0], seen


def main():
    raw = NATIVE.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("native ELF format changed")
    phoff = struct.unpack_from("<I", raw, 28)[0]
    kind, offset, vaddr, _, filesz, _, _, _ = struct.unpack_from("<IIIIIIII", raw, phoff)
    if kind != 1:
        raise RuntimeError("native load segment changed")
    for entry, expected in NATIVE_BYTES.items():
        if not vaddr <= entry < vaddr + filesz - len(expected):
            raise RuntimeError("native locale function unmapped")
        actual = raw[offset + entry - vaddr:offset + entry - vaddr + len(expected)]
        if actual != expected:
            raise RuntimeError(f"native locale bytes changed: {entry:#x}")
    if struct.unpack_from("<I", raw, offset + 0x460124 - vaddr)[0] != 0x20002928:
        raise RuntimeError("native locale table literal changed")
    if "audio_uart_page_460084" not in USER.read_text():
        raise RuntimeError("locale lookup user changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "page_locale_lookup_460050.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    symbols = {"audio_uart_page_460050", "audio_uart_page_460084"}
    if names(obj, "-g", "--defined-only") != symbols or names(obj, "-u") != {COMPARATOR}:
        raise RuntimeError("C locale object symbol contract changed")
    oracle_elf = OUT / "page_locale_oracle.elf"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", "audio_uart_page_460084",
                    f"--defsym={COMPARATOR}=0x101001", str(obj), "-o", str(oracle_elf)], check=True)
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", str(oracle_elf)], text=True)
    entries = {p[-1]: int(p[0], 16) for line in output.splitlines()
               if len(p := line.split()) == 3 and p[-1] in symbols}
    if set(entries) != symbols:
        raise RuntimeError("C locale oracle entries changed")
    old_image = segments(NATIVE)
    new_image = segments(oracle_elf)
    cases = [(0, -1, False), (1, -1, False), (1, 0, False),
             (7, 0, False), (7, 3, False), (7, 6, False), (7, -1, False),
             (157, 0, True), (157, 1, True), (157, 19, True),
             (157, 156, True), (157, -1, True)]
    for count, match, wrapper in cases:
        native_entry = 0x460084 if wrapper else 0x460050
        c_entry = entries["audio_uart_page_460084" if wrapper else "audio_uart_page_460050"]
        old = run(old_image, native_entry, 0x46cacc, count, match, wrapper)
        new = run(new_image, c_entry, 0x101000, count, match, wrapper)
        expected = match if 0 <= match < count else 0xffff
        if old != new or old[0] != expected:
            raise RuntimeError(f"locale search mismatch: {count}, {match}, {wrapper}, {old}, {new}")
    before = names(BASE, "-u")
    if "audio_uart_page_460084" not in before or COMPARATOR in before:
        raise RuntimeError("Apollo Main locale imports changed")
    linked = OUT / "apollo-main-page-locale-lookup.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"audio_uart_page_460084"} or after - before:
        raise RuntimeError(f"unexpected locale import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_PAGE_LOCALE_LOOKUP_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_functions": {hex(a): b.hex() for a, b in NATIVE_BYTES.items()},
        "native_table_address": "0x20002928", "native_compare": "0x46cacc",
        "oracle_cases": len(cases),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "oracle_elf": str(oracle_elf.relative_to(ROOT)), "oracle_elf_sha256": sha(oracle_elf),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Oracle controls comparator outcomes and table entries; native RAM table contents are unverified.",
                   "Full-image placement and hardware behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

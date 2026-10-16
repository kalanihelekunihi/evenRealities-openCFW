#!/usr/bin/env python3
"""Bind redirect initializer with its stock-addressed companion mutex cell."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "file_redirect_init_474d9c.c"
RAM_SOURCE = COMP / "file_redirect_mutex_ram.c"
LINKER = COMP / "file_redirect_mutex_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-file-tlsf-backing-ram/apollo-main-file-tlsf-backing-ram-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-file-redirect-init"
ORACLE = OUT / "oracle-receipt.json"
PROVIDER = "audio_file_redirect_init_474d9c"
RAM = "g2_codec_redirect_mutex"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_FILE_REDIRECT_INIT_C_ORACLE" or \
            oracle["cases"] != 32 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("redirect initializer oracle changed")
    OUT.mkdir(parents=True, exist_ok=True)
    body = OUT / "file_redirect_init_474d9c.o"
    ram = OUT / "file_redirect_mutex_ram.o"
    base_cmd = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                "-Wextra", "-Werror", "-c"]
    subprocess.run(base_cmd + [str(SOURCE), "-o", str(body)], check=True)
    subprocess.run(base_cmd + [str(RAM_SOURCE), "-o", str(ram)], check=True)
    if names(body, "--defined-only") != {PROVIDER} or \
            names(ram, "--defined-only") != {RAM}:
        raise RuntimeError("redirect source symbols changed")
    placement = OUT / "redirect-mutex-placement.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-nostdlib", "-Wl,-Ttext=0x100000", "-Wl,-T," + str(LINKER),
                    "-Wl,-e,0x100000", str(ram), "-o", str(placement)], check=True)
    with placement.open("rb") as f:
        elf = ELFFile(f)
        section = elf.get_section_by_name(".opencfw.fileheap.redirect_mutex")
        sy = {s.name: s for s in elf.get_section_by_name(".symtab").iter_symbols()}
        if section["sh_addr"] != 0x200748f4 or section["sh_size"] != 4 or \
                section["sh_type"] != "SHT_NOBITS" or \
                sy[RAM]["st_value"] != 0x200748f4 or sy[RAM]["st_size"] != 4:
            raise RuntimeError("redirect mutex placement changed")
    before = names(BASE, "-u")
    if len(before) != 176 or PROVIDER in names(BASE, "--defined-only") or \
            RAM in names(BASE, "--defined-only"):
        raise RuntimeError("Apollo redirect base changed")
    linked = OUT / "apollo-main-file-redirect-init-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(body), str(ram),
                    "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if after != before or not {PROVIDER, RAM} <= names(linked, "--defined-only"):
        raise RuntimeError("Apollo redirect frontier changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_FILE_REDIRECT_INIT_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "ram_source": str(RAM_SOURCE.relative_to(ROOT)), "ram_source_sha256": sha(RAM_SOURCE),
               "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
               "placement_elf": str(placement.relative_to(ROOT)), "placement_sha256": sha(placement),
               "object": str(body.relative_to(ROOT)), "object_sha256": sha(body),
               "ram_object": str(ram.relative_to(ROOT)), "ram_object_sha256": sha(ram),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 176, "unresolved_after": 176,
               "imports_resolved": [], "imports_added": [],
               "provider_linked": PROVIDER, "ram_address": "0x200748f4",
               "startup_wired": False, "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Redirect initializer is linked but boot ordering is not yet bound.",
                          "Final global RAM collision, whole-image link and hardware remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], 176, 176, sha(path))

if __name__ == "__main__":
    main()

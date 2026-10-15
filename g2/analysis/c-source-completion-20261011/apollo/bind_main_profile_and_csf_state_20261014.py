#!/usr/bin/env python3
"""Bind exact BLE profile ROM bytes, pointer cell, and shared CSF storage."""
import json
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/comm_profile_state.c"
CSF_SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_atts_csf_storage.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-atts-ccc-alloc/apollo-main-atts-ccc-alloc.o"
OUT = G2 / "build/c-firmware/20261014/main-profile-and-csf-state"
TABLE = "audio_ble_comm_profile_table"
SLOT = "audio_ble_comm_profile_slot"
CSF = "audio_ble_connection_state_table"
CSF_ALIAS = "audio_ble_csf_state_20073e04"
ROM = 0x78c9a4
EXPECTED = bytes((9, 0, 1, 0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 0, 0, 0))


def bytes_at(segments, address, length):
    for base, data in segments:
        if base <= address and address + length <= base + len(data):
            return data[address-base:address-base+length]
    raise RuntimeError(f"native ROM not mapped: {address:#x}")


def symbol_rows(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(path)], text=True)
    return {parts[-1]: parts for line in output.splitlines()
            if len(parts := line.split()) == 4}


def main():
    native_segments, _ = image(NATIVE)
    if bytes_at(native_segments, ROM, 16) != EXPECTED or \
       bytes_at(native_segments, ROM + 16, 4) != b"IDLE":
        raise RuntimeError("native profile ROM span or boundary changed")
    if "native 0x20073e04" not in CSF_SOURCE.read_text():
        raise RuntimeError("CSF source ownership annotation changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "comm_profile_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {TABLE, SLOT} or names(obj, "-u"):
        raise RuntimeError("profile source symbol contract changed")
    obj_rows = symbol_rows(obj)
    if int(obj_rows[TABLE][1], 16) != 16 or int(obj_rows[SLOT][1], 16) != 4:
        raise RuntimeError("profile table or pointer-cell dimensions changed")
    with __import__("tempfile").TemporaryDirectory() as directory:
        trial = Path(directory) / "profile.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", TABLE,
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        segments, symbols = image(trial)
        if bytes_at(segments, symbols[TABLE], 16) != EXPECTED:
            raise RuntimeError("compiled profile table differs from native ROM")
    before = names(BASE, "-u")
    base_defined = names(BASE, "-g", "--defined-only")
    if not {TABLE, SLOT, CSF_ALIAS} <= before or CSF not in base_defined:
        raise RuntimeError("Apollo Main profile or CSF contracts changed")
    base_rows = symbol_rows(BASE)
    if int(base_rows[CSF][1], 16) != 16:
        raise RuntimeError("source-owned CSF state dimension changed")
    linked = OUT / "apollo-main-profile-and-csf-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", f"--defsym={CSF_ALIAS}={CSF}",
                    str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    address_lines = subprocess.check_output(["arm-none-eabi-nm", "-g", str(linked)], text=True)
    addresses = {parts[-1]: parts[0] for line in address_lines.splitlines()
                 if len(parts := line.split()) == 3 and parts[-1] in {CSF, CSF_ALIAS}}
    if before - after != {TABLE, SLOT, CSF_ALIAS} or after - before or \
       addresses.get(CSF) != addresses.get(CSF_ALIAS):
        raise RuntimeError(f"profile or CSF binding failed: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PROFILE_AND_CSF_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_profile_origin": hex(ROM), "native_profile_bytes": EXPECTED.hex(),
               "native_profile_boundary": "0x78c9b4 IDLE", "native_profile_slot": "0x20074358",
               "native_csf_origin": "0x20073e04", "csf_bytes": 16,
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "csf_source": str(CSF_SOURCE.relative_to(ROOT)), "csf_source_sha256": sha(CSF_SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "linker_alias": f"{CSF_ALIAS}={CSF}",
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Profile ROM bytes and CSF object dimensions are exact, but final absolute placement remains open.",
                          "Profile pointer cell initialization depends on bleCommHandlerInit sequencing.",
                          "Whole-image and hardware behavior remain separate gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

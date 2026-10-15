#!/usr/bin/env python3
"""Compare native/C ATT CCC initialization and its trace selection."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
                               UC_ARM_REG_SP)

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/atts_ccc_init.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-atts-csf-open/apollo-main-atts-csf-open.o"
OUT = G2 / "build/c-firmware/20261014/main-atts-ccc-init"
ENTRY = "audio_ble_slave_apply_record_52c244"
PROVIDERS = {"audio_ble_atts_ccc_alloc_table_52bb8a": 0x52bb8a,
             "audio_ble_atts_ccc_update_52bb64": 0x52bb64,
             "audio_ble_hci_vendor_log_enabled_4c9c50": 0x4c9c50,
             "audio_ble_hci_vendor_compare_44b610": 0x44b610,
             "audio_log_flags": 0x43d0ce,
             "audio_log_extended": 0x43d574,
             "audio_ble_wsf_trace": 0x52a63c}
STATE, TABLE, VALUES, STOP = 0x20073b00, 0x20050000, 0x20010000, 0x10010000
MEMSET = 0x43c0e4


def cstr(cpu, pointer):
    out = bytearray()
    for index in range(200):
        value = cpu.mem_read(pointer + index, 1)[0]
        if value == 0:
            return bytes(out).decode("ascii")
        out.append(value)
    raise RuntimeError(f"unterminated string {pointer:#x}")


def run(segments, entry, connection, allocated, count, initial, vendor, log_flags):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_write(STATE, bytes(0x18))
    uc.mem_write(STATE + 0x14, bytes([count]))
    uc.mem_write(TABLE, b"\xa5" * 16)
    values = struct.pack("<5H", 0, 1, 0x1234, 0, 0x8001)
    uc.mem_write(VALUES, values)
    uc.reg_write(UC_ARM_REG_R0, connection)
    uc.reg_write(UC_ARM_REG_R1, VALUES if initial else 0)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls = []

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
            return
        r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                          (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
        if address == 0x4c9c50:
            calls.append(("vendor",))
            result = vendor
        elif address == 0x44b610:
            a, b = bytes(cpu.mem_read(r0, r2)), bytes(cpu.mem_read(r1, r2))
            calls.append(("compare", a, b, r2))
            result = next((x-y for x, y in zip(a, b) if x != y), 0) & 0xffffffff
        elif address == 0x43d0ce:
            calls.append(("flags",))
            result = log_flags
        elif address == 0x43d574:
            sp = cpu.reg_read(UC_ARM_REG_SP)
            line, message, arg = struct.unpack("<III", cpu.mem_read(sp, 12))
            calls.append(("extended", r0, cstr(cpu, r1), cstr(cpu, r2),
                          cstr(cpu, r3), line, cstr(cpu, message), arg))
            result = 0
        elif address == 0x52a63c:
            calls.append(("trace", cstr(cpu, r0), cstr(cpu, r1), r2))
            result = 0
        elif address == 0x52bb8a:
            calls.append(("allocate", r0))
            result = TABLE if allocated else 0
        elif address == 0x52bb64:
            calls.append(("update", r0, r1, r2, r3))
            result = 0
        elif address == MEMSET:
            cpu.mem_write(r0, bytes([r2 & 0xff]) * r1)
            result = r0
        else:
            return
        cpu.reg_write(UC_ARM_REG_R0, result)
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=4000)
    return calls, bytes(uc.mem_read(TABLE, 16)), bytes(uc.mem_read(STATE, 0x18))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "atts_ccc_init.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defined = {ENTRY, "audio_ble_atts_ccc_runtime_20073b00"}
    if names(obj, "-g", "--defined-only") != defined or \
       names(obj, "-u") != set(PROVIDERS):
        raise RuntimeError("ATT CCC source symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "ccc.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", f"-Tbss={STATE:#x}",
                        "-e", ENTRY,
                        *(f"--defsym={name}={address | 1}" for name, address in PROVIDERS.items()),
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        if symbols["audio_ble_atts_ccc_runtime_20073b00"] != STATE:
            raise RuntimeError("trial CCC state placement changed")
        cases = [(connection, allocated, count, initial, vendor, log_flags)
                 for connection in (0, 1, 3, 0x123401)
                 for allocated in (0, 1) for count in (0, 1, 3, 5)
                 for initial in (0, 1) for vendor in (0, 1)
                 for log_flags in (0, 2)]
        for case in cases:
            native = run(native_segments, 0x52c244, *case)
            compiled = run(native_segments + source_segments, symbols[ENTRY], *case)
            if native != compiled:
                raise RuntimeError(f"ATT CCC mismatch {case}: {native[0]} != {compiled[0]}")
    before = names(BASE, "-u")
    base_defined = names(BASE, "-g", "--defined-only")
    added = {"audio_ble_atts_ccc_alloc_table_52bb8a", "audio_ble_atts_ccc_update_52bb64"}
    if ENTRY not in before or "audio_ble_atts_ccc_runtime_20073b00" not in before or \
       not (set(PROVIDERS) - added) <= base_defined:
        raise RuntimeError("Apollo Main ATT CCC base contract changed")
    linked = OUT / "apollo-main-atts-ccc-init.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != defined or after - before != added:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_ATTS_CCC_INIT_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x52c244", "native_state_origin": hex(STATE),
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["CCC table allocation and per-entry update remain separate lower C contracts.",
                          "Absolute CCC RAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

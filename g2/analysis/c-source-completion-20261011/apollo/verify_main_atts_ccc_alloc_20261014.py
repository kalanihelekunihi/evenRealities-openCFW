#!/usr/bin/env python3
"""Compare native/C CCC table allocation, reuse, and invalid diagnostics."""
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/atts_ccc_alloc.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-atts-ccc-update/apollo-main-atts-ccc-update.o"
OUT = G2 / "build/c-firmware/20261014/main-atts-ccc-alloc"
ENTRY = "audio_ble_atts_ccc_alloc_table_52bb8a"
PROVIDERS = {"audio_wsf_buffer_alloc": 0x530446,
             "audio_ble_hci_vendor_log_enabled_4c9c50": 0x4c9c50,
             "audio_ble_hci_vendor_compare_44b610": 0x44b610,
             "audio_log_flags": 0x43d0ce,
             "audio_log_extended": 0x43d574,
             "audio_ble_wsf_trace": 0x52a63c}
STATE, TABLE, STOP = 0x20073b00, 0x20050000, 0x10010000


def cstr(cpu, pointer):
    out = bytearray()
    for index in range(200):
        value = cpu.mem_read(pointer + index, 1)[0]
        if value == 0:
            return bytes(out).decode("ascii")
        out.append(value)
    raise RuntimeError(f"unterminated string {pointer:#x}")


def run(segments, entry, connection, count, existing, allocated, vendor, log_flags):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_write(STATE, bytes(0x18))
    uc.mem_write(STATE + 0x14, bytes([count]))
    slot = STATE + (((connection & 0xff) - 1) * 4)
    if (connection & 0xff) != 0 and existing:
        uc.mem_write(slot, struct.pack("<I", 0x20051000))
    uc.reg_write(UC_ARM_REG_R0, connection)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls = []

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
            return
        r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                          (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
        if address == 0x530446:
            calls.append(("alloc", r0))
            result = TABLE if allocated else 0
        elif address == 0x4c9c50:
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
        else:
            return
        cpu.reg_write(UC_ARM_REG_R0, result)
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=1800)
    return calls, uc.reg_read(UC_ARM_REG_R0), bytes(uc.mem_read(STATE, 0x18))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "atts_ccc_alloc.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    storage = {"audio_ble_atts_ccc_runtime_20073b00"}
    if names(obj, "-g", "--defined-only") != {ENTRY} or \
       names(obj, "-u") != set(PROVIDERS) | storage:
        raise RuntimeError("CCC allocator source symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "alloc.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", ENTRY,
                        *(f"--defsym={name}={address | 1}" for name, address in PROVIDERS.items()),
                        f"--defsym=audio_ble_atts_ccc_runtime_20073b00={STATE:#x}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(connection, count, existing, allocated, vendor, log_flags)
                 for connection in (0, 1, 3, 0x123400, 0x123401)
                 for count in (0, 3, 0xff) for existing in (0, 1)
                 for allocated in (0, 1) for vendor in (0, 1)
                 for log_flags in (0, 2)]
        for case in cases:
            native = run(native_segments, 0x52bb8a, *case)
            compiled = run(native_segments + source_segments, symbols[ENTRY], *case)
            if native != compiled:
                raise RuntimeError(f"CCC allocator mismatch {case}: {native[:2]} != {compiled[:2]}")
    before = names(BASE, "-u")
    if ENTRY not in before or \
       not set(PROVIDERS) | storage <= names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main CCC allocator base contract changed")
    linked = OUT / "apollo-main-atts-ccc-alloc.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {ENTRY} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_ATTS_CCC_ALLOC_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x52bb8a", "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["WSF pool allocation is an existing C provider.",
                          "Absolute CCC RAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

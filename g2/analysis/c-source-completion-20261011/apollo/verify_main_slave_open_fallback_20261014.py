#!/usr/bin/env python3
"""Compare native/C slave address-resolution scan and busy logging."""
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_open_fallback.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-pair-record-iter/apollo-main-pair-record-iter.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-open-fallback"
ENTRY = "audio_ble_slave_open_fallback_4b3606"
PROVIDERS = {"audio_ble_subsystem_child_479418": 0x479418,
             "audio_ble_pair_record_next_47a630": 0x47a630,
             "audio_ble_link_mask_select_47ae78": 0x47ae78,
             "audio_ble_slave_record_key_4b6eea": 0x4b6eea,
             "audio_ble_slave_resolution_request_4d27f6": 0x4d27f6,
             "audio_log_flags": 0x43d0ce,
             "audio_log_extended": 0x43d574,
             "compressed_log_output": 0x43ce9e}
STATE, CONNECTIONS, MESSAGE, STOP = 0x200719c8, 0x200717b0, 0x20010000, 0x10010000
ROWS = (0x20067a30, 0x20067af8)


def cstr(cpu, pointer):
    out = bytearray()
    for index in range(200):
        value = cpu.mem_read(pointer + index, 1)[0]
        if value == 0:
            return bytes(out).decode("ascii")
        out.append(value)
    raise RuntimeError(f"unterminated native string at {pointer:#x}")


def run(segments, entry, pending, rows_count, matching, flags, message_id):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    msg = bytearray(20)
    msg[:2] = struct.pack("<H", message_id)
    uc.mem_write(MESSAGE, bytes(msg))
    uc.mem_write(STATE, bytes(0x80))
    uc.mem_write(STATE + 0x70, struct.pack("<I", 0x12345678))
    uc.mem_write(STATE + 0x74, bytes([pending]))
    uc.mem_write(CONNECTIONS + (message_id - 1) * 0x30 + 4, b"\x03")
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls = []

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
            return
        r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                          (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
        if address == 0x479418:
            calls.append(("reset",))
            result = 0
        elif address == 0x47a630:
            calls.append(("next", r0))
            result = ROWS[0] if r0 == 0 and rows_count >= 1 else \
                     ROWS[1] if r0 == ROWS[0] and rows_count >= 2 else 0
        elif address == 0x47ae78:
            calls.append(("select", r0, r1, r2))
            result = r0 + 7 if (r0 == ROWS[0] and matching == 1) or \
                     (r0 == ROWS[1] and matching == 2) else 0
        elif address == 0x4b6eea:
            calls.append(("key", r0))
            result = 0x200712a4
        elif address == 0x4d27f6:
            calls.append(("request", r0, r1, r2))
            result = 0
        elif address == 0x43d0ce:
            calls.append(("log_flags",))
            result = flags
        elif address == 0x43d574:
            sp = cpu.reg_read(UC_ARM_REG_SP)
            line, message = struct.unpack("<II", cpu.mem_read(sp, 8))
            calls.append(("log_extended", r0, cstr(cpu, r1), cstr(cpu, r2),
                          cstr(cpu, r3), line, cstr(cpu, message)))
            result = 0
        elif address == 0x43ce9e:
            calls.append(("log_compact", r0, cstr(cpu, r1), cstr(cpu, r2)))
            result = 0
        else:
            return
        cpu.reg_write(UC_ARM_REG_R0, result)
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=1500)
    return calls, bytes(uc.mem_read(STATE, 0x80))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_open_fallback.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    storage = {"audio_ble_subsystem_link_state_200719c8",
               "audio_ble_discovery_connection_records_200717b0"}
    if names(obj, "-g", "--defined-only") != {ENTRY} or \
       names(obj, "-u") != set(PROVIDERS) | storage:
        raise RuntimeError("slave fallback source symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "fallback.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", ENTRY,
                        *(f"--defsym={name}={address | 1}" for name, address in PROVIDERS.items()),
                        f"--defsym=audio_ble_subsystem_link_state_200719c8={STATE}",
                        f"--defsym=audio_ble_discovery_connection_records_200717b0={CONNECTIONS}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(pending, rows_count, matching, flags, message_id)
                 for pending in (0, 1) for rows_count in (0, 1, 2)
                 for matching in (0, 1, 2) for flags in (0, 1, 2, 4, 7)
                 for message_id in (1, 3)]
        for case in cases:
            native = run(native_segments, 0x4b3606, *case)
            compiled = run(native_segments + source_segments, symbols[ENTRY], *case)
            if native != compiled:
                raise RuntimeError(f"slave fallback mismatch {case}: {native} != {compiled}")
    before = names(BASE, "-u")
    defined = names(BASE, "-g", "--defined-only")
    added = {"audio_ble_slave_resolution_request_4d27f6"}
    if ENTRY not in before or not set(PROVIDERS) - added | storage <= defined:
        raise RuntimeError("Apollo Main fallback base contract changed")
    linked = OUT / "apollo-main-slave-open-fallback.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {ENTRY} or after - before != added:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_OPEN_FALLBACK_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x4b3606", "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Resolution packet 0x4d27f6 remains a lower C contract.",
                          "Provider internals, absolute RAM placement and whole-image/hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

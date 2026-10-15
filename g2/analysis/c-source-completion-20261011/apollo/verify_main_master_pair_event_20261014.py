#!/usr/bin/env python3
"""Compare Apollo Main pair-event provider calls for both connection paths."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP)

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/pair_event.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-pair-state/apollo-main-master-pair-state.o"
OUT = G2 / "build/c-firmware/20261014/main-master-pair-event"
ENTRY, MESSAGE, TABLE, ENABLED, RECORD, LINK, STOP = (
    0x4bb098, 0x20020000, 0x200717b0, 0x20071509, 0x20044000, 0x20045000, 0x10010000)
PROVIDERS = {"audio_ble_hci_vendor_log_enabled_4c9c50": 0x4c9c50,
             "audio_ble_hci_vendor_compare_44b610": 0x44b610,
             "audio_log_flags": 0x43d0ce,
             "audio_log_extended": 0x43d574,
             "audio_ble_wsf_trace": 0x52a63c,
             "audio_ble_link_mask_select_47ae78": 0x47ae78,
             "DmSecGetLocalIrk": 0x4d2524,
             "DmPrivAddDevToResList": 0x4d282e}


def run(segments, entry, connection, enabled, logging, link, flags):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_write(MESSAGE, struct.pack("<H", 0x1234) + bytes(30))
    uc.mem_write(ENABLED, bytes([enabled]))
    uc.mem_write(TABLE, struct.pack("<I", RECORD) * 8)
    uc.mem_write(LINK, bytes([0x5a] * 0x30))
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_R1, connection)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls = []
    targets = {value: name for name, value in PROVIDERS.items()}

    def string(address):
        return bytes(uc.mem_read(address, 100)).split(b"\0", 1)[0].decode("ascii")

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
            return
        if address == 0x530d54:  # Native predicate reads the same ENABLED cell.
            cpu.reg_write(UC_ARM_REG_R0, enabled)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
            return
        if address not in targets:
            return
        name = targets[address]
        r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                          (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
        if name == "audio_ble_hci_vendor_log_enabled_4c9c50":
            cpu.reg_write(UC_ARM_REG_R0, logging)
        elif name == "audio_ble_hci_vendor_compare_44b610":
            left, right = bytes(cpu.mem_read(r0, r2)), bytes(cpu.mem_read(r1, r2))
            calls.append((name, left, right, r2))
            cpu.reg_write(UC_ARM_REG_R0, 0 if left == right else 1)
        elif name == "audio_log_flags":
            cpu.reg_write(UC_ARM_REG_R0, flags)
        elif name == "audio_log_extended":
            sp = cpu.reg_read(UC_ARM_REG_SP)
            line, fmt, value = struct.unpack("<III", bytes(cpu.mem_read(sp, 12)))
            calls.append((name, r0, string(r1), string(r2), string(r3),
                          line, string(fmt), value))
        elif name == "audio_ble_wsf_trace":
            calls.append((name, string(r0), string(r1), r2))
        elif name == "audio_ble_link_mask_select_47ae78":
            calls.append((name, r0, r1, r2))
            cpu.reg_write(UC_ARM_REG_R0, LINK if link else 0)
        elif name == "DmSecGetLocalIrk":
            calls.append((name,))
            cpu.reg_write(UC_ARM_REG_R0, 0x20077000)
        elif name == "DmPrivAddDevToResList":
            sp = cpu.reg_read(UC_ARM_REG_SP)
            last, handle = struct.unpack("<II", bytes(cpu.mem_read(sp, 8)))
            calls.append((name, r0, r1, r2, r3, last, handle))
        else:
            raise RuntimeError(f"unplanned provider: {name}")
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.emu_start(entry | 1, STOP + 2, count=2000)
    return calls


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "pair_event.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_ble_master_pair_event_4bb098"}:
        raise RuntimeError("pair-event C definition changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "pair_event.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_master_pair_event_4bb098",
                        *(f"--defsym={name}={address | 1}" for name, address in PROVIDERS.items()),
                        f"--defsym=audio_ble_discovery_connection_records_200717b0={TABLE}",
                        "--defsym=audio_ble_hci_controller_state_20071478=0x20071478",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(conn, enabled, logging, link, flags)
                 for conn in (0, 1, 2, 4)
                 for enabled in (0, 1) for logging in (0, 1)
                 for link in (0, 1) for flags in (0, 2)]
        for args in cases:
            native = run(native_segments, ENTRY, *args)
            compiled = run(native_segments + source_segments,
                           symbols["audio_ble_master_pair_event_4bb098"], *args)
            if native != compiled:
                raise RuntimeError(f"pair-event differs: {args} {native} {compiled}")
    before = names(BASE, "-u")
    if "audio_ble_master_pair_event_4bb098" not in before:
        raise RuntimeError("Main pair-event import absent")
    linked = OUT / "apollo-main-master-pair-event.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"audio_ble_master_pair_event_4bb098"} or after - before:
        raise RuntimeError(f"unexpected Main pair-event import delta {before-after} {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_MASTER_PAIR_EVENT_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": hex(ENTRY), "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Provider calls are intercepted; native and C provider internals are not compared here.",
                          "Diagnostic output is compared only through the intercepted provider ABI; hardware pairing remains unqualified.",
                          "The privacy-enable byte aliases offset 0x91 in the source-owned HCI state; absolute RAM placement remains open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

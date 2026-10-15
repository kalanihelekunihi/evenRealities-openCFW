#!/usr/bin/env python3
"""Compare Apollo BLE master dispatch B call routing, then compose its C unit."""
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/dispatch_b.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-lvgl-label-graph/apollo-main-lvgl-label.o"
OUT = G2 / "build/c-firmware/20261014/main-master-dispatch-b"
ENTRY = 0x503c32
STOP = 0x10010000
ROW = 0x200717b0
MESSAGE = 0x20010000
CALLS = {
    "audio_ble_master_event_5037ea": 0x5037ea,
    "audio_ble_master_event_503810": 0x503810,
    "audio_ble_master_event_5038da": 0x5038da,
    "audio_ble_master_event_50390c": 0x50390c,
    "audio_ble_master_event_50391c": 0x50391c,
    "audio_ble_master_event_5038b8": 0x5038b8,
    "audio_ble_master_event_503820": 0x503820,
    "audio_ble_master_event_503880": 0x503880,
    "audio_ble_master_event_50389e": 0x50389e,
    "audio_ble_slave_disconnect_event": 0x4bb04a,
    "audio_ble_hci_driver_radio_boot": 0x4b48a6,
    "audio_ble_dm_device_reset": 0x4b3026,
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    rows = subprocess.check_output(["arm-none-eabi-nm", *options, str(path)], text=True)
    return {row.split()[-1] for row in rows.splitlines() if row.strip()}


def image(path):
    with path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(segment["p_vaddr"], segment.data()) for segment in elf.iter_segments()
                    if segment["p_type"] == "PT_LOAD"]
        symbols = {symbol.name: symbol["st_value"]
                   for symbol in elf.get_section_by_name(".symtab").iter_symbols()}
    return segments, symbols


def run(segments, entry, connection, event):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(0x100000, 0x100000)
    uc.mem_map(0x400000, 0x400000)
    uc.mem_map(0x10000000, 0x20000)
    uc.mem_map(0x20000000, 0x100000)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_write(MESSAGE, struct.pack("<HB", connection, event) + bytes(16))
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    trace = []
    targets = {address: name for name, address in CALLS.items()}

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address in targets:
            name = targets[address]
            r0 = cpu.reg_read(UC_ARM_REG_R0)
            r1 = cpu.reg_read(UC_ARM_REG_R1)
            trace.append((name, r0, r1 if name.startswith("audio_ble_master_event") else 0))
            cpu.reg_write(UC_ARM_REG_R0, 0)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=1000)
    return trace


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "dispatch_b.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_ble_comm_master_dispatch_b"}:
        raise RuntimeError("dispatch C provider changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "dispatch.elf"
        aliases = [f"--defsym={name}={address | 1}"
                   for name, address in CALLS.items()]
        aliases.append(f"--defsym=audio_ble_discovery_connection_records_200717b0={ROW}")
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_comm_master_dispatch_b", *aliases, str(obj),
                        "-o", str(trial)], check=True, capture_output=True)
        original_segments, _ = image(NATIVE)
        source_segments, source_symbols = image(trial)
        cases = [(connection, event) for connection in (0, 1, 2, 3, 4, 0x100)
                 for event in (0x27, 0x28, 0x2a, 0x2b, 0x2c, 0x2d,
                               0x2f, 0x32, 0x3a, 0x3b, 0x3f, 0x79, 0xff)]
        for connection, event in cases:
            original = run(original_segments, ENTRY, connection, event)
            source = run(original_segments + source_segments,
                         source_symbols["audio_ble_comm_master_dispatch_b"], connection, event)
            if original != source:
                raise RuntimeError(f"native/C dispatch differs: {(connection, event)} {original} {source}")
    before = names(BASE, "-u")
    if "audio_ble_comm_master_dispatch_b" not in before:
        raise RuntimeError("Main dispatch import absent")
    linked = OUT / "apollo-main-master-dispatch-b.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    added = after - before
    expected = set(CALLS) - names(BASE, "-g", "--defined-only")
    expected |= {"audio_ble_discovery_connection_records_200717b0"} - before
    if before - after != {"audio_ble_comm_master_dispatch_b"} or added != expected:
        raise RuntimeError(f"unexpected Main dispatch import delta: {added} != {expected}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_MASTER_DISPATCH_B_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entry": hex(ENTRY), "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
        "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
        "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
        "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(added),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Child handlers are call boundaries; their source bodies remain to be selected.",
                   "Native/C test compares routing and argument registers, not child state mutation.",
                   "Connection-record storage ownership and hardware behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

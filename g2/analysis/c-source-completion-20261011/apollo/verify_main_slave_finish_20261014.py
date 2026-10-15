#!/usr/bin/env python3
"""Compare second-stage slave event routing to native 0x4b45b0."""
import json
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_finish.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-dm-runtime-bindings/apollo-main-master-dm-runtime-bindings.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-finish"
ENTRY, MESSAGE, TABLE, STOP = 0x4b45b0, 0x20020000, 0x200717b0, 0x10010000
CHILDREN = {f"audio_ble_slave_finish_{addr:06x}": addr for addr in (
    0x4b3944, 0x4b39de, 0x4b3aa8, 0x4b3aea, 0x4b3aec,
    0x4b3a86, 0x4b3b4c, 0x4b39f6, 0x4b3bb4, 0x4b3bd2, 0x4b3ba0)}


def run(segments, entry, event, connection):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_write(MESSAGE, bytes((connection & 0xff, connection >> 8, event)) + bytes(13))
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls = []
    targets = {value: name for name, value in CHILDREN.items()}

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address in targets:
            calls.append((targets[address], cpu.reg_read(UC_ARM_REG_R0),
                          cpu.reg_read(UC_ARM_REG_R1)))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.emu_start(entry | 1, STOP + 2, count=1000)
    return calls


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_finish.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_ble_comm_slave_finish"} or \
       names(obj, "-u") != set(CHILDREN) | {"audio_ble_discovery_connection_records_200717b0"}:
        raise RuntimeError("slave finish C symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "slave_finish.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_comm_slave_finish",
                        *(f"--defsym={name}={address | 1}" for name, address in CHILDREN.items()),
                        f"--defsym=audio_ble_discovery_connection_records_200717b0={TABLE}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(event, connection)
                 for event in (0x26, 0x27, 0x28, 0x2a, 0x2b, 0x2c, 0x2d,
                               0x2f, 0x30, 0x31, 0x3a, 0x3b, 0x3f, 0x40)
                 for connection in (0, 1, 2, 3, 4, 0xffff)]
        for args in cases:
            native = run(native_segments, ENTRY, *args)
            try:
                compiled = run(native_segments + source_segments,
                               symbols["audio_ble_comm_slave_finish"], *args)
            except Exception as exc:
                raise RuntimeError(f"compiled slave finish failed for {args}") from exc
            if native != compiled:
                raise RuntimeError(f"slave finish differs: {args} {native} {compiled}")
    before = names(BASE, "-u")
    if "audio_ble_comm_slave_finish" not in before:
        raise RuntimeError("Main slave finish import absent")
    linked = OUT / "apollo-main-slave-finish.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 472 or len(after) != 482 or \
       before - after != {"audio_ble_comm_slave_finish"} or after - before != set(CHILDREN):
        raise RuntimeError(f"unexpected Main slave import delta {before-after} {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_FINISH_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": hex(ENTRY), "child_contracts": {n: hex(a) for n, a in CHILDREN.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Eleven lower slave-event bodies remain C contracts and are cut at native entries.",
                          "This dispatcher is compiled to the Cortex-M4 Thumb subset supported by Apollo's M55.",
                          "The live connection table absolute placement and physical BLE behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare native/C 22-byte slave security request packets."""
import json
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_security_request.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-slave-resolve/apollo-main-slave-resolve.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-security-request"
ENTRY = "audio_ble_dm_sec_resolve_52bb20"
PROVIDERS = {"audio_wsf_msg_alloc": 0x4bf99e,
             "audio_ble_stack_copy16_542a44": 0x542a44,
             "audio_wsf_msg_send": 0x4bf9ba}
STATE, PACKET, LINK, STOP = 0x20073b78, 0x20050000, 0x20043000, 0x10010000


def run(segments, entry, allocated, connection, flag, selected, handler):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_write(PACKET, b"\xa5" * 22)
    uc.mem_write(LINK, bytes(range(16)))
    uc.mem_write(STATE + 0x0c, bytes([handler]))
    for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3),
                          (connection, flag, selected, LINK)):
        uc.reg_write(reg, value)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls = []

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
            return
        r0, r1 = cpu.reg_read(UC_ARM_REG_R0), cpu.reg_read(UC_ARM_REG_R1)
        if address == 0x4bf99e:
            calls.append(("alloc", r0))
            cpu.reg_write(UC_ARM_REG_R0, PACKET if allocated else 0)
        elif address == 0x542a44:
            data = bytes(cpu.mem_read(r1, 16))
            calls.append(("copy16", r0, r1, data))
            cpu.mem_write(r0, data)
        elif address == 0x4bf9ba:
            calls.append(("send", r0, r1, bytes(cpu.mem_read(r1, 22))))
        else:
            return
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=400)
    return calls, bytes(uc.mem_read(PACKET, 22))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_security_request.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {ENTRY} or \
       names(obj, "-u") != set(PROVIDERS) | {"audio_ble_dm_privacy_state"}:
        raise RuntimeError("slave security source symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "security.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", ENTRY,
                        *(f"--defsym={name}={address | 1}" for name, address in PROVIDERS.items()),
                        f"--defsym=audio_ble_dm_privacy_state={STATE}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(allocated, connection, flag, selected, handler)
                 for allocated in (0, 1) for connection in (0, 3, 0x123456ff)
                 for flag in (0, 1, 0x100, 0x101) for selected in (0, 0x93)
                 for handler in (0, 7)]
        for case in cases:
            native = run(native_segments, 0x52bb20, *case)
            compiled = run(native_segments + source_segments, symbols[ENTRY], *case)
            if native != compiled:
                raise RuntimeError(f"slave security mismatch {case}: {native} != {compiled}")
    before = names(BASE, "-u")
    if ENTRY not in before or \
       not set(PROVIDERS) | {"audio_ble_dm_privacy_state"} <= names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main slave security base contract changed")
    linked = OUT / "apollo-main-slave-security-request.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {ENTRY} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_SECURITY_REQUEST_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x52bb20", "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Existing WSF allocation, copy16, and send C providers are shared.",
                          "Absolute RAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()

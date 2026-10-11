#!/usr/bin/env python3
"""Compare ack wrapper with the same real original CMSIS event-set callee."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_IPSR, UC_ARM_REG_LR, UC_ARM_REG_PC,
                               UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP,
                               UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "g2/components/audio/source_candidate_20261010/ack_event_provider.c"
OBJECT = Path("/tmp/g2-audio-arm-inventory/122-source_candidate_20261010-ack_event_provider.o")
original = OTA.read_bytes()[0x20:]
with tempfile.TemporaryDirectory(prefix="g2-audio-ack-") as temp:
    linked = Path(temp) / "ack.elf"
    binary = Path(temp) / "ack.bin"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e", "audio_ack_index",
                    "--defsym=osEventFlagsSet=0x4495e5", str(OBJECT), "-o", str(linked)],
                   check=True, capture_output=True)
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", "--only-section=.text",
                    str(linked), str(binary)], check=True)
    compiled = binary.read_bytes()


def run(index, initial_bits, variant):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(original) + 4095) & ~4095)
    u.mem_write(0x438000, original)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    u.mem_map(0xe000e000, 0x2000)
    event_group = 0x20006800
    u.mem_write(0x200040f4, struct.pack("<I", event_group))
    u.mem_write(event_group, struct.pack("<7I", initial_bits, 0,
                                        event_group + 12, 0xffffffff,
                                        event_group + 12, event_group + 12, 0))
    u.mem_write(0x20074a3c, struct.pack("<I", 1))
    u.mem_write(0x20074a30, struct.pack("<I", 0))
    u.reg_write(UC_ARM_REG_IPSR, 0)
    u.reg_write(UC_ARM_REG_R0, index)
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x100101)
    writes = []
    calls = []
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _u, _access, a, s, v, _data:
               writes.append([a, s, v]) if a < 0x2007d000 else None)
    u.hook_add(UC_HOOK_CODE, lambda cpu, a, _s, _data:
               calls.append([cpu.reg_read(UC_ARM_REG_R0), cpu.reg_read(UC_ARM_REG_R1)])
               if a == 0x4495e4 else None)
    u.emu_start(0x4c9c3d if variant == "original" else 0x100001,
                0x100100, count=20000)
    return {"event_group": bytes(u.mem_read(event_group, 28)).hex(),
            "event_bits": struct.unpack("<I", u.mem_read(event_group, 4))[0],
            "calls": calls, "writes": writes,
            "sp": u.reg_read(UC_ARM_REG_SP), "pc": u.reg_read(UC_ARM_REG_PC)}


cases = []
for index in (0, 3, 7, 31, 32, 256):
    for initial_bits in (0, 8, 0x40000000):
        a = run(index, initial_bits, "original")
        b = run(index, initial_bits, "compiled")
        expected = (1 << (index & 255)) if (index & 255) < 32 else 0
        assert a == b, (index, initial_bits, a, b)
        assert a["calls"] == [[0x20006800, expected]], a
        # CMSIS reserves bit31; zero and bit31 masks leave the group unchanged.
        admitted = expected if expected and not (expected & 0x80000000) else 0
        assert a["event_bits"] == initial_bits | admitted, a
        assert a["sp"] == 0x2007e000 and a["pc"] == 0x100100
        cases.append({"index": index, "initial_bits": initial_bits,
                      "original": a, "compiled": b, "match": True})

report = {"cases": cases, "matched": len(cases), "total": len(cases),
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "scope": "real original osEventFlagsSet callee, empty waiter list, synthetic event group and scheduler globals; no concurrent manager"}
Path(__file__).with_name("ack-event-execution.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} original/source ack comparisons pass")

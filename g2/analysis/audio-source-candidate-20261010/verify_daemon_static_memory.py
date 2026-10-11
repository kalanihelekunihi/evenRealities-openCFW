#!/usr/bin/env python3
"""Compare original and source timer-daemon static memory outputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP,
                               UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "g2/components/audio/source_candidate_20261010/daemon_static_memory.c"
OBJECT = Path("/tmp/g2-audio-arm-inventory/121-source_candidate_20261010-daemon_static_memory.o")
original = OTA.read_bytes()[0x20:]
with tempfile.TemporaryDirectory(prefix="g2-audio-daemon-static-") as temp:
    binary = Path(temp) / "text.bin"
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", "--only-section=.text",
                    str(OBJECT), str(binary)], check=True)
    compiled = binary.read_bytes()


def run(outputs, variant):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(original) + 4095) & ~4095)
    u.mem_write(0x438000, original)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    u.mem_write(0x20010000, b"\xa5" * 64)
    u.reg_write(UC_ARM_REG_R0, outputs[0])
    u.reg_write(UC_ARM_REG_R1, outputs[1])
    u.reg_write(UC_ARM_REG_R2, outputs[2])
    u.reg_write(UC_ARM_REG_SP, 0x2007f000)
    u.reg_write(UC_ARM_REG_LR, 0x100101)
    writes = []
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _u, _access, a, s, v, _data: writes.append([a, s, v]))
    u.emu_start(0x4d3611 if variant == "original" else 0x100001, 0x100100, count=20)
    return {"sp": u.reg_read(UC_ARM_REG_SP), "pc": u.reg_read(UC_ARM_REG_PC),
            "ram": bytes(u.mem_read(0x20010000, 64)).hex(), "writes": writes}


cases = []
for outputs in ((0x20010000, 0x20010004, 0x20010008),
                (0x20010010, 0x20010014, 0x20010018),
                (0x20010000, 0x20010000, 0x20010004),
                (0x20010008, 0x20010000, 0x20010008)):
    a = run(outputs, "original")
    b = run(outputs, "compiled")
    assert a == b and a["sp"] == 0x2007f000
    assert a["writes"] == [[outputs[0], 4, 0x20071ea0],
                           [outputs[1], 4, 0x2003fa98],
                           [outputs[2], 4, 4096]]
    cases.append({"output_cells": outputs, "original": a, "compiled": b,
                  "match": True})

report = {"cases": cases, "matched": len(cases), "total": len(cases),
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "scope": "isolated output writes in synthetic RAM; no daemon task creation"}
Path(__file__).with_name("daemon-static-memory-execution.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} original/source daemon static-memory comparisons pass")

#!/usr/bin/env python3
"""Compare isolated stock and source PendSV request side effects."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_SP,
                               UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "g2/components/audio/source_candidate_20261010/yield_provider.c"
OBJECT = Path("/tmp/g2-audio-arm-inventory/120-source_candidate_20261010-yield_provider.o")
original = OTA.read_bytes()[0x20:]
with tempfile.TemporaryDirectory(prefix="g2-audio-yield-") as temp:
    binary = Path(temp) / "text.bin"
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", "--only-section=.text",
                    str(OBJECT), str(binary)], check=True)
    compiled = binary.read_bytes()


def run(initial, variant):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(original) + 4095) & ~4095)
    u.mem_write(0x438000, original)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    u.mem_map(0xe000e000, 0x2000)
    u.mem_write(0xe000ed04, initial.to_bytes(4, "little"))
    u.reg_write(UC_ARM_REG_SP, 0x2007f000)
    u.reg_write(UC_ARM_REG_LR, 0x100101)
    writes = []
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _u, _access, a, s, v, _data: writes.append([a, s, v]))
    u.emu_start(0x4420bd if variant == "original" else 0x100001, 0x100100, count=12)
    return {"sp": u.reg_read(UC_ARM_REG_SP), "pc": u.reg_read(UC_ARM_REG_PC),
            "icsr": int.from_bytes(u.mem_read(0xe000ed04, 4), "little"),
            "writes": writes}


cases = []
for initial in (0, 1, 0x20000000, 0xffffffff):
    a = run(initial, "original")
    b = run(initial, "compiled")
    assert a == b and a["sp"] == 0x2007f000
    assert a["writes"] == [[0xe000ed04, 4, 0x10000000]]
    cases.append({"icsr_before": initial, "original": a, "compiled": b, "match": True})

report = {"cases": cases, "matched": len(cases), "total": len(cases),
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "scope": "isolated write and barriers; mapped synthetic ICSR, no exception delivery"}
Path(__file__).with_name("yield-request-execution.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} original/source PendSV request comparisons pass")

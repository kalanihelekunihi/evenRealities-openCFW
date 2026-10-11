#!/usr/bin/env python3
"""Compare stock 64-bit tick wrapper with source across selected contexts."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_BASEPRI, UC_ARM_REG_IPSR, UC_ARM_REG_LR,
                               UC_ARM_REG_PC, UC_ARM_REG_PRIMASK, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_SP,
                               UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "g2/components/audio/source_candidate_20261010/codec_tick_provider.c"
OBJECT = Path("/tmp/g2-audio-arm-inventory/124-source_candidate_20261010-codec_tick_provider.o")
original = OTA.read_bytes()[0x20:]
with tempfile.TemporaryDirectory(prefix="g2-audio-codec-tick-") as temp:
    binary = Path(temp) / "text.bin"
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", "--only-section=.text",
                    str(OBJECT), str(binary)], check=True)
    compiled = binary.read_bytes()


def run(tick, scheduler, ipsr, primask, basepri, variant):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(original) + 4095) & ~4095)
    u.mem_write(0x438000, original)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    u.mem_map(0xe000e000, 0x2000)
    u.mem_write(0x20074a34, tick.to_bytes(4, "little"))
    u.mem_write(0x20074a3c, scheduler.to_bytes(4, "little"))
    u.reg_write(UC_ARM_REG_IPSR, ipsr)
    u.reg_write(UC_ARM_REG_PRIMASK, primask)
    u.reg_write(UC_ARM_REG_BASEPRI, basepri)
    u.reg_write(UC_ARM_REG_SP, 0x2007f000)
    u.reg_write(UC_ARM_REG_LR, 0x100101)
    writes = []
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _u, _access, a, s, v, _data:
               writes.append([a, s, v]) if a < 0x2007e000 else None)
    u.emu_start(0x58fac9 if variant == "original" else 0x100001,
                0x100100, count=100)
    return {"r0": u.reg_read(UC_ARM_REG_R0), "r1": u.reg_read(UC_ARM_REG_R1),
            "sp": u.reg_read(UC_ARM_REG_SP), "pc": u.reg_read(UC_ARM_REG_PC),
            "tick_after": int.from_bytes(u.mem_read(0x20074a34, 4), "little"),
            "writes": writes}


cases = []
for scheduler, ipsr, primask, basepri in ((1, 0, 0, 0), (1, 15, 0, 0),
                                          (0, 0, 1, 0), (0, 0, 0, 0x30)):
    for tick in (0, 1, 0x12345678, 0x80000000, 0xffffffff):
        a = run(tick, scheduler, ipsr, primask, basepri, "original")
        b = run(tick, scheduler, ipsr, primask, basepri, "compiled")
        assert a == b, (tick, scheduler, ipsr, primask, basepri, a, b)
        assert (a["r0"], a["r1"], a["tick_after"]) == (tick, 0, tick)
        assert a["sp"] == 0x2007f000 and not a["writes"]
        cases.append({"context": [scheduler, ipsr, primask, basepri],
                      "tick": tick, "original": a, "compiled": b, "match": True})

report = {"cases": cases, "matched": len(cases), "total": len(cases),
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "scope": "selected task/ISR/masked contexts, synthetic tick RAM; no tick production, timeout progression or device scheduling"}
Path(__file__).with_name("codec-tick-execution.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} original/source codec tick comparisons pass")

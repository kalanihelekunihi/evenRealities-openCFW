#!/usr/bin/env python3
"""Compare original Apollo getters with freshly compiled source objects."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "g2/components/audio/source_candidate_20261010/kernel_read_providers.c"
OBJECT = Path("/tmp/g2-audio-arm-inventory/116-source_candidate_20261010-kernel_read_providers.o")
original = OTA.read_bytes()[0x20:]
with tempfile.TemporaryDirectory(prefix="g2-audio-getters-") as temp:
    binary = Path(temp) / "text.bin"
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=.text", str(OBJECT), str(binary)], check=True)
    compiled = binary.read_bytes()


def run(name, address, value, variant):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(original) + 4095) & ~4095)
    u.mem_write(0x438000, original)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    u.mem_write(address, value.to_bytes(4, "little"))
    u.reg_write(UC_ARM_REG_SP, 0x2007f000)
    u.reg_write(UC_ARM_REG_LR, 0x100101)
    start = ({"audio_tick": 0x454eff, "receiver_current_task": 0x45589d}[name]
             if variant == "original" else
             {"audio_tick": 0x100001, "receiver_current_task": 0x10000d}[name])
    writes = []
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _u, _access, a, s, v, _user: writes.append([a, s, v]))
    before = bytes(u.mem_read(address, 4))
    u.emu_start(start, 0x100100, count=8)
    return {"r0": u.reg_read(UC_ARM_REG_R0), "sp": u.reg_read(UC_ARM_REG_SP),
            "ram_before": before.hex(), "ram_after": bytes(u.mem_read(address, 4)).hex(),
            "writes": writes, "pc": u.reg_read(UC_ARM_REG_PC)}


cases = []
for name, address in (("audio_tick", 0x20074a34),
                      ("receiver_current_task", 0x20074a20)):
    for value in (0, 1, 0x12345678, 0x80000000, 0xffffffff):
        a = run(name, address, value, "original")
        b = run(name, address, value, "compiled")
        assert a == b and a["r0"] == value and a["sp"] == 0x2007f000
        assert a["ram_before"] == a["ram_after"] and not a["writes"]
        cases.append({"name": name, "input_word": value, "original": a,
                      "compiled": b, "match": True})

report = {"cases": cases, "matched": len(cases), "total": len(cases),
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "scope": "direct getter entry, synthetic RAM, Cortex-M4 Unicorn profile; no scheduler timing or hardware"}
(Path(__file__).with_name("kernel-read-execution.json")).write_text(json.dumps(report, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} original/source getter comparisons pass")

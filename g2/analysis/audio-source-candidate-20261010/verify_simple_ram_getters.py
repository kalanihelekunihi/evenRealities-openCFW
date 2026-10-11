#!/usr/bin/env python3
"""Exercise two original byte getters and source-built counterparts."""
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
SOURCE = ROOT / "g2/components/audio/source_candidate_20261010/simple_ram_getters.c"
OBJECT = Path("/tmp/g2-audio-arm-inventory/117-source_candidate_20261010-simple_ram_getters.o")
original = OTA.read_bytes()[0x20:]
with tempfile.TemporaryDirectory(prefix="g2-audio-simple-getters-") as temp:
    binary = Path(temp) / "text.bin"
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", "--only-section=.text",
                    str(OBJECT), str(binary)], check=True)
    compiled = binary.read_bytes()


def run(name, value, variant):
    address = 0x20004543 if name == "platform_log_flags" else 0x200038f1
    entry = {"platform_log_flags": 0x43d0cf, "audio_role": 0x4abe61}[name]
    source_entry = {"platform_log_flags": 0x100001, "audio_role": 0x10000d}[name]
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(original) + 4095) & ~4095)
    u.mem_write(0x438000, original)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    u.mem_write(address, bytes([value]))
    u.reg_write(UC_ARM_REG_SP, 0x2007f000)
    u.reg_write(UC_ARM_REG_LR, 0x100101)
    writes = []
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _u, _access, a, s, v, _data: writes.append([a, s, v]))
    u.emu_start(entry if variant == "original" else source_entry, 0x100100, count=8)
    return {"r0": u.reg_read(UC_ARM_REG_R0), "sp": u.reg_read(UC_ARM_REG_SP),
            "ram_after": bytes(u.mem_read(address, 1)).hex(),
            "pc": u.reg_read(UC_ARM_REG_PC), "writes": writes}


cases = []
for name in ("platform_log_flags", "audio_role"):
    for value in (0, 1, 2, 0x80, 0xff):
        a = run(name, value, "original")
        b = run(name, value, "compiled")
        assert a == b and a["r0"] == value and a["ram_after"] == f"{value:02x}"
        assert a["sp"] == 0x2007f000 and not a["writes"]
        cases.append({"name": name, "input_byte": value, "original": a,
                      "compiled": b, "match": True})

report = {"cases": cases, "matched": len(cases), "total": len(cases),
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "scope": "direct getter entry, synthetic RAM, Cortex-M4 Unicorn profile; no producer or hardware behavior"}
Path(__file__).with_name("simple-ram-getter-execution.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} original/source byte getter comparisons pass")

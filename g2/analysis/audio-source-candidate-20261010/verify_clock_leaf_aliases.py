#!/usr/bin/env python3
"""Compare two Apollo clock leaf originals with their source alias entries."""
import hashlib
import json
from pathlib import Path
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OBJECT = Path("/tmp/g2-audio-arm-inventory/134-source_candidate_20261010-clock_leaf_aliases.o")
TEXT = Path("/tmp/g2-audio-clock-leaf-new.text")
raw = OTA.read_bytes()[32:]
compiled = TEXT.read_bytes()

def run(variant, op, reference, target, mmio):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(raw) + 4095) & ~4095)
    u.mem_write(0x438000, raw)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    u.mem_map(0x40004000, 0x1000)
    u.mem_map(0x40020000, 0x1000)
    u.mem_write(0x400204d8, struct.pack("<I", mmio))
    u.mem_write(0x40004044, struct.pack("<I", mmio))
    u.mem_write(0x40004020, struct.pack("<I", mmio))
    out = 0x20006100
    u.mem_write(out, b"\xa5\xa5\xa5\xa5")
    if op == "pll_power_enabled":
        entry = 0x4800e5 if variant == "original" else 0x100125
        u.reg_write(UC_ARM_REG_R0, out)
    elif op == "hfrc_target":
        entry = 0x4d3915 if variant == "original" else 0x100269
        u.reg_write(UC_ARM_REG_R0, reference)
        u.reg_write(UC_ARM_REG_R1, target)
        u.reg_write(UC_ARM_REG_R2, out)
    elif op == "hfrc_force":
        entry = 0x4d391f if variant == "original" else 0x10013d
        u.reg_write(UC_ARM_REG_R0, target)
    else:
        entry = 0x4d3945 if variant == "original" else 0x10016d
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x100301)
    writes = []
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _cpu, _access, address, size, value, _data:
               writes.append([address, size, value]) if address < 0x2007d000 else None)
    u.emu_start(entry, 0x100300, count=100)
    return {"return": u.reg_read(UC_ARM_REG_R0), "out": bytes(u.mem_read(out, 4)).hex(),
            "writes": writes, "sp": u.reg_read(UC_ARM_REG_SP), "pc": u.reg_read(UC_ARM_REG_PC)}

cases = []
for mmio in (0, 0x80000000, 0x40000000, 0xffffffff):
    for op in ("pll_power_enabled",):
        original = run("original", op, 0, 0, mmio)
        source = run("source", op, 0, 0, mmio)
        assert original == source, (op, mmio, original, source)
        cases.append({"op": op, "mmio": mmio, "result": original})
for reference, target in ((1, 100), (10, 123), (1000, 999), (0xffffffff, 0xffffffff)):
    op = "hfrc_target"
    original = run("original", op, reference, target, 0)
    source = run("source", op, reference, target, 0)
    assert original == source, (op, reference, target, original, source)
    cases.append({"op": op, "reference": reference, "target": target, "result": original})
for op, target, mmio in (("hfrc_force", 0, 0xffffffff),
                         ("hfrc_force", 1, 0),
                         ("hfrc_force", 0x100, 0x24),
                         ("hfrc_force", 0xff, 0x80000000),
                         ("hfrc_disable", 0, 0),
                         ("hfrc_disable", 0, 1),
                         ("hfrc_disable", 0, 0xffffffff),
                         ("hfrc_disable", 0, 0x12345678)):
    original = run("original", op, 0, target, mmio)
    source = run("source", op, 0, target, mmio)
    assert original == source, (op, target, mmio, original, source)
    cases.append({"op": op, "target": target, "mmio": mmio, "result": original})
assert all(x["result"]["sp"] == 0x2007e000 and x["result"]["pc"] == 0x100300 for x in cases)
result = {"matched": len(cases), "total": len(cases), "cases": cases,
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "scope": "Apollo clock leaf original versus Clang Cortex-M55 alias on synthetic MMIO/output RAM, unchanged SP and matching return/nonstack writes. No live clock readiness or div-by-zero trap."}
Path(__file__).with_name("clock-leaf-alias-execution.json").write_text(json.dumps(result, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} clock leaf original/source cases pass")

#!/usr/bin/env python3
"""Compare same-object critical-entry aliases with authenticated stock entry."""
import hashlib
import json
from pathlib import Path
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_BASEPRI, UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "g2/components/audio/source_candidate_20261010/critical_entry_aliases.c"
OLD = Path("/tmp/g2-audio-arm-inventory/090-timer_wake_providers_offline-port.o")
NEW = Path("/tmp/g2-audio-arm-inventory/126-source_candidate_20261010-critical_entry_aliases.o")
BIN = Path("/tmp/g2-audio-critical-alias.bin")
raw = OTA.read_bytes()[32:]
compiled = BIN.read_bytes()

def run(variant, kind, initial_mask, initial_nesting):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(raw) + 4095) & ~4095)
    u.mem_write(0x438000, raw)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    u.mem_write(0x2000309c, struct.pack("<I", initial_nesting))
    u.reg_write(UC_ARM_REG_BASEPRI, initial_mask)
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x100101)
    trace = []
    last_mask = [initial_mask]
    count = [0]
    def on_code(cpu, address, _size, _data):
        count[0] += 1
        mask = cpu.reg_read(UC_ARM_REG_BASEPRI)
        if mask != last_mask[0]:
            trace.append(["basepri", mask, count[0]])
            last_mask[0] = mask
    def on_write(_cpu, _access, address, size, value, _data):
        if address == 0x2000309c:
            trace.append(["nesting", value, count[0]])
    u.hook_add(UC_HOOK_CODE, on_code)
    u.hook_add(UC_HOOK_MEM_WRITE, on_write)
    start = (0x4420d1 if kind == "enter" else 0x4420e9) if variant == "original" else (0x10001d if kind == "enter" else 0x100049)
    u.emu_start(start, 0x100100, count=200)
    return {"trace": trace,
            "basepri": u.reg_read(UC_ARM_REG_BASEPRI),
            "nesting": struct.unpack("<I", u.mem_read(0x2000309c, 4))[0],
            "sp": u.reg_read(UC_ARM_REG_SP),
            "pc": u.reg_read(UC_ARM_REG_PC)}

cases = []
for kind in ("enter", "exit"):
    for mask in (0, 16, 32, 48, 64, 128, 240):
        for nesting in ((0, 1, 2, 0xffffffff) if kind == "enter" else (1, 2, 0xffffffff)):
            original = run("original", kind, mask, nesting)
            alias = run("alias", kind, mask, nesting)
            assert original["basepri"] == alias["basepri"] == (48 if kind == "enter" else (0 if nesting == 1 else mask))
            assert original["nesting"] == alias["nesting"] == ((nesting + 1) if kind == "enter" else (nesting - 1)) & 0xffffffff
            assert original["sp"] == alias["sp"] == 0x2007e000
            assert original["pc"] == alias["pc"] == 0x100100
            # Count differs by code generation; compare ordering and values of
            # architectural side effects, and retain instruction indices.
            assert [row[:2] for row in original["trace"]] == [row[:2] for row in alias["trace"]]
            cases.append({"kind": kind, "initial_basepri": mask, "initial_nesting": nesting,
                          "original": original, "alias": alias})

result = {"cases": cases, "matched": len(cases), "total": len(cases),
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "old_object_sha256": hashlib.sha256(OLD.read_bytes()).hexdigest(),
          "alias_object_sha256": hashlib.sha256(NEW.read_bytes()).hexdigest(),
          "scope": "Enter and nonzero-depth exit compare ordered BASEPRI transition and nesting update, final state, SP, PC. Zero-depth exit fatal branch excluded. Instruction counts retained but not asserted equal; no physical interrupt latency claim."}
Path(__file__).with_name("critical-entry-alias-execution.json").write_text(json.dumps(result, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} critical-entry original/source state comparisons pass")

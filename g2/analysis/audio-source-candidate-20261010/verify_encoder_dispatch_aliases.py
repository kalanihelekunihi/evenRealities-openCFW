#!/usr/bin/env python3
"""Exercise two same-object provider aliases against pinned Apollo entries."""
import hashlib
import json
from pathlib import Path
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP,
                               UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
raw = OTA.read_bytes()[32:]
encoder = Path("/tmp/g2-audio-encoder-alias-m4.bin").read_bytes()
dispatch = Path("/tmp/g2-audio-dispatch-alias-m4.bin").read_bytes()

def fixture(text):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(raw) + 4095) & ~4095)
    u.mem_write(0x438000, raw)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, text)
    u.mem_map(0x20000000, 0x100000)
    u.reg_write(UC_ARM_REG_SP, 0x200ff000)
    u.reg_write(UC_ARM_REG_LR, 0x100801)
    return u

def run_encoder(variant, duration, rate, null):
    u = fixture(encoder)
    config = 0x20010000
    u.mem_write(config, bytes([0xa5]) * 0x8000)
    u.mem_write(config + 4, struct.pack("<II", duration, rate))
    u.mem_write(config + 24, struct.pack("<I", 0xdeadbeef))
    u.reg_write(UC_ARM_REG_R0, 0 if null else config)
    entry = 0x57a927 if variant == "original" else 0x100199
    u.emu_start(entry, 0x100800, count=200000)
    return {"config": bytes(u.mem_read(config, 0x8000)).hex(),
            "sp": u.reg_read(UC_ARM_REG_SP), "pc": u.reg_read(UC_ARM_REG_PC)}

def run_dispatch(variant, action, enable, callback):
    u = fixture(dispatch)
    metadata = 0x20041000
    u.mem_write(0x20073274, struct.pack("<I", 0x100901 if callback else 0))
    u.reg_write(UC_ARM_REG_R0, action)
    u.reg_write(UC_ARM_REG_R1, enable)
    u.reg_write(UC_ARM_REG_R2, metadata)
    entry = 0x480313 if variant == "original" else 0x10006d
    hit = []
    def stop(cpu, address, _size, _data):
        if address == 0x100900:
            hit.append("before-callback")
            cpu.emu_stop()
    u.hook_add(UC_HOOK_CODE, stop)
    u.emu_start(entry, 0x100800, count=200)
    return {"stop": hit or ["return"], "r0": u.reg_read(UC_ARM_REG_R0),
            "r1": u.reg_read(UC_ARM_REG_R1) if callback else None,
            "r2": u.reg_read(UC_ARM_REG_R2) if callback else None,
            "sp": u.reg_read(UC_ARM_REG_SP),
            "pc": u.reg_read(UC_ARM_REG_PC)}

cases = []
for duration, rate, null in ((10000, 16000, False), (7500, 48000, False),
                             (1234, 16000, False), (10000, 16000, True)):
    original = run_encoder("original", duration, rate, null)
    alias = run_encoder("alias", duration, rate, null)
    assert original == alias, (duration, rate, null)
    cases.append({"provider": "audio_encoder_setup", "duration": duration,
                  "rate": rate, "null": null, "match": True})
for action, enable, callback in ((3, 1, False), (259, 257, False),
                                 (3, 1, True), (259, 257, True)):
    original = run_dispatch("original", action, enable, callback)
    alias = run_dispatch("alias", action, enable, callback)
    assert original == alias, (action, enable, callback, original, alias)
    cases.append({"provider": "stock_dispatch", "action": action,
                  "enable": enable, "callback": callback,
                  "observed": original, "match": True})

result = {"matched": len(cases), "total": len(cases), "cases": cases,
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "scope": "Encoder null, two valid and one invalid selector with full 32 KiB config workspace; dispatcher null callback and nonnull arguments stop before external callback. No encode frame or callback body execution."}
Path(__file__).with_name("encoder-dispatch-alias-execution.json").write_text(json.dumps(result, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} encoder/dispatch alias comparisons pass")

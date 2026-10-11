#!/usr/bin/env python3
"""Compare watchdog-stop wrapper through the same real original CMSIS timer peer."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_IPSR, UC_ARM_REG_LR, UC_ARM_REG_PC,
                               UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R7,
                               UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "g2/components/audio/source_candidate_20261010/watchdog_stop_provider.c"
OBJECT = Path("/tmp/g2-audio-arm-inventory/125-source_candidate_20261010-watchdog_stop_provider.o")
original = OTA.read_bytes()[0x20:]
with tempfile.TemporaryDirectory(prefix="g2-audio-watchdog-") as temp:
    linked = Path(temp) / "watchdog.elf"
    binary = Path(temp) / "watchdog.bin"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e", "audio_watchdog_stop",
                    "--defsym=audio_timer_stop=0x4494d9", str(OBJECT), "-o", str(linked)],
                   check=True, capture_output=True)
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", "--only-section=.text",
                    str(linked), str(binary)], check=True)
    compiled = binary.read_bytes()


def run(handle_mode, ipsr, variant):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(original) + 4095) & ~4095)
    u.mem_write(0x438000, original)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    u.mem_map(0xe000e000, 0x2000)

    def w(address, *values):
        u.mem_write(address, struct.pack("<" + "I" * len(values), *values))

    q = 0x20006000
    timer = 0x20006408
    w(0x20074a3c, 1)
    w(0x20074a30, 0)
    w(0x20074a34, 100)
    w(0x20074ab0, q)
    # The original queue initializer creates a real 10x16 command queue.
    for register, value in ((UC_ARM_REG_R0, 10), (UC_ARM_REG_R1, 16)):
        u.reg_write(register, value)
    from unicorn.arm_const import UC_ARM_REG_R2, UC_ARM_REG_R3
    u.reg_write(UC_ARM_REG_R2, q + 80)
    u.reg_write(UC_ARM_REG_R3, 0)
    w(0x2007e000, q)
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x2007f001)
    u.emu_start(0x441697, 0x2007f000, count=20000)
    assert u.reg_read(UC_ARM_REG_PC) == 0x2007f000

    w(timer + 0x18, 50)
    u.mem_write(timer + 0x28, bytes([1 if handle_mode == "active" else 0]))
    w(0x20074a98, 0 if handle_mode == "null" else timer)
    before_timer = bytes(u.mem_read(timer, 44))
    u.reg_write(UC_ARM_REG_IPSR, ipsr)
    u.reg_write(UC_ARM_REG_R7, 0x55aa55aa)
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x100101)
    calls = []
    writes = []
    def record_call(cpu, address, _size, _data):
        if address == 0x4494d8:
            calls.append([hex(address), cpu.reg_read(UC_ARM_REG_R0)])
        elif address == 0x47e7b0:
            calls.append([hex(address), cpu.reg_read(UC_ARM_REG_R0),
                          cpu.reg_read(UC_ARM_REG_R1)])
    u.hook_add(UC_HOOK_CODE, record_call)
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _u, _access, a, s, v, _data:
               writes.append([a, s, v]) if a < 0x2007d000 else None)
    u.emu_start(0x53c31d if variant == "original" else 0x100001,
                0x100100, count=20000)
    return {"calls": calls, "writes": writes,
            "queue": bytes(u.mem_read(q, 0x200)).hex(),
            "timer": bytes(u.mem_read(timer, 44)).hex(),
            "timer_unchanged": bytes(u.mem_read(timer, 44)) == before_timer,
            "sp": u.reg_read(UC_ARM_REG_SP), "pc": u.reg_read(UC_ARM_REG_PC)}


cases = []
for mode, ipsr in (("null", 0), ("active", 0), ("inactive", 0),
                   ("active", 15)):
    a = run(mode, ipsr, "original")
    b = run(mode, ipsr, "compiled")
    assert a == b, (mode, ipsr, {key: (a[key], b[key]) for key in a if a[key] != b[key]})
    assert a["sp"] == 0x2007e000 and a["pc"] == 0x100100
    assert a["timer_unchanged"]
    if mode == "active" and ipsr == 0:
        assert [entry[0] for entry in a["calls"]] == ["0x4494d8", "0x47e7b0"]
        assert a["calls"][0][1] == 0x20006408
        assert a["calls"][1][1:3] == [0x20006408, 3]
    cases.append({"timer_mode": mode, "ipsr": ipsr,
                  "original": a, "compiled": b, "match": True})

report = {"cases": cases, "matched": len(cases), "total": len(cases),
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "scope": "real osTimerStop and queue initializer/producer with synthetic coherent active timer; no daemon command consumption, expiry or callback cancellation"}
Path(__file__).with_name("watchdog-stop-execution.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} original/source watchdog-stop comparisons pass")

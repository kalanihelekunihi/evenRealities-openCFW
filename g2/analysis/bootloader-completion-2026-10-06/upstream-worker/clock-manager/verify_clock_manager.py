#!/usr/bin/env python3
"""Differentially exercise the private clock request/release dispatchers."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                     UC_HOOK_CODE)
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BLOB = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BLOB_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
BASE = 0x410000
STOP = 0x08000000
USER_BITS = 0x20026e74
POWER_BASE = 0x40010000
POWER_AREA_SIZE = 0x404
POWER_HELPER = 0x41d92c
STOCK = {"request": 0x4222f0, "release": 0x422364}
STOCK_PROVIDERS = {
    (0, 0): 0x421a30, (0, 1): 0x421a94, (0, 2): 0x421bd2,
    (0, 3): 0x421b08, (0, 4): 0x421d5e, (0, 5): 0x421eba,
    (0, 6): 0x4220b2,
    (1, 0): 0x421a62, (1, 1): 0x421ad6, (1, 2): 0x421cce,
    (1, 3): 0x421b5c, (1, 4): 0x421e4a, (1, 5): 0x422040,
    (1, 6): 0x422220,
}

spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def status(operation, clock_id, user_id):
    return 0x100 + (operation << 7) + (clock_id << 4) + user_id


class Machine:
    def __init__(self, source=False, segments=(), symbols=None):
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.source = source
        self.finished = False
        self.events = []
        self.trace = {}
        self.cpu.mem_map(BASE, 0x25000)
        self.cpu.mem_write(BASE, BLOB.read_bytes())
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(POWER_BASE, 0x1000)
        self.cpu.mem_map(STOP, 0x10000)
        if source:
            self.cpu.mem_map(0x10000, 0x10000)
            for segment in segments:
                self.cpu.mem_write(segment["address"], segment["data"])
            self.symbols = symbols
            self.source_provider_entries = {
                symbols[f"opencfw_bl_clock_{'release' if op else 'request'}_id{clock_id}"] & ~1:
                (op, clock_id)
                for op in (0, 1) for clock_id in range(7)}
        else:
            self.symbols = {}
            self.provider_entry = None
        self.cpu.hook_add(UC_HOOK_CODE, self.code)

    def provider(self, operation, clock_id, user_id):
        operation &= 0xff
        clock_id &= 0xff
        user_id &= 0xff
        self.events.append([operation, clock_id, user_id])
        return status(operation, clock_id, user_id)

    def code(self, uc, pc, size, _):
        if pc == STOP:
            self.finished = True
            uc.emu_stop()
            return
        if self.source and pc in self.source_provider_entries:
            operation, clock_id = self.source_provider_entries[pc]
            if clock_id in (0, 1, 3):
                self.trace[pc] = bytes(uc.mem_read(pc, size))
                return
            user_id = uc.reg_read(a.UC_ARM_REG_R0)
            uc.reg_write(a.UC_ARM_REG_R0,
                         self.provider(operation, clock_id, user_id))
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if not self.source and pc in STOCK_PROVIDERS.values():
            reverse = {address: pair for pair, address in STOCK_PROVIDERS.items()}
            operation, clock_id = reverse[pc]
            if clock_id in (0, 1, 3):
                self.trace[pc] = bytes(uc.mem_read(pc, size))
                return
            user_id = uc.reg_read(a.UC_ARM_REG_R0)
            uc.reg_write(a.UC_ARM_REG_R0,
                         self.provider(operation, clock_id, user_id))
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if not self.source:
            self.trace[pc] = bytes(uc.mem_read(pc, size))

    def prepare(self, fixture):
        self.cpu.mem_write(USER_BITS, bytes(56))
        for clock_id, users in [(0, fixture.get("present_users", []))] + [
                (int(clock_id), users) for clock_id, users in
                fixture.get("present_by_class", {}).items()]:
            for user in users:
                offset = clock_id * 8 + (user >> 5) * 4
                old = int.from_bytes(self.cpu.mem_read(USER_BITS + offset, 4), "little")
                self.cpu.mem_write(USER_BITS + offset,
                                   (old | (1 << (user & 31))).to_bytes(4, "little"))
        self.cpu.mem_write(POWER_BASE, bytes(POWER_AREA_SIZE))
        self.cpu.reg_write(a.UC_ARM_REG_PRIMASK, fixture.get("primask", 0))
        self.cpu.mem_write(0x20000088,
                           int(fixture.get("class1_enabled", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x2000008c,
                           int(fixture.get("class3_enabled", 0)).to_bytes(4, "little"))

    def run(self, operation, clock_id, user_id, fixture=None):
        fixture = fixture or {}
        self.events = []
        self.trace = {}
        self.prepare(fixture)
        entry = ((self.symbols["clock_request"] if operation == 0 else
                  self.symbols["clock_release"]) if self.source else
                 STOCK["request" if operation == 0 else "release"])
        for register, value in zip(
                (a.UC_ARM_REG_R0, a.UC_ARM_REG_R1), (clock_id, user_id)):
            self.cpu.reg_write(register, value & 0xffffffff)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.finished = False
        self.cpu.emu_start(entry | 1, STOP + 2, count=10000)
        assert self.finished, (self.source, operation, clock_id, user_id,
                               hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return {"status": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "events": list(self.events),
                "primask": self.cpu.reg_read(a.UC_ARM_REG_PRIMASK),
                "user_bits": bytes(self.cpu.mem_read(USER_BITS, 56)).hex(),
                "power_area": bytes(self.cpu.mem_read(POWER_BASE,
                                                       POWER_AREA_SIZE)).hex()}

    def run_power_update(self, register_id, value, fixture=None):
        fixture = fixture or {}
        self.events = []
        self.trace = {}
        self.prepare(fixture)
        entry = (self.symbols["opencfw_bl_power_register_update"]
                 if self.source else POWER_HELPER)
        self.cpu.reg_write(a.UC_ARM_REG_R0, register_id & 0xffffffff)
        self.cpu.reg_write(a.UC_ARM_REG_R1, value & 0xffffffff)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.finished = False
        self.cpu.emu_start(entry | 1, STOP + 2, count=10000)
        assert self.finished, (self.source, register_id, value,
                               hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return {"status": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "primask": self.cpu.reg_read(a.UC_ARM_REG_PRIMASK),
                "power_area": bytes(self.cpu.mem_read(POWER_BASE,
                                                       POWER_AREA_SIZE)).hex()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert sha(BLOB) == BLOB_SHA
    _, segments, symbols = elf.elf_info(args.elf)
    cases = []
    trace = {}
    # Include valid/invalid boundaries, 8-bit aliases, and broad raw-register
    # values to prove explicit UXTb-equivalent argument truncation.
    inputs = [
        (0, 0), (1, 56), (2, 57), (3, 0x100), (4, 0x138),
        (5, 0x139), (6, 0xffffffff), (7, 0), (0x100, 0),
        (0x102, 0x1238), (0xff, 56), (0xffffff06, 0xffffff38),
        (0x101, 0x139), (0x107, 0x10000),
    ]
    for operation in (0, 1):
        for clock_id, user_id in inputs:
            stock, source = Machine(), Machine(True, segments, symbols)
            fixture = {"primask": 1 if user_id in (0x138, 0xffffff38) else 0}
            observed_stock = stock.run(operation, clock_id, user_id, fixture)
            observed_source = source.run(operation, clock_id, user_id, fixture)
            assert observed_stock == observed_source, {
                "operation": operation, "clock_id": clock_id,
                "user_id": user_id, "stock": observed_stock,
                "source": observed_source}
            cases.append({"operation": "request" if operation == 0 else "release",
                          "arguments": [clock_id, user_id],
                          "result": observed_stock})
            trace.update(stock.trace)

    # Exercise the recovered class-0 bit-set/bit-clear provider on each word
    # boundary, with both enabled and disabled PRIMASK and idempotent calls.
    for operation, user_id, present, primask in [
            (0, 0, [], 0), (0, 31, [], 1), (0, 32, [], 0),
            (0, 56, [56], 1), (1, 0, [], 0), (1, 31, [31], 1),
            (1, 32, [32], 0), (1, 56, [56], 1)]:
        fixture = {"present_users": present, "primask": primask}
        stock, source = Machine(), Machine(True, segments, symbols)
        observed_stock = stock.run(operation, 0, user_id, fixture)
        observed_source = source.run(operation, 0, user_id, fixture)
        assert observed_stock == observed_source, {
            "operation": operation, "clock_id": 0, "user_id": user_id,
            "fixture": fixture, "stock": observed_stock,
            "source": observed_source}
        cases.append({"operation": "request" if operation == 0 else "release",
                      "arguments": [0, user_id], "fixture": fixture,
                      "result": observed_stock})
        trace.update(stock.trace)

    # Class 1 is bookkeeping gated by the recovered global enable word.
    # Class 3 adds its exact register-15 writes around bit transitions.
    provider_cases = [
        (0, 1, 7, {"class1_enabled": 0, "primask": 0}),
        (0, 1, 7, {"class1_enabled": 1, "primask": 0}),
        (0, 1, 7, {"class1_enabled": 1, "primask": 1}),
        (0, 1, 7, {"class1_enabled": 1, "present_by_class": {1: [7]}, "primask": 1}),
        (1, 1, 7, {"present_by_class": {1: [7]}, "primask": 1}),
        (1, 1, 7, {"present_by_class": {1: [7, 8]}, "primask": 0}),
        (1, 1, 7, {"primask": 0}),
        (0, 3, 7, {"class3_enabled": 0, "primask": 0}),
        (0, 3, 7, {"class3_enabled": 1, "primask": 0}),
        (0, 3, 7, {"class3_enabled": 1, "primask": 1}),
        (0, 3, 7, {"class3_enabled": 1, "present_by_class": {3: [7]}, "primask": 1}),
        (1, 3, 7, {"present_by_class": {3: [7]}, "primask": 1}),
        (1, 3, 7, {"present_by_class": {3: [7, 8]}, "primask": 0}),
        (1, 3, 7, {"primask": 1}),
    ]
    for operation, clock_id, user_id, fixture in provider_cases:
        stock, source = Machine(), Machine(True, segments, symbols)
        observed_stock = stock.run(operation, clock_id, user_id, fixture)
        observed_source = source.run(operation, clock_id, user_id, fixture)
        assert observed_stock == observed_source, {
            "operation": operation, "clock_id": clock_id,
            "user_id": user_id, "fixture": fixture,
            "stock": observed_stock, "source": observed_source}
        cases.append({"operation": "request" if operation == 0 else "release",
                      "arguments": [clock_id, user_id], "fixture": fixture,
                      "result": observed_stock})
        trace.update(stock.trace)

    # Compare the lower 0x41d92c routine directly across legal, rejected, and
    # out-of-range requests, with all bus accesses confined to mapped SRAM.
    power_cases = [(15, 3), (15, 10), (0, 0), (0, 0x800),
                   (5, 0x2000), (5, 0x4000), (223, 0), (224, 0)]
    for register_id, value in power_cases:
        fixture = {"primask": (register_id + value) & 1}
        stock, source = Machine(), Machine(True, segments, symbols)
        observed_stock = stock.run_power_update(register_id, value, fixture)
        observed_source = source.run_power_update(register_id, value, fixture)
        assert observed_stock == observed_source, {
            "register_id": register_id, "value": value,
            "fixture": fixture, "stock": observed_stock,
            "source": observed_source}
        cases.append({"operation": "power_register_update",
                      "arguments": [register_id, value], "fixture": fixture,
                      "result": observed_stock})
        trace.update(stock.trace)

    used = {pc + i for pc, raw in trace.items() for i in range(len(raw))}
    image = BLOB.read_bytes()
    function_specs = {
        "request": (0x4222f0, 0x422364,
                    "53cfb358989e68ae979d2814964a3e779ae0f0eba76836f99d409393d0e78d51"),
        "release": (0x422364, 0x4223d8,
                    "6a131868a276083764d4714178857124ccb4209a5f3e7552d874aba7f7c1a54e"),
        "class1_request": (0x421a94, 0x421ad6,
                    "0b01e6b1f407cd164536ca7c894b0cb48dcf7c2497814eb3187860633f189a4c"),
        "class1_release": (0x421ad6, 0x421b08,
                    "9aea3a0a0c095098f5c43b3cb3b34fb1565983cda5769771928650d440ef58d5"),
        "class3_request": (0x421b08, 0x421b5c,
                    "891c88359e96db91d98fd0b159621ca6da87bc784c0e3280f4a625dcc1aad579"),
        "class3_release": (0x421b5c, 0x421ba4,
                    "0ec002b261917a95a5afe815494a62f850408c5de5b3a911e81fe3b1df23d06d"),
        "power_register_update": (0x41d92c, 0x41d9aa,
                    "69608d49656b5685af08e567db6cb31852e5ee8d50767fc393d8bf31c6f2c114"),
        "any_class_user": (0x4215ae, 0x4215dc,
                    "11a6cf814c1a66760a988880dac541c55419e26aa1f4c7ef2de27b9a0d7e019f"),
        "user_bit_query": (0x4215dc, 0x4215fe,
                    "8dc0a88874cc74f9148e7ae8b6e70f50b7cd1f732db5b74982a8abcccb1bd6f5"),
        "user_bit_update": (0x421632, 0x4216b2,
                    "bc7fc361719841b4cd3b48adad0bb774fe817371892b0a9cbe4e8744c5ec2a8e"),
        "critical_save": (0x41b8ec, 0x41b8f4,
                    "720733fcf19a5635fcab0791fcc2b007294712bb27536443ff79490821c168cf"),
    }
    stock_functions = {}
    for name, (start, end, digest) in function_specs.items():
        body = image[start - BASE:end - BASE]
        assert hashlib.sha256(body).hexdigest() == digest
        stock_functions[name] = {"range": [hex(start), hex(end)],
                                 "size": end - start, "sha256": digest}

    stock_data_specs = {
        "power_register_standard_mode_bits":
            (0x433460, 28, "b735c04032541cece197c93699f0753d37d7af5937bb6cdff15def90dbfe30fc"),
        "power_register_nonstandard_bits":
            (0x43347c, 28, "cc26c6f666de586a513054c9c0ccc99f0d76e213cd5f8a4638264390cb245804"),
        "class3_request_value":
            (0x43414c, 4, "9d9f290527a6be626a8f5985b26e19b237b44872b03631811df4416fc1713178"),
        "class3_release_value":
            (0x434150, 4, "9d9f290527a6be626a8f5985b26e19b237b44872b03631811df4416fc1713178"),
    }
    stock_data = {}
    for name, (address, size, digest) in stock_data_specs.items():
        data = image[address - BASE:address - BASE + size]
        assert len(data) == size and hashlib.sha256(data).hexdigest() == digest
        stock_data[name] = {"address": hex(address), "size": size,
                            "sha256": digest, "bytes": data.hex()}

    result = {
        "status": "PASS", "cases": len(cases),
        "original_instruction_bytes_reached": len(used),
        "original_image_sha256": BLOB_SHA,
        "source_elf_sha256": sha(args.elf),
        "stock_functions": stock_functions,
        "stock_data": stock_data,
        "source_sha256": {
            "clock_manager.c": sha(ROOT / "g2/components/bootloader/clock_manager/clock_manager.c"),
            "clock_manager.h": sha(ROOT / "g2/components/bootloader/clock_manager/clock_manager.h"),
            "clock_class_providers.c": sha(ROOT / "g2/components/bootloader/clock_manager/clock_class_providers.c"),
            "clock_class_providers.h": sha(ROOT / "g2/components/bootloader/clock_manager/clock_class_providers.h"),
            "provider_test_stubs.c": sha(HERE / "provider_test_stubs.c"),
        },
        "trace": {hex(pc): raw.hex() for pc, raw in sorted(trace.items())},
        "comparisons": cases,
        "provider_entry_points_intercepted": {
            f"{'release' if op else 'request'}_{clock_id}": hex(address)
            for (op, clock_id), address in STOCK_PROVIDERS.items()
            if clock_id in (2, 4, 5, 6)},
        "limits": [
            "Classes 0, 1, and 3 with the direct power-register helper execute as stock and source code; providers for classes 2 and 4 through 6 are intercepted at their stock entry points.",
            "The seven-row user bitmap address 0x20026e74 and its 8-byte row geometry are recovered from stock literal 0x00422210; classes 0, 1, and 3 use one bit per user rather than request counts.",
            "No MMIO, concurrency, clock stability, interrupt timing, or hardware behavior is modeled.",
            "C dispatcher source is linkable only when class providers 2, 4, 5, and 6 are supplied; classes 0, 1, and 3 are reconstructed here.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in
                      ("status", "cases", "original_instruction_bytes_reached")}))


if __name__ == "__main__":
    main()

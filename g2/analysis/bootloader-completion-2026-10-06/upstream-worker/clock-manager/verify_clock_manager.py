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
HFADJ_BASE = 0x40004000
DELAY_MODE_REGISTER = 0x40021000
CLOCK4_BUSY = 0x2002719c
CLOCK4_CALLBACK_POINTER = 0x20027044
CLOCK2_BUSY = 0x2002719b
CLOCK2_CALLBACK_POINTER = 0x20027040
CLOCK5_BUSY = 0x2002719d
CLOCK5_CALLBACK_POINTER = 0x20027048
RADIO_MODE_REGISTER = 0x4002012c
RADIO_CONFIG_REGISTER = 0x40020128
RADIO_BASE_REGISTER = 0x40020120
STOCK_RADIO_MODE_APPLY = 0x41d3e4
STOCK_DELAY_US = 0x41d1c0
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
        self.delay_cycles = []
        self.delay_calls = 0
        self.delay_clear_after = 0
        self.cpu.mem_map(0, 0x1000)
        self.cpu.mem_map(BASE, 0x25000)
        self.cpu.mem_write(BASE, BLOB.read_bytes())
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(HFADJ_BASE, 0x1000)
        self.cpu.mem_map(POWER_BASE, 0x1000)
        self.cpu.mem_map(0x40020000, 0x1000)
        self.cpu.mem_map(0x40008000, 0x1000)
        self.cpu.mem_map(0xc0007000, 0x1000)
        self.cpu.mem_map(0x0fff8000, 0x1000)
        self.cpu.mem_map(DELAY_MODE_REGISTER, 0x1000)
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
        if pc == 0x40:
            self.delay_cycles.append(uc.reg_read(a.UC_ARM_REG_R0))
            self.delay_calls += 1
            if (self.delay_clear_after and
                    self.delay_calls >= self.delay_clear_after and
                    (uc.mem_read(CLOCK4_BUSY, 1) != b"\0" or
                     uc.mem_read(CLOCK2_BUSY, 1) != b"\0" or
                     uc.mem_read(CLOCK5_BUSY, 1) != b"\0")):
                uc.mem_write(CLOCK4_BUSY, b"\0")
                uc.mem_write(CLOCK2_BUSY, b"\0")
                uc.mem_write(CLOCK5_BUSY, b"\0")
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if self.source and pc in self.source_provider_entries:
            operation, clock_id = self.source_provider_entries[pc]
            if clock_id in (0, 1, 2, 3, 4, 5, 6):
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
            if clock_id in (0, 1, 2, 3, 4, 5, 6):
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
        self.cpu.mem_write(HFADJ_BASE, bytes(0x100))
        self.cpu.mem_write(DELAY_MODE_REGISTER,
                           int(fixture.get("delay_clock_mode", 0)).to_bytes(4, "little"))
        self.cpu.reg_write(a.UC_ARM_REG_PRIMASK, fixture.get("primask", 0))
        self.cpu.mem_write(0x20000088,
                           int(fixture.get("class1_enabled", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x2000008c,
                           int(fixture.get("class3_enabled", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(CLOCK4_BUSY,
                           bytes([int(fixture.get("class4_busy", 0)) & 0xff]))
        timeout_address = fixture.get("callback_timeout_address", 0x20025000)
        self.cpu.mem_write(CLOCK4_CALLBACK_POINTER,
                           int(timeout_address if fixture.get("class4_busy", 0) else 0).to_bytes(4, "little"))
        self.cpu.mem_write(timeout_address,
                           int(fixture.get("callback_timeout", 10)).to_bytes(4, "little"))
        self.cpu.mem_write(0x20000550,
                           bytes([int(fixture.get("class4_request_allowed", 0)) & 0xff]))
        self.cpu.mem_write(0x20027030,
                           int(fixture.get("class4_config_present", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x20026fec,
                           int(fixture.get("class4_config_value", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x2002719e,
                           bytes([int(fixture.get("class4_deferred_flag", 0)) & 0xff]))
        self.cpu.mem_write(0x40004044,
                           int(fixture.get("hfadj_enable_word", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x40004020,
                           int(fixture.get("hfadj_config_word", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x20000551,
                           bytes([int(fixture.get("class5_feature_enabled", 0)) & 0xff]))
        self.cpu.mem_write(0x20027034,
                           int(fixture.get("class5_config_present", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(CLOCK5_BUSY,
                           bytes([int(fixture.get("class5_busy", 0)) & 0xff]))
        timeout_address = fixture.get("class5_callback_timeout_address", 0x20025008)
        self.cpu.mem_write(CLOCK5_CALLBACK_POINTER,
                           int(timeout_address if fixture.get("class5_busy", 0) else 0).to_bytes(4, "little"))
        self.cpu.mem_write(timeout_address,
                           int(fixture.get("class5_callback_timeout", 10)).to_bytes(4, "little"))
        self.cpu.mem_write(0x2002719f,
                           bytes([int(fixture.get("class5_initialize_flag", 0)) & 0xff]))
        config_bytes = bytes(fixture.get("class5_config", [1, 2, 0, 0, 5, 0, 0, 0]))
        assert len(config_bytes) == 8
        self.cpu.mem_write(0x20026ff8, config_bytes)
        self.cpu.mem_write(0x40004030,
                           int(fixture.get("dual_switch_status", 0x01000000)).to_bytes(4, "little"))
        self.cpu.mem_write(0x40004044,
                           int(fixture.get("dual_switch_register",
                                           fixture.get("hfadj_enable_word", 0))).to_bytes(4, "little"))
        self.cpu.mem_write(0x40004048,
                           int(fixture.get("clkgen_divider", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x4000404c,
                           int(fixture.get("clkgen_enable", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x40004050,
                           int(fixture.get("clkgen_value", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x2002719a,
                           bytes([int(fixture.get("class6_feature_enabled", 0)) & 0xff]))
        self.cpu.mem_write(0x200271a0,
                           bytes([int(fixture.get("class6_initialize_flag", 0)) & 0xff]))
        self.cpu.mem_write(0x2002703c,
                           int(fixture.get("syspll_handle", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x20027010,
                           int(fixture.get("syspll_context_flags", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x20027014,
                           int(fixture.get("syspll_context_word1", 0)).to_bytes(4, "little"))
        pll_config = bytes(fixture.get("class6_config",
                                       [0, 1, 1, 12, 2, 1, 10, 0, 3, 0, 0, 0]))
        assert len(pll_config) == 12
        self.cpu.mem_write(0x20027004, pll_config)
        self.cpu.mem_write(0x4002000c,
                           int(fixture.get("syspll_revision", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x40020060,
                           int(fixture.get("syspll_ready_flags", 0x000f0000)).to_bytes(4, "little"))
        self.cpu.mem_write(0x400204d8,
                           int(fixture.get("syspll_control0", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x400204dc,
                           int(fixture.get("syspll_control1", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x400204e0,
                           int(fixture.get("syspll_control2", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x400204e4,
                           int(fixture.get("syspll_lock_status", 1)).to_bytes(4, "little"))
        self.cpu.mem_write(0x40008858,
                           int(fixture.get("syspll_ref_config", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x400201b0,
                           int(fixture.get("syspll_isolation", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x20000080,
                           int(fixture.get("class2_enabled", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0x2000007c,
                           int(fixture.get("class2_mode_selector", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(CLOCK2_BUSY,
                           bytes([int(fixture.get("class2_busy", 0)) & 0xff]))
        timeout_address = fixture.get("class2_callback_timeout_address", 0x20025004)
        self.cpu.mem_write(CLOCK2_CALLBACK_POINTER,
                           int(timeout_address if fixture.get("class2_busy", 0) else 0).to_bytes(4, "little"))
        self.cpu.mem_write(timeout_address,
                           int(fixture.get("class2_callback_timeout", 10)).to_bytes(4, "little"))
        self.cpu.mem_write(RADIO_MODE_REGISTER,
                           int(fixture.get("radio_mode_word", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(RADIO_BASE_REGISTER,
                           int(fixture.get("radio_base_word", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(RADIO_CONFIG_REGISTER,
                           int(fixture.get("radio_config_word", 0)).to_bytes(4, "little"))
        self.cpu.mem_write(0xc0007000,
                           int(fixture.get("radio_config_mask", 0xffffffff)).to_bytes(4, "little"))
        self.cpu.mem_write(0x20000090,
                           int(fixture.get("radio_config_low", 0x2d)).to_bytes(4, "little"))
        self.cpu.mem_write(0x20000094,
                           int(fixture.get("radio_config_high", 7)).to_bytes(4, "little"))
        self.cpu.mem_write(0x0fff8c00,
                           int(fixture.get("radio_config_fixed", 0x005b0000)).to_bytes(4, "little"))

    def run(self, operation, clock_id, user_id, fixture=None):
        fixture = fixture or {}
        self.events = []
        self.trace = {}
        self.delay_cycles = []
        self.delay_calls = 0
        self.delay_clear_after = fixture.get("delay_clear_after", 0)
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
        self.cpu.emu_start(entry | 1, STOP + 2, count=300000)
        assert self.finished, (self.source, operation, clock_id, user_id,
                               hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return {"status": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "events": list(self.events),
                "primask": self.cpu.reg_read(a.UC_ARM_REG_PRIMASK),
                "user_bits": bytes(self.cpu.mem_read(USER_BITS, 56)).hex(),
                "power_area": bytes(self.cpu.mem_read(POWER_BASE,
                                                       POWER_AREA_SIZE)).hex(),
                "hfadj": bytes(self.cpu.mem_read(0x40004020, 4)).hex() +
                         bytes(self.cpu.mem_read(0x40004044, 4)).hex(),
                "radio_mode": bytes(self.cpu.mem_read(RADIO_MODE_REGISTER, 4)).hex(),
                "radio_config": bytes(self.cpu.mem_read(RADIO_CONFIG_REGISTER, 4)).hex(),
                "class2_busy": bytes(self.cpu.mem_read(CLOCK2_BUSY, 1)).hex(),
                "class2_callback_pointer": bytes(self.cpu.mem_read(CLOCK2_CALLBACK_POINTER, 4)).hex(),
                "class5_busy": bytes(self.cpu.mem_read(CLOCK5_BUSY, 1)).hex(),
                "class5_callback_pointer": bytes(self.cpu.mem_read(CLOCK5_CALLBACK_POINTER, 4)).hex(),
                "class5_control": bytes(self.cpu.mem_read(0x2002719f, 1)).hex(),
                "dual_switch": bytes(self.cpu.mem_read(0x40004044, 4)).hex(),
                "clkgen": bytes(self.cpu.mem_read(0x40004048, 4)).hex() +
                          bytes(self.cpu.mem_read(0x4000404c, 4)).hex() +
                          bytes(self.cpu.mem_read(0x40004050, 4)).hex(),
                "class6_control": bytes(self.cpu.mem_read(0x200271a0, 1)).hex() +
                                  bytes(self.cpu.mem_read(0x2002703c, 4)).hex() +
                                  bytes(self.cpu.mem_read(0x20027010, 8)).hex(),
                "syspll": bytes(self.cpu.mem_read(0x400204d8, 4)).hex() +
                          bytes(self.cpu.mem_read(0x400204dc, 4)).hex() +
                          bytes(self.cpu.mem_read(0x400204e0, 4)).hex() +
                          bytes(self.cpu.mem_read(0x400204e4, 4)).hex() +
                          bytes(self.cpu.mem_read(0x40008858, 4)).hex() +
                          bytes(self.cpu.mem_read(0x400201b0, 4)).hex(),
                "delay_cycles": list(self.delay_cycles)}

    def run_radio_mode_apply(self, mode, value, arg3, value_seed, fixture=None):
        fixture = fixture or {}
        self.events = []
        self.trace = {}
        self.delay_cycles = []
        self.delay_calls = 0
        self.delay_clear_after = fixture.get("delay_clear_after", 0)
        self.prepare(fixture)
        value_address = 0x20025020
        if value is None:
            value_pointer = 0
        else:
            if isinstance(value, int):
                value_data = value.to_bytes(4, "little")
            else:
                value_data = bytes(value)
            self.cpu.mem_write(value_address, value_data)
            value_pointer = value_address
        entry = (self.symbols["opencfw_bl_radio_mode_apply"] if self.source
                 else STOCK_RADIO_MODE_APPLY)
        for register, raw in zip((a.UC_ARM_REG_R0, a.UC_ARM_REG_R1,
                                  a.UC_ARM_REG_R2, a.UC_ARM_REG_R3),
                                 (mode, value_pointer, arg3, value_seed)):
            self.cpu.reg_write(register, raw & 0xffffffff)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.finished = False
        self.cpu.emu_start(entry | 1, STOP + 2, count=300000)
        assert self.finished, (self.source, mode,
                               hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return {"status": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "value": self.cpu.reg_read(a.UC_ARM_REG_R1),
                "events": list(self.events),
                "primask": self.cpu.reg_read(a.UC_ARM_REG_PRIMASK),
                "user_bits": bytes(self.cpu.mem_read(USER_BITS, 56)).hex(),
                "base": bytes(self.cpu.mem_read(RADIO_BASE_REGISTER, 4)).hex(),
                "radio_mode": bytes(self.cpu.mem_read(RADIO_MODE_REGISTER, 4)).hex(),
                "radio_config": bytes(self.cpu.mem_read(RADIO_CONFIG_REGISTER, 4)).hex(),
                "delay_cycles": list(self.delay_cycles)}

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

    def run_delay_us(self, microseconds, mode):
        self.events = []
        self.trace = {}
        self.delay_cycles = []
        self.delay_calls = 0
        self.delay_clear_after = 0
        self.prepare({"delay_clock_mode": mode})
        entry = (self.symbols["opencfw_bl_delay_us"] if self.source else
                 STOCK_DELAY_US)
        self.cpu.reg_write(a.UC_ARM_REG_R0, microseconds & 0xffffffff)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.finished = False
        self.cpu.emu_start(entry | 1, STOP + 2, count=10000)
        assert self.finished, (self.source, microseconds, mode,
                               hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return {"delay_cycles": list(self.delay_cycles)}


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
        (0, 4, 7, {"class4_request_allowed": 0, "primask": 0}),
        (0, 4, 7, {"class4_request_allowed": 1, "primask": 0}),
        (0, 4, 7, {"class4_request_allowed": 1, "class4_config_present": 1,
                   "class4_config_value": 0x20, "delay_clear_after": 2,
                   "primask": 1}),
        (0, 4, 7, {"class4_request_allowed": 1,
                   "present_by_class": {4: [8]}, "primask": 0}),
        (0, 4, 7, {"class4_request_allowed": 1, "class4_config_present": 1,
                   "class4_config_value": 0x30, "class4_deferred_flag": 1,
                   "primask": 1}),
        (0, 4, 7, {"class4_busy": 1, "present_by_class": {4: [7]},
                   "callback_timeout": 3, "delay_clear_after": 2,
                   "primask": 0}),
        (1, 4, 7, {"present_by_class": {4: [7]},
                   "hfadj_enable_word": 0xa0, "primask": 1}),
        (1, 4, 7, {"present_by_class": {4: [7, 8]},
                   "hfadj_enable_word": 0xa0, "primask": 0}),
        (1, 4, 7, {"hfadj_enable_word": 0xa0, "primask": 1}),
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

    # Class 2 coordinates a two-state radio mode, its register writes, a
    # callback timeout slot, and the per-user bitmap. Exercise the enabled,
    # conflict, mode-2, mode-3, existing-user, and last-release paths.
    class2_cases = [
        (0, 7, {"class2_enabled": 0, "primask": 1}),
        (0, 7, {"class2_enabled": 1, "class2_mode_selector": 0,
               "radio_mode_word": 0, "delay_clear_after": 2, "primask": 1}),
        (0, 7, {"class2_enabled": 1, "class2_mode_selector": 1,
               "radio_mode_word": 0, "primask": 0}),
        (0, 7, {"class2_enabled": 1, "class2_mode_selector": 0,
               "radio_mode_word": 1 << 8, "primask": 1}),
        (0, 7, {"class2_enabled": 1, "class2_mode_selector": 1,
               "radio_mode_word": 1, "primask": 0}),
        (0, 7, {"class2_enabled": 1, "class2_mode_selector": 0,
               "radio_mode_word": 1, "primask": 1}),
        (0, 7, {"class2_enabled": 1, "present_by_class": {2: [7]},
               "class2_busy": 1, "class2_callback_timeout": 3,
               "delay_clear_after": 2, "primask": 0}),
        (1, 7, {"present_by_class": {2: [7, 8]}, "radio_mode_word": 1,
               "primask": 1}),
        (1, 7, {"present_by_class": {2: [7]}, "radio_mode_word": 1,
               "primask": 0}),
        (1, 7, {"primask": 1}),
    ]
    for operation, user_id, fixture in class2_cases:
        stock, source = Machine(), Machine(True, segments, symbols)
        observed_stock = stock.run(operation, 2, user_id, fixture)
        observed_source = source.run(operation, 2, user_id, fixture)
        assert observed_stock == observed_source, {
            "operation": operation, "clock_id": 2, "user_id": user_id,
            "fixture": fixture, "stock": observed_stock,
            "source": observed_source}
        cases.append({"operation": "request" if operation == 0 else "release",
                      "arguments": [2, user_id], "fixture": fixture,
                      "result": observed_stock})
        trace.update(stock.trace)

    # Exercise every selector in the shared stock mode helper through its
    # direct four-register ABI, including the 64-bit R0/R1 return and nested
    # class-2 request/release paths used only by selectors 5 and 6.
    radio_mode_cases = [
        (0, None, 0, 0, {"radio_base_word": 0xa5a5a5ff}),
        (0, 1, 0, 0, {"radio_base_word": 0xa5a5a5ff}),
        (1, None, 0, 0, {"radio_base_word": 0x1234567f}),
        (2, None, 0, 0, {"delay_clear_after": 1}),
        (2, 1, 0, 0, {"delay_clear_after": 1}),
        (3, None, 0, 0, {}),
        (3, 1, 0, 0, {}),
        (4, None, 0, 0, {}),
        (5, None, 0, 0, {"class2_enabled": 1, "class2_mode_selector": 0,
                         "radio_mode_word": 1, "delay_clear_after": 1}),
        (5, 0, 0, 0x10203040,
         {"class2_enabled": 1, "class2_mode_selector": 0,
          "radio_mode_word": 1, "delay_clear_after": 1}),
        (5, 3, 0, 0, {"class2_enabled": 1, "class2_mode_selector": 0,
                      "radio_mode_word": 1, "delay_clear_after": 1}),
        (5, 1, 0, 0, {"class2_enabled": 1, "class2_mode_selector": 0,
                      "radio_mode_word": 1, "delay_clear_after": 1}),
        (5, 2, 0, 0x55667788,
         {"class2_enabled": 1, "class2_mode_selector": 0,
          "radio_mode_word": 1, "delay_clear_after": 1}),
        (5, 7, 0, 0,
         {"class2_enabled": 1, "class2_mode_selector": 0,
          "radio_mode_word": 1, "delay_clear_after": 1}),
        (5, 8, 0, 0, {"class2_enabled": 1, "class2_mode_selector": 0,
                      "radio_mode_word": 1, "delay_clear_after": 1}),
        (5, 3, 0, 0xaabbccdd, {"class2_enabled": 0}),
        (6, None, 0, 0xfeedbeef,
         {"present_by_class": {2: [52]}, "radio_mode_word": 0x103}),
        (6, None, 0, 0x12345678, {}),
        (7, None, 0, 0x87654321, {}),
    ]
    for mode, value, arg3, value_seed, fixture in radio_mode_cases:
        stock, source = Machine(), Machine(True, segments, symbols)
        observed_stock = stock.run_radio_mode_apply(
            mode, value, arg3, value_seed, fixture)
        observed_source = source.run_radio_mode_apply(
            mode, value, arg3, value_seed, fixture)
        assert observed_stock == observed_source, {
            "operation": "radio_mode_apply", "mode": mode, "value": value,
            "fixture": fixture, "stock": observed_stock,
            "source": observed_source}
        cases.append({"operation": "radio_mode_apply",
                      "arguments": [mode, value, arg3, value_seed],
                      "fixture": fixture, "result": observed_stock})
        trace.update(stock.trace)

    # Class 5 owns generator enable/config state and nests an auxiliary class
    # 2 or 3 clock request for user 0x36. Readiness polling and callback drain
    # are synthetic and are compared against the exact stock call graph.
    class5_cases = [
        (0, 7, {"class5_feature_enabled": 0, "primask": 1}),
        (0, 7, {"class5_feature_enabled": 1, "class5_config_present": 0,
               "primask": 0}),
        (0, 7, {"class5_feature_enabled": 1, "class5_config_present": 1,
               "class3_enabled": 1, "class5_config": [1, 2, 0, 0, 5, 0, 0, 0],
               "dual_switch_status": 0x01000000, "delay_clear_after": 2,
               "primask": 1}),
        (0, 7, {"class5_feature_enabled": 1, "class5_config_present": 1,
               "class3_enabled": 1, "class5_config": [1, 2, 0, 0, 5, 0, 0, 0],
               "dual_switch_status": 0, "delay_clear_after": 103,
               "primask": 0}),
        (0, 7, {"class5_feature_enabled": 1, "class5_config_present": 1,
               "class3_enabled": 0, "class5_config": [1, 2, 0, 0, 5, 0, 0, 0],
               "primask": 0}),
        (0, 7, {"class5_feature_enabled": 1, "class5_config_present": 1,
               "class2_enabled": 1, "class2_mode_selector": 0,
               "class5_config": [0, 2, 0, 0, 5, 0, 0, 0],
               "delay_clear_after": 2, "primask": 1}),
        (0, 7, {"class5_feature_enabled": 1, "class5_config_present": 1,
               "present_by_class": {5: [7]}, "class5_busy": 1,
               "class5_callback_timeout": 3, "delay_clear_after": 2,
               "primask": 0}),
        (0, 8, {"class5_feature_enabled": 1, "class5_config_present": 1,
               "class3_enabled": 1, "class5_config": [0, 3, 0, 0,
                                                           255, 255, 255, 31],
               "dual_switch_status": 0x01000000, "primask": 1}),
        (0, 9, {"class5_feature_enabled": 1, "class5_config_present": 1,
               "present_by_class": {5: [9]}, "class5_busy": 1,
               "class5_callback_timeout": 0, "primask": 0}),
        (1, 7, {"present_by_class": {5: [7, 8]},
               "class5_config_present": 1, "primask": 1}),
        (1, 7, {"present_by_class": {3: [54], 5: [7]},
               "class5_config_present": 1,
               "class5_config": [1, 2, 0, 0, 5, 0, 0, 0],
               "class5_busy": 1, "dual_switch_register": 0x20,
               "clkgen_divider": 0x80000003, "clkgen_value": 0x1234,
               "primask": 0}),
        (1, 7, {"primask": 1}),
    ]
    for operation, user_id, fixture in class5_cases:
        fixture = dict(fixture)
        stock, source = Machine(), Machine(True, segments, symbols)
        observed_stock = stock.run(operation, 5, user_id, fixture)
        observed_source = source.run(operation, 5, user_id, fixture)
        assert observed_stock == observed_source, {
            "operation": operation, "clock_id": 5, "user_id": user_id,
            "fixture": fixture, "stock": observed_stock,
            "source": observed_source}
        cases.append({"operation": "request" if operation == 0 else "release",
                      "arguments": [5, user_id], "fixture": fixture,
                      "result": observed_stock})
        trace.update(stock.trace)

    # Class 6 initializes, configures, enables, and polls the private PLL
    # handle. Its requested class-2/3 dependencies run as source and stock;
    # PLL status/lock registers remain synthetic.
    class6_cases = [
        (0, 7, {"class6_feature_enabled": 0, "primask": 1}),
        (0, 7, {"class6_feature_enabled": 1, "class2_enabled": 1,
               "class2_mode_selector": 0, "class3_enabled": 1,
               "delay_clear_after": 2, "primask": 0}),
        (0, 7, {"class6_feature_enabled": 1, "class2_enabled": 1,
               "class2_mode_selector": 0, "class3_enabled": 1,
               "class6_config": [1, 1, 1, 20, 3, 2, 10, 0, 3, 0, 0, 0],
               "delay_clear_after": 2, "primask": 1}),
        (0, 8, {"class6_feature_enabled": 1, "class2_enabled": 1,
               "class2_mode_selector": 0, "class3_enabled": 1,
               "class6_config": [1, 1, 1, 20, 8, 1, 10, 0, 3, 0, 0, 0],
               "delay_clear_after": 1, "primask": 0}),
        (0, 9, {"class6_feature_enabled": 1, "class2_enabled": 1,
               "class2_mode_selector": 0, "class3_enabled": 1,
               "class6_config": [1, 1, 1, 20, 3, 8, 10, 0, 3, 0, 0, 0],
               "delay_clear_after": 1, "primask": 1}),
        (0, 10, {"class6_feature_enabled": 1, "class2_enabled": 1,
                "class2_mode_selector": 0, "class3_enabled": 1,
                "class6_config": [1, 1, 1, 20, 3, 4, 10, 0, 3, 0, 0, 0],
                "delay_clear_after": 1, "primask": 0}),
        (0, 11, {"class6_feature_enabled": 1, "class2_enabled": 1,
                "class2_mode_selector": 0, "class3_enabled": 1,
                "class6_config": [1, 1, 1, 20, 3, 2, 10, 0, 3, 0, 0, 0],
                "syspll_revision": 0x22, "delay_clear_after": 1,
                "primask": 1}),
        (0, 7, {"class6_feature_enabled": 1, "class2_enabled": 1,
               "class2_mode_selector": 0, "class3_enabled": 1,
               "class6_config": [0, 1, 1, 64, 2, 1, 10, 0, 3, 0, 0, 0],
               "delay_clear_after": 2, "primask": 0}),
        (0, 7, {"class6_feature_enabled": 1, "class2_enabled": 1,
               "class2_mode_selector": 0, "class3_enabled": 1,
               "syspll_ready_flags": 0, "delay_clear_after": 2,
               "primask": 1}),
        (0, 7, {"class6_feature_enabled": 1, "class2_enabled": 1,
               "class2_mode_selector": 0, "class3_enabled": 1,
               "syspll_lock_status": 0, "delay_clear_after": 2,
               "primask": 0}),
        (0, 7, {"class6_feature_enabled": 1, "class2_enabled": 1,
               "class2_mode_selector": 0, "class3_enabled": 1,
               "present_by_class": {6: [7]}, "primask": 1}),
        (1, 7, {"present_by_class": {6: [7, 8]},
               "primask": 0}),
        (1, 7, {"present_by_class": {2: [53], 6: [7]},
               "syspll_handle": 0x20027010,
               "syspll_context_flags": 0x03504c30,
               "syspll_control0": 0, "class6_config": [0, 1, 1, 12, 2, 1, 10, 0, 3, 0, 0, 0],
               "primask": 1}),
        (1, 7, {"present_by_class": {6: [7]}, "primask": 1}),
    ]
    for operation, user_id, fixture in class6_cases:
        stock, source = Machine(), Machine(True, segments, symbols)
        observed_stock = stock.run(operation, 6, user_id, fixture)
        observed_source = source.run(operation, 6, user_id, fixture)
        assert observed_stock == observed_source, {
            "operation": operation, "clock_id": 6, "user_id": user_id,
            "fixture": fixture, "stock": observed_stock,
            "source": observed_source}
        cases.append({"operation": "request" if operation == 0 else "release",
                      "arguments": [6, user_id], "fixture": fixture,
                      "result": observed_stock})
        trace.update(stock.trace)

    # Run the recovered delay conversion directly in both CPU and clock modes.
    for microseconds, mode in [(0, 0), (1, 0), (10, 0), (1, 0x10),
                               (10, 0x10), (1000, 0)]:
        stock, source = Machine(), Machine(True, segments, symbols)
        observed_stock = stock.run_delay_us(microseconds, mode)
        observed_source = source.run_delay_us(microseconds, mode)
        assert observed_stock == observed_source, {
            "microseconds": microseconds, "mode": mode,
            "stock": observed_stock, "source": observed_source}
        cases.append({"operation": "delay_us",
                      "arguments": [microseconds, mode],
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
        "class2_request": (0x421bd2, 0x421cce,
                    "beaa4d231ad6eca158c9b2aac09a55b69258e213980ac1ce2cd704a33d1344f5"),
        "class2_release": (0x421cce, 0x421d28,
                    "3dac14d8bed9201a8c8e9147d2216bb399ccb35b33642840d4ad49ad3a691c6e"),
        "class5_request": (0x421eba, 0x422040,
                    "5d5e8bce49145dfddb318e0aff9baf61150e00e95f6fc7c804fde126dd11f68c"),
        "class5_release": (0x422040, 0x4220b2,
                    "fa335e0a8bf71ef86975470840768672bd90ad0eaac982abfc68e8c84de0bd17"),
        "class5_callback_finish": (0x421e8c, 0x421eba,
                    "113121d1847a984448cf18c516a0fbab330809872367ea03a787d3ba61b95985"),
        "class6_request": (0x4220b2, 0x42220e,
                    "701cc62514c5618aece1f206044e7815375082c6e4a9afa4eafd0e331f331e96"),
        "class6_release": (0x422220, 0x42228e,
                    "f26f053665f5477df6aa97d2e596f08b7045112332919102a5b1dd72d219ea36"),
        "radio_mode_sample": (0x41d676, 0x41d68c,
                    "99d5d0ab5ea09e8dd0364a2598e84f2e5be0036f16363430412566d7374359f1"),
        "radio_mode_apply": (0x41d3e4, 0x41d43c,
                    "83045d8e1a536eac5c198d6779d9e4a542e3ac151100ce2d372f1d44122c2aa1"),
        "radio_callback_finish": (0x421ba4, 0x421bd2,
                    "7bce9267762f0c94865d13a566fd4c0476bf127b1f1781e659016de79124461b"),
        "delay_us_status_check": (0x41d246, 0x41d28a,
                    "c6bf044dbb8f4a358cc93e10eff0b2ec7065b47f8ff08cde9f912d749fd42ef9"),
        "dual_switch": (0x426c8c, 0x426ccc,
                    "d5d433be0f71af7fbc03305660d1bc32acda58b54d51bbbdde573bdc2437c041"),
        "clkgen_config": (0x426ccc, 0x426d1e,
                    "c9ec02c292145c709613ed59045b804cbe0e697d86c83ed579bd2e3075a49b62"),
        "clkgen_disable": (0x426d1e, 0x426d2c,
                    "b6e29296fa925d2ee116e96d5fa22e60265cdccedfe9072766a7adf69042a70e"),
        "syspll_initialize": (0x4272ac, 0x427308,
                    "3284295a51640dd35e9518837d69df3369ff537705ef07e88586fb2a0f8a1414"),
        "syspll_deinitialize": (0x427310, 0x427360,
                    "1eba50a003fd2dbc10b692f916c95ac832659ee8245f1420e20cf06373631424"),
        "syspll_enable": (0x427360, 0x4273dc,
                    "0d2de1918fa403072986f15453ed612b3afd5383b89bdd95e8bf599ddb454280"),
        "syspll_disable": (0x4273dc, 0x42740c,
                    "18fb22183427c03dff67cd845829f31b77a1cf974c0c91eda17e83308934dc73"),
        "syspll_configure": (0x42740c, 0x427522,
                    "61aad9e2393f589de90e10cd74396e589ee4aa1547947732738abb105a1ba2af"),
        "syspll_lock_wait": (0x427522, 0x427588,
                    "978d2a48a7b3971bfb7e0d4f2006836aeacb4c137467dfead90d41377316be3e"),
        "syspll_power_initialize": (0x41ca5c, 0x41caa2,
                    "4e78ebc35ec7a632b5cb26969044d5f81ea3942b2b369bf62d62e0f2d078aaf9"),
        "syspll_power_restore": (0x41caa2, 0x41cae2,
                    "e0488df348358b7e2b372e1c2f9ef533baaa134c5f49738f63a65dde00e56c7e"),
        "syspll_power_down": (0x41cae8, 0x41caf8,
                    "94bc003904f7d8f5f3c6d8724cfe7fd61cd5f6009bc56af0400f70caf746a1dc"),
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
        "class4_request": (0x421d5e, 0x421e4a,
                    "680cf0628b0c3ed785836da7faeb3fcecf7ab51a02c90ed91c2c5b18442ef899"),
        "class4_release": (0x421e4a, 0x421e8c,
                    "f4f21abad8199cfea2524c7335d809b7f624100c1e34b693c08025ae1fb40a2a"),
        "class4_callback_finish": (0x421d28, 0x421d5e,
                    "4b8c76a46e4a846d4c3320718698134d79310d3b4c6a4dc3cb5b0602ab00ba20"),
        "callback_wait_loop": (0x4216b2, 0x4216d4,
                    "eb69fa2933ef30723f342fbc330927d681c6ca5d2ac077b77bf5e7ed1689a795"),
        "delay_us": (0x41d1c0, 0x41d210,
                    "c336d5c93475c6521bab00509a8ad8aaa1078b3bdc313ae43107777520af1895"),
        "hfadj_enable": (0x426c58, 0x426c72,
                    "92fca357b06260aa313efd81bb3c38360a6730eab3b08ae30034113f558e4036"),
        "hfadj_configure": (0x426c72, 0x426c7e,
                    "2d973a6679b7557ee0db61ece3b5e87083256d7f60d653509001616459a23d5f"),
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
            "clock_class_provider4.c": sha(ROOT / "g2/components/bootloader/clock_manager/clock_class_provider4.c"),
            "clock_class_provider4.h": sha(ROOT / "g2/components/bootloader/clock_manager/clock_class_provider4.h"),
            "clock_class_provider2.c": sha(ROOT / "g2/components/bootloader/clock_manager/clock_class_provider2.c"),
            "clock_class_provider2.h": sha(ROOT / "g2/components/bootloader/clock_manager/clock_class_provider2.h"),
            "clock_class_provider5.c": sha(ROOT / "g2/components/bootloader/clock_manager/clock_class_provider5.c"),
            "clock_class_provider5.h": sha(ROOT / "g2/components/bootloader/clock_manager/clock_class_provider5.h"),
            "clock_class_provider6.c": sha(ROOT / "g2/components/bootloader/clock_manager/clock_class_provider6.c"),
            "clock_class_provider6.h": sha(ROOT / "g2/components/bootloader/clock_manager/clock_class_provider6.h"),
        },
        "trace": {hex(pc): raw.hex() for pc, raw in sorted(trace.items())},
        "comparisons": cases,
        "provider_entry_points_intercepted": {},
        "limits": [
            "Classes 0 through 6 execute as stock and compiled source; provider entry interception is not used.",
            "All classes use one bit per user in the seven-row bitmap at 0x20026e74; requests are idempotent rather than counted.",
            "Class 2 uses the same bitmap ownership rule, coordinates mode selectors 2/3/4, and adopts a local callback timeout through 0x20027040.",
            "The source mode-apply helper implements the exact selectors used by class 2 (2, 3, and 4); the other selectors of the larger stock mode routine remain outside this provider.",
            "Classes 5 and 6 execute nested class-2/3 providers as compiled source. Their MMIO, PLL status and lock flags, readiness polling, and callback progress remain synthetic.",
            "Clock-4 delay conversion executes on the Cortex-M33 FPU. The external ROM cycle-wait routine at Thumb address 0x41 (raw branch target 0x40) is intercepted and advances the synthetic callback flag in tests.",
            "SRAM, enable words, and peripheral register blocks are synthetic. No physical MMIO, interrupt delivery, clock stability, silicon timing, or clock-rate interpretation is modeled.",
            "The dispatcher source has source providers for classes 0 through 6; the other mode-apply selectors and board/runtime behavior remain outside these bounded providers.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in
                      ("status", "cases", "original_instruction_bytes_reached")}))


if __name__ == "__main__":
    main()

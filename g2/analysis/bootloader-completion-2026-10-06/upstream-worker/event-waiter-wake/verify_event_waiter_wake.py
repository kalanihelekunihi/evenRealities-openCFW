#!/usr/bin/env python3
"""Differentially exercise the stock event-waiter wake and missed-yield path."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from unicorn import (Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE,
                     UC_MODE_MCLASS, UC_MODE_THUMB)
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BLOB = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BLOB_BASE = 0x410000
BLOB_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
STOP = 0x08000000
STOCK_REMOVE = 0x41872c
STOCK_MISSED_YIELD = 0x4189a2
STOCK_MASK = 0x41b2f8
EVENT_LIST = 0x20021000
STATE_LIST = 0x20021040
THREAD = 0x20022000
CURRENT = 0x20022100
PENDING_LIST = 0x20026f5c
READY_BASE = 0x20024870
TIMER_LIST = 0x20024000
TIMER_ITEM = 0x20024100
PRIORITY = 5

spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Machine:
    def __init__(self, source=False, segments=(), symbols=None):
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.source = source
        self.symbols = symbols or {}
        self.finished = False
        self.trace = {}
        self.writes = []
        self.fatal_store = False
        self.cpu.mem_map(0, 0x1000)
        self.cpu.mem_map(BLOB_BASE, 0x25000)
        self.cpu.mem_write(BLOB_BASE, BLOB.read_bytes())
        self.cpu.mem_map(0x10000, 0x10000)
        for segment in segments:
            self.cpu.mem_write(segment["address"], segment["data"])
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(0xfffff000, 0x1000)
        self.cpu.mem_map(STOP, 0x10000)
        self.cpu.hook_add(UC_HOOK_CODE, self.code)
        self.cpu.hook_add(UC_HOOK_MEM_WRITE, self.memory_write)

    def code(self, uc, pc, size, _):
        if pc == STOP:
            self.finished = True
            uc.emu_stop()
        elif not self.source:
            self.trace[pc] = bytes(uc.mem_read(pc, size))

    def memory_write(self, uc, access, address, size, value, _):
        if 0x20000000 <= address < 0x20040000:
            self.writes.append([address, size, value & ((1 << (size * 8)) - 1)])
        if address == 0xffffffff:
            self.fatal_store = True
            self.finished = True
            uc.emu_stop()

    def put32(self, address, value):
        self.cpu.mem_write(address, int(value & 0xffffffff).to_bytes(4, "little"))

    def get32(self, address):
        return int.from_bytes(self.cpu.mem_read(address, 4), "little")

    def initialize_list(self, address, item=None, index_is_item=False):
        sentinel = address + 8
        self.put32(address, 1 if item else 0)
        self.put32(address + 4, item if (item and index_is_item) else sentinel)
        self.put32(sentinel, 0xffffffff)
        self.put32(sentinel + 4, item if item else sentinel)
        self.put32(sentinel + 8, item if item else sentinel)
        self.put32(sentinel + 12, 0)
        if item:
            self.put32(item + 4, sentinel)
            self.put32(item + 8, sentinel)
            self.put32(item + 12, THREAD)
            self.put32(item + 16, address)

    def prepare(self, fixture):
        self.writes = []
        self.fatal_store = False
        tcb = THREAD
        event_item = tcb + 24
        state_item = tcb + 4
        self.initialize_list(EVENT_LIST,
                             None if fixture.get("empty_event", False) else event_item,
                             fixture.get("event_index_is_item", False))
        self.initialize_list(STATE_LIST, state_item,
                             fixture.get("state_index_is_item", False))
        # Ensure node owner/container slots are correct after both list setup.
        if not fixture.get("empty_event", False):
            self.put32(event_item + 12, tcb)
            self.put32(event_item + 16, EVENT_LIST)
        self.put32(tcb + 44, fixture.get("waiter_priority", PRIORITY))
        self.put32(tcb + 20, STATE_LIST)
        self.put32(tcb + 40, 0 if fixture.get("empty_event", False) else EVENT_LIST)

        current_priority = fixture.get("current_priority", 3)
        self.put32(CURRENT + 44, current_priority)
        self.put32(0x20027134, CURRENT)
        self.put32(0x2002714c, fixture.get("highest_priority", 2))
        self.put32(0x20027158, fixture.get("yield_pending", 0))
        self.put32(0x2002716c, fixture.get("suspend_depth", 0))
        self.initialize_list(PENDING_LIST)
        ready = READY_BASE + 20 * fixture.get("waiter_priority", PRIORITY)
        self.initialize_list(ready)
        self.initialize_list(TIMER_LIST,
                             TIMER_ITEM if fixture.get("timer_active", False) else None)
        if fixture.get("timer_active", False):
            self.put32(TIMER_ITEM, fixture.get("timer_expiry", 8765))
        self.put32(0x20027138, TIMER_LIST)
        self.put32(0x20027164, fixture.get("next_unblock", 12345))
        self.cpu.reg_write(a.UC_ARM_REG_PRIMASK, fixture.get("primask", 0))

    def snapshot(self, result):
        addresses = {
            "event_list": (EVENT_LIST, 24),
            "state_list": (STATE_LIST, 24),
            "thread": (THREAD, 52),
            "pending_list": (PENDING_LIST, 24),
            "ready_list": (READY_BASE + PRIORITY * 20, 24),
            "timer_list": (TIMER_LIST, 24),
            "globals": (0x20027134, 0x40),
        }
        memory = {name: bytes(self.cpu.mem_read(address, size)).hex()
                  for name, (address, size) in addresses.items()}
        return {"result": result,
                "memory": memory,
                "primask": self.cpu.reg_read(a.UC_ARM_REG_PRIMASK),
                "writes": list(self.writes),
                "fatal_store": self.fatal_store}

    def run_remove(self, fixture):
        self.prepare(fixture)
        entry = (self.symbols["opencfw_bl_remove_event_waiter"] if self.source
                 else STOCK_REMOVE)
        self.cpu.reg_write(a.UC_ARM_REG_R0, EVENT_LIST)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.finished = False
        self.cpu.emu_start(entry | 1, STOP + 2, count=100000)
        if not self.finished:
            raise AssertionError((self.source, "remove did not finish",
                                  hex(self.cpu.reg_read(a.UC_ARM_REG_PC))))
        return self.snapshot(self.cpu.reg_read(a.UC_ARM_REG_R0))

    def run_missed_yield(self, initial):
        self.writes = []
        self.put32(0x20027158, initial)
        entry = (self.symbols["opencfw_bl_missed_yield"] if self.source
                 else STOCK_MISSED_YIELD)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.finished = False
        self.cpu.emu_start(entry | 1, STOP + 2, count=1000)
        assert self.finished
        return {"yield_pending": self.get32(0x20027158),
                "writes": list(self.writes)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    image = BLOB.read_bytes()
    assert sha(image) == BLOB_SHA
    _, segments, symbols = elf.elf_info(args.elf)
    cases = []
    traces = {}
    fixtures = [
        ("awake_higher_indexes", {"suspend_depth": 0, "waiter_priority": 5,
                                   "current_priority": 3, "highest_priority": 2,
                                   "event_index_is_item": True,
                                   "state_index_is_item": True}),
        ("awake_equal", {"suspend_depth": 0, "waiter_priority": 5,
                          "current_priority": 5, "highest_priority": 5}),
        ("awake_lower", {"suspend_depth": 0, "waiter_priority": 4,
                          "current_priority": 7, "highest_priority": 8}),
        ("awake_higher_timer_active", {"suspend_depth": 0,
                                        "waiter_priority": 5,
                                        "current_priority": 3,
                                        "timer_active": True,
                                        "timer_expiry": 0x12345678}),
        ("suspended_higher", {"suspend_depth": 1, "waiter_priority": 6,
                               "current_priority": 2}),
        ("suspended_equal", {"suspend_depth": 1, "waiter_priority": 6,
                              "current_priority": 6}),
        ("empty_list_null_owner", {"empty_event": True}),
    ]
    for name, fixture in fixtures:
        stock, source = Machine(), Machine(True, segments, symbols)
        got_stock = stock.run_remove(fixture)
        got_source = source.run_remove(fixture)
        if fixture.get("empty_event"):
            # The invalid store is the fatal boundary, not a function return;
            # Unicorn stops before the store retires so R0 is incidental.
            got_stock.pop("result")
            got_source.pop("result")
        assert got_stock == got_source, {
            "case": name, "fixture": fixture,
            "stock": got_stock, "source": got_source}
        cases.append({"name": name, "fixture": fixture, "result": got_stock})
        traces.update(stock.trace)

    missed_cases = []
    for initial in (0, 1, 0xffffffff):
        stock, source = Machine(), Machine(True, segments, symbols)
        got_stock = stock.run_missed_yield(initial)
        got_source = source.run_missed_yield(initial)
        assert got_stock == got_source == {
            "yield_pending": 1,
            "writes": [[0x20027158, 4, 1]]}
        missed_cases.append({"initial": hex(initial), "result": got_stock})
        traces.update(stock.trace)

    used = {pc + i for pc, raw in traces.items()
            for i in range(len(raw))}
    functions = {
        "event_waiter_remove": (0x41872c, 0x418822,
            "98a6d87479774e44e46f42c02e98b09f46bf1fc1b1240b6cd172b96625468a06"),
        "missed_yield": (0x4189a2, 0x4189ac,
            "86fecf54abdabf46c2e923791f342997647d2d42a74db84fa9207d5756b39d17"),
    }
    stock_functions = {}
    for name, (start, end, digest) in functions.items():
        body = image[start - BLOB_BASE:end - BLOB_BASE]
        assert sha(body) == digest
        stock_functions[name] = {"range": [hex(start), hex(end)],
                                 "size": end - start, "sha256": digest}

    result = {
        "status": "PASS",
        "event_waiter_cases": cases,
        "missed_yield_cases": missed_cases,
        "original_instruction_bytes_reached": len(used),
        "original_image_sha256": BLOB_SHA,
        "source_elf_sha256": sha(args.elf.read_bytes()),
        "source_sha256": {
            "event_waiter_wake.c": sha((ROOT / "g2/components/bootloader/thread_creation/event_waiter_wake.c").read_bytes()),
            "event_waiter_wake.h": sha((ROOT / "g2/components/bootloader/thread_creation/event_waiter_wake.h").read_bytes()),
            "timer_wait.c": sha((ROOT / "g2/components/bootloader/thread_creation/timer_wait.c").read_bytes()),
            "scheduler_resume.c": sha((ROOT / "g2/components/bootloader/thread_creation/scheduler_resume.c").read_bytes()),
        },
        "stock_functions": stock_functions,
        "trace": {hex(pc): raw.hex() for pc, raw in sorted(traces.items())},
        "limits": [
            "SRAM list heads and scheduler words are synthetic; no live kernel, task, queue, interrupt, or peripheral is used.",
            "The fatal null-owner case reaches the stock interrupt-mask helper and invalid write to 0xffffffff; execution stops at that write before the infinite loop.",
            "The linked list-unlink and next-unblock helpers are existing thread_creation source; unrelated timer and scheduler entry points are garbage-collected from this isolated ELF.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"],
                      "event_waiter_cases": len(cases),
                      "missed_yield_cases": len(missed_cases),
                      "original_instruction_bytes_reached": len(used)}))


if __name__ == "__main__":
    main()

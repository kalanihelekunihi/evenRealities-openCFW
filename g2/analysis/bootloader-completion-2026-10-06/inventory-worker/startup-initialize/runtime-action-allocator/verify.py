"""Pair stock release/free with source release/native RTOS heap on valid blocks."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                     UC_HOOK_CODE)
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
BOOT_PATH = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
IMAGE_SHA256 = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
ARENA_BASE = 0x2000055c
ARENA_SIZE = 0x14000
ARENA = (ARENA_BASE, ARENA_SIZE)
HEAP_GLOBALS = (0x20027020, 0x2002711c - 0x20027020)
TCB_STATIC = 0x20018200
STACK_STATIC = 0x20018000
STOP = 0x08000000
ORIGINAL_EXTENTS = {
    "release_storage": (0x418ae8, 0x418b28),
    "rtos_allocate": (0x419730, 0x419830),
    "rtos_free": (0x419830, 0x4198a0),
    "rtos_heap_initialize": (0x4198a0, 0x4198fa),
    "rtos_heap_insert": (0x4198fa, 0x419956),
}

parser = argparse.ArgumentParser()
parser.add_argument("--elf", required=True, type=Path)
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
blob = BOOT_PATH.read_bytes()
assert hashlib.sha256(blob).hexdigest() == IMAGE_SHA256
elf_reader_path = ROOT / "g2/components/bootloader/update_core/elf_reader.py"
spec = importlib.util.spec_from_file_location("owned_elf_reader", elf_reader_path)
elf_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_reader)
_, source_segments, source_symbols = elf_reader.elf_info(args.elf)
for required in ["opencfw_boot_thread_release_storage",
                 "opencfw_boot_rtos_heap_initialize",
                 "opencfw_bl_rtos_allocate", "opencfw_bl_rtos_free",
                 "test_suspend_calls", "test_resume_calls",
                 "test_malloc_failed_calls", "test_mask_calls",
                 "test_event_count", "test_events"]:
    assert required in source_symbols, required


def write32(cpu, address, value):
    cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))


def read32(cpu, address):
    return struct.unpack("<I", cpu.mem_read(address, 4))[0]


class Machine:
    def __init__(self, source):
        self.source = source
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        for low, size in [(0x10000, 0x10000), (0x08000000, 0x2000),
                          (0x20000000, 0x40000), (0x410000, 0x30000)]:
            self.cpu.mem_map(low, size)
        if source:
            for segment in source_segments:
                self.cpu.mem_write(segment["address"], segment["data"])
        else:
            self.cpu.mem_write(0x410000, blob)
        self.events = []
        self.trace = {}
        self.done = False
        self.failures = []
        self.cpu.hook_add(UC_HOOK_CODE, self.code)

    def code(self, cpu, pc, size, _):
        pc &= ~1
        if pc == STOP:
            self.done = True
            cpu.emu_stop()
            return
        if not self.source:
            for name, (start, end) in ORIGINAL_EXTENTS.items():
                if start <= pc < end:
                    self.trace[pc] = size
        if not self.source and pc in (0x4181d8, 0x418228):
            self.events.append(1 if pc == 0x4181d8 else 2)
            cpu.reg_write(a.UC_ARM_REG_R0, 0)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            return
        if not self.source and pc in (0x41b2f8, 0x41b5f6):
            label = "fatal" if pc == 0x41b2f8 else "malloc_failed"
            self.failures.append(label)
            self.events.append(4 if label == "fatal" else 3)
            cpu.emu_stop()

    def invoke(self, entry, args=()):
        self.done = False
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        for idx, reg in enumerate([a.UC_ARM_REG_R0, a.UC_ARM_REG_R1,
                                   a.UC_ARM_REG_R2, a.UC_ARM_REG_R3]):
            self.cpu.reg_write(reg, args[idx] if idx < len(args) else 0)
        if isinstance(entry, str):
            address = source_symbols[entry] & ~1
        else:
            address = entry
        self.cpu.emu_start(address | 1, STOP + 2, count=50000)
        assert self.done and not self.failures, (self.source, entry, args, self.failures)
        if self.source:
            assert read32(self.cpu, source_symbols["test_malloc_failed_calls"]) == 0
            assert read32(self.cpu, source_symbols["test_mask_calls"]) == 0
        return self.cpu.reg_read(a.UC_ARM_REG_R0)

    def source_events(self):
        count = read32(self.cpu, source_symbols["test_event_count"])
        return [read32(self.cpu, source_symbols["test_events"] + 4*i)
                for i in range(count)]

    def state(self, tcb, stack):
        result = {
            "arena": bytes(self.cpu.mem_read(*ARENA)).hex(),
            "heap_globals": bytes(self.cpu.mem_read(*HEAP_GLOBALS)).hex(),
            "tcb": bytes(self.cpu.mem_read(tcb, 112)).hex(),
            "stack_header": bytes(self.cpu.mem_read(stack, 16)).hex(),
            "suspend_calls": read32(self.cpu, source_symbols["test_suspend_calls"]) if self.source else self.events.count(1),
            "resume_calls": read32(self.cpu, source_symbols["test_resume_calls"]) if self.source else self.events.count(2),
            "events": self.source_events() if self.source else list(self.events),
        }
        return result


def prepare(mode):
    pair = [Machine(False), Machine(True)]
    allocations = []
    results = []
    for machine in pair:
        machine.invoke(0x4198a0 if not machine.source else "opencfw_boot_rtos_heap_initialize")
        if mode == 0:
            stack = machine.invoke(0x419730 if not machine.source else "opencfw_bl_rtos_allocate", [256])
            tcb = machine.invoke(0x419730 if not machine.source else "opencfw_bl_rtos_allocate", [112])
            assert stack and tcb and stack + 256 <= tcb
            owned = True
        elif mode == 1:
            stack = STACK_STATIC
            tcb = machine.invoke(0x419730 if not machine.source else "opencfw_bl_rtos_allocate", [112])
            assert tcb and tcb != stack
            owned = True
        else:
            stack, tcb, owned = STACK_STATIC, TCB_STATIC, False
        machine.cpu.mem_write(stack, b"S" * 256)
        machine.cpu.mem_write(tcb, b"\xcc" * 112)
        write32(machine.cpu, tcb + 12*4, stack)
        machine.cpu.mem_write(tcb + 0x6d, bytes([mode]))
        before = machine.state(tcb, stack)
        # The allocator proof relies on real allocated headers for every block
        # which the selected ownership value will release.
        if mode == 0:
            assert read32(machine.cpu, stack - 4) & 0x80000000
            assert read32(machine.cpu, tcb - 4) & 0x80000000
        elif mode == 1:
            assert read32(machine.cpu, tcb - 4) & 0x80000000
        results.append({"tcb": tcb, "stack": stack, "owned_heap": owned,
                        "before": before})
    assert results[0]["tcb"] == results[1]["tcb"]
    assert results[0]["stack"] == results[1]["stack"]
    assert results[0]["before"] == results[1]["before"], mode
    return pair, results


cases = []
trace = {}
for ownership in (0, 1, 2):
    pair, fixtures = prepare(ownership)
    release_results = []
    for machine, fixture in zip(pair, fixtures):
        entry = "opencfw_boot_thread_release_storage" if machine.source else 0x418ae8
        machine.invoke(entry, [fixture["tcb"]])
        trace.update(machine.trace)
        after = machine.state(fixture["tcb"], fixture["stack"])
        release_results.append(after)
    assert release_results[0] == release_results[1], (ownership, release_results)
    free_count = read32(pair[0].cpu, 0x20027118)
    expected_frees = {0: 2, 1: 1, 2: 0}[ownership]
    assert free_count == expected_frees, (ownership, free_count)
    assert read32(pair[1].cpu, 0x20027118) == expected_frees
    cases.append({"ownership": ownership,
                  "ownership_meaning": {0: "stack+TCB", 1: "TCB only", 2: "none"}[ownership],
                  "stack": hex(fixtures[0]["stack"]), "tcb": hex(fixtures[0]["tcb"]),
                  "freed_block_count": free_count, "result": release_results[0]})

used = set()
for pc, size in trace.items():
    used.update(range(pc, pc + size))
    off = pc - 0x410000
    assert blob[off:off+size]
coverage = {}
for name, (lo, hi) in ORIGINAL_EXTENTS.items():
    body = set(range(lo, hi))
    visited = body & used
    coverage[name] = {
        "extent": [hex(lo), hex(hi)], "extent_bytes": hi - lo,
        "visited_bytes": len(visited),
        "unvisited_ranges": [],
        "body_sha256": hashlib.sha256(blob[lo-0x410000:hi-0x410000]).hexdigest(),
    }
    missing = sorted(body - visited)
    if missing:
        groups = []
        for addr in missing:
            if not groups or addr != groups[-1][1]:
                groups.append([addr, addr + 1])
            else:
                groups[-1][1] += 1
        coverage[name]["unvisited_ranges"] = [[hex(a0), hex(a1)] for a0, a1 in groups]

source_files = {
    "runtime_action.c": ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/runtime-action-416200/runtime_action.c",
    "rtos_heap.c": ROOT / "g2/components/bootloader/thread_creation/rtos_heap.c",
    "platform_cuts.c": HERE / "platform_cuts.c",
    "verify.py": HERE / "verify.py",
    "module.ld": HERE / "module.ld",
    "Makefile": HERE / "Makefile",
}
output = {
    "status": "PASS", "cases": len(cases),
    "original_image_sha256": hashlib.sha256(blob).hexdigest(),
    "source_elf_sha256": hashlib.sha256(args.elf.read_bytes()).hexdigest(),
    "source_files_sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest()
                            for name, path in source_files.items()},
    "coverage": coverage,
    "comparisons": cases,
    "limits": [
        "The fixture initializes and allocates its own valid RTOS heap; it does not use prior test-case pointers or copied corpus state.",
        "Only ownership values 0, 1, and 2 are exercised; malformed ownership and invalid/double frees are outside this test.",
        "Scheduler suspend/resume are synthetic no-op providers. Heap bytes are deterministic Unicorn RAM; no physical allocator concurrency or hardware behavior is claimed.",
        "This compares the bounded release-storage path plus allocator against stock; it does not validate whole-task termination, deferred self-delete reclamation, scheduler drain, or firmware integration.",
    ],
}
args.output.write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps({"status": output["status"], "cases": output["cases"], "coverage": coverage}, indent=2))

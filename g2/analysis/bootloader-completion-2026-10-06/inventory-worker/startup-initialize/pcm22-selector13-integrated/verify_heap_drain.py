"""Repeat valid-heap ownership proof with the current whole-runtime ELF."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import struct
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                     UC_HOOK_CODE)
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
BOOT_PATH = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
EXPECTED_BOOT = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
EXPECTED_CANDIDATE = "cf30c67430b8ad3f4e06c4fb70e510f80fc09a7449a64767d29322e41a2c23a1"
HEAP_BASE, HEAP_SIZE = 0x2000055c, 0x14000
HEAP_END = HEAP_BASE + HEAP_SIZE
HEAP_GLOBALS = (0x20027020, 0x2002711c - 0x20027020)
STATIC_TCB, STATIC_STACK = 0x20018200, 0x20018000
STOP = 0x08000000
STOCK_EXTENTS = {
    "idle_cleanup":(0x418a98,0x418ad4),
    "release_storage": (0x418ae8, 0x418b28),
    "rtos_allocate": (0x419730, 0x419830),
    "rtos_free": (0x419830, 0x4198a0),
    "rtos_heap_initialize": (0x4198a0, 0x4198fa),
    "rtos_heap_insert": (0x4198fa, 0x419956),
}
parser = argparse.ArgumentParser()
parser.add_argument("--candidate-elf", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--cleanup-addon",type=Path,required=True)
args = parser.parse_args()
boot = BOOT_PATH.read_bytes()
assert hashlib.sha256(boot).hexdigest() == EXPECTED_BOOT
candidate_hash = hashlib.sha256(args.candidate_elf.read_bytes()).hexdigest()
assert candidate_hash == EXPECTED_CANDIDATE, candidate_hash

segments = []
symbols = {}
section_layout = []
with args.candidate_elf.open("rb") as f:
    elf = ELFFile(f)
    assert elf.elfclass == 32 and elf.little_endian
    assert elf["e_machine"] == "EM_ARM" and elf["e_type"] == "ET_EXEC"
    for segment in elf.iter_segments():
        if segment["p_type"] != "PT_LOAD":
            continue
        lo = int(segment["p_vaddr"])
        filesz = int(segment["p_filesz"])
        memsz = int(segment["p_memsz"])
        end = lo + memsz
        assert filesz <= memsz
        assert any(start <= lo <= end <= limit for start, limit in [
            (0x10000, 0x20000), (0x30000, 0x40000), (0x50000, 0x60000),
            (0x410000, 0x434477), (0x20000000, 0x20040000)])
        assert not (lo < HEAP_END and end > HEAP_BASE), (
            "candidate static segment collides with RTOS heap",
            hex(lo), hex(end), hex(HEAP_BASE), hex(HEAP_END))
        segments.append({"address": lo, "filesz": filesz, "memsz": memsz,
                         "data": segment.data(), "flags": int(segment["p_flags"])})
    symtab = elf.get_section_by_name(".symtab")
    assert symtab is not None
    symbols = {s.name: int(s["st_value"]) for s in symtab.iter_symbols()
               if s.name and s["st_shndx"] != "SHN_UNDEF"}
    for section in elf.iter_sections():
        if section.name in [".boot_iom_context_pool", ".text", ".source_cache"]:
            section_layout.append({"name": section.name,
                                   "address": int(section["sh_addr"]),
                                   "size": int(section["sh_size"]),
                                   "type": section["sh_type"]})

NEEDED = ["opencfw_boot_thread_release_storage", "opencfw_bl_rtos_allocate",
          "opencfw_bl_rtos_free", "opencfw_bl_scheduler_suspend",
          "opencfw_bl_scheduler_resume"]
for name in NEEDED:
    assert name in symbols, name
assert section_layout and any(s["name"] == ".boot_iom_context_pool"
                              and s["address"] == HEAP_END for s in section_layout)


def write32(cpu, address, value):
    cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))


def read32(cpu, address):
    return struct.unpack("<I", cpu.mem_read(address, 4))[0]


class Machine:
    def __init__(self, source):
        self.source = source
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        for low, size in [(0x10000, 0x10000), (0x30000, 0x10000), (0x50000,0x1000), (0xe000e000,0x1000),
                          (0x08000000, 0x2000), (0x20000000, 0x40000),
                          (0x410000, 0x30000)]:
            self.cpu.mem_map(low, size)
        if source:
            # The source side maps only PT_LOAD bytes from the immutable whole-
            # runtime ELF. It never loads stock executable firmware bytes.
            for segment in segments:
                if segment["filesz"]:
                    self.cpu.mem_write(segment["address"], segment["data"])
        else:
            self.cpu.mem_write(0x410000, boot)
        self.events = []
        self.trace = {}
        self.failures = []
        self.done = False
        self.scheduler_cuts = ({symbols[name] & ~1: event for name, event in [
            ("opencfw_bl_scheduler_suspend", 1),
            ("opencfw_bl_scheduler_resume", 2)]} if source else {})
        self.cpu.hook_add(UC_HOOK_CODE, self.code)

    def code(self, cpu, pc, size, _):
        pc &= ~1
        if pc == STOP:
            self.done = True
            cpu.emu_stop()
            return
        if not self.source:
            for start, end in STOCK_EXTENTS.values():
                if start <= pc < end:
                    self.trace[pc] = size
            if pc in (0x4181d8, 0x418228):
                self.events.append(1 if pc == 0x4181d8 else 2)
                cpu.reg_write(a.UC_ARM_REG_R0, 0)
                cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
                return
            if pc == 0x41b5f6:
                self.failures.append("fatal" if pc == 0x41b2f8 else "malloc-failed")
                cpu.emu_stop()
                return
        elif pc in self.scheduler_cuts:
            self.events.append(self.scheduler_cuts[pc])
            cpu.reg_write(a.UC_ARM_REG_R0, 0)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            return
        elif pc == 0x41b5f6:
            self.failures.append("malloc-failed")
            cpu.emu_stop()

    def invoke(self, entry, call_args=()):
        self.done = False
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        for i, reg in enumerate([a.UC_ARM_REG_R0, a.UC_ARM_REG_R1,
                                 a.UC_ARM_REG_R2, a.UC_ARM_REG_R3]):
            self.cpu.reg_write(reg, call_args[i] if i < len(call_args) else 0)
        address = (symbols[entry] & ~1) if isinstance(entry, str) else entry
        self.cpu.emu_start(address | 1, STOP + 2, count=80000)
        assert self.done and not self.failures, (self.source, entry, call_args, self.failures)
        return self.cpu.reg_read(a.UC_ARM_REG_R0)

    def state(self, tcb, stack):
        return {
            "arena_sha256": hashlib.sha256(self.cpu.mem_read(HEAP_BASE, HEAP_SIZE)).hexdigest(),
            "heap_globals": bytes(self.cpu.mem_read(*HEAP_GLOBALS)).hex(),
            "tcb": bytes(self.cpu.mem_read(tcb, 112)).hex(),
            "stack_prefix": bytes(self.cpu.mem_read(stack, 16)).hex(),
            "events": list(self.events),
        }


def assert_pair(pair, what):
    left, right = what(pair[0]), what(pair[1])
    assert left == right, (left, right)
    return left


cases = []
trace = {}
for ownership in (0, 1, 2):
    pair = [Machine(False), Machine(True)]
    pointers = []
    for machine in pair:
        alloc = 0x419730 if not machine.source else "opencfw_bl_rtos_allocate"
        free = 0x419830 if not machine.source else "opencfw_bl_rtos_free"
        # Exercise the real allocator on both sides, then coalesce the probe
        # back to form a valid empty heap before creating this ownership case.
        probe = machine.invoke(alloc, [32])
        assert probe
        machine.invoke(free, [probe])
        if ownership == 0:
            stack = machine.invoke(alloc, [256])
            tcb = machine.invoke(alloc, [112])
            assert stack and tcb and stack + 256 <= tcb
        elif ownership == 1:
            stack = STATIC_STACK
            tcb = machine.invoke(alloc, [112])
            assert tcb and tcb != stack
        else:
            stack, tcb = STATIC_STACK, STATIC_TCB
        machine.cpu.mem_write(stack, b"S" * 256)
        machine.cpu.mem_write(tcb, b"\xcc" * 112)
        write32(machine.cpu, tcb + 48, stack)
        machine.cpu.mem_write(tcb + 0x6d, bytes([ownership]))
        if ownership == 0:
            assert read32(machine.cpu, stack - 4) & 0x80000000
            assert read32(machine.cpu, tcb - 4) & 0x80000000
        elif ownership == 1:
            assert read32(machine.cpu, tcb - 4) & 0x80000000
        pointers.append((tcb, stack))
    assert pointers[0] == pointers[1]
    before = assert_pair(pair, lambda m: m.state(*pointers[0]))
    free_before = [read32(m.cpu, 0x20027118) for m in pair]
    assert free_before[0] == free_before[1] == 1
    for machine in pair:
        tcb=pointers[0][0];item=tcb+4;end=0x20026f78
        for address,value in [(0x20026f70,1),(0x20026f74,end),(end,0xffffffff),(end+4,item),(end+8,item),(item,0),(item+4,end),(item+8,end),(item+12,tcb),(item+16,0x20026f70),(0x20027140,1),(0x20027144,2),(0x200004c4,0)]:
            write32(machine.cpu,address,value)
        target = ("opencfw_boot_idle_cleanup" if machine.source else 0x418a98)
        machine.invoke(target, [0,0,0,0xabcddcba])
        assert read32(machine.cpu,0x20026f70)==0 and read32(machine.cpu,0x20027140)==0 and read32(machine.cpu,0x20027144)==1
        trace.update(machine.trace)
    after = assert_pair(pair, lambda m: m.state(*pointers[0]))
    free_after = [read32(m.cpu, 0x20027118) for m in pair]
    delta = free_after[0] - free_before[0]
    expected = {0: 2, 1: 1, 2: 0}[ownership]
    assert free_after[0] == free_after[1] and delta == expected, (ownership, free_before, free_after)
    if ownership in (0, 1):
        assert after["events"][-(2*expected):] == [event for _ in range(expected) for event in (1, 2)]
    cases.append({"ownership": ownership,
                  "meaning": {0: "stack+TCB", 1: "TCB only", 2: "none"}[ownership],
                  "stack": hex(pointers[0][1]), "tcb": hex(pointers[0][0]),
                  "pre_release_state": before, "post_release_state": after,
                  "free_counter_before": free_before[0],
                  "free_counter_after": free_after[0],
                  "release_free_count_delta": delta})

used = set()
for pc, size in trace.items():
    used.update(range(pc, pc + size))
    off = pc - 0x410000
    assert boot[off:off+size]
coverage = {}
for name, (lo, hi) in STOCK_EXTENTS.items():
    extent = set(range(lo, hi))
    visited = used & extent
    gaps = sorted(extent - visited)
    ranges = []
    for pc in gaps:
        if not ranges or pc != ranges[-1][1]:
            ranges.append([pc, pc + 1])
        else:
            ranges[-1][1] += 1
    coverage[name] = {
        "extent": [hex(lo), hex(hi)], "extent_bytes": hi - lo,
        "visited_bytes": len(visited),
        "unvisited_ranges": [[hex(a0), hex(a1)] for a0, a1 in ranges],
        "stock_body_sha256": hashlib.sha256(boot[lo-0x410000:hi-0x410000]).hexdigest(),
    }

input_hashes = {
    "candidate_elf": candidate_hash,
    "verify_integrated.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "original_bootloader": hashlib.sha256(boot).hexdigest(),
}
result = {
    "status": "PASS", "cases": len(cases),
    "candidate_elf": str(args.candidate_elf),
    "candidate_elf_sha256": candidate_hash,
    "input_sha256": input_hashes,
    "candidate_relevant_sections": section_layout,
    "heap_layout": {
        "rtos_arena_start": hex(HEAP_BASE), "rtos_arena_end_exclusive": hex(HEAP_END),
        "rtos_arena_bytes": HEAP_SIZE,
        "candidate_load_segments_overlapping_arena": [],
        "iom_context_pool_starts_at_heap_end": True,
        "rtos_heap_init_and_insert_are_inlined_in_candidate_allocator": True,
    },
    "coverage": coverage, "comparisons": cases,
    "limits": [
        "Candidate source executions load only its immutable ELF PT_LOAD content and do not load the stock bootloader; only its scheduler suspend/resume functions are controlled code cuts.",
        "The whole-runtime candidate places .boot_iom_context_pool at the exact RTOS arena end, so it does not overlap [0x2000055c,0x2001455c). The unrelated TLSF/source allocator initializer is not called; the tested RTOS allocation performs its own initialization path.",
        "Ownership fixtures 0/1/2 use valid allocated headers only for heap-owned blocks. Ownership 2 uses static TCB/stack after a probe allocation has been freed and coalesced to validate a live empty heap.",
        "Synthetic Unicorn RAM and no-op scheduler cut returns; this is not a hardware allocator, concurrent free, malformed ownership, OOM, whole-task delete, or byte-identity proof.",
    ],
}
args.output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": result["status"], "cases": result["cases"],
                  "heap_layout": result["heap_layout"],
                  "visited": {k: v["visited_bytes"] for k, v in coverage.items()}}, indent=2))

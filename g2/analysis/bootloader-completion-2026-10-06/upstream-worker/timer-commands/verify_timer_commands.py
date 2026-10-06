#!/usr/bin/env python3
"""Differentially execute the timer command drain against the locked image."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                     UC_HOOK_CODE, UC_HOOK_MEM_WRITE_UNMAPPED)
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BLOB = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BLOB_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
BASE = 0x410000
STOP = 0x08000000
QUEUE = 0x20030200
BUFFER = 0x20030000
TIMER = 0x20031000
CALLBACK = 0x2003F001
LIST_NOW = 0x20026F98
LIST_WRAP = 0x20026FAC

spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_reader)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Machine:
    def __init__(self, source=False, segments=(), symbols=None):
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.source = source
        self.symbols = symbols or {}
        self.trace = {}
        self.callbacks = []
        self.frees = []
        self.callback_updates = []
        self.fault = None
        self.cpu.mem_map(BASE, 0x25000)
        self.cpu.mem_write(BASE, BLOB.read_bytes())
        self.cpu.mem_map(0x10000, 0x10000)
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(0x40000000, 0x10000)
        self.cpu.mem_map(0x08000000, 0x1000)
        if source:
            for seg in segments:
                address = seg["address"]
                data = seg["data"]
                self.cpu.mem_write(address, data)
            self.entry = self.symbols["opencfw_bl_timer_process_commands"] & ~1
            self.source_free = self.symbols["opencfw_bl_rtos_free"] & ~1
        else:
            self.entry = 0x419546
            self.source_free = 0x419830
        self.cpu.hook_add(UC_HOOK_CODE, self.code)
        self.cpu.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED, self.invalid_write)

    def invalid_write(self, uc, access, address, size, value, _):
        self.fault = {"pc": hex(uc.reg_read(a.UC_ARM_REG_PC)),
                      "address": hex(address), "size": size,
                      "value": hex(value), "source": self.source}
        return False

    def u32(self, address):
        return struct.unpack("<I", self.cpu.mem_read(address, 4))[0]

    def w32(self, address, value):
        self.cpu.mem_write(address, struct.pack("<I", value & 0xFFFFFFFF))

    def code(self, uc, pc, size, _):
        if pc == STOP:
            uc.emu_stop()
            return
        if not self.source and BASE <= pc < BASE + len(BLOB.read_bytes()) \
                and pc not in (0x419830,):
            self.trace[pc] = bytes(uc.mem_read(pc, size))
        if pc == CALLBACK & ~1:
            r0 = uc.reg_read(a.UC_ARM_REG_R0)
            r1 = uc.reg_read(a.UC_ARM_REG_R1)
            self.callbacks.append([r0, r1])
            if self.callback_updates:
                self.w32(TIMER + 6 * 4, self.callback_updates.pop(0))
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if pc == self.source_free:
            self.frees.append(uc.reg_read(a.UC_ARM_REG_R0))
            self.w32(0x20030FF0, self.frees[-1])
            self.w32(0x20030FF4, self.u32(0x20030FF4) + 1)
            uc.reg_write(a.UC_ARM_REG_R0, 0)
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))

    def run(self):
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2003FFF0)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP)
        self.cpu.emu_start(self.entry | 1, STOP, count=100000)


def init(m, now, messages, state=0, period=10, active=False):
    m.cpu.mem_write(0x20000000, b"\0" * 0x40000)
    # Queue control block and 50-entry ring buffer, with the observed 16-byte
    # command message geometry.
    for off, value in [(0, BUFFER), (1, BUFFER), (2, BUFFER + 50 * 16),
                       (3, BUFFER - 16), (14, len(messages)), (15, 50), (16, 16)]:
        m.w32(QUEUE + off * 4, value)
    for i, message in enumerate(messages):
        m.cpu.mem_write(BUFFER + i * 16, struct.pack("<4I", *(x & 0xFFFFFFFF for x in message)))
    # Two five-word timer-list sentinels. The list index anchors are list+8.
    for addr in (LIST_NOW, LIST_WRAP):
        for off, value in [(0, 0), (1, addr + 8), (2, 0xFFFFFFFF),
                           (3, addr + 8), (4, addr + 8)]:
            m.w32(addr + off * 4, value)
    m.w32(0x20027148, now)
    m.w32(0x20027150, 0)  # Stock runtime-mode provider returns mode 1.
    m.w32(0x20027188, now)
    m.w32(0x20027178, LIST_NOW)
    m.w32(0x2002717C, LIST_WRAP)
    m.w32(0x20027180, QUEUE)
    m.cpu.mem_write(TIMER, b"\0" * 44)
    m.w32(TIMER + 6 * 4, period)
    m.w32(TIMER + 8 * 4, CALLBACK)
    m.cpu.mem_write(TIMER + 0x28, bytes([state]))
    if active:
        m.w32(TIMER + 4, now - 1)
        m.w32(TIMER + 8, LIST_NOW + 8)
        m.w32(TIMER + 12, LIST_NOW + 8)
        m.w32(TIMER + 16, TIMER)
        m.w32(TIMER + 20, LIST_NOW)
        m.w32(LIST_NOW, 1)
        m.w32(LIST_NOW + 12, TIMER + 4)
        m.w32(LIST_NOW + 16, TIMER + 4)
    # Put the callback stub at an address with Thumb bit set in stored pointers.
    m.cpu.mem_write(CALLBACK & ~1, b"\x70\x47")


def state(m):
    return {
        "queue": bytes(m.cpu.mem_read(QUEUE, 80)).hex(),
        "timer": bytes(m.cpu.mem_read(TIMER, 44)).hex(),
        "lists": bytes(m.cpu.mem_read(LIST_NOW, 80)).hex(),
        "clock": bytes(m.cpu.mem_read(0x20027148, 0x44)).hex(),
        "callbacks": m.callbacks,
        "frees": m.frees,
        "free_observation": bytes(m.cpu.mem_read(0x20030FF0, 8)).hex(),
        "critical_nesting": m.u32(0x200004C4),
        "basepri": m.cpu.reg_read(a.UC_ARM_REG_BASEPRI),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert sha(BLOB) == BLOB_SHA
    _, segments, symbols = elf_reader.elf_info(args.elf)
    fixtures = []
    for command in range(11):
        fixtures.append((f"command-{command}", [[command, 5, TIMER, 0x1234]],
                         dict(state=0, period=10, active=False)))
    fixtures.extend([
        ("negative-callback", [[0xFFFFFFFF, CALLBACK, 0x11223344, 0x55667788]],
         dict(state=0, period=10, active=False)),
        ("remove-active", [[3, 0, TIMER, 0]],
         dict(state=1, period=10, active=True)),
        ("reload-bit2", [[1, 5, TIMER, 0]],
         dict(state=4, period=10, active=False)),
        ("bit3-only", [[1, 5, TIMER, 0]],
         dict(state=8, period=10, active=False)),
        ("static-delete", [[5, 0, TIMER, 0]],
         dict(state=2, period=10, active=False)),
        ("dynamic-delete", [[5, 0, TIMER, 0]],
         dict(state=0, period=10, active=False)),
        ("reconfigure-active", [[4, 21, TIMER, 0]],
         dict(state=1, period=10, active=True)),
        ("expired-reload", [[7, 5, TIMER, 0]],
         dict(state=4, period=10, active=False)),
        ("callback-changes-period", [[1, 5, TIMER, 0]],
         dict(state=4, period=10, active=False, callback_updates=[12, 14, 16])),
        ("wrapped-reconfigure", [[4, 32, TIMER, 0]],
         dict(now=0xFFFFFFF0, state=0, period=10, active=False)),
        ("wrapped-start-expired", [[1, 0xFFFFFFF8, TIMER, 0]],
         dict(now=0xFFFFFFF0, state=0, period=10, active=False)),
        ("drain-three", [[1, 5, TIMER, 0], [8, 0, TIMER, 0], [4, 21, TIMER, 0]],
         dict(state=0, period=10, active=False)),
    ])
    comparisons = []
    trace = {}
    for label, messages, fixture in fixtures:
        pair = [Machine(), Machine(True, segments, symbols)]
        results = []
        for m in pair:
            setup = dict(fixture)
            callback_updates = setup.pop("callback_updates", [])
            now = setup.pop("now", 100)
            init(m, now, messages, **setup)
            m.callback_updates = list(callback_updates)
            try:
                m.run()
            except Exception as error:
                raise RuntimeError((label, m.fault, hex(m.cpu.reg_read(a.UC_ARM_REG_PC)))) from error
            results.append(state(m))
        assert results[0] == results[1], (label, results)
        trace.update(pair[0].trace)
        comparisons.append({"case": label, "result": results[0]})
    trace_bytes = {pc + offset for pc, raw in trace.items() for offset in range(len(raw))}
    trace_ranges = []
    for address in sorted(trace_bytes):
        if not trace_ranges or address != trace_ranges[-1][1]:
            trace_ranges.append([address, address + 1])
        else:
            trace_ranges[-1][1] += 1
    report = {
        "status": "PASS",
        "cases": len(comparisons),
        "distinct_original_instruction_bytes": len(trace_bytes),
        "original_image_sha256": BLOB_SHA,
        "source_elf_sha256": sha(args.elf),
        "source_sha256": {
            str((ROOT / "g2/components/bootloader/thread_creation" / name).relative_to(ROOT)):
                sha(ROOT / "g2/components/bootloader/thread_creation" / name)
            for name in ["timer_commands.c", "timer_commands.h", "timer_wait.c",
                         "timer_wait.h", "queue_receive.c", "queue_receive.h"]
        },
        "runtime_source_sha256": {
            str((ROOT / name).relative_to(ROOT)): sha(ROOT / name)
            for name in ["g2/components/bootloader/thread_creation/kernel_runtime.c",
                         "g2/components/bootloader/queue/runtime_mode.c"]
        },
        "fixture_sha256": {name: sha(HERE / name) for name in
                            ["verify_timer_commands.py", "fixture_providers.c", "module.ld"]},
        "original_trace_ranges": [[hex(start), hex(end)] for start, end in trace_ranges],
        "comparisons": comparisons,
        "limits": [
            "Stock processor, queue-get (0x41a114), queue ring-copy, kernel critical enter/exit, timer sampling (0x4194e2), active-item unlink (0x41b5a8), timer insertion (0x419508), and reload (0x4193de) execute from the image. The source profile runs queue_receive.c, kernel_runtime.c, runtime_mode.c, and timer_wait.c. Dynamic free at 0x419830 is intercepted at entry and compared with an observation stub.",
            "Synthetic 32-bit tick values and coherent queue/list storage only; no physical time, interrupt scheduling, expiration (0x419406), rollover (0x41965c), or hardware behavior is asserted.",
            "Timer state bit2 is the reload dispatch test in the command processor and constructor; timer expiry uses the same LSLS #29/sign-test pattern.",
            "This is a source-vs-image semantic differential, not byte equality or complete firmware source reproduction."
        ]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ["status", "cases", "distinct_original_instruction_bytes"]}))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Bounded original-vs-source execution for four bootloader queue wrappers.

Kernel queue providers and the runtime-state helper are intercepted at their
exact stock BL entries. Original wrapper/context instructions execute; provider
behavior is deterministic synthetic input. No device/hardware interaction.
"""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "bootverify", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

v.ENTRIES.update({
    "queue_context": 0x41602A,
    "queue_create": 0x416816,
    "queue_put": 0x4168A2,
    "queue_get": 0x416920,
})

CONTEXT_MODE = 0x418B56
CREATE_STATIC = 0x419C9C
CREATE_DYNAMIC = 0x419D08
PUT_BLOCKING = 0x419EC0
PUT_ISR = 0x41A024
GET_BLOCKING = 0x41A114
GET_ISR = 0x41A3B0
ICSR = 0xE000ED04
DATA = 0x20005000
QUEUE = 0x20006000


class QueueMachine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        if source:
            aliases = {
                "queue_context": "opencfw_bl_queue_is_nonblocking_context",
                "queue_create": "opencfw_bl_queue_create",
                "queue_put": "opencfw_bl_queue_put",
                "queue_get": "opencfw_bl_queue_get",
            }
            for short, symbol in aliases.items():
                self.symbols["opencfw_boot_" + short] = self.symbols[symbol]
        self.ctx_mode = 0
        self.kernel_result = 1
        self.handle_result = QUEUE
        self.woken_result = 0
        self.provider_events = []

    def code(self, uc, pc, size, user):
        r0, r1, r2, r3 = self.args()
        if pc == CONTEXT_MODE:
            self.events.append(["context_mode", self.ctx_mode])
            self.ret(self.ctx_mode)
            return
        if pc == CREATE_DYNAMIC:
            self.events.append(["create_dynamic", r0, r1, r2])
            self.ret(self.handle_result)
            return
        if pc == CREATE_STATIC:
            sp = uc.reg_read(v.a.UC_ARM_REG_SP)
            fifth = self.u(sp)
            self.events.append(["create_static", r0, r1, r2, r3, fifth])
            self.ret(self.handle_result)
            return
        if pc == PUT_BLOCKING:
            self.events.append(["put_blocking", r0, r1, r2, r3])
            self.ret(self.kernel_result)
            return
        if pc == PUT_ISR:
            self.events.append(["put_isr", r0, r1, r3])
            self.w(r2, self.woken_result)
            self.ret(self.kernel_result)
            return
        if pc == GET_BLOCKING:
            self.events.append(["get_blocking", r0, r1, r2])
            self.ret(self.kernel_result)
            return
        if pc == GET_ISR:
            self.events.append(["get_isr", r0, r1])
            self.w(r2, self.woken_result)
            self.ret(self.kernel_result)
            return
        super().code(uc, pc, size, user)

    def invoke(self, name, args, fixture):
        self.ctx_mode = fixture.get("ctx_mode", 0)
        self.kernel_result = fixture.get("kernel_result", 1)
        self.handle_result = fixture.get("handle_result", QUEUE)
        self.woken_result = fixture.get("woken", 0)
        self.provider_events = []
        self.cpu.reg_write(v.a.UC_ARM_REG_PRIMASK, fixture.get("primask", 0))
        self.cpu.reg_write(v.a.UC_ARM_REG_BASEPRI, fixture.get("basepri", 0))
        self.w(ICSR, fixture.get("icsr_initial", 0))
        if name == "queue_create" and args[2]:
            self.cpu.mem_write(args[2], struct.pack(
                "<IIIIII", 0, 0, *fixture["attrs"]))
        if name == "queue_get" and args[2]:
            self.w(args[2], fixture.get("priority_initial", 0xA5A5A5A5))
        result = self.run(name, args)
        result["icsr"] = self.u(ICSR)
        if name == "queue_get" and args[2]:
            result["priority_out"] = self.u(args[2])
        return result


def compare(name, args, fixture, segments, symbols, cases, trace):
    machines = [QueueMachine(), QueueMachine(True, segments, symbols)]
    results = [m.invoke(name, args, fixture) for m in machines]
    keys = ["return", "events", "icsr"]
    if name == "queue_get" and args[2]:
        keys.append("priority_out")
    left = {k: results[0][k] for k in keys}
    right = {k: results[1][k] for k in keys}
    assert left == right, (name, args, fixture, left, right)
    trace.update(machines[0].trace)
    cases.append({"function": name, "arguments": args, "fixture": fixture,
                  "observed": left})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    _, segments, symbols = v.elf.elf_info(args.elf)
    cases, trace = [], {}

    for fixture in [{}, {"ctx_mode": 1}, {"ctx_mode": 2},
                    {"primask": 1}, {"basepri": 0x20},
                    {"ctx_mode": 1, "primask": 1, "basepri": 0x20}]:
        compare("queue_context", [], fixture, segments, symbols, cases, trace)

    attrs_ptr = DATA + 0x400
    attr_rows = [
        (None, None),
        ((DATA + 0x100, 0x50, DATA + 0x200, 24), "static"),
        ((0, 0, 0, 0), "dynamic"),
        ((DATA + 0x100, 0x4F, DATA + 0x200, 24), "invalid-small-cb"),
        ((DATA + 0x100, 0x50, DATA + 0x200, 23), "invalid-small-mq"),
        ((0, 0x50, 0, 0), "invalid-partial"),
        ((DATA + 0x100, 0x50, DATA + 0x200, 0), "invalid-partial"),
        ((DATA + 0x100, 0x50, DATA + 0x200, 0), "wrapped-product"),
    ]
    for (fields, label) in attr_rows:
        if label == "wrapped-product":
            count, item_size, mq_size = 0x10000, 0x10000, 0
        else:
            count, item_size, mq_size = 3, 8, fields[3] if fields else 0
        args3 = 0 if fields is None else attrs_ptr
        f = {} if fields is None else {"attrs": fields}
        f["label"] = label
        compare("queue_create", [count, item_size, args3], f,
                segments, symbols, cases, trace)
    for count, item_size in [(0, 8), (3, 0)]:
        compare("queue_create", [count, item_size, 0], {},
                segments, symbols, cases, trace)
    compare("queue_create", [1, 8, 0], {"ctx_mode": 1},
            segments, symbols, cases, trace)

    for name in ["queue_put", "queue_get"]:
        for fixture, timeout in [({}, 0), ({}, 9), ({}, 0xFFFFFFFF),
                                  ({"ctx_mode": 1}, 0),
                                  ({"primask": 1}, 0), ({"basepri": 0x20}, 0)]:
            for kernel_result in [1, 0]:
                f = dict(fixture, kernel_result=kernel_result, woken=1)
                if name == "queue_put":
                    params = [QUEUE, DATA, 0xA5, timeout]
                else:
                    params = [QUEUE, DATA, DATA + 0x300, timeout]
                    f["priority_initial"] = 0xA5A5A5A5
                compare(name, params, f, segments, symbols, cases, trace)
        invalid = [0, DATA, 0, 0] if name == "queue_put" else [QUEUE, 0, 0, 0]
        compare(name, invalid, {}, segments, symbols, cases, trace)
        if name == "queue_put":
            compare(name, [QUEUE, DATA, 0, 5], {"ctx_mode": 1},
                    segments, symbols, cases, trace)
        else:
            compare(name, [QUEUE, DATA, DATA + 0x300, 5], {"ctx_mode": 1},
                    segments, symbols, cases, trace)

    used = {int(pc, 0) + i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    out = {
        "status": "PASS",
        "cases": len(cases),
        "per_function": {name: sum(c["function"] == name for c in cases)
                         for name in v.ENTRIES if name.startswith("queue_")},
        "original_sha256": v.SHA,
        "elf_sha256": v.sha(args.elf),
        "source_sha256": {p.name: v.sha(p) for p in HERE.iterdir()
                          if p.suffix in [".c", ".h", ".ld", ".py"]},
        "distinct_original_instruction_bytes": len(used),
        "original_trace": trace,
        "comparisons": cases,
        "limits": [
            "Only original wrapper/context instructions execute; kernel queue providers and runtime-mode helper are intercepted at their exact local entries.",
            "PRIMASK and BASEPRI paths are exercised; a nonzero IPSR was not injected by this fixture.",
            "Timeout is forwarded unchanged. Unit conversion/kernel tick frequency are outside this wrapper evidence.",
            "ICSR is synthetic mapped memory; no physical interrupt controller is touched.",
            "No kernel scheduling, queue storage mutation, real ISR wakeup, or runtime behavior is claimed.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"status": out["status"], "cases": out["cases"],
                      "per_function": out["per_function"],
                      "distinct_original_instruction_bytes": len(used)}, indent=2))


if __name__ == "__main__":
    main()

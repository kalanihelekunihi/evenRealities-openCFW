#!/usr/bin/env python3
"""Compare the stock enable body with its readable source under Unicorn.

Only mspi_cq_init is intercepted; its target/arguments/order are recorded.
The memory-mapped CQCFG page is synthetic RAM, and no hardware is accessed.
"""
import argparse
import hashlib
import importlib.util
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "bootverify", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

ENTRY = 0x425066
CQ_INIT = 0x423F28
HANDLE = 0x20010000
MSPI_BASE = 0x40060000
MSPI_SPAN = 0x4000
STATE_SPAN = 0x8D0
v.ENTRIES["enable"] = ENTRY


class EnableMachine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        self.cpu.mem_map(MSPI_BASE, MSPI_SPAN)
        if source:
            self.symbols["opencfw_boot_enable"] = self.symbols[
                "opencfw_bl_mspi_enable"]
            self.cq_init_address = self.symbols["mspi_cq_init"] & ~1
        else:
            self.cq_init_address = CQ_INIT
        self.provider_calls = []

    def code(self, uc, pc, size, user):
        if pc == self.cq_init_address:
            args = self.args()
            self.provider_calls.append(args[:3])
            self.ret(0)
            return
        super().code(uc, pc, size, user)

    def setup(self, case):
        state = bytearray(((i * 37 + 11) ^ 0xA5) & 0xFF
                          for i in range(STATE_SPAN))
        prefix = 0x01BEBEBE
        if case.get("bad_magic"):
            prefix ^= 1
        if case.get("uninitialized"):
            prefix &= ~0x01000000
        if case.get("already_enabled"):
            prefix |= 0x02000000
        state[0:4] = prefix.to_bytes(4, "little")
        module = case.get("module", 0)
        state[4:8] = module.to_bytes(4, "little")
        state[8] = 0 if case.get("unconfigured") else 1
        state[0x14:0x18] = case.get("queue_argument", 0x13579BDF).to_bytes(4, "little")
        context = case.get("queue_context", 0 if case.get("no_queue") else 0x20023400)
        state[0x18:0x1C] = context.to_bytes(4, "little")
        self.cpu.mem_write(HANDLE, bytes(state))
        self.cpu.mem_write(MSPI_BASE, b"\xA5" * MSPI_SPAN)
        self.provider_calls = []

    def invoke(self, case):
        self.setup(case)
        result = self.run("enable", [0 if case.get("null_handle") else HANDLE])
        return {
            "return": result["return"],
            "providers": self.provider_calls,
            "state": bytes(self.cpu.mem_read(HANDLE, STATE_SPAN)).hex(),
            "mspi": bytes(self.cpu.mem_read(MSPI_BASE, MSPI_SPAN)).hex(),
        }


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    assert sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)

    cases = [
        {"null_handle": True},
        {"bad_magic": True},
        {"uninitialized": True},
        {"unconfigured": True},
        {"no_queue": True},
        {"no_queue": True, "already_enabled": True},
        {"module": 0},
        {"module": 1, "queue_argument": 0x20045600,
         "queue_context": 0x20046700},
        {"module": 2, "already_enabled": True,
         "queue_argument": 0x20057800, "queue_context": 0x20058900},
    ]
    comparisons = []
    trace = {}
    machines = [EnableMachine(), EnableMachine(True, segments, symbols)]
    for case in cases:
        results = [m.invoke(case) for m in machines]
        if results[0] != results[1]:
            before = bytes.fromhex(results[0]["state"])
            after = bytes.fromhex(results[1]["state"])
            original_mspi = bytes.fromhex(results[0]["mspi"])
            source_mspi = bytes.fromhex(results[1]["mspi"])
            raise AssertionError({
                "case": case,
                "return": [results[0]["return"], results[1]["return"]],
                "provider_calls": [results[0]["providers"], results[1]["providers"]],
                "state_diff": [(i, before[i], after[i])
                               for i in range(STATE_SPAN) if before[i] != after[i]],
                "mspi_diff": [(i, original_mspi[i], source_mspi[i])
                              for i in range(MSPI_SPAN)
                              if original_mspi[i] != source_mspi[i]],
            })
        trace.update(machines[0].trace)
        comparisons.append({"case": case, "observed": results[0]})

    used = {int(pc, 0) + i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    source_files = [p for p in HERE.iterdir()
                    if p.is_file() and p.suffix in {".c", ".h", ".ld", ".py"}]
    source_files.append(ROOT / "g2/components/foundation/ambiq_mspi/ambiq_mspi_compat.h")
    output = {
        "status": "PASS",
        "cases": len(comparisons),
        "original_sha256": v.SHA,
        "original_function_range": ["0x00425066", "0x004250f0"],
        "original_function_sha256": "3e8eafec68e5f33ec128fd64c1386692323e9b175993c267d6a2bb7ec3ac155c",
        "elf_sha256": sha(args.elf),
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in source_files},
        "distinct_original_instruction_bytes": len(used),
        "original_trace": trace,
        "comparisons": comparisons,
        "limits": [
            "The mspi_cq_init provider is intercepted and records arguments only; no queue is initialized.",
            "CQCFG is synthetic RAM; no peripheral, clock, DMA, or hardware behavior is modeled.",
            "The sparse state comparison covers 0x8d0 bytes; newly named offsets are grounded in this function's stock loads/stores, not a complete semantic HAL state model.",
            "This validates the 138-byte enable function only, not neighboring MSPI APIs, startup, or byte-identical firmware reconstruction."
        ]
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({k: output[k] for k in
                      ["status", "cases", "distinct_original_instruction_bytes"]}))


if __name__ == "__main__":
    main()

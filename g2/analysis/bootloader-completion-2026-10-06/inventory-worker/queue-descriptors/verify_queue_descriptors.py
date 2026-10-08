#!/usr/bin/env python3
"""Original/source differential for three finite Apollo CMDQ helpers."""
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
ADDR = {"alloc": 0x42790A, "post": 0x4279F0, "reset": 0x427BAA}
RANGE_END = {"alloc": 0x4279BD, "post": 0x427A55, "reset": 0x427C11}
SYMBOL = {"alloc": "opencfw_provider_42790a",
          "post": "opencfw_provider_4279f0",
          "reset": "opencfw_provider_427baa"}
for name, address in ADDR.items():
    v.ENTRIES["qd_" + name] = address

Q, OPS, BUFFER = 0x20006000, 0x20007000, 0x20010000
MMIO = 0x40000000


class Machine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        self.cpu.mem_map(MMIO, 0x10000)
        if source:
            critical = v.BLOB.read_bytes()[0x41B8EC-v.BASE:0x41B8F4-v.BASE]
            self.cpu.mem_write(0x41B8EC, critical)
            self.exec_ranges.append((0x41B8EC, 0x41B8F4))
            for name, symbol in SYMBOL.items():
                self.symbols["opencfw_boot_qd_" + name] = self.symbols[symbol]

    def put32(self, address, value):
        self.cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))

    def get32(self, address):
        return struct.unpack("<I", self.cpu.mem_read(address, 4))[0]

    def setup(self, mode, *, flags=0x01CDCDCD, write=0, producer=0,
              current=0, end_index=0, low=0, count=1,
              read_address=BUFFER+0x1000, read_front=BUFFER+0x800):
        # q words correspond to the exact offsets read/written by the helpers.
        q = [flags, BUFFER, read_address, read_front,
             BUFFER + write, BUFFER + producer, 0x1000, current,
             end_index, OPS, 0]
        self.cpu.mem_write(Q, struct.pack("<11I", *q))
        # Resource-like row. Each field names a synthetic peripheral register.
        row = [MMIO+0x10, MMIO+0x14, MMIO+0x18, MMIO+0x1c,
               MMIO+0x20, 0x4000, 0, 0x55aa, 0, 0]
        self.cpu.mem_write(OPS, struct.pack("<10I", *row))
        self.put32(MMIO+0x10, 0xffffffff)
        self.put32(MMIO+0x14, read_front)
        self.put32(MMIO+0x18, low)
        self.put32(MMIO+0x1c, 0x87654321)
        self.put32(MMIO+0x20, 0)
        return (Q, count, 0x20008000, 0x20008004) if mode == "alloc" else \
            ((Q, 1) if mode == "post" else (Q,))

    def state(self):
        return {"queue": bytes(self.cpu.mem_read(Q, 44)),
                "buffer": bytes(self.cpu.mem_read(BUFFER, 0x1000)),
                "ops": bytes(self.cpu.mem_read(OPS, 40)),
                "outputs": bytes(self.cpu.mem_read(0x20008000, 8)),
                "mmio": bytes(self.cpu.mem_read(MMIO, 0x100))}

    def invoke(self, name, args):
        return self.run("qd_" + name, list(args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    fixtures = {
        "post": [
            {"flags": 0x01CDCDCD, "write": 0, "producer": 8,
             "current": 4, "end_index": 9, "low": 0x12340002},
            {"flags": 0x01CDCDCD, "write": 0, "producer": 8,
             "current": 4, "end_index": 9, "low": 0x12340002,
             "read_address": 0x20080000},
            {"flags": 0x01CDCDCD, "write": 0, "producer": 0,
             "current": 0, "end_index": 0, "low": 0},
            {"flags": 0, "write": 0, "producer": 8,
             "current": 1, "end_index": 9, "low": 0},
        ],
        "alloc": [
            {"flags": 0x01CDCDCD, "write": 0, "producer": 0,
             "current": 4, "end_index": 4, "low": 4, "count": 3},
            {"flags": 0x01CDCDCD, "write": 0x800, "producer": 0x800,
             "current": 4, "end_index": 4, "low": 4, "count": 2},
            {"flags": 0x01CDCDCD, "write": 0xff0, "producer": 0xff0,
             "current": 4, "end_index": 4, "low": 4, "count": 1},
            {"flags": 0x01CDCDCD, "write": 0, "producer": 8,
             "current": 4, "end_index": 4, "low": 4, "count": 1},
            {"flags": 0x01CDCDCD, "write": 0, "producer": 0,
             "current": 0, "end_index": 4, "low": 4, "count": 255},
            {"flags": 0x01CDCDCD, "write": 0, "producer": 0,
             "current": 255, "end_index": 0, "low": 0, "count": 2},
            {"flags": 0x01CDCDCD, "write": 0, "producer": 0,
             "current": 0, "end_index": 0, "low": 0, "count": 0},
            {"flags": 0x01CDCDCD, "write": 0, "producer": 0,
             "current": 0, "end_index": 0, "low": 0, "count": 1,
             "pointer_null": True},
            {"flags": 0, "write": 0, "producer": 0,
             "current": 0, "end_index": 0, "low": 0, "count": 1},
        ],
        "reset": [
            {"flags": 0x01CDCDCD, "write": 0x28, "producer": 0x48,
             "current": 0x400, "end_index": 7, "low": 0x12},
            {"flags": 0x03CDCDCD, "write": 0, "producer": 0,
             "current": 0, "end_index": 0, "low": 0},
            {"flags": 0, "write": 0, "producer": 0,
             "current": 0, "end_index": 0, "low": 0},
        ],
    }
    result_cases, trace = [], {}
    for name, selected in fixtures.items():
        for fixture in selected:
            pointer_null = bool(fixture.get("pointer_null", False))
            fixture = {k: v for k, v in fixture.items() if k != "pointer_null"}
            machines = [Machine(), Machine(True, segments, dict(symbols))]
            callargs = []
            for machine in machines:
                callargs.append(machine.setup(name, **fixture))
            if pointer_null:
                callargs = [tuple(list(a[:2]) + [0] + list(a[3:]))
                            if name == "alloc" else a for a in callargs]
            results = [m.invoke(name, a) for m, a in zip(machines, callargs)]
            states = [m.state() for m in machines]
            # The v.Machine snapshots include caller-visible incidental R0 and
            # common harness state; here return values are part of the ABI.
            assert results[0]["return"] == results[1]["return"], (name, fixture, results)
            assert states[0] == states[1], (name, fixture,
                                             {k: [s[k].hex() for s in states]
                                              for k in states[0]
                                              if states[0][k] != states[1][k]})
            trace.update(machines[0].trace)
            result_cases.append({"function": name, "fixture": fixture,
                                 "return": results[0]["return"],
                                 "state_sha256": hashlib.sha256(
                                     b"".join(states[0].values())).hexdigest()})
    used = {int(pc, 0)+i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    blob = v.BLOB.read_bytes()
    source_files = [HERE / "verify_queue_descriptors.py",
                    HERE / "Makefile", HERE / "module.ld",
                    ROOT / "g2/components/bootloader/nor_mspi_queue/queue_descriptors.c",
                    ROOT / "g2/components/bootloader/nor_mspi_queue/queue_descriptors.h"]
    result = {"status": "PASS", "cases": len(result_cases),
              "distinct_original_instruction_bytes": len(used),
              "original_sha256": v.SHA,
              "stock_ranges": {name: hex(address) for name, address in ADDR.items()},
              "stock_range_sha256": {name: hashlib.sha256(
                  blob[ADDR[name]-v.BASE:RANGE_END[name]-v.BASE+1]).hexdigest()
                  for name in ADDR},
              "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(
                  path.read_bytes()).hexdigest() for path in source_files},
              "source_elf_sha256": v.sha(args.elf),
              "cases_detail": result_cases,
              "limits": ["Queue state and MMIO are synthetic; no device was accessed.",
                         "The helpers allocate/post/reset descriptors only; they do not demonstrate physical CQ execution or completion."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k: result[k] for k in ("status", "cases",
                                              "distinct_original_instruction_bytes")}, indent=2))


if __name__ == "__main__":
    main()

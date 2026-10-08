#!/usr/bin/env python3
"""Compare the source initializer runner and qsort with locked-image execution."""
import argparse
import hashlib
import importlib.util
import json
import random
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location(
    "bootv", ROOT / "g2/components/bootloader/update_core/verify.py"
)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
v.ENTRIES["init_table"] = 0x41F9F8
v.ENTRIES["init_priority_compare"] = 0x41F9F0

TABLE = 0x433440
SCRATCH = 0x20022E00
INPUT = 0x20010000
STOP = v.STOP
CALLBACKS = {
    0x2003F001: "A",
    0x2003F101: "B",
    0x2003F201: "C",
    0x2003F301: "D",
    0x4301D7: "platform-sequence",
    0x43194D: "services",
    0x415591: "redirect",
    0x41FD71: "allocator",
}


def packed(rows):
    return b"".join(struct.pack("<II", callback, priority)
                    for callback, priority in rows)


class InitMachine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        self.events = []
        self.trace = {}
        self.sorted_records = None
        self.finish = False

    def code(self, uc, pc, size, _):
        if pc == STOP:
            self.finish = True
            uc.emu_stop()
            return
        if pc in {address & ~1 for address in CALLBACKS}:
            address = pc | 1
            self.events.append(CALLBACKS[address])
            self.ret()
            return
        if not self.source:
            self.trace[hex(pc)] = bytes(uc.mem_read(pc, size)).hex()
            if pc == 0x41FA26:
                count = (self.u(0x41FA44) - self.u(0x41FA40)) // 8
                count = min(count, 256)
                self.sorted_records = bytes(uc.mem_read(SCRATCH, count * 8))
        else:
            assert any(lo <= pc < hi for lo, hi in self.exec_ranges), (
                "source machine reached code outside its ELF or named cuts", hex(pc)
            )
        super().code(uc, pc, size, _)

    def run_entry(self, entry, args):
        self.finish = False
        self.events = []
        for reg, value in zip(
                [v.a.UC_ARM_REG_R0, v.a.UC_ARM_REG_R1,
                 v.a.UC_ARM_REG_R2, v.a.UC_ARM_REG_R3], args + [0] * 4):
            self.cpu.reg_write(reg, value)
        self.cpu.reg_write(v.a.UC_ARM_REG_SP, v.SP)
        self.cpu.reg_write(v.a.UC_ARM_REG_LR, STOP | 1)
        self.cpu.emu_start(entry | 1, STOP + 2, count=2_000_000)
        assert self.finish, ("execution budget", hex(entry), hex(
            self.cpu.reg_read(v.a.UC_ARM_REG_PC)))
        return self.cpu.reg_read(v.a.UC_ARM_REG_R0)


def make_stock(rows, segments=(), symbols=None):
    m = InitMachine()
    m.w(0x41FA40, TABLE)
    m.w(0x41FA44, TABLE + len(rows) * 8)
    if rows:
        m.cpu.mem_write(TABLE, packed(rows))
    return m


def make_source(rows, segments, symbols):
    m = InitMachine(True, segments, symbols)
    raw = packed(rows)
    if raw:
        m.cpu.mem_write(INPUT, raw)
    return m


def run_rows(rows, segments, symbols, label):
    stock = make_stock(rows)
    stock.run_entry(0x41F9F8, [])
    assert stock.sorted_records is not None, (label, "stock qsort result not observed")
    source = make_source(rows, segments, symbols)
    source.run_entry(symbols["opencfw_boot_init_table_run"],
                     [INPUT, INPUT + len(rows) * 8])
    assert source.events == stock.events, (label, stock.events, source.events)
    # The source runner is expected to use fixed scratch and visit qsort output.
    assert bytes(source.cpu.mem_read(SCRATCH, min(len(rows), 256) * 8)) == stock.sorted_records
    return {
        "name": label,
        "input_records": len(rows),
        "effective_records": min(len(rows), 256),
        "callback_order": stock.events,
        "stock_qsort_output_sha256": hashlib.sha256(stock.sorted_records).hexdigest(),
        "source_sort_matches_stock": bytes(source.cpu.mem_read(
            SCRATCH, min(len(rows), 256) * 8)) == stock.sorted_records,
    }, stock


def run_fixed_table(segments, symbols):
    rows = [
        (0x4301D7, 1), (0x43194D, 1),
        (0x415591, 25), (0x41FD71, 26),
    ]
    raw = packed(rows)
    stock = make_stock(rows)
    stock.run_entry(0x41F9F8, [])
    assert stock.sorted_records == raw
    source = InitMachine(True, segments, symbols)
    source.cpu.mem_write(TABLE, raw)
    source.run_entry(symbols["opencfw_boot_init_table_default"], [])
    source_sorted = bytes(source.cpu.mem_read(SCRATCH, len(raw)))
    assert source_sorted == raw, ("fixed source table order", source_sorted.hex())
    assert source.events == stock.events
    return {
        "name": "locked-fixed-table-noarg-entry",
        "input_records": len(rows),
        "effective_records": len(rows),
        "callback_order": stock.events,
        "stock_qsort_output_sha256": hashlib.sha256(raw).hexdigest(),
        "source_sort_matches_stock": True,
    }, stock


def compare_pair(segments, symbols, left, right):
    data = struct.pack("<II", 0, left) + struct.pack("<II", 0, right)
    stock = InitMachine()
    source = InitMachine(True, segments, symbols)
    for m in (stock, source):
        m.cpu.mem_write(INPUT, data)
    stock_value = stock.run_entry(0x41F9F0, [INPUT, INPUT + 8])
    source_value = source.run_entry(symbols["opencfw_boot_init_priority_compare"],
                                    [INPUT, INPUT + 8])
    assert stock_value == source_value, (left, right, stock_value, source_value)
    return {"left_priority": left, "right_priority": right,
            "return_u32": stock_value}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    for name in ("opencfw_boot_init_table_run", "opencfw_boot_init_table_default",
                 "opencfw_boot_init_priority_compare"):
        assert name in symbols, ("missing source symbol", name)

    cases = []
    trace = {}
    fixtures = [
        ("locked-four-record-table", [
            (0x2003F001, 1), (0x2003F101, 1),
            (0x2003F201, 25), (0x2003F301, 26),
        ]),
        ("equal-priorities-and-null-callbacks", [
            (0x2003F001, 3), (0, 2), (0x2003F101, 3),
            (0x2003F201, 1), (0, 3), (0x2003F301, 2), (0x2003F101, 1),
        ]),
        ("empty-table", []),
        ("count-cap-257", [
            (0x2003F001, i) for i in range(256)
        ] + [(0x2003F301, 0)]),
    ]
    for name, rows in fixtures:
        record, stock = run_rows(rows, segments, symbols, name)
        trace.update(stock.trace)
        cases.append(record)
    record, stock = run_fixed_table(segments, symbols)
    cases.append(record)
    trace.update(stock.trace)

    qsort_inputs = [
            ("one-record", [5]),
            ("insertion-cutoff-32", [((i * 17) + 3) % 23 for i in range(32)]),
            ("quicksort-cutoff-33-equal", [7] * 33),
            ("median3-41-mixed", [i % 7 for i in range(41)]),
            ("median9-42-mixed", [i % 7 for i in range(42)]),
            ("median9-64-all-equal", [9] * 64),
            ("median9-64-mixed", [((i * 13) + (i // 3)) % 11 for i in range(64)]),
            ("median9-128-mixed", [((i * 29) + (i // 7)) % 17 for i in range(128)]),
    ]
    # Exercise both sides of the cutoff and median sampling thresholds with
    # reproducible orderings, including duplicate-heavy inputs.
    qsort_rng = random.Random(0x423A48)
    for count in [2, 31, 32, 33, 34, 40, 41, 42, 47, 63, 64, 65,
                  96, 127, 128, 129, 255, 256]:
        qsort_inputs.extend([
            (f"{count}-ascending", list(range(count))),
            (f"{count}-descending", list(range(count - 1, -1, -1))),
            (f"{count}-random-unique", qsort_rng.sample(range(count), count)),
            (f"{count}-random-seven-keys",
             [qsort_rng.randrange(7) for _ in range(count)]),
            (f"{count}-random-two-keys",
             [qsort_rng.randrange(2) for _ in range(count)]),
        ])
    qsort_cases = []
    for name, keys in qsort_inputs:
        rows = [(0x2003F001 + (i << 1), key) for i, key in enumerate(keys)]
        stock = make_stock(rows)
        stock.run_entry(0x423D08, [TABLE, len(rows), 8,
                                   0x41F9F1])
        expected = bytes(stock.cpu.mem_read(TABLE, len(rows) * 8))
        source = make_source(rows, segments, symbols)
        source.run_entry(symbols["opencfw_boot_init_sort"],
                         [INPUT, len(rows), 8,
                          symbols["opencfw_boot_init_priority_compare"]])
        actual = bytes(source.cpu.mem_read(INPUT, len(rows) * 8))
        assert actual == expected, (name, expected.hex(), actual.hex())
        qsort_cases.append({
            "name": name,
            "count": len(rows),
            "input_key_sha256": hashlib.sha256(packed(rows)).hexdigest(),
            "sorted_record_sha256": hashlib.sha256(expected).hexdigest(),
            "stock_source_exact_record_match": True,
        })
        trace.update(stock.trace)

    comparator_cases = [
        compare_pair(segments, symbols, 0, 0),
        compare_pair(segments, symbols, 1, 3),
        compare_pair(segments, symbols, 3, 1),
        compare_pair(segments, symbols, 0xFFFFFFFF, 1),
        compare_pair(segments, symbols, 0, 0x80000000),
    ]
    used = {int(pc, 0) + i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    sources = [p for p in HERE.iterdir()
               if p.suffix in {".c", ".h", ".S", ".ld", ".py", ""}
               and p.name != "__pycache__"]
    report = {
        "status": "PASS",
        "cases": len(cases),
        "qsort_cases": qsort_cases,
        "comparator_cases": comparator_cases,
        "original_sha256": v.SHA,
        "elf_sha256": v.sha(args.elf),
        "source_sha256": {str(p.name): v.sha(p) for p in sources if p.is_file()},
        "distinct_original_trace_bytes": len(used),
        "original_trace": trace,
        "comparisons": cases,
        "limits": [
            "The locked image executes 0x41f9f8 and original qsort/comparator instructions directly; the compiled source executes its own runner, qsort, comparator, and null-skip/callback loop without stock-code execution or a qsort provider cut.",
            "qsort differential cases compare complete eight-byte records for deterministic sorted, reverse, random unique, duplicate-heavy, and equal-key inputs from counts 1 through 256, including the insertion cutoff and median-of-nine boundary. They do not establish byte identity or exhaust every qsort input/record width.",
            "Callback entries are synthetic test functions: RAM entries for isolated runner cases and external cuts at the locked callback addresses for the fixed-table test. The callback bodies are covered separately in initializer-callbacks; the allocator callback is covered separately by the allocator component. No peripheral, hardware startup, or complete bootloader source/byte identity claim is made.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "cases": report["cases"],
                      "comparator_cases": len(comparator_cases),
                      "distinct_original_trace_bytes": len(used)}, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Bounded original/source sort comparison across native 128-byte chunk edges."""
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = ROOT / "g2/components/bootloader/init_table"
spec = importlib.util.spec_from_file_location("init_verify", HERE / "verify_init_table.py")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

elf = ROOT / "g2/build/bootloader-completion/init-table-wide-review/qsort.elf"
_, segments, symbols = mod.v.elf.elf_info(elf)
class CountingMachine(mod.InitMachine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        self.comparisons = 0
        self.compare_call_sites = Counter()
        self.compare_trace = []
        self.record_width = 0
        self.compare_pc = ((symbols or {}).get('opencfw_boot_init_priority_compare',0) & ~1) if source else 0x41f9f0
    def code(self, uc, pc, size, user):
        if pc == self.compare_pc:
            self.comparisons += 1
            self.compare_call_sites[hex(uc.reg_read(mod.v.a.UC_ARM_REG_LR) & ~1)] += 1
            if len(self.compare_trace) < 1000:
                left = uc.reg_read(mod.v.a.UC_ARM_REG_R0)
                right = uc.reg_read(mod.v.a.UC_ARM_REG_R1)
                width = self.record_width
                self.compare_trace.append((left, right,
                    int.from_bytes(bytes(uc.mem_read(left+4,4)),'little'),
                    int.from_bytes(bytes(uc.mem_read(right+4,4)),'little'),
                    hashlib.sha256(bytes(uc.mem_read(left,width))).hexdigest() if width else '',
                    hashlib.sha256(bytes(uc.mem_read(right,width))).hexdigest() if width else '',
                    uc.reg_read(mod.v.a.UC_ARM_REG_LR) & ~1))
        super().code(uc, pc, size, user)
rows = []
for width in (8, 63, 64, 127, 128, 129, 256, 257, 384):
    for count in (2, 33, 42):
        # Every record has a unique whole-record identity while the comparator
        # sees only the priority word at byte offset 4, as in the Boot table.
        raw = bytearray(width * count)
        for i in range(count):
            key = (i * 17 + 3) % 11
            struct.pack_into("<II", raw, i * width, 0x20030001 + 2 * i, key)
            for j in range(8, width):
                raw[i * width + j] = (i * 37 + j * 13) & 255
        stock = CountingMachine()
        source = CountingMachine(True, segments, symbols)
        stock.record_width = source.record_width = width
        for machine in (stock, source):
            machine.cpu.mem_write(mod.INPUT, bytes(raw))
        stock.run_entry(0x423d08, [mod.INPUT, count, width, 0x41f9f1])
        source.run_entry(symbols["opencfw_boot_init_sort"],
                         [mod.INPUT, count, width,
                          symbols["opencfw_boot_init_priority_compare"]])
        original = bytes(stock.cpu.mem_read(mod.INPUT, len(raw)))
        rebuilt = bytes(source.cpu.mem_read(mod.INPUT, len(raw)))
        assert original == rebuilt, (width, count,
                                     hashlib.sha256(original).hexdigest(),
                                     hashlib.sha256(rebuilt).hexdigest())
        assert stock.comparisons == source.comparisons, (width, count,
                                                         stock.comparisons,
                                                         source.comparisons)
        assert [item[:6] for item in stock.compare_trace] == [item[:6] for item in source.compare_trace], (width, count)
        divergence = next((i for i,(a,b) in enumerate(zip(stock.compare_trace, source.compare_trace)) if a[:6]!=b[:6]), min(len(stock.compare_trace),len(source.compare_trace)))
        rows.append({"width": width, "count": count,
                     "exact_record_match": True,
                     "compare_calls_original": stock.comparisons,
                     "compare_calls_source": source.comparisons,
                     "compare_call_sites_original": dict(stock.compare_call_sites),
                     "compare_call_sites_source": dict(source.compare_call_sites),
                     "first_comparison_divergence": divergence,
                     "comparison_window_original": stock.compare_trace[max(0,divergence-3):divergence+5] if width==8 else [],
                     "comparison_window_source": source.compare_trace[max(0,divergence-3):divergence+5] if width==8 else [],
                     "output_sha256": hashlib.sha256(original).hexdigest()})
for count in (0, 1, 2, 3, 4, 8, 32):
    stock = CountingMachine()
    source = CountingMachine(True, segments, symbols)
    stock.record_width = source.record_width = 0
    for machine in (stock, source):
        machine.cpu.mem_write(mod.INPUT, struct.pack('<II', 0x20030001, 7))
    stock.run_entry(0x423d08, [mod.INPUT, count, 0, 0x41f9f1])
    source.run_entry(symbols['opencfw_boot_init_sort'],
                     [mod.INPUT, count, 0,
                      symbols['opencfw_boot_init_priority_compare']])
    assert stock.comparisons == source.comparisons, (count, stock.comparisons, source.comparisons)
    rows.append({'width': 0, 'count': count,
                 'compare_calls': stock.comparisons, 'exact_record_match': True})
out = {"status": "PASS_BOUNDED_RECORD_AND_ORDERED_COMPARATORS",
       "original_image_sha256": mod.v.SHA,
       "source_elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
       "cases": rows,
       "limits": "27 deterministic wide-record matrices match whole-record output and ordered comparator pointer/key/full-record SHA-256 arguments, including ties and widths crossing 64, 128 and 256; seven width-zero guard/comparison-schedule cases match. No hardware execution or exhaustive comparator/width domain proof."}
path = Path(__file__).with_name("qsort-width-oracle.json")
path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"status": out["status"], "cases": len(rows)}))

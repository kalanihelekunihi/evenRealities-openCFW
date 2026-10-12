#!/usr/bin/env python3
"""Classify register branch sites in corrected-PC stock stage1.

This is a finite syntactic control-flow audit, not whole-body equivalence.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
stock = root / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage1.bin"
objdump = root / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump"
listing = subprocess.check_output([
    str(objdump), "-D", "-b", "binary", "-m", "csky", "--no-show-raw-insn",
    "--adjust-vma=0x0fffffe8", "--start-address=0x10000100",
    "--stop-address=0x10001324", str(stock),
], text=True)
observed = {}
for line in listing.splitlines():
    match = re.match(r"([0-9a-f]+):\s+(jmp|jsr)\s+(r\d+)\b", line)
    if match:
        observed[int(match.group(1), 16)] = (match.group(2), match.group(3))

table = {0x1000020c, 0x10000282, 0x10000312,
         0x10000b2c, 0x10000bf6, 0x10000cc8}
computed_calls = {0x10000d92: 0x10003100, 0x10000dc8: 0x10000100}
returns = {0x10000134, 0x1000017c, 0x100001ba, 0x100001e0,
           0x10000762, 0x10000e58, 0x10000e98, 0x10000eb4,
           0x10000ece, 0x10000eda, 0x10000f5a, 0x10000fda}
assert set(observed) == table | set(computed_calls) | returns
assert all(observed[a] == ("jmp", "r15") for a in returns)
assert all(observed[a][0] == "jmp" for a in table)
assert all(observed[a] == ("jsr", "r3") for a in computed_calls)

# The two call destinations are established by immediate construction in the
# native loader at 0x10000d8a/0x10000dc0, not by table-word coincidence.
result = {
    "result": "PASS_REGISTER_BRANCH_SITE_CENSUS",
    "stock_sha256": hashlib.sha256(stock.read_bytes()).hexdigest(),
    "runtime_address_rule": "file offset + 0x0fffffe8",
    "register_branch_sites": len(observed),
    "return_sites": [hex(x) for x in sorted(returns)],
    "table_dispatch_sites": [hex(x) for x in sorted(table)],
    "computed_calls": {hex(k): hex(v) for k, v in computed_calls.items()},
    "unclassified_register_branch_sites": [],
    "limits": [
        "Disassembler branch-site classification does not prove table range or native body effects.",
        "The stage2 entry is an interstage target; its physical loading remains a separate contract.",
    ],
}
(here / "computed-edge-census-receipt.json").write_text(json.dumps(result, indent=2) + "\n")
print(result["result"], len(observed))

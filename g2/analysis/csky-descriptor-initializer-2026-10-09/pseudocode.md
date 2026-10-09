# Conditional descriptor-table initializer 0x102058D4

Partial instruction-backed interpretation; unreviewed/not admitted. Extent
`0x102058D4–0x10205950` maps to child `0x28D0–0x294C`, payload
`0xEE60–0xEEDC`. SHA-256 is
`c13a69a60ee8e84ee09a3825ae1d2d7802a908f58b0ac5deac21c071f9d72d33`.
114 code bytes end with JMP r15 at `0x10205944`; 2-byte BKPT follows, then
two 32-bit literals at `0x10205948/0x1020594C`: `0x20027350`, `0x004100FF`.

## Candidate readable interpretation

The following assumes the decoded MULA.32.L is low-word multiply-add and
BNEZAD decrements then branches on nonzero. Those exact instruction semantics
still require manual-backed validation before this interpretation can be
admitted; no original execution is claimed. Follow-up `SEMANTICS.md` binds
the exact pinned operational definitions and observed caller ABI, resolving
the software model while retaining the manufacturer-document cross-check.

```c
/* Reconstructed candidate, not production code or authenticated SDK source. */
void initialize_rows(void)
{
    uint32_t table = 0x20027350;
    for (uint32_t row = 0; row != 10; ++row) {
        uint32_t row_base = table + row * 144;
        uint32_t next = row_base + 44;
        for (uint32_t slot = 0; slot != 8; ++slot) {
            uint32_t descriptor = row_base + slot * 12;
            store32(descriptor + 32, 0x10000 | (128 + slot));
            store32(descriptor + 36, next & 0x0fffffff);
            next += 12;
        }
        store32(row_base + 128, 0x10088);
        store32(row_base + 16, 0x004100ff);
    }
}
```

The original order is inner descriptor control word then masked pointer,
followed by row+128 and row+16 stores. The loop builds self-referential pointer
values rather than copying an input buffer. No input pointer is read. The final
register contents and preserved-register ABI must be checked against the caller
before treating this as a conventional C void function.

Observed direct BSR at `0x10205D20` is the only matching direct call in the
hash-pinned complete-XIP decode. This census does not prove global reachability
or exclude indirect callers. No source-family/configuration attribution follows
from the inferred descriptor meaning. Registered KWS and acquired AIoT did not
provide an exact constant/structure source binding in the bounded search.

## Evidence and limits

`verify.py` authenticates child/payload/tool, exact mapping, complete instruction
tiling, return/BKPT separation and both literal values. `results.json` records
actual decoder argv/exit code, integer spans, input hashes, instructions and
caller. A fresh 117-contract scope scan has no recognized overlap. The shared
load-accessor packets and adjacent existing body at `0x10205950` remain outside
this packet's count. The original sealed campaign evidence is untouched.

The useful new understanding is a fixed-address, nested descriptor initializer
with explicit constants and ordered writes. Exact MULA/BNEZAD semantics, live
address-space activation, memory/global purpose, caller ABI and independent
review remain open. These are static-recovery prerequisites; no physical
behavior, scheduler observation, executed instruction count or admission is
claimed.

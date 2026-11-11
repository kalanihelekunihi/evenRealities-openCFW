# R1 FlashDB traversal leaves in C

Four assembly helpers in `runtime/native_flashdb_iterator.c` now use C. The
outer query iterator remains assembly; its instruction-body bytes are unchanged.
The retained sector-reader and nested log-read frame contracts are not relaxed.

The C helpers preserve native ordered, conditional field reads:

- `r1_fdb_native_last_sector` (`0x6a158`) reads size/limit at database +12/+16,
  rejects a wrapping traversed-plus-size value above the limit, then reads sector
  address +4. It subtracts one size, or wraps to limit minus size.
- `r1_fdb_native_next_sector` (`0x6a194`) uses the same budget test, advances
  sector address by size, and wraps to zero when the result reaches/exceeds limit.
- `r1_fdb_native_last_tsl` (`0x6a176`) rejects sector status byte +1 only when
  equal to one. Otherwise it reads entry address +12 and requires at least
  sector address +112 before subtracting 32.
- `r1_fdb_native_next_tsl` (`0x6a1b2`) uses the same exact status test, advances
  entry address by 32, and permits equality with sector's last-entry address +20.

All arithmetic is native unsigned 32-bit arithmetic, including overflow before
comparisons. Terminal results use `UINT32_MAX`; no signed bounds or saturating
arithmetic is substituted. Packed volatile word views preserve unaligned loads
and avoid speculative field reads along early-return routes.

REA/Ghidra confirms both forward helpers. Its default analysis lacks the two
reverse-helper entries; those errors are retained without coverage credit.
Direct Thumb disassembly and execution of the locked application supply the
reverse helpers' local evidence. These observations do not establish corpus
coverage or whole-source readiness.

The actual normal C object passes 13,944 paired stock/C emulator cases without
function stubs: 3,568 for each sector helper and 3,404 for each log-entry helper.
Cases cover unsigned boundary equality, wrapping arithmetic, traversal budgets,
full status bytes, the 112-byte header/first-entry boundary, 32-byte entry stride,
unaligned records and null-pointer faults or short circuits. They compare ordered
byte/word reads, untouched record guards, R0, successful-return SP, saved
registers and interrupt masks; XPSR/IT state resets before each invocation. Two
negative controls (exclusive rather than inclusive forward entry end, and
rejecting equality in traversal budget) are rejected. These are seeded-record
checks, not complete iterator or physical-flash execution. Private stack traffic,
caller-clobbered registers/flags, arbitrary corrupted pointers and asynchronous
memory changes remain outside the evidence.

All 573 R1 units compile without failures or duplicate strong symbols. Application
imports remain 176 and bootloader imports remain 34. The manifest and every
unrelated object retain their hashes. Five official qualification profiles
compile, but only the unchanged assembly iterator qualifies; none of the new C
helpers qualifies. That assembly-only candidate was not promoted. The source
plan remains unchanged, and a fresh full hybrid application equals the locked
646,408-byte stock image: 3,881 source-built bytes, 642,279 binary pull-through
bytes and 248 resource bytes. These stored-byte provenance counts do not prove
executable-C coverage, admission of the new C into the hybrid, or full source
completeness. No G2 implementation or workflow gate changed.

See [flash-traversal-c-review.json](flash-traversal-c-review.json) for hashes,
current objects, test paths and qualification evidence.

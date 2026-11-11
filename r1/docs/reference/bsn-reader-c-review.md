# Capacity-aware C product BSN reader

`r1/src/application/board/native_product_bsn.c` supplies the BSN storage provider
used by hardware variant detection. It reads the existing 124-byte nv_r1 class
and introduces no state owner. The hardware detector now passes its actual
30-byte buffer size to `r1_product_bsn_read`. A thin `r1_product_bsn_get` native
compatibility entry retains a documented 30-byte destination requirement.

The [stock record layout and recovery validators](../correlation/NV-RECOVERY-CORRELATION.md)
reserve bytes 0..29 for the BSN and byte 30 for its length. Recovery accepts lengths
1..30; the native getter also performs a zero-byte copy for length 0. For lengths
0..30 the C reader copies the stored bytes, clipped to destination capacity.
For erased length `0xff` it preserves the stock 21-byte ff fill, also capacity-clipped.
No terminator or padding is appended, and the new API returns bytes written.
Null destinations and zero capacity return 0 without storage access.

Malformed lengths 31..254 intentionally use the same bounded erased-value
fallback. Native unchecked copies for those lengths can exceed the BSN field
and its callers' buffers; that unsafe behavior is not reproduced. The private
record starts as ff bytes, so failed or short reads without a supplied length
also produce the defined erased-value fallback. These are explicit C behaviors,
not equivalence to native overflow, private garbage or null-pointer faults.

The [machine-readable review](bsn-reader-c-review.json) records 6,128 direct
stock/C comparisons and 1,084 actual cached-class comparisons. They cover valid/
erased lengths, all byte values in checked detector positions, cache hits,
late cache changes and defined partial records. A separate 11,501 direct and
2,312 cached-class C-only checks cover capacities, every malformed length,
partial records and class-size failures. Eleven compiled defects are rejected,
followed by an unmodified cached-class rerun. Callee saves, stack guards and
interrupt masks are checked.

Another 734 comparisons execute the actual C BSN reader, detector, model selector,
calibration, IQS configuration, ports and registry across all twenty records.
This setup probe executes standard copy/fill routines; KV and device callbacks
are prepared models. The leaf/cached-class error-path probes model copy/fill.
The [REA review](bsn-reader-rea-review.json) pins the getter bytes and pseudocode
and identifies the three resolved direct callers; static analysis may omit
indirect callers. Future smaller legacy buffers must use the bounded API.

An early loop-based probe exhibited a skipped return with a global Unicorn
memory-read observer. Limiting that observer to the mutable configuration range
lets the same original object pass all 734 setup cases. The final implementation
uses bounded bulk copies and also passes with actual memory routines. This is
probe evidence, not a physical fault claim or a firmware memory-library change.

The normal build compiles 840 units (758 application, 82 bootloader), with 74
application imports and 22 bootloader linker imports. One import closes without
adding imports. All 836 prior nongenerated objects outside the detector unit
remain unchanged; only that unit's detector text section changes, while its
existing cache owners remain identical. The R1 manifest check passes. Global
`make sources-check` still reports the pre-existing unlisted G2
`resident_rom_thumb_set.S`. Final linking, runtime placement, physical timing
and device boot remain unverified. Byte identity is not required.

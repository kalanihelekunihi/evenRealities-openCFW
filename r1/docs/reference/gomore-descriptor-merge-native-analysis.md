# R1 descriptor merge: native memory and FP contract

REA identifies the 158-byte routine at `0x72024`. The native interface has
seven integer arguments: output, initial start, unused timezone, bypass,
previous descriptor, addition descriptor and profile. The existing portable
helper has a different ABI and boolean return. Its frontier row now records
an unresolved native route. The [receipt](gomore-descriptor-merge-native-analysis.json)
binds REA bytes, replay, independent checks and unchanged production hashes.

The routine clears forty output bytes through the native memory-clear provider,
then writes byte 36 to 3, word 0 to the captured initial start, and byte 37 to
the low profile byte. Any nonzero bypass skips all source reads and returns 3.
There are no pointer guards. Output/source aliases therefore observe clearing
and header writes before source data is read.

On a merged path, it reloads previous word 0 and stores output word 0. It then
loads previous/addition words and stores their wrapping sums in the native
order **8, 20, 12, 16, 24**, rather than numerical offset order. Source values
are not snapshotted. It computes the wrapping sum of the count words at offset
32. Nonpositive signed totals skip both count and mean stores, leaving those
output fields as produced by clearing or intervening aliases. All completed
merged calls return the raw combined count in R0.

A positive total is stored to output+32 **before input counts are reloaded**.
With aliases, that store can change the count used for weighting while the
captured total remains the denominator. Native FP loads read previous count,
previous mean and addition mean; convert previous count signed to binary32;
multiply it by previous mean; reload/convert addition count; multiply-add the
addition mean with separate binary32 product/add rounding; convert the captured
total signed to binary32; divide; and store the mean to output+28. The native
VMLA is not a fused FMA. Integer zero total cannot reach the literal-zero FP
branch after the preceding positive-total check.

The native replay passes **2,616 cases**, including **19 matching-to-contract
faults** and 2,597 completed returns. It exercises normal output, output equal
to either source, shifted overlaps, wrapping/signed count extremes, bypass and
profile extremes, invalid pointers and 36 memory-clear return mutations. Actual
native memory clear executes. An independent sequential-memory shadow checks
header/sum/count stores, order, widths and final SRAM. Hook values are truncated
to their store width, so a byte store from register `0xffffffff` is compared as
255. Invalid-pointer effective addresses wrap to 32 bits in the shadow.

There are **2,121 FP paths** and **481 exact rational finite-result checks**.
The oracle rounds signed integer conversions, both products, addition and
division separately to binary32, using the selected rounding direction. Inputs
also include signed zero, infinities, quiet/signaling NaNs with payloads,
subnormals and maximum finite values. Seven FPSCR configurations cover all
rounding modes, FZ, DN and preexisting cumulative flags. NaN/Inf/FZ results are
recorded for future stock/C comparison without claiming a rational oracle for
them. FP context is activated with a real VLDR before assigning FPSCR, avoiding
Unicorn's lazy-context reset. Saved integer and FP registers, SP, masks,
control bits and preexisting cumulative flags are checked.

This establishes native behavior, not compiled-C equivalence or physical
hardware validation. All 667 production sources/objects, the manifest and
canonical byte-qualified plan remain unchanged; relocatable imports remain
165 application and 34 bootloader. The next implementation must preserve the
seven-argument ABI, clear-before-read aliases, unusual sum order, post-store
count reloads, raw R0 returns and FP results/flags. Any compiler arithmetic
that changes NaN selection, rounding or instruction side effects needs further
work before this native route can be promoted.

The subsequent [C review](gomore-descriptor-merge-c-review.md) implements this
ABI and verifies production C result bits, FPSCR and aliases through the
actual C engine and interval-update caller.

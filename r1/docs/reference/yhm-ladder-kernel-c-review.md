# YHM2710 charger ladder C kernel

`r1/src/application/board/native_yhm_ladder.c` now expresses selection and
register-update sequencing in ordinary C, without register variables, empty
assembly constraints or direct SP observations. It replaces the implementation
in [the earlier ladder review](yhm-ladder-c-review.md); there is one canonical
algorithm. A small naked entry retains an existing scratch span forty bytes
below incoming SP and passes it explicitly to the C kernel. That span is required
because the native read can leave its destination untouched. No default byte is
invented. The wrapper preserves normal callee-saved state, while private kernel
frames and live temporary register choices are outside the comparison contract.

The algorithm retains eight compare-absolute calls, strict earlier-entry tie
selection, unconditional register-one write, preserved low five bits and ignored
read/write statuses. The existing compare-absolute helper remains responsible
for the observed signaling NaN/FPSCR behavior. A volatile positive multiplication
intermediate preserves the stock multiply-then-subtract rounding order. Without
it, Clang moved the negation into the multiplication, changing operands in
nondefault rounding modes. This rejected variant is retained as a compiled
defect control. Volatile table reads also preserve runtime table multiplication.

Fresh REA bytes at 0x35508 match the preserved raw application image. Earlier
REA evidence in the predecessor review supplies the full code/table context;
the new byte receipt and current artifact hashes are in
[yhm-ladder-kernel-c-review.json](yhm-ladder-kernel-c-review.json).

The normal product object passes **23,872 paired stock/C cases (47,744
executions)**, covering 611 input encodings and 32 FP configurations: all rounding
modes, flush-to-zero, default-NaN and clean/sticky status. All eight helper
operands and FPSCR snapshots match, including NaNs, infinities, subnormals,
selected table points and neighboring ties. Transport cases cover byte and
full-word writes, untouched reads, raw errors and write-callback mutations.
Selected indices, transport arguments/bytes, final scratch, SP, callee-saved
integer/FP registers and interrupt masks agree. The actual existing C math helper
executes. Five compiled defect variants are rejected: later ties, initialized
scratch, early return on read error, lost low bits and reassociated multiplication.

The normal build compiles all **800 units (718 application, 82 bootloader)**
without failures or duplicate strong symbols. Application imports remain **96**;
bootloader metadata imports remain 22. Strict GNU bootloader linking succeeds.
All 797 other nongenerated object hashes are unchanged; generated boot crypto
and vectors retain identical allocated bytes/relocations. The existing qualified
four-byte charger dispatch tail also retains its bytes/relocations. Source-plan
selections are unchanged; this work makes no new byte-identity claim.

Register transport is modeled, and the table is placed at its stock address in
the comparison fixture. Physical charger behavior and single-wire timing remain
unverified. Private frames, live temporary registers, incidental caller-clobbered
outputs, APSR, faults and concurrency are excluded. Full application final linking
remains outstanding. The R1 manifest check passes; the global check retains the
unrelated unlisted G2 resident-ROM assembly file.

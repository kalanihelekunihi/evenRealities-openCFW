# R1 hourly health-sample accumulation in C

`native_health_average.c` now expresses the accumulator at `0x5aba0` and the
calendar helper's body at `0x5aca6` in C. The [review receipt](health-average-c-review.json)
binds production source/object hashes, REA bytes, paired replays, negative controls,
qualification and normal composition. Two small assembly boundaries remain:
a calendar frame bridge and the native unsigned float-to-integer conversion.

The accumulator accepts unsigned types 0 through 5, obtains the local hour from
the original timestamp, and selects an eight-byte row. Zero count or a different
hour clears the entire row before installing the new hour. Count increments as a
16-bit value, sum wraps as 32 bits, and the result converts the unsigned sum and
count separately to float, divides, performs native truncating/saturating `VCVT`,
then returns the low 16 bits. Unsupported types use the stock repeated log-mode
queries/messages/tags and return zero. Count wrapping to zero must preserve native
infinity/NaN conversion and FPSCR exceptions; an out-of-range ordinary C cast
cannot promise that behavior, so the final conversion remains explicit assembly.

The calendar bridge preserves the native 16-byte frame and restores both complete
calendar words into R2/R3. Its C body clears the eight bytes, obtains UTC offset,
invokes the existing calendar provider and returns byte 4. The actual bridge runs
under the accumulator in the fixture. Calendar addresses match native: caller
SP-16 directly and SP-32 through accumulation. Provider-call depths are larger by
16 bytes due to the C worker: native 16/32 versus C 32/48. Logging depths remain
16. Caller-clobbered registers, APSR and private stack residue are excluded except
that direct helper cases explicitly check restored R2/R3. Callee-saved integer/FP
registers, SP, masks, R0, row contents and FPSCR are checked.

There are 2,012 paired native/C cases covering count 0/1/65534/65535, changing
hours, unsigned sum and sample wrap, float rounding modes, type 5, unsupported
full-word types, changing log modes and callback mutation before row access.
Direct helper cases cover arbitrary calendar bytes and UTC offsets. Six compiled
defects are rejected: rejecting type 5, reversed hour-reset condition, missing
count increment, signed sum conversion, rounding instead of truncating conversion,
and selecting the wrong calendar byte. Calendar/offset and log providers remain
modeled boundaries. Physical and concurrent behavior are not established.

The existing owned rows remain a 40-byte cold-zero prefix with identical contents
and section flags. Stock accepts index 5, but that does not prove ownership of a
sixth row. The C implementation preserves its wrapping address calculation and
the fixture checks adjacent sixth-row behavior without adding RAM ownership.

All 632 units compile and both relocatable compositions pass without duplicate
strong symbols. All 631 other objects are unchanged. The manifest and application/
bootloader import sets remain unchanged at 172/34. Neither reconstructed root
passes instruction qualification, so the source plan remains at 4,313 source-built
bytes. A fresh hybrid application matches the locked official artifact, retaining
641,847 executable pull-through bytes and 248 resource bytes. Complete source-only
linking and whole-image C/hardware validation remain unfinished.

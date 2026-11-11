# RTC tick ordering and calendar frame

`board/native_rtc_lifecycle.c` now expresses the stock tick memory sequence
explicitly in C: read divider; capture/increment/store epoch; then load signed
UTC offset and convert the retained epoch value. Counter and alarm-record
accesses use volatile views. Calendar minute/second reads and callback reload
follow the stock short-circuit order. The callback still receives the low
hour byte, and divider is reset after callback return.

A 14-byte ABI bridge preserves stock's 48-byte calendar scratch span at entry
SP minus 64, below its saved registers. The C kernel uses that span and returns
the native divider result through R0. Native `0x56274` supplies the evidence;
no opcode array, executable blob or guessed peripheral provider is introduced.

All 8,400 direct stock/C comparisons pass with modeled calendar conversion and
alarm callbacks. Cases cover divider thresholds, epoch wrap, signed offset
extremes, zero/partial/full calendar writes, minute/second mismatch, null alarm
callbacks, callback divider mutation, and controlled epoch/offset mutation after
the epoch store. A further 720 comparisons execute the actual stock and C
calendar-conversion layers together; only alarm callbacks remain modeled there.

The old source has a concrete ordering counterexample: its compiler loaded
UTC offset before storing the incremented epoch. When the controlled probe
changes offset from 0 to 1 immediately after that store, stock and corrected C
convert epoch 1061, while old C converts 1001. This establishes an ordering
mismatch, not a claim about physical race frequency. The old compiler inlined
calendar conversion; the counterexample observes its gmtime input at the
corresponding conversion boundary rather than inventing an old scratch pointer.

Checks compare raw R0, conversion inputs, exact scratch address/48-byte contents,
alarm sequence/hour, complete counter/record state, R4-R11, SP, interrupt masks
and call alignment. All other preexisting lifecycle function bytes/normalized
relocations are unchanged. All 562 R1 units compile with zero failures or
duplicate strong symbols; imports remain 211 application / 34 bootloader,
the other 561 units are unchanged and source checks pass. Physical RTC delivery,
complete fault/concurrency equivalence, native byte identity and final source-only
firmware remain unproven. The source plan and G2 gates are unchanged. Exact
bindings are in the [machine-readable review](rtc-c-tick-frame-review.json).

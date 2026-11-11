# Goodix accelerometer callback registration in C

REA confirms the previously unlisted entry `0x815cc` owns registration of the
three callback words at `0x2002fd28`, `0x2002fd2c` and `0x2002fd30`. Stock checks
all three input words before storing any of them. It returns zero without
changing the table when any word is null; otherwise it stores start, stop and
sample words in address order and returns one. It does not validate pointer
alignment, executable ranges or Thumb bits.

`stock_gsensor_callbacks.c` now implements that policy and owns the shared
12-byte table. The header deliberately retains opaque pointer-sized words:
registration does not call them, and the concrete consumer signatures still
need target evidence. Static assertions bind table extent and sample offset.
Volatile stores preserve word width/order. This does not promise atomic
publication against interrupts; stock uses a multiword store instruction,
whereas compiler-selected C stores must be checked again for final placement.

The controlled execution probe passes 1,029 paired cases (2,058 executions),
covering every null combination, nonzero odd/even/high pointer words and three
initial table states. It compares return words, ordered stores, rejected-table
preservation, adjacent canaries, preserved registers, stack and interrupt masks.
Callback execution and caller-clobbered registers/flags are outside this probe.

The full report `build/sources-goal-r1-goodix-gsensor-register/report.json`
compiles 566 R1 units without failures or duplicate strong symbols. Imports
remain 199 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-gsensor-registration-review.json) binds REA, source,
execution probe, frontier record and normal build by hash.

The C body is 38 bytes versus 20 stock instruction bytes, and is not
byte-qualified. The canonical source plan is unchanged. Callback target
bindings, cold-state initialization/final addresses, interrupt interleavings,
physical accelerometer behavior and complete source-only byte identity remain
unverified. The [sample/cache analysis](goodix-gsensor-boundary-review.md)
records the next consumer obligations. G2 gates are unchanged.

# Independent review 2227

**Result:** PASS_SCOPED.

The source and all receipt files match their hashes. A fresh isolated replay regenerated all 20 fixtures exactly without helper interceptions.

Observed ordering agrees with the instructions: 6BD4 readiness and 6140 descriptor update precede 6AC0 mode handling; saved-mode 0/5 transitions run original port helpers, then 8FD0. Version 1 mismatch returns 64 before range setup. Version 2 proceeds through original 664C, 6608, A324 and 4480; with the modeled clear-bit status, the poll reaches its 441-delay timeout, which 664C ignores before continuing setup writes. Saved modes 2/4 use the fast path, while 255 returns 1 after readiness/descriptor enable.

The replay verifies factory words `0x55`/`0xAA`, configuration mode/count, register-block start and first record, delay count/arguments, call order, and R4/R8/PRIMASK/SP. An extra isolated assertion on the same original-code runs confirmed descriptor word+8 is `0x91` after the 6140 OR and 6AC0 bit-4/5 updates.

**Limits:** Factory bytes, scale byte 2, source records, register block and status are supplied model data. Physical readiness, elapsed-time behavior, MMIO effects, arbitrary configuration, callback behavior and concurrency are not established. No canonical admission is made.

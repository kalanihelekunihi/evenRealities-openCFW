# QEMU-ARC stub-arg canonicalization vs hwdrivers false-EQUAL (2026-11-23 2:02 AM CST, America/Chicago)

Cross-stream alert: hwdrivers pointer canonicalization collapsed any stub-arg value in [0x8, text-max] to a single pointer sentinel, so small integer args (pin 9 vs 10) compared equal.

## What this stream's harness does

`build/em-ctl/h/driver.c` (used via `--hdir /w/build/em-ctl/h`):

`stub_hit` runs every argument through `nrm()`:

- stack window `[0xfe0000, 0xfff000)`: hash `STKW` pointed-to words (frame-layout independence).
- image VA `[0xc00000, 0xfe0000)` and 4-byte aligned: return `0x1a6e0000 ^ first word` (orig/cand stub data sit at different addresses).
- otherwise the raw value is hashed.

`mnorm()` for typo-RAM memhash collapses every word whose *value* is in `[0xc00000, 0xfe0000)` to the single sentinel `0xc0dec0de` (image pointers stored in RAM).

## Can it collapse integer args the same way?

No for the reported 9-vs-10 class.

- The image range starts at `0xc00000` (link.ld `.text`), not `0x8`. Integers 0..0xbfffff are hashed as themselves. Pin 9 vs 10 would still mismatch.
- `nrm` does not map the whole range to one sentinel; it xors the pointed-to first word, so distinct objects with distinct first words stay distinct.
- Driver `gen()` never emits values in `[0xc00000, 0xfe0000)`, so top-level random inputs cannot land in the collapse window.

Residual (different, narrower than hwdrivers): a *computed or constant* 4-byte-aligned integer stub arg in `[0xc00000, 0xfe0000)` is treated as a data pointer. Two such integers that happen to read the same first word would be a false EQUAL on callhash. `mnorm` can also hide two different image-range integers stored in typo-RAM, because they become the same sentinel.

No typo-RAM proof in this stream was found that passes integer stub args in that window (typical args are small constants, typo-RAM addresses `0x80xxxx`, or `0xf00xxx` MMIO). Affected-proof rerun is not required for the 9-vs-10 failure mode. Hardening would be to apply `nrm` only to pointer-typed stub parameters (qm.py already parses signatures; stubs are currently all `u32`). That change belongs in the shared harness and was not applied here.

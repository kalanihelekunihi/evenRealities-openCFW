# Touch SCB MMIO and linked simulator review

Scope: read-only cycle review of `touch_scb_mmio.c/.h`, the isolated ARM simulator entry/linker script/verification script, MMIO host tests, and Make integration. No firmware or shared state was changed.

## Cycle 1 finding and cycle 2 disposition

In cycle 1, `simulator/verify.py` used Python `assert` for nearly every evidence invariant. Python optimization would remove those checks. In cycle 2, the script added an explicit `if not __debug__: raise RuntimeError(...)` before running the verifier; a unit test checks that `-O` is rejected. This closes the optimized-mode fail-open risk while the verifier still uses assertions in normal mode. I attempted an optimized run against the earlier snapshot using the configured Unicorn environment; it exited with signal 132 before producing a report, so no false PASS was observed.

The earlier verifier also overwrote `--output`. Cycle 2 changes this to exclusive `open('x')`, preventing silent evidence clobber.

## MMIO semantics and boundary

The implementation's volatile accesses align with the recovered code: read FIFO status at `+0x308`; sample `RX_CTRL` at `+0x300`; select byte mode when `(CTRL & 0x18)==0`, halfword mode otherwise; read a 32-bit FIFO word from `+0x340` per element and store its low 8 or 16 bits. The callback-based raw API preserves the zero-count callee call and width sample. The checked path captures width for its transfer callback, checks halfword destination alignment and capacity, and avoids FIFO reads on rejected capacity/alignment cases. The header correctly requires caller serialization so configuration does not change mid-operation.

Physical/synthetic boundary is described well: module API does not hardcode a board base, the simulator maps a synthetic SCB block, FIFO hook supplies a predetermined word sequence, and no interrupt, clock, concurrent consumer, bus electrical behavior, real FIFO side effect, or hardware startup is claimed. Comparison executes authenticated original callee+wrapper bytes and the linked module without callee stubs. The saved result reports 8 comparisons and 5 new checked-adapter cases; source tests separately validate guards, truncation, and alignment/capacity behavior.

The checked API cannot portably prove the address is mapped MMIO; cycle 2 documents that the caller must provide a live mapped block and rejects bases above `UINTPTR_MAX-0x340`. The raw API is intentionally unchecked and its header documents the live-mapped, non-overflowing range precondition.

## Simulator and evidence provenance

The linker script is clearly isolated from the stock touch image link map and adds only callable module exports, with no vectors or startup. In cycle 1 the ELF loader lacked structural bounds. Cycle 2 adds a 2 MiB input cap, bounds header tables and symbol tables, limits PT_LOAD sizes to 64 KiB, checks file extents and restricts segments to the simulator code/RAM windows.

The verifier authenticates the official touch image and hard-pins the original wrapper/callee slice hashes. It records the linked ELF SHA-256 and checks executed instruction bytes against loaded ELF segments. The separate build-provenance artifact binds the recorded component, Makefile, entry/linker inputs and compiler/linker versions to the ELF and comparison output.

The earlier cycle-2 comparison artifact was stale during review. The final trigger-cycle comparison below is fresh against the current verifier and linked ELF.

## Integration and validation limits

Make targets build an isolated Cortex-M0+ callable ELF and run comparisons; this is not a firmware link or a hardware provider. The host MMIO tests exercise simulated registers, not Unicorn/original-instruction equivalence. The simulator report and checked-adapter cases should remain explicitly separate from original behavior. The compile/link unittest now exists and checks ELF symbols, invalid ELF rejection, and optimized-mode rejection; the standalone `touch-scb-simulator-test` target performs the actual execution comparison.

Current reviewed SHA-256 values:

- `touch_scb_mmio.c`: `783266dd5cadfdb30c1d3fd52f94425f01e5dda86dc33e92f3ba7105f47516bd`
- `touch_scb_mmio.h`: `6e721710034dfc7ffb8aa92286ea6dd11c7d24892e7260b572a21a5046517ef1`
- `simulator/entry.c`: `3db94486f00ee71c83163e97908177c5094696dba4bd3d4422594142901fb199`
- `simulator/module.ld`: `35197fc939bca0ac513fac9d05196110c2b93803ab3efcbc2cfa9af19b88fa37`
- `simulator/verify.py`: `f6406ae39531066fbb2a4defad968bb048605908b95ac1c65b02825530e17966`
- `test_touch_scb_mmio.py`: `18064dd772bfdb1270a70748d2f9cfc6fa4c672cbe2bca2867da51c6c5a0e6d0`
- `test_touch_scb_simulator.py`: `3e17cc1b3451de469aad5a3e9e526f12c209ea40d26cb508898ac25bac303f2f`
- `g2/Makefile`: `d8145becfc61c418130fe0f67efca7479b3c61d7ed3a16d7b5f47be60ed119ec`

## Final RX/TX review update

The final TX path retains the stock raw arithmetic: `depth - (status & 0x1ff)` is unsigned 32-bit subtraction, so a malformed used count greater than depth wraps. The checked adapter instead rejects `used > depth` before any TX FIFO store and preserves `actual_out`. The new malformed halfword case uses depth 8, used 17, and request 17; the wrapped available count is large, but the transfer stays bounded to 17 elements (34 source bytes), making the raw behavior observable without an unbounded fixture. This addresses the earlier request-2-only coverage concern. Other vectors include 16/8-entry configurations, byte/halfword widths, empty/full FIFO, clamps, max request, and low-nine-bit status behavior. Checked cases cover success, full, capacity, malformed status, null/unaligned/overflow base, halfword alignment and null source.

The final comparison artifact is `g2/build/foundation/touch-scb-trigger-final/comparison-reviewed.json` (the older `comparison.json` remains stale). I independently checked it reports PASS, with 8 RX comparisons + 6 checked RX cases, 12 TX comparisons + 9 checked TX cases, 5 FIFO valid original/linked cases + 4 checked-invalid cases, and 232 unique original instruction bytes. Its `script_sha256` matches the current verifier, its ELF digest matches the linked ELF, and all 10 source-manifest hashes match the current `.c/.h/.ld` files. The malformed TX vector reports actual=17 and 17 writes. Parent reports all 18 focused tests passed; I did not rerun them.

No critical coverage weakening found. The external `g2/analysis/touch-mmio-cycle-2026-10-05/build-provenance.json` now records the current Makefile, component, entry/linker inputs, compiler/linker versions, linked ELF hash, target, and comparison path; I checked all recorded source hashes against the current files and found no mismatch. The comparison itself also binds the current verifier and ELF hashes.

The saved invalid cases are intentionally not compared against a normal return from stock code: the stock function executes `BKPT #1` and raises an emulator exception. The independently saved original-code trace at `next-fifo/results.json` confirms this branch reads only FIFO_CONFIG, reaches the BKPT instruction, and does not write RX_FIFO_CTRL. The linked helper instead returns an explicit invalid-level result, with no write; documentation identifies this as the added checked API behavior.

Current final RX/TX SHA-256 values:

- `touch_scb_mmio.c`: `783266dd5cadfdb30c1d3fd52f94425f01e5dda86dc33e92f3ba7105f47516bd`
- `touch_scb_mmio.h`: `246a8d858507f86efca279f1bcc3f2acf832b728db77d5a81163812fc1cf9c6f`
- `touch_scb_tx.c`: `26c4c1d6cce94e42d5d7c2a117c6c592e297d9f8bb3b692add121430c904403c`
- `touch_scb_tx.h`: `70d8e9f60fd9c67ccdd0217f036265f9b4f213c9dfae58af2a490ea4cb427829`
- `simulator/verify.py`: `9d090c09be5456e30b14d1022fb871478b440b65cc937c2a9184e9c47da10364`
- `simulator/entry.c`: `743efcbea6e2787216a8ee3e65c55c794edf816d3fe8da45a403910baf37a377`
- `touch_scb_fifo.c`: `f6c5439760848024e1bb297d3ab413aa4644f69e42c61c2b4ec692d2da94caca`
- `touch_scb_fifo.h`: `b0cc52cc1f2c60ffb3da0c4a3931159b44c252f8343237f044db6ce7a600efbd`
- `test_touch_scb_tx.py`: `68635ef18e28741ded444fbaf45d0225db1d9276d6042a890e669bc7a801f9f0`
- `test_touch_scb_simulator.py`: `20f5bcfee4fb90e80f9f64f1a3250c9df59e7320d1e0d8026947869ba610e211`
- `g2/Makefile`: `e9fe738fc381f5c98b9a467799e030964d9748663ab90a8dbd0ce0019a48a1d6`
- `comparison-reviewed.json`: `1af62f000a4a400b1781726fbbf57b00b554203ea3700249bf30a11722a9a65e`
- `build-provenance.json`: `d6aebc567540f512c3b933cbd3b70abd119f092a56eb3fa551ccb75b6b17dd0a`

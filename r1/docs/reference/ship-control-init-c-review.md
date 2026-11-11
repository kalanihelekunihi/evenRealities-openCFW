# Ship-control operation and calibrated wait in C

Current implementation: [ordinary C ship-control startup loop](ship-init-pure-c-review.md). Fixed-register/frame observations described below are historical.

`board/native_yhm_initialize.c` now supplies missing stock `0x80e74` and its
forwarding branch at `0x50754`. The historical analog-initialization name does
not imply an ADC operation: stock opens the ship-mode handle from YHM context
`0x2000687c + 8`, reloads that handle and dispatches slot `0x18` with arguments
`(1,0)`, then calls the calibrated delay at `0x99d00` 200 times with argument
64,000. Return statuses do not stop the sequence. The existing handles
initializer's separate `(0,0)` operation remains unchanged.

Empty register constraints preserve native live R4–R8, including incoming
values before each initialization, the delay pointer and descending loop count.
Both Clang and GCC expose the native 24-byte frame. Each passes 384 paired
stock/C cases with 202 provider calls per case. Tests cover both entries, null,
ordinary, all-ones and frame-address handle values, error returns, two register
seeds and interrupt-mask states, and handle mutation after open/operation or
during each delay. They compare ordered context and saved-frame accesses,
complete provider traces/live R4–R11, final context/frame and observed final R0.
Exactly two context reads occur, including the callback-visible reload after
open; no handle reload occurs during delays. Wrong owner, operation argument,
loop count and delay argument variants are rejected.

`tools/build/qualify_sources.py` admits only the exact four-byte forwarding
branch. The longer outer C body is not byte-identical, and the calibrated
six-byte delay primitive remains assembly to preserve timing/flags. Registry
and delay providers are modeled. APSR and caller-clobbered R1/R2/R3/R12,
electrical response, actual elapsed time, arbitrary aliases, faults and
concurrency remain unproven.

All 581 R1 units compile. All 580 other objects, manifest and import sets remain
unchanged, as do the earlier handles initializer's bytes and relocations. The
hybrid now contains 4,069 source-built bytes, 642,091 fallback bytes and 248
resource bytes. Application SHA-256 remains
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
This does not prove a complete source-only rebuild. Reproducible probes,
compiler results, REA evidence and qualification are under
`build/goal-r1-ship-control-init-c`; durable results are in the adjacent JSON.

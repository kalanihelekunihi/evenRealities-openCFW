# R1 single-box peripheral resource sharing C candidate

`r1/src/application/runtime/native_prs.c` compiles the pinned Nordic SDK PRS
implementation with local configuration: only box 4 enabled, logging disabled,
and out-of-line functions retained. The vendor source is unchanged. No shared
SDK configuration is changed. The SDK's extra read-only log module metadata is
not claimed to reproduce stock data.

REA reads from the locked application corroborate the dispatcher at `0x34410`,
acquire at `0x7acd4`, release at `0x7ad0e`, and lookup at `0x84cd8`. Lookup accepts
only `0x40002000`. The native scatter decoder produces eight zero bytes at
`0x20007940`: handler word, acquired byte, and three padding bytes. The fixture
links the actual candidate state at that address; normal relocatable composition
does not independently establish its final placement.

The compiled candidate and stock match across 576 four-call sequences (2,304
paired calls): acquire, acquire again, release, acquire. Cases cover accepted and
unrecognized bases, null and non-null callbacks, free/busy state, four raw critical
nesting bytes, and state mutations at both critical helper boundaries. The SDK
checks acquired after entering the critical region, preserves state on busy,
returns 17 on busy and zero otherwise, and clears handler and acquired on release.
State padding and adjacent guards match. All ABI callee registers and SP are
preserved on return. Five negative variants (busy success, missing handler store,
missing acquired store, and either missing release clear) fail the comparison.

Eight dispatch cases per implementation preserve callback R0, other registers,
SP, and raw LR, including three EXC_RETURN tokens. Execution stops at the callback;
this does not exercise actual exception return. The dispatcher does not consult
acquired. The lookup is exercised through both acquire and release.

Acquire uses a 24-byte candidate frame versus stock's 16 bytes; its nesting byte
and live callee registers at critical helper calls differ. Critical helper bodies
are modeled. Timing, electrical behavior, real interrupt delivery, arbitrary
aliases, faults, and concurrency remain unproven. No inline assembly is added.

All 589 R1 units compile and compose without duplicate strong symbols. The prior
588 object files are identical; application/bootloader unresolved sets remain
164/34. Qualification compiles this candidate but selects none of its four
functions. The source plan is unchanged. A fresh canonical hybrid build retains
the locked application hash with 4,245 source-built, 641,915 executable fallback,
and 248 resource bytes. This is progress in hardware C coverage, not a complete
source-only or byte-identical C reconstruction.

Machine-readable evidence, source hashes, REA observations, negative controls,
and report pointers: `prs-c-review.json`. Reproducible ignored probes:
`build/goal-r1-prs-c/{scatter,verify,negative,qualify,publish}.py`.

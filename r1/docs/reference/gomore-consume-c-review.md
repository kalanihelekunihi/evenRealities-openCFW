# R1 packed sleep consumer and interval validation in C

`native_gomore_consume.c` supplies the native five-argument consumer at
`0x69644` and recent-interval predicate at `0x72af0`. The [review receipt](gomore-consume-c-review.json)
binds source/object hashes, REA stock bytes, replay artifacts, qualification and
normal composition. The ordinary C body preserves the saved payload pointer
through the 88-byte clear, validates the interval against the live context clock,
selects the output kind, extracts/refines the packed timeline, scores it,
adjusts the start time with the stock clamp and publishes the mapped metrics.
The incoming fourth count argument is unused by stock; the live count used by
refinement and scoring is local. The final stored count reload occurs after the
scorer, preserving provider mutations.

At this review's checkpoint, two assembly boundaries remained. The native local frame
retains one raw byte after an 11-byte table copy; the following provider consumes
a 12-byte word view. The frame bridge preserves that byte and exposed local
addresses. It does not fabricate a zero-padding contract. Stock's signaling
`VCMPE` comparison also raises IOC for quiet NaNs, unlike an ordinary C
comparison. An initial ordinary comparison failed the differential FPSCR check;
the source at this checkpoint retained the signaling comparison and FPSCR read while keeping the
branch, clamp, conversion and arithmetic in C. These boundaries are not evidence
of a fully C firmware or instruction identity.

The [signaling comparison follow-up](gomore-consume-signaling-c-review.md)
replaces that VCMPE/VMRS expression with C plus FPSCR compiler builtins and
revalidates the packed consumer. The raw local-frame bridge still remains.

## Subsequent C frame closure, 2026-11-11

The native entry's handwritten frame bridge is now ordinary C using
`__builtin_alloca(128)` and integer-address adjustment of the resulting
stack pointer. Under the pinned Arm Clang profile, two saved registers plus
the 136-byte stack allocation place the worker's exposed frame and provider
SP at the native `entry SP-144`. The worker uses frame bytes 20..115 inside
the allocation; outgoing stack arguments occupy bytes 0..7. The table's
twelfth, raw byte at frame+31 is left untouched. This is compiler-profile
dependent and is checked by machine replay, not claimed as portable ISO C.

The normal production object SHA-256 is
`363cc44d3a28e6d945734cb2173a47ba99f5543cf18364e051853ec879b80db2`.
Its 1,537 paired stock/C cases pass in the original consumer fixture and in
the later history, timeline, and score-flow chain fixtures. They compare
provider arguments and frame positions, raw padding, output state, return,
saved registers, interrupt masks and FPSCR. A plain 116-byte C array fails
the frame check. The same unit's other three function bodies are byte
unchanged. The fresh `build/sources-r1-gomore-frame-c-20261111/report.json`
compiles all 1,045 R1 units; strict application and bootloader receipts are
`build/r1-link-gomore-frame-c-20261111/report.json` and
`build/r1-boot-link-gomore-frame-c-20261111/report.json`. Both link, with zero
undefined references and zero application archive members. Actual device
behavior and stock byte identity remain unverified.

The consumer passed 1,537 paired stock/C replays, comparing outputs, provider
arguments and memory at boundaries, raw table padding, logical faults, R0,
callee-saved integer and FP registers, SP, masks and FPSCR. Cases include
nonpositive timeline lengths, mutations during clear/extraction/scoring/history,
quiet/signaling NaNs, infinities, subnormals, rounding/FZ/DN settings and wrapping
interval arithmetic. A further 1,260 standalone predicate pairs cover flag gating,
899/900/86400/86401-second boundaries, timestamp equality and 32-bit wraparound.
Six compiled defects are rejected: short clear, lost payload, zeroed raw padding,
wrong kind flag, quiet comparison and wrong score field. Total: 2,797 paired cases.

The native provider-call frame is 144 bytes; the C worker uses 200 bytes including
the bridge. Table/metric addresses retain their native offsets. Caller-clobbered
register residue, APSR and private outgoing stack slots are excluded. Lower clear,
table lookup, timeline extraction, refinement, scoring and history providers are
modeled. The fixture does not establish physical, concurrent or full-chain behavior.
No new RAM globals are introduced.

All 628 units compile and both relocatable compositions pass without duplicate
strong symbols. All 627 earlier objects remain identical. Application imports
change from 168 to 172 because resolving this consumer exposes five lower native
providers: table record `0x684b4`, packed extraction `0x68354`, refinement
`0x81040`, scoring wrapper `0x68fbc` and history shifting `0x748d4`. Their frontier
routes now identify the native ABI dependencies instead of analysis-plan symbols.
Bootloader imports remain 34. Manifest checks pass.

Neither new root passes instruction qualification; the exact source plan remains
unchanged at 4,299 source-built bytes. The fresh hybrid application matches the
locked official artifact, with 641,861 executable bytes still pulled through and
248 resource bytes. This is not a complete source-only link or hardware proof.

## Subsequent dependency correction

The [history reconstruction](gomore-history-c-review.md) found that stock passes
the signed adjustment in R1 to history. This review's original one-argument modeled
history call did not check that contract. The subsequent source corrects the
prototype/call; its stronger fixture compares both arguments and executes actual
C history/marker code with payload checks. Treat the original receipt as historical
and use the follow-up for the corrected consumer proof and current composition.

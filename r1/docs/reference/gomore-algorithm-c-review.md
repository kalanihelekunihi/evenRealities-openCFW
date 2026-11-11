# R1 sixteen-stage algorithm coordinator in C

`native_gomore_algorithm.c` supplies stock `0x5ff94` with typed provider
boundaries in `native_gomore_stages.h`. The [receipt](gomore-algorithm-c-review.json)
binds REA bytes, production source/object, shared declarations, replay, fault
boundaries, defect controls, consolidation, qualification and composition.

The coordinator preserves sixteen live control reads in native order. Control
zero uses the supplied delta; one uses delta one and is cleared after the call;
two becomes three without dispatch; other byte values suppress dispatch. Captured
control governs the clear even if the provider mutates that byte. Low-byte status
is published after each stage. The existing marker/no-op is reused, not duplicated;
its production C body is the exact native `bx lr` leaf. Final raw return is
context+0x37fd.

The activity-window stage uses unsigned-to-float delta in S0 and pointers in
R0..R3, including context+0x88. Native integer/stack arguments are explicitly
typed for all other stages. The old generic owner and its unused descriptor table
are removed; that table's erroneous activity offset 0x30 does not survive as a
second stock implementation. No assembly or persistent RAM is added.

The production object passes **4,512 native/C cases**, each checked against an
independent ordered-call/state oracle. Coverage includes all 256 control values
at each stage, delta extremes, four rounding modes, mixed controls and provider
changes to current/future controls and FP rounding mode. Provider-entry/marker
FPSCR, outgoing argument words, status/context effects, final return, SP and saved
integer/high-FP registers agree. The float oracle uses integer rounding logic.
Eight compiled defective variants are rejected.

Nine boundary cases agree on partial status writes and unmapped read address/size:
eight fault and one completes. Work providers are not reached there. Actual
native/C host adapters, resamplers, wrappers, filters, interpolation and coordinator
pass **334 integration cases**, including **nine faults**, with **3,259 modeled
logger/stage calls**. Full 0x3ae4-byte context views and numeric scratch pointers
are compared without normalization. Stock clear/move/marker execute; the sixteen
work providers and logger remain modeled. Private stack aliases and provider SP
equality are outside this proof, as is physical device behavior.

The normal build compiles **685 units** (611 application, 74 bootloader), with
**179 application and 34 bootloader unresolved imports**. All **683 previous units
outside the consolidated generic owner** retain identical source/object hashes.
The coordinator import is resolved and its sixteen lower provider imports become
explicit, explaining the increase from 164 to 179. Those existing generic provider
hints are not accepted native implementations without separate ABI review and
consolidation. Source checks and relocatable composition pass without new failures
or duplicate strong symbols.

Qualification selects no new replacement. The canonical source plan is unchanged;
hybrid raw equality still depends on executable stock pull-through. Fully C
firmware, a complete source-only final link and byte-identical reconstruction
remain unproven. Reproduction artifacts are under
`build/goal-r1-gomore-algorithm-c/`; the normal report is
`build/sources-goal-r1-gomore-algorithm-c/report.json`.

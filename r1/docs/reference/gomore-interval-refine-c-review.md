# R1 interval refinement in C

`native_gomore_interval_refine.c` implements the 200-byte native interface at
`0x58b70` in ordinary C. The [receipt](gomore-interval-refine-c-review.json)
binds REA evidence, production hashes, paired comparisons, defect controls,
qualification and builds. No RAM or assembly is added. The existing C native
memory-move provider and upstream memmove/memcpy bodies handle both record moves
and preserve the final native R0 return.

The implementation follows the [native analysis](gomore-interval-refine-native-analysis.md).
It snapshots all 32 current bytes, then reads the live current flag and live
start/end fields. Span and gap wrap unsigned but their native comparisons are
signed. The aggregate numerator/count are converted signed to binary32 and
divided before previous-flag, span and policy rejections. A volatile C average
preserves that early evaluation and its FPSCR side effects. Its signed raw-bit
comparison with `0x3ea3d70a` avoids an FP comparison changing FPSCR conditions.

Statuses 2, 1, 3, 5 and 0 retain native precedence. A successful merge copies
the captured previous start, conditionally adds flag bit 4 and clears status;
other snapshot fields survive. Zero aggregate count skips the numerator read.
There are no added pointer guards or assumptions that the live source still
matches its snapshot. The context and timezone arguments remain unused.

**3,708 direct stock/C comparisons** pass, including 47 faults and the exact
3,192-case native baseline. An additional 512 seeded cases vary spans, gaps,
counts, sums, flags, aliases, rounding, DN/FZ, cumulative flags and FPSCR
condition bits; four targeted negative-count cases expose otherwise invisible
conversion side effects. There are 3,195 ratio/oracle paths: 2,492 actual
calculations and 703 zero-count paths. Exact rational arithmetic predicts
binary32 rounding and inexact flags. Full FPSCR values match stock, including
early flags on rejected paths and the rounding-dependent 576/1800 threshold.

**1,698 more comparisons** execute the actual C compose caller, refinement
and movement providers. Another **2,152 comparisons** execute actual C engine,
compose, refinement, descriptor merge, setter and memory routines. Interval
build remains modeled. Those integrated corpora include two and 32 matching
faults. Total: **7,558 paired cases, 81 faults and 7,477 completed returns**.

The direct replay checks independent status/record oracles, guarded SRAM,
movement order, completed return values, preserved integer/FP registers, SP,
masks and FPSCR. Integrated replays compare provider arguments, records, state
and relevant ordered engine stores. Private stack identity, caller-clobbered
registers and interrupted-fault R0 are excluded. FP context is activated before
assigning FPSCR. Physical/concurrent behavior is not established.

Twelve compiled defects are rejected: unsigned span or gap, floating ratio
comparison, skipped early FP evaluation, unsigned numerator or denominator,
inclusive ratio or gap threshold, snapshot rather than live flags, current
rather than previous start, unsigned policy and normalized return value.

All **670 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **669 previous sources/objects** are unchanged.
Resolving refinement adds no imports, leaving **164 application / 34 bootloader
imports**. Interval build at `0x692e4` remains native.

Instruction qualification rejects the compiled bytes. The canonical plan
remains 4,369 source-built bytes, 641,791 executable pull-through bytes and
248 resource bytes. A fresh hybrid application matches the locked artifact
through pull-through. Complete source-only linking, byte-identical rebuilding,
context initialization and physical hardware validation remain unfinished.

The remaining interval-build dependency now has a [native analysis](gomore-interval-build-native-analysis.md),
including signaling history comparisons, calendar capture/reload boundaries
and its distinct class byte 28. Its C native route remains unresolved.

The [interval-build C review](gomore-interval-build-c-review.md) now supplies
that native interface and verifies build/refinement through compose and the
engine. Calendar conversion is the newly exposed native dependency.

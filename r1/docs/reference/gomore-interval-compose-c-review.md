# R1 interval compose in C

`native_gomore_interval_compose.c` implements the 130-byte native routine at
`0x67558` in ordinary C. The [receipt](gomore-interval-compose-c-review.json)
binds REA bytes/instructions, production hashes, paired replay, rejected
defects, qualification and builds. No RAM or assembly is added.

The nine-argument interface forwards context, mode, stored interval, timezone,
controls, source descriptor, aggregation and policy to native build. It moves
all 32 built bytes to a private snapshot, captures snapshot words 16 and 20
**after that move returns**, and invokes native refinement with the snapshot.
It moves the refined work record back to the snapshot, restores the captured
two words, and rounds the unsigned wrapping end-minus-start span down to a
multiple of 30 seconds before publishing the full record. Lower build/refine
return values do not control publication.

All three moves use the existing `r1_native_memory_move` C provider and its
upstream memmove/memcpy bodies. Stock `0x2775c` is not ISO memcpy: its forward
path leaves destination-end in R0 and its backward-overlap path leaves source
in R0. Compose forwards that final result. An initial comparison caught the
incorrect ISO-return substitution; reusing the existing native provider fixes
it without creating another memory implementation.

Validation passes **1,698 direct stock/C cases**, including two matching final
output faults and 1,024 seeded random cases. It covers wrapping intervals,
metadata patterns, mode/provider-return extremes, output aliases to controls,
source or stored interval, refinement-side snapshot changes, mutations after
each move and injected move return values. An independent output calculation
checks saved metadata, unsigned span rounding and post-copy output mutations.
Actual C movement executes against the stock movement routine. Both native
lower routines end by publishing all 32 bytes on returning paths, supporting
the fixture's full-record build/refine contract.

Another **2,152 stock/C cases** execute the actual C interval engine, compose,
descriptor merge, setter and memory routines. Build and refinement remain
modeled; their argument order and work/snapshot bindings are checked. The
engine's signed clamp, live inputs, policy aliases and 32 matching faults
remain covered. Total: **3,850 paired cases, 34 faults and 3,816 completed
returns**. Provider order/arguments, guarded SRAM, result records, native R0 on
completed compose returns, preserved integer registers, SP, masks and FPSCR
are checked. Private stack identity and interrupted-fault R0 are excluded.
Physical/concurrent execution is not established.

Ten compiled defects are rejected: wrong metadata word, omitted second-word
restore, capture from work before the first move, absolute end rounding,
signed span division, ceiling rounding, swapped build mode, wrong refinement
policy, short record move and normalized return value.

All **669 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **668 previous sources/objects** are unchanged.
Resolving compose exposes native build at `0x692e4` and refinement at `0x58b70`,
leaving **165 application / 34 bootloader imports**. These are newly exposed
lower interfaces rather than bindings to incompatible portable APIs.

Instruction qualification rejects compose's relocation pattern. The canonical
plan remains 4,369 source-built bytes, 641,791 executable pull-through bytes
and 248 resource bytes. A fresh hybrid application matches the locked artifact
through pull-through. Complete source-only linking, byte-identical rebuilding,
context initialization and physical hardware validation remain unfinished.

The refinement dependency now has a [native analysis](gomore-interval-refine-native-analysis.md),
including live-source flags, signed duration limits and early FP side effects.
Its C native route remains unresolved.

The [refinement C review](gomore-interval-refine-c-review.md) now supplies that
interface and verifies this compose caller with actual C refinement and
movement. Interval build remains native.

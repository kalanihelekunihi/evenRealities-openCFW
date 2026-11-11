# R1 sleep-interval engine in C

`native_gomore_interval_engine.c` implements the 258-byte native interface at
`0x7244e` in ordinary C. The [receipt](gomore-interval-engine-c-review.json)
binds REA bytes/instructions, production hashes, paired replay, rejected
defects, qualification and builds. No assembly or RAM is added. The existing
C second-word setter and memory routines are reused; the unit explicitly enables
unaligned accesses so packed policy loads retain native word accesses and faults.

The implementation follows the [native analysis](gomore-interval-engine-native-analysis.md).
It clears output byte 26 before testing the context enable byte; disabled calls
return 64 and active completed calls return zero. It snapshots the descriptor,
passes the native five-argument interface through to compose, preserves the
signed comparison of the wrapped clamp difference, and copies the candidate
to stored state only when flag bit 3 is set. It reloads auxiliary, flags,
timezone and current time before merge, preserving their native signedness
and values. Lower return registers do not become success/failure checks.

After copying the result to the caller, the engine reloads the policy pointer.
The first unaligned word load at policy+2 precedes its context+304 store, which
precedes the second load at policy+6 and context+308 store. This preserves
output-pointer aliases and overlapping source/destination words. Finally it
zeros control byte 0 and commits both live control words. Other control bytes
are not normalized to their initial values. The private candidate need not be
initialized: REA shows the returning native compose routine always copies all
32 bytes to its output; the fixture supplies that full record contract.

Validation passed **2,152 direct stock/C comparisons** and **2,152 comparisons
using the actual C second-word setter and upstream musl memcpy**. Each corpus
contains 32 matched faults, 708 clamps (including 288 large wrapped differences)
and 72 provider-mutation configurations, 66 reached. Enable/flag/mode/timezone
extremes, rounding, output/context/policy aliases, source overlap, lower errors
and live control changes are included. Null output faults before context access;
invalid policy pointers fault after output copying and before final controls.

Another **2,328 comparisons** execute the actual C interval-update caller,
engine, setter, memcpy, EABI memory clear, musl memset, propagation and packed
accessors. These include 400 matching faults and shared-context mutations.
Compose and descriptor merge remain modeled in all corpora. Total: **6,632
paired cases, 464 faults and 6,168 completed returns**.

Comparisons assert provider arguments/order, candidate contents, guarded SRAM,
ordered engine stores and widths, saved registers, SP, masks and FPSCR on
completed returns. Private stack bytes and caller-clobbered state are excluded.
Setter/copy internal store widths are excluded when those actual C providers
execute; resulting memory and engine-level write order remain compared.
No physical/concurrent execution or final firmware linking is established.

Twelve compiled defects are rejected: unsigned clamp, nonzero-flag persistence,
boolean merge flag, unsigned timezone, unsigned auxiliary, cached current time,
early policy-pointer capture, early second-policy-word load, wrong policy offset,
normalized controls, wrong disabled return and omitted initial output flag clear.

All **667 units** compile and both relocatable compositions pass without duplicate
strong symbols. All **666 previous sources and objects** remain unchanged.
Resolving the engine exposes native compose at `0x67558` and descriptor merge
at `0x72024`, leaving **165 application / 34 bootloader imports**. These are
newly visible lower dependencies, not added replacements for already resolved
providers.

Instruction qualification rejects the engine's relocation pattern. The canonical
plan remains 4,369 source-built bytes, 641,791 executable pull-through bytes and
248 resource bytes. A fresh hybrid application matches the locked artifact
through pull-through. Complete source-only linking, byte-identical reconstruction,
context initialization and physical hardware validation remain unfinished.

The descriptor-merge dependency now has a [native analysis](gomore-descriptor-merge-native-analysis.md),
including clear-before-read aliases, ordered sums, live count reloads and FP
results/flags for the upcoming C implementation. Its native route remains unresolved.

The [descriptor-merge C review](gomore-descriptor-merge-c-review.md) now provides
that native interface and verifies this engine through the actual C merge and
its memory routines. Compose remains native.

The [compose C review](gomore-interval-compose-c-review.md) now provides that
interface and verifies this engine with actual C compose, merge and movement.
Build and refinement are the newly exposed native dependencies.

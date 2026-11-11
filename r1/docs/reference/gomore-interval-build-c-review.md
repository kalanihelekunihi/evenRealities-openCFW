# R1 interval build in C

`native_gomore_interval_build.c` implements the 518-byte native interface at
`0x692e4` in ordinary C. The [receipt](gomore-interval-build-c-review.json)
binds REA bytes, production hashes, compiler route, paired replay, defect
controls, qualification and builds. No assembly or RAM is added. The existing
C memory-clear and native memory-move providers are reused; calendar conversion
at `0x59cb0` is the remaining native dependency.

The implementation follows the [native analysis](gomore-interval-build-native-analysis.md):
wrapped source/time arithmetic, preceding counts, exact source-type and high
threshold selectors, fifteen-slot history scan, unsigned start/end clamps,
pre-calendar metadata/minimum/timezone capture, and fresh post-calendar hours,
auxiliary and source metric/average reads. Build class is byte 28, separately
from refinement's merge-status byte 29. Native movement's R0 is forwarded.
The thirteen-byte calendar output buffer is explicitly aligned for its native
word/halfword stores.

The comparison requires signaling **VCMPE**, including invalid for quiet NaNs
and IDC for flushed subnormals. Clang's plain comparison emitted quiet VCMP;
its strict-exception request and FENV pragma were unsupported for this target.
An experimental C FPSCR model passed comparisons, but is not the production
implementation. The existing license-free GCC 9 route emits VCMPE/VMRS directly
from ordinary C `>` with signaling/rounding/trapping flags. The production unit
uses that simpler route, with no inline assembly, FPSCR write intrinsic or
manual FPSCR emulation. The small noinline comparison helper makes its behavior
observable in replay. FP contraction is disabled for the ratio calculations.

**4,936 complete-routine stock/C cases** pass, including eight faults and the
exact 4,676-case native baseline. The additional 256 seeded cases cover signed
timezones, varied metadata/preceding counts, aliases and full FPSCR state; four
negative-numerator cases check signed average conversion. The independent
oracles check records, history slots, complete FPSCR and 1,126 ratio paths.
There are 10,284 history comparisons and 216 calendar-return mutations. They
distinguish captured fields from live reads and preserve rounding-sensitive
classification.

A focused matrix passes **18,792 native VCMPE/C helper comparisons**: 1,044 raw
binary32 samples, both thresholds and nine FPSCR configurations. Inputs include
signed zeros, infinities, NaNs with payloads, signaling NaNs, subnormals,
threshold neighbors and seeded arbitrary bit patterns. Boolean results and
complete FPSCR match; masks, SP and saved integer registers are checked.

Another **1,698 stock/C cases** execute actual C compose, build, refinement
and movement, including history/NaN conditions propagated through the caller.
A further **2,152 cases** execute the actual C interval engine, compose, build,
refinement, descriptor merge, setter and memory routines. Calendar output is
modeled in all corpora with its observed thirteen-byte shape. Together these
are **8,786 routine pairs with 42 faults**, plus the 18,792 focused comparison
pairs. Integrated replays compare complete resulting FPSCR rather than assuming
its condition bits stay at entry values.

Thirteen compiled defects are rejected using recorded native counterexamples:
quiet NaN comparison, software subnormal flushing that loses IDC, inclusive
history comparison, boolean high-threshold selection, wrong history slot,
wrong class byte, late minimum read, cached auxiliary, positive-only shift,
floating metric or ratio comparison, unsigned numerator and normalized return.
Every mutant compiles under the production GCC warning/error policy before
its behavioral comparison is rejected.

Direct comparisons include independent scalar/history/rational oracles,
guarded SRAM, provider order/arguments, records, completed return values,
preserved integer/FP registers, SP, masks and FPSCR. Integrated comparisons
retain relevant engine write order and state checks. Private stack identity,
caller-clobbered state and interrupted-fault R0 are excluded. FP context is
activated before assigning FPSCR; cold-FPU/task-context and physical/concurrent
execution remain unproven.

All **671 units** compile and both relocatable compositions pass without
strong-symbol duplicates. All **670 previous sources/objects** remain
unchanged. Resolving build exposes `r1_gomore_epoch_to_civil_native`, so imports
remain **164 application / 34 bootloader**. Its native route is recorded
explicitly rather than binding the incompatible portable calendar API.

Instruction qualification rejects the body's relocation pattern. The canonical
plan remains 4,369 source-built bytes, 641,791 executable pull-through bytes
and 248 resource bytes; the fresh hybrid application matches the locked
artifact through pull-through. Complete source-only linking, byte-identical
rebuilding, calendar binding, context initialization and hardware validation
remain unfinished.

The subsequent [calendar C review](gomore-calendar-c-review.md) supplies that
native interface and verifies the actual converter through build and the
closed C interval-engine graph. Other firmware imports remain unresolved.

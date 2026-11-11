# R1 accelerometer preprocessing stage in C

`native_gomore_accel_stage.c` implements stock `0x5ed14..0x5ef19` (518 bytes)
as `r1_gomore_stage_5ed14_native`, closing the coordinator's accelerometer-stage
import. Its reset, history, collector, statistics, float conversion and square-root
dependencies now use the existing C providers. The classifier is declared as
`r1_gomore_accel_features_native` at stock `0x67e4c`; it remains unresolved in the
normal source composition, with its spectral helpers still to reconstruct.
No stub or retained executable body is introduced into the C source.

Unsigned elapsed values above eight clear the output before resetting the
622-byte state, then return one. Other gaps advance a slot, shift 175 halfwords
and mirror 25 in native order. Only unavailable byte value one increments the
gap count and returns an unavailable result; other nonzero values remain present.
Ordinary signed-positive warmup bytes decrement once. Live descriptor/flag reads
retain behavior when aliases or providers change them.

On present input the stage clears magnitude/x/y/z scratch arrays in that order,
52 bytes each. It converts 25 x/y/z float samples to raw signed words and stores
the low halfwords. Magnitude uses three signed-halfword squares, 32-bit wrapped
addition, signed float conversion, sqrt and native-equivalent signed conversion.
It shifts/appends the waveform, calls the C collector, conditionally fills seven
windows from the live magnitude array, counts eight zero history slots and
selects classifier versus missing-output reset at the four-zero boundary.
Returns remain one for reset/unavailable and zero for processed windows,
including those that produce a missing-output record.

The recorded GCC9 profile generates the native 248-byte provider frame. Relative
to its own SP, z/y/x/magnitude arrays begin at +8/+60/+112/+164. Each contains
26 halfwords, with the spare element cleared. Private register saves differ;
future compiler/profile changes require the same address/depth checks.

Validation of final normal-build objects passes:

- 5,816 native/C stage pairs, including 66 logical faults. Cases include signed
  warmup bytes, gap/reset boundaries, all relevant unavailable-byte distinctions,
  zero-history thresholds, nonfinite/subnormal/extreme samples, FP modes,
  state/descriptor/output aliases and stack-backed input/output arrays.
  The stock classifier executes 2,217 times in each side of this fixture.
- 1,512 modeled-provider pairs. Providers clobber allowed registers, return
  controlled raw FP values and nonzero status words, change descriptor flags
  mid-gap/clear, replace post-collector warmup/zero history and mutate magnitude
  scratch. Root conversion and shift/counter/publication logic execute directly.
- 960 native/C sixteen-stage-coordinator pairs through the actual accelerometer
  stage and its C lower providers. The other fifteen stage providers are modeled.
- Eleven rejected defects: reset boundary, unsigned warmup, mirror offset,
  shortened shift, warmup underflow, shortened scratch clear, unsigned square
  conversion, warm-fill equality, zero-count equality, missing counter reset
  and treating every nonzero unavailable byte as unavailable.

Comparisons retain external memory/output/errno, ordered public writes,
provider arguments/depth/FPSCR, results, preserved general/FP registers, SP and
interrupt masks. Fault cases compare access and preceding publications; precise
fault-PC/exception-frame equality is not established. APSR—including sticky Q
from native SMLABB overflow—caller-clobbered registers and private save residue
are excluded. Physical and concurrent sensor behavior remain unverified.

The fresh normal build compiles 711 units (637 application, 74 bootloader)
without failures or duplicate strong symbols; manifest validation passes.
Imports remain 178 application / 34 bootloader: the stage import is removed and
its classifier import is added. Fourteen other coordinator-stage providers
remain unresolved. The frontier marks the classifier as a missing native
provider; earlier checked/injected-callback utilities retain `_checked` names.

Qualification selects zero bytes for the stage. The canonical plan stays at
4,381 source-built executable bytes, 641,779 stock executable bytes and 248
resource bytes. The fresh R1 hybrid application matches stock; complete
source-only linking, C byte identity and full source completeness remain
unfinished. The [machine receipt](gomore-accel-stage-c-review.json) binds REA,
source/object hashes, frame evidence and all validation results.

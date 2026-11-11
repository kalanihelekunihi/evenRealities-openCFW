# R1 accelerometer feature collector in C

`native_gomore_accel_collect.c` implements stock `0x4834a..0x484a7` (350 bytes)
as `r1_gomore_accel_collect_native`. It computes four means before publishing
any, then writes the three axis means, axis deviations, fourth-channel mean
and deviation, capped range and four mean differences in native order. Each
halfword store reloads the live cursor at offset 82. Difference count is the
signed low byte of the full count; cursor advancement keeps values below eight
and otherwise writes zero. The existing C conversion preserves VCVT saturation
and FPSCR behavior rather than introducing an out-of-range C cast.

The recorded GCC9 profile generates the native 56-byte provider frame. Saved
state/x/y/z words start at SP+0/+4/+8/+12. The fourth-channel pointer is reloaded
from incoming stack SP+56; count is captured from SP+60 before providers run.
The third-channel pointer is reloaded from its saved SP+12 word, while state,
x/y and count remain cached. Explicit volatile fields/parameter retain these
observed reads. Other private register-save offsets differ; native R12
preservation and arbitrary private-frame inspection are not established.

Verification of final normal-build objects passes:

- 1,600 actual native/C collector pairs, including 30 logical fault cases.
  The candidate executes C statistics, conversion and sqrt/errno providers.
  Tests cover all 256 cursor bytes, signed/full count boundaries, overlapping
  arrays and state, input arrays over incoming argument words, FP modes and
  late faults after preceding publications.
- 896 modeled-provider pairs. Providers replace the incoming fourth pointer
  and count, modify saved argument slots and the live cursor, clobber allowed
  registers, and return raw means and controlled FP classes. NaNs, infinities,
  conversion limits, signed zeros/subnormals and FPSCR modes are covered.
  These checks distinguish live fourth/z reloads from cached count/state/x/y.
- 216 actual accelerometer-stage replays through the C collector, four C
  statistics, three C history/reset helpers, C conversion and C sqrt/errno.
  Stage and spectrum remain stock; EABI memory clear remains stock. All
  provider execution counts match the reference and are recorded.
- Eight rejected defects: cached fourth pointer, wrong saved third-channel
  slot, masked cursor, full-width difference count, extra early mean
  publication, inclusive wrap boundary, word-wide slot stores and reordered
  difference publication.

Comparisons retain full external buffer hashes, ordered public writes, provider
arguments/depth/FPSCR, R0, preserved general/FP registers, SP and masks. Fault
cases compare logical access and preceding writes. Caller-clobbered registers,
APSR, private save residue and full exception-frame/fault-PC equality are
excluded. The precise frame is compiler/profile dependent and must be rechecked
if either changes. The earlier typed summary and raw planner helper keep their
checked/injected-callback APIs with `_checked` names; the native frontier now
names this provider.

All 710 units (636 application, 74 bootloader) compile and compose without
failures or duplicate strong symbols; imports remain 178/34. The accelerometer
stage `0x5ed14` itself remains unresolved. Manifest validation passes. Exact
qualification selects zero bytes for this collector, leaving the canonical
plan at 4,381 source-built executable bytes, 641,779 stock executable bytes and
248 resource bytes. The fresh R1 hybrid matches stock. Physical/concurrent
sensor behavior, complete source-only linking and C byte identity remain
unfinished. The [machine receipt](gomore-accel-collect-c-review.json) binds REA,
source/object hashes, frame evidence and all validation results.

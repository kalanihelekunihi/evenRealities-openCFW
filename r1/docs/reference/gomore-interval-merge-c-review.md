# R1 optical interval merger and derivative selector in C

`native_gomore_interval_merge.c` implements merger `0x4857c` and maximum derivative
index `0x64774`. `native_gomore_peak_match.c` additionally preserves the two native
reference bytes that become visible as merger record padding. The guarded generic
utilities retain their bodies under `_checked`; an inaccurate duplicate-loop
comment is corrected. No assembly, executable blob, trap or persistent RAM is added.

The merger clears its output first, snapshots the wrapped window offset before
compaction, caches the post-compaction interval count, and reloads live candidate
and publication counts at native use sites. It captures incoming indices and
sample values before calling the derivative selector. The native tail retry
recomputes the same candidate once before entering the tail path; an exact
duplicate instead advances to the next candidate. Insertion captures source words
in middle/value/end/start order and publishes shifted records in that order;
new records publish four ascending words. Insertion updates the live count before
record publication, while append updates it afterward. Capacity and final ordering
failures preserve their distinct native count/output effects.

Mixed overlaps retain encoded-double tolerance decisions, raw .7/.3 scale
constants, low-byte width distances and repeated signaling comparisons. The
selected-record copy at native `0x48848` writes **only a private stack copy**.
It does not replace the persisted interval. A targeted initially unordered state
reaches that exact native block, then fails validation with count zero while the
record bytes remain unchanged. This is kept rather than repairing the stock
algorithm. A separate duplicate vector proves one derivative call and no record
publication. A distinct-NaN sum vector confirms sample-before-accumulator order.

The derivative helper loads next sample before current and subtracts before
checking its signed exclusive loop bound, including empty/reversed ranges. It
retains the full incoming begin word when no update occurs and truncates only
updated indices to 16 bits. It adds no empty-input guard.

## Padding that escapes the native stack

Native merger's frame is 128 bytes. The new record at own SP+8 has a middle
halfword at SP+12 and an untouched halfword at SP+14. Its four-word publication
therefore exposes the two incoming stack bytes at **entry SP-114**. These bytes
cannot be replaced with zero or treated as irrelevant private scratch.

The preserved counterexample runs native peak+merge versus the prior C peak and
new C merger. The C producer left `0020` where stock left `0000`, changing offsets
95, 111, 127, 143, 159 and 175: exactly one padding byte in each of six published
records. The old peak object and recovered source are preserved under `build/`,
and the recovered source hash matches its original build report. The probe
explicitly selects that old object, so the old mismatch remains reproducible
without reverting the current implementation.

The C merger uses the GCC CFA builtin to capture the native stack halfword after
initial output clearing and before its private worker reuses that region. It
places the captured value in the record and restores the same physical halfword
on normal return. The peak matcher now publishes its initialized private reference
bytes 14 and 15 to entry SP-114 before either success or failure return. That is
the native reference-array footprint consumed by the next stock merger. It is
transient stack compatibility, not a global side channel or an uninitialized C
object read. The small CFA probe and actual wrapper disassembly establish the
recorded compiler's entry-SP calculation without an assembler SP adapter.

The C wrapper is 24 bytes and worker 104 bytes, retaining native **128-byte
provider depth** at compaction and derivative calls. The peak matcher remains
120 bytes; its CFA-based publication is independent of that difference. These
statements apply to the recorded GCC9 profile. Other compilers/profiles require
fresh ABI validation. Arbitrary buffers overlapping a callee's private frame,
all private layout, multiword bus atomicity, guard-page/fault timing and physical
hardware execution are not proved.

## Verification

- **604 nonfault derivative pairs and 600 merger pairs** pass, with six dedicated
  fault pairs, three incoming stack-argument aliases, and targeted discarded-copy,
  exact-duplicate and NaN-mean vectors. The random merger cases include 434 native
  successes and 166 native failure returns. Cases cover raw FP patterns and seven
  rounding/FZ/DN modes, zero through forty stored intervals, wrapped offsets,
  overlapping caller buffers and live count aliases. Raw return, full external
  buffer bytes, ordered writes, complete FPSCR, provider arguments, SP and
  preserved general/FP registers agree.
- Another **600 modeled merger pairs**, five dedicated faults and the same alias
  and targeted vectors pass. Compact/derivative models clobber caller-saved GP/FP
  registers, mutate live inputs/counts after capture, change the window after
  the offset snapshot and return high-word derivative bits that native stores
  must truncate. They are caller/ABI evidence, not derivative-body coverage.
- Native block counters establish execution of insertion, append, tail replace,
  retry, overlap/width decisions, capacity and validation failures, plus the
  explicitly targeted discarded local copy. These counters are bounded branch
  evidence, not a proof for every possible state.
- **63 sequential peak/merge pairs** across counts 0, 1, 2, 3, 6, 14, 15, 16 and 20
  and seven FP modes pass. Each side performs **126 merger calls**, checking full
  record bytes, nonzero inherited reference padding, a subsequent merge and the
  retained physical stack halfword.
- The modified peak producer retains the earlier **1,656 actual and 456 modeled
  peak comparisons**, including their fault and incoming-argument alias checks.
  The independent peak tests still exclude general private scratch; the new
  sequential fixture supplies the escaping-padding evidence.
- **112 optical-root pairs** pass the strict trace, including **112 C merger
  calls** and exact nested compaction/extrema SP and pointers. These particular
  root cases make zero derivative calls; the direct and sequential tests cover
  that path. Direct C compact entries are recorded once, alongside redirected
  native calls, so the trace does not omit newly direct C calls.
- **14 compiled defects** are rejected: derivative empty guard, offset scale/order,
  zero padding, missing padding restore, unmasked middle, dropped retry, duplicate
  overwrite, persisted private replacement, shift/write/count order, premature
  capacity, mean operand order and zero producer padding. Compile/link or harness
  errors do not count; rejection requires a stock/C or inherited-padding mismatch.

New/modified pipeline providers execute in C in these fixtures. Qsort, power/root
and raw soft-double primitives still execute stock code where bound by the
fixture. Private stack writes are excluded except for the explicitly compared
inherited halfword and record bytes. No full source-only runtime or physical
validation is claimed.

The final build passes **705 units: 631 application and 74 bootloader**, with no
failures or duplicate strong symbols. Application/bootloader imports remain
**179 / 34**, with the same import sets. All **702 prior objects** outside the
checked-API owner and the intentionally modified padding producer are unchanged.
All **704 padding-checkpoint objects** outside the checked-API owner are identical
to the final build, binding earlier expanded peak replay to the final artifact.

Scoped qualification selects zero regions. Hybrid equality passes with 4,381
source-built executable bytes, 641,779 stock executable bytes and 248 resource
bytes; the canonical plan is unchanged. The optical root, complete source linking,
whole executable byte identity and physical validation remain open. The
[receipt](gomore-interval-merge-c-review.json) binds evidence.

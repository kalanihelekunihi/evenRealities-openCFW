# R1 optical peak matcher in C

`native_gomore_peak_match.c` implements the native seven-word ABI at `0x64380`.
It connects the existing C statistics, inclusive sort and quantized valley selector.
The old guarded, provider-injected utility retains its behavior under
`gomore_primitives_peak_candidate_match_checked`. No assembly, executable data,
trap, persistent RAM or alternate stock implementation is introduced.

The instruction-led implementation preserves initial output clearing, private
20-byte clears, low-count cleanup, reference-copy count capture and subsequent
count reload, live candidate-count reads during workspace fill/filtering, quartile
sorting, ordered strict threshold filtering, byte counters, output-array clear
order, direct pairing and strict fallback spacing/tail bounds. The fallback reads
the previous published candidate again and uses the quantized selector. Success
publishes reference count before candidate count, recomputes live output spacing,
then stores the median. Failure clears reference count, candidate count and output
in that order. The workspace argument is captured before initial output clearing;
reference-count and output arguments retain their later volatile reloads.

REA pseudocode suggests a misleading early loop and comparison temporaries.
Native instructions show low-count failure. Carry branches consume the encoded
ordering from `0x27f0c`: negative words retain their bits; other words map to
`0x8000000000000000 - bits`; carry means transformed second operand is at least
the first. The C helper uses unsigned integer arithmetic, preserving signed-zero
and NaN encodings rather than replacing this with an IEEE double comparison.

The final production object passes:

- **1,656 native dependency pairs**, including 1,333 caller-buffer overlap cases
  and 465 successful randomized selections, plus **three incoming stack-argument
  alias cases and seven invalid-pointer fault cases**. These compare result,
  complete external buffer writes/state, full FPSCR, return completion, SP and
  preserved general/FP registers. Native dependency entry counts agree, including
  558 valley selections and 870 subrange sorts. Counts exercised are 0 through 20;
  the native private arrays do not establish safe behavior for larger counts.
- **456 modeled dependency pairs**, including 333 overlap cases and 71 successful
  randomized selections, plus the same three stack aliases and seven faults.
  Providers clobber caller-saved general/FP registers, supply raw special-value
  returns, reverse sort data, and sometimes mutate the live candidate count.
  Normalized argument traces and externally visible results agree.
- **5,144 raw-double encoded-carry pairs** against native `0x27f0c`. A probe wrapper
  compiles the exact production carry expression because the production compiler
  inlines the private helper. The full matcher tests also exercise that expression.
- **112 actual optical-root pairs**, substituting this C matcher together with C
  statistics, extrema, append/compaction and processing helpers. The native root
  invokes the C matcher 112 times and subrange sort 208 times. These root cases
  make zero valley calls; direct matcher cases supply that branch coverage.

The direct and caller fixtures execute native qsort, power, square root, EABI
clear/move and soft-double primitives. Statistics, sort wrapper, valley selector
and special-value providers use C. Existing reviews independently cover lower C
providers; this fixture is not proof of a fully C runtime. Fault replay checks
observed accesses and FP state, not every hardware bus/alignment condition.
Private stack writes are excluded from comparisons. C's own frame is 120 bytes
versus native 128, and private-array offsets differ. Instruction identity and
private layout equality are not claimed.

The source build passes **700 units: 626 application, 74 bootloader**, with no
failures or duplicate strong symbols. Imports remain 179 application and 34
bootloader. All 698 previous objects outside the renamed checked-API owner are
unchanged. Scoped qualification selects zero regions. Hybrid equality passes
with 4,381 source-built executable bytes, 641,779 stock executable bytes and 248
resource bytes; the canonical plan is unchanged. Complete C linking, the optical
root, whole executable byte identity and physical hardware validation remain open.

The [receipt](gomore-peak-match-c-review.json) binds production and replay evidence.

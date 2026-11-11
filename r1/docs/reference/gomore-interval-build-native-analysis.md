# R1 interval build: native history, time and status contract

REA identifies the complete 518-byte routine at `0x692e4`. Its nine arguments
are output, context/history, mode, stored interval, timezone halfword pointer,
controls, source descriptor, unused aggregation and policy. The existing
portable helper is a different API and is not an accepted native binding.
The frontier now records an unresolved route. The [receipt](gomore-interval-build-native-analysis.json)
binds REA code/literals, executable replay and unchanged production hashes.

The routine clears a private 32-byte result, sets flag byte 26 to 4, and
captures source start plus preceding byte 38 times 60 into result word 8.
It captures source end into word 12. Source type byte 37 equal to 2, with
policy byte 4 zero, selects the unadjusted source start; otherwise start is
adjusted. A nonzero context word 172 raises start by unsigned maximum.

Mode 1 or nonzero policy byte 4 skips history adjustment. Otherwise, nonzero
control word 4 shifts source end by its wrapping product with 60. With zero
shift, the routine examines at most fifteen history slots. Each timestamp is
`source_end - 1 - index*60` with 32-bit wrap. The minute modulo-15 slot uses
the current minute when timestamp remainder is 59, otherwise the previous
minute slot, wrapping slot zero to 14. A sample strictly greater than threshold
stops the scan; all preceding samples subtract sixty seconds each. Context
byte 182 exactly 1 selects `0x3f59999a` (0.85); all other values select
`0x3f333333` (0.7).

The native instruction is **VCMPE**, followed by copying FPSCR conditions into
APSR for the branch. Quiet and signaling NaNs both set invalid, produce
unordered conditions and count as nonbreaking samples. Flush-to-zero
subnormal inputs set IDC. Equal samples do not stop the scan. FPSCR condition
bits from the last history comparison survive later integer status checks and
ratio arithmetic. These effects cannot be inferred from a boolean result alone.

Selected end is first raised to start, then a nonzero context word 164 lowers
it by unsigned minimum. That second clamp can leave end below start; duration
is the unsigned wrapping difference divided by 60. Metadata from stored word
4, start and signed policy minimum halfword 0 are captured before calendar
conversion. The signed timezone halfword contributes start+minutes*60 modulo
32 bits. Native calendar `0x59cb0` writes thirteen bytes; build reads its hour
at byte 10. Its return register is ignored.

After calendar conversion, policy hours 6/7 and controls auxiliary byte 2 are
read fresh. Outside `begin <= hour < end`, duration threshold is 20 minutes;
inside, it is 180. The source metric at word 28 is then compared as a signed
raw word with `0x42c80000`, rather than through a floating comparison. Metric
at or above that raw threshold produces class 1. Otherwise, duration at least
900 minutes triggers signed binary32 conversion/division of source word 24
by source word 8; zero denominator selects positive zero without reading the
numerator. A signed raw ratio above `0x3e570a3d` produces class 2.

For the remaining paths, reaching the duration threshold sets flags 0x1c
and class 0. A shorter interval meeting the captured signed minimum and live
hour window gets flags 0x0c and class 3. Other short intervals retain flags 4
and get class 4. Hours are read again for that final window check. The final
32-byte movement forwards native R0, destination end on the tested path.

**Build class is byte 28. Refinement's merge status is byte 29.** They are
separate fields and must not share one portable status assignment. Record
words 0/4 are selected start/end; words 8/12 are captured source start/end;
word 16 is stored metadata and word 20 repeats selected start. Flag byte 26,
auxiliary byte 27 and class byte 28 occupy the otherwise cleared tail.

The native replay passes **4,676 cases**, including eight faults and every
class 0–4. It covers duration/hour/metric/count boundaries, wrapping shifts,
clamps, preceding counts, source profiles and output aliases. Actual native
clear/movement execute. The calendar provider is modeled with the observed
thirteen-byte output shape. Of the cases, 968 execute **10,284 history
comparisons**, including equality, NaNs, subnormals, threshold selector 2,
minute wrap and end-time wrap. A scalar/history oracle predicts selected slots,
records and complete FPSCR state. An exact-rational oracle checks **1,095
ratio paths**, including conversions, rounding and cumulative inexact.

There are **216 calendar-return mutation cases**. They distinguish captured
minimum, clamps, timezone and metadata from fresh hours, auxiliary, metric
and ratio inputs. For a 900-minute interval with count 1,800 and sum 378,
nearest/downward/toward-zero rounding give class 0, while upward rounding
crosses the stock ratio threshold and gives class 2. Saved integer/FP
registers, SP, masks and complete FPSCR are checked on returns. Private stack
identity, caller-clobbered registers and interrupted-fault R0 are excluded.

This is native analysis, not compiled-C or hardware proof. All 670 production
sources/objects, the manifest and canonical plan are unchanged; imports remain
164 application / 34 bootloader. The next C binding must preserve signed/raw
comparisons, VCMPE effects, wrapped history selection, capture/reload points,
distinct status fields and native memory-move return. Calendar binding and
physical/concurrent behavior remain unresolved.

The subsequent [C review](gomore-interval-build-c-review.md) implements this
contract with compiler-generated signaling comparisons and reproduces this
native baseline before expanded and integrated verification.

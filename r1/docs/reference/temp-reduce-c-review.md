# Ten-sample temperature reduction reconstructed in C

The private frame/register contract below is superseded by the [explicit C workspace](temp-reduce-pure-c-review.md). Historical alias tests remain evidence of the earlier implementation.

`runtime/native_temperature_reduce.c` supplies missing stock `0x51108` in C.
It acquires the bus, enables the sensor pair, calls `osDelay(80)`, then reads
ten paired samples with `osDelay(5)` after every pair, including the last.
It disables/releases the sensor bus before reading the calibration record.
Errors do not short-circuit this native sequence.

Each channel accumulates modulo 2^32, tracks signed extrema using stock's
initial minimum 65,535 and maximum -65,536, subtracts those extrema, divides
the signed wrapped remainder by eight toward zero, and narrows to signed
16 bits. Initial halfwords are published at output offsets 1 and 3. If any
of the first six calibration bytes is not 0xff, mode 0 subtracts and mode 1
adds the corresponding signed offset; other modes leave the value unchanged.
Both offsets are loaded before the first calibrated output store, while the
second mode byte is loaded afterward. The output pointer is reloaded for each
store. Count byte 2 is written last. Ring and SDK logs preserve repeated mode
queries and all six signed result/extrema arguments.

The configured Clang profile exposes the native 72-byte frame: logging words
at +0..16, calibration at +20..27 and saved output pointer at +32. Empty R4–R11
constraints preserve provider state throughout sampling and reduction. R4/R5
hold channel-2 maximum/minimum; R8/R9 hold channel-0 maximum/minimum; R10/R11
hold sums. R6 changes from the first sample to the second reduced value, and
R7 changes from sample index to the first reduced value. No executed assembly or opcode data implements this routine.

The probe passes 36,720 paired stock/C cases against an independent signed
trimming/calibration oracle, covering signed boundaries, wrapped sums, random
full-word samples, calibration modes/negative offsets and changing log modes.
Another 6,120 paired cases compare complete 72-byte provider-frame snapshots,
including outputs aliased into calibration offsets 19–22. Their calibration
and output side effects match stock. A further 120 direct product smoke cases
pass. The manifest product, qualified compile and tested probe have identical
function/data bytes and relocations, so the larger probe evidence applies to
the product implementation. Tests compare provider sequences, live R4–R11,
logging arguments, final outputs/calibration, preserved registers/SP and masks.
Wrong extrema sentinels, unsigned trimming, wrong calibration mode, nine-sample
count and collapsed mode queries are rejected.

This is not an exact selection. A strict first-instruction probe shows native
saving incoming R0 at caller SP-40 first, while C saves R4 at SP-36 first.
Qualification admits no region. Full provider-frame equality does not establish
private instruction/access ordering or arbitrary control-frame aliases.
All hardware/record/log providers are modeled; electrical response, actual
timing, faults and concurrency remain unproven. Caller-clobbered registers,
flags and return R0 of this void entry are excluded from behavioral comparison.

All 586 R1 units compile. All 585 prior objects and the 164/34 import sets
remain unchanged. The source plan and canonical hybrid hash remain unchanged,
with 4,245 source-built bytes. Complete source-only rebuilding remains open.
Reproducible probes, REA evidence, qualification and audit are under
`build/goal-r1-temp-reduce-c`; durable results are in the adjacent JSON.

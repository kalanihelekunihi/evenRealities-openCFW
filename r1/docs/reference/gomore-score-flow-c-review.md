# R1 native statistics and score coordination in C

`native_gomore_score_flow.c` supplies the two-stage statistics coordinator at
`0x68f8c` and prepare/score entry at `0x68fbc`. Both use ordinary C with no new
assembly, globals or executable data. The [review receipt](gomore-score-flow-c-review.json)
binds production source/object hashes, REA bytes, direct and combined replays,
negative controls, qualification and normal composition.

The coordinator forwards its original four integer arguments to the interval
statistics provider with the metrics pointer as argument five. It then calls the
stage statistics provider with the same four arguments and metrics plus 28 bytes,
using wrapping 32-bit address arithmetic. Prepare/score takes seven integer/pointer
arguments, ignores its fifth mode argument as stock does, runs the coordinator,
passes the original metrics pointer to the numerical scorer, and stores its
hard-float S0 return into the caller's score pointer. No score conversion or
validation is added. The deeper statistics and numerical score routines remain
explicit native ABI imports rather than analysis-plan API substitutes.

There are 504 paired direct coordinator/prepare cases covering ignored mode
values, arbitrary argument words, provider mutations, output/metrics/data aliases,
unaligned metrics, a null score-store fault, interrupt masks, FPSCR and raw S0
results including quiet/signaling NaNs, infinities and signed zero. A further
1,537 pairs execute the actual C consumer, timeline/sample helpers, history/prefix
and score coordinators together. They compare payload/workspace bytes, raw table
padding, provider arguments and FPSCR. The chain still models table lookup,
refinement, numerical statistics/scorer and clearing. Five compiled defects are
rejected: wrong stage offset, missing first stage, wrong score input, lost output
score and using the ignored mode as duration. Total: 2,041 paired cases.

Provider stack frames differ. Native statistics calls use 32 bytes directly or
48 through prepare; production C uses 32, with a tail call at depth zero for the
direct coordinator's second stage. Numerical score uses native 16 versus C 32.
Caller-clobbered integer/FP registers, raw R0, APSR and private stack residue are
excluded. Callee-saved integer/FP registers, SP, masks and FPSCR are checked.
No physical or concurrent behavior is established.

All 631 units compile and both relocatable compositions succeed without duplicate
strong symbols. All 630 earlier objects remain identical. Resolving prepare/score
exposes interval statistics `0x68fd4`, stage statistics `0x69128` and numerical
score `0x6778c`, so application imports change from 170 to 172; bootloader imports
remain 34. The consumer's table lookup and refinement remain unresolved as well.
Manifest checks pass. Neither coordinator passes byte qualification. The exact
source plan remains unchanged at 4,299 source-built bytes; a fresh hybrid
application matches the locked artifact, retaining 641,861 executable pull-through
bytes and 248 resource bytes. Complete source-only linking and hardware validation
remain unfinished.

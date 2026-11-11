# R1 packed interval staging and exact word-store leaf in C

`native_gomore_stage.c` supplies the packed-output staging wrapper at `0x726c4`
and the selector's word-store leaf at `0x6476c`. [The review receipt](gomore-stage-c-review.json)
binds production source/object hashes, REA bytes, differential replays, negative
controls, qualification and the promoted source plan.

The wrapper clears 32 local bytes, copies the complete caller record into them,
and calls the native consumer with both context arguments, the staged record,
count pointer and workspace pointer. It returns the consumer's full raw word,
without normalizing errors or copying staged modifications back to the source.
It adds no pointer, count or status policy. The remaining native consumer at
`0x69644` has an explicit five-argument interface; the differently shaped
analysis-plan API is not used as an ABI substitute.

The word-store leaf writes the full second word and preserves its incoming R0
value. Its production C body is exactly `str r1,[r0,#4]; bx lr`, matching all four
stock bytes. It passed 436 paired full-state cases comparing every integer
register, SP/LR, APSR, masks, CONTROL, FPSCR and S0–S31, plus store address,
width/value and logical null faults. A compiled wrong-offset store is rejected.
Only this leaf enters the exact source plan, adding four source-built bytes.
All previous units/regions remain intact. Its frontier identity/integration
flags are true; the staging wrapper's remain false.

The staging wrapper passed 786 paired native/C cases covering raw context and
return words, count/workspace/source aliases, unaligned source buffers,
interrupt masks and mutations during clear/copy/consume. Another 288 pairs
execute the actual C interval dispatcher and staging wrapper together, checking
payload restoration and error normalization after the staged consumer returns.
Six compiled staging defects are rejected: short clearing/copying, wrong state,
forwarding the original record, swapped output pointers and a masked result.
There are 1,510 paired cases and seven negative controls overall.

The production staging buffer is at caller SP-64 versus native SP-56, with
provider-call depth 72 versus 64 bytes. Addresses are normalized for that data
comparison; all staged bytes and observable outputs are compared. Lower selector,
consumer, clear and copy operations remain modeled boundaries in the integration
fixture. Caller-clobbered registers, flags and private stack bytes are excluded
from the wrapper comparison. The exact leaf has the stronger full-state proof.
A GNU GCC 9 probe produces a 50-byte staging body versus native 54 and production
Clang 60; it does not establish identity, and the production toolchain is unchanged.
This unit introduces no RAM ownership.

All 627 units compile and both relocatable payloads compose without duplicate
strong symbols. All 626 prior objects are unchanged. Resolving the staging import
exposes the native consumer, so counts stay at 168 application and 34 bootloader
imports. Exact qualification accepts only the four-byte leaf. The updated hybrid
has 4,299 source-built bytes, 641,861 executable pull-through bytes and 248 resource
bytes, matching locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Physical/concurrent consumer behavior, complete source linking and whole-image
source completeness remain open.

The subsequent [consumer C reconstruction](gomore-consume-c-review.md) supplies
the consumer and interval predicate. Five lower native providers remain unresolved;
that follow-up preserves explicit raw-frame and signaling-comparison boundaries.

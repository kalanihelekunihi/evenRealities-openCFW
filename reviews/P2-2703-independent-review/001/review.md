# Independent review 2703 — indexed enable4 original chain

**Result: PASS_SCOPED.** The pinned source, ITCM image, candidate artifacts, and all nine body hashes match the receipt. An isolated replay passed all 256 fixtures with no firmware-function interceptions.

The full dispatcher and direct-entry paths match the decoded instructions. With table index 49 and initial done byte 1, the original path runs the query/count/popcount, bit setter, enable/config leaves, pending cleanup/countdown, interrupt masking, and original FP/ITCM delay chain. Ordered writes, mask values, countdown writes and delays, returned status, high registers, and stack restoration all matched the fixture assertions. The wrapper dispatches operation 4 to the original enable4 body and forwards the index. The active/pending=0 case publishes the temporary frame pointer and then cleanup skips, leaving that pointer in the shared field; this is the decoded and observed behavior, with no assertion that the pointer remains valid after return.

The fixtures do not cover done=0 creation of new pending work, other indices, asynchronous transitions, concurrent calls, or physical hardware effects. This private evidence remains `accepted:false` and does not establish canonical admission or whole-image completeness.

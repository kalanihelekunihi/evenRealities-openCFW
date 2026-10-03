# Independent review 2827 — handler 0 wait/service chain

**Result: PASS_SCOPED.** The source, corrected handler0 body, ITCM image, and candidate artifact hashes verify. The isolated 128-fixture replay passes with the original wait/service and handler chain.

The fixtures cover runtime bit 0 set, `newfirst=0`, pending index equal to `oldfirst=1`, `newsecond=0`, and service flag 0. Both ready and timeout cases run; the replay checks ordered writes, delay counts, ITCM iterations, call order, packed return, and register/frame/mask preservation. Alternate flags, indices, categories, active op4, broader hardware/readiness behavior, and caller ownership remain outside scope. `accepted` remains false.

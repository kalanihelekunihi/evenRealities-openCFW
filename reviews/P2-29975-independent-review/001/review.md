# Independent review 29975

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-fresh-counter-update-signed-rechecks-frame40-return-30374-map/001`. Its listed hashes match the candidate receipt and the input hash matches the locked Apollo image. Independent reassembly confirms the full 66-byte interval `[0x4EAF34,0x4EAF76)` decodes contiguously as 29 Thumb instructions.

The `4EB1C0` call receives R2=250, incoming R7 as R1, and a fresh word through current R5 as R0. The actual postcall R4 selects whether the pointed-to fresh word is incremented or decremented; each path uses the actual word read and stores the wrapped 32-bit result. Subsequent literal and pointee loads are independent fresh reads. The signed negative check stores zero; otherwise a fresh word is signed-compared with 3 and values at least 3 are replaced by 2. Because of the intervening independent reads, no stable final counter range is implied. At the shared return, `ADD SP,#20` followed by `POP {R4,R5,R6,R7,PC}` consumes mutable stack contents and advances SP by another 20 bytes. Earlier control-flow paths may bypass this counter routine.

This is bounded partial evidence only. The next address is outside the map; no helper behavior, global coverage, source completeness, freeze, or byte equality is established.

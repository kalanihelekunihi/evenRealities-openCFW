# Independent review 29995

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-null-gated-helper-saved-r7-return-frame8-30394-map/001`. Its file hashes and locked image hash match the receipt. Independent reassembly confirms the exact 14-byte interval `[0x4EB1B2,0x4EB1C0)` as six contiguous Thumb instructions.

`PUSH {R7,LR}` creates an eight-byte frame. The actual incoming R0 is compared with zero; only nonzero reaches the opaque `44EA04` call, after setting R2=0. At either return path, `POP {R0,PC}` reads fresh mutable stack words into R0 and PC and advances SP by eight. Thus the helper's R0 result is not claimed as the outward return value; the saved R7 slot becomes R0. The candidate's bounded description matches these semantics.

This is partial evidence for only the listed interval. No helper behavior, global coverage, source completeness, freeze, or byte equality is established.

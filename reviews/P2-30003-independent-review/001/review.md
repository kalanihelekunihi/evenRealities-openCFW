# Independent review 30003

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-stack-configuration-or-direct-helper-frame120-return-30402-map/001`. Candidate file hashes and locked image hash match the receipt. Independent reassembly verifies all 96 bytes in `[0x4EB2BC,0x4EB31C)` as 39 contiguous Thumb instructions.

The actual R5 zero branch sets R2=0, passes current R7 and R4 as R1/R0 to `44EA04`, then joins the shared epilogue. The nonzero branch passes current SP to `4503D6`; after that call, it stores the actual current R4 at SP+0 and calls `4506CE` with R2=R7, R1=R8, R0=current SP. It then stores the actual postcall R5 at SP+48. Three separate fresh literal loads are stored at current SP offsets +4, +16 and +32, with intervening NOPs represented as no-ops. The fresh actual R6 base receives byte 1 at offset 292 before `450408` is called with the current SP. The shared epilogue adds 96 to SP and restores six fresh words into R4/R5/R6/R7/R8/PC, advancing SP by 24 and honoring mutable frame contents.

This is bounded partial evidence. No opaque helper structure behavior, global coverage, source completeness, freeze, or byte equality is established.

# Independent review 30001

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-actual-three-value-event843-staging-frame120-middle-30400-map/001`. Candidate hashes and locked image hash match the receipt. Independent reassembly verifies all 78 bytes in `[0x4EB26E,0x4EB2BC)` as 28 contiguous Thumb instructions.

The bit1 query gates event843, whose stack slots receive current R5/R7/R8 and a fresh word from `4EBDE0`, alongside the listed fresh diagnostic words. A separate bit0/bit2 query branch reads `4EBDE4`, stages current R5 and R7, copies R8 to R3 with nonflag MOV, then copies the fresh word into R2. `MOVS.W R0,#0x10C00000` yields N=Z=C=0 and preserves V. Calls use their actual postcall register state, and the continuation is outside this interval.

This is bounded partial evidence only; no helper behavior, global coverage, source completeness, freeze, or byte equality is established.

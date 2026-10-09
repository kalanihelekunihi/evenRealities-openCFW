# Independent review 29969

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-input-one-helper-gate-event691-frame40-middle-30368-map/001`. The receipt and all five listed hashes match. Independent reassembly confirms all 96 bytes decode contiguously as 33 instructions over `[0x4EAE14,0x4EAE74)`.

The fresh `[R5]` word feeds `44E498`; actual returned R0 is copied to R6 with MOVS flags, then R4 is tested against 1. The `4EAC60` call's actual R0 zero/nonzero split is preserved. On its zero branch, the separate query calls gate event691 by bit1, then later `43CE9E` by bit0 or bit2 from independent helper results. Event691 stack slots, literal loads and helper arguments match the instructions. `MOVS.W R0,#0x10000000` produces N=Z=C=0 and preserves V. On the nonzero `4EAC60` route, `ADDS.W R7,R6,#288` updates full NZCV as specified before branching outside the span. No stable helper results, preserved R4/R5/R6, or ABI assumptions are made.

This remains bounded, partial evidence. Its external paths are excluded; no helper closure, global coverage, source completeness, freeze, or byte equality is established.

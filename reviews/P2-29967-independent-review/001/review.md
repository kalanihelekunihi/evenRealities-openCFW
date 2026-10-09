# Independent review 29967

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-fresh-global-word-zero-gate-event680-frame40-middle-30366-map/001`. The receipt and all five listed candidate file hashes match. Independent reassembly confirms the 80-byte interval `[0x4EADC4,0x4EAE14)` is tiled by 27 instructions without mismatch.

The fresh literal and current pointee word gate are distinct, with a nonzero word branching to the excluded boundary. Three separate query calls use left shifts by 30, 31, and 29, so the resulting N gates bit 1, bit 0, and bit 2 of their respective actual results. Event680 uses the fresh literal-backed SP+4 argument, immediate 680 at SP, fresh literal arguments in R3/R2/R1, and R0=1. `MOV.W R0,#680` does not update flags, while `MOVS R0,#1` updates N/Z. The later `MOVS.W R0,#0x04000000` yields N=Z=C=0 and preserves V from the rotated immediate expansion. Current post-call register state is retained; calls are not assumed equal or ABI-preserving.

This is a bounded partial prefix. Its exit routes continue outside the interval; no helper, caller, or global completeness claim is made.

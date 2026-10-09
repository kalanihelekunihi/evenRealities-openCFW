# Independent review 29997

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-three-incoming-arguments-null-gate-event831-frame120-prefix-30396-map/001`. Candidate hashes and the locked-image hash match its receipt. Independent reassembly confirms the exact span `[0x4EB1C0,0x4EB212)` contains 82 contiguous bytes and 30 Thumb instructions.

The entry saves six registers (24 bytes) and reserves 96 more bytes for a nominal 120-byte frame. It copies incoming R0/R1/R2 into R4/R7/R5 using flag-setting MOVS forms, then branches out of range when R4 is nonzero. On the null path, independent query calls test bit1 for event831 and bit0 or bit2 for the later `43CE9E` call. Event831 stack arguments and fresh literals match the decoded stores and loads. `MOVS.W R0,#0x04000000` yields N=Z=C=0 and preserves V. The external targets and continuations are outside this prefix, and helper postcall registers are treated as actual state rather than preserved values.

This is bounded partial evidence only; no helper behavior, global coverage, source completeness, freeze, or byte equality is established.

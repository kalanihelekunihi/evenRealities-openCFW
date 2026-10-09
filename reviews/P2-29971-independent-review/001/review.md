# Independent review 29971

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-alternate-helper-gate-event698-frame40-middle-30370-map/001`. The candidate file hashes match its receipt and its input hash matches the locked Apollo image. Independent reassembly confirms all 82 bytes decode contiguously across `[0x4EAE74,0x4EAEC6)` as 27 Thumb instructions.

The actual result from `4EACC0` controls the first branch: nonzero reaches `4EAEC2`, where `SUBS.W R7,R6,#288` updates full NZCV from the actual R6; the instruction at `4EAEC6` is outside the map. On the zero path, the bit-1 test and later bit-0/bit-2 tests use separate `43D0CE` calls and their own flags. Event 698 is reached only on the bit-1 route and uses the listed fresh literal/global reads and current SP argument slots. `MOVS.W R0,#0x10000000` sets N=Z=C=0 and preserves V. The later route's copy from the fresh `4EB774` word into R2 and call `43CE9E` are also represented without assuming helper register preservation. The five PC-relative word references match the locked image.

This is bounded partial evidence only. External destinations and continuations are outside the interval; no helper closure, global coverage, source completeness, freeze, or byte equality is established.

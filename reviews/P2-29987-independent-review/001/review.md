# Independent review 29987

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-dispatch10-or72-event769-frame48-middle-30386-map/001`. Candidate hashes and locked image hash match the receipt. Independent reassembly confirms the 64-byte span `[0x4EB0DC,0x4EB11C)` decodes contiguously as 22 Thumb instructions.

The first independent bit1 query gates event769. Its SP stores use the current stack and the event uses fresh `0x4EB79C`, `0x4EB78C`, `0x4EB328`, and `0x4EB32C` word loads. Separate bit0 and bit2 calls gate `43CE9E`; `MOVS.W R0,#0x0C000000` yields N=Z=C=0 and preserves V. No postcall register or query result is treated as stable, and literal values are distinguished from pointees. The candidate's reference list agrees with the decoded PC-relative loads.

This is bounded partial evidence. The interval ends before any continuation; no helper behavior, global coverage, source completeness, freeze, or byte equality is established.

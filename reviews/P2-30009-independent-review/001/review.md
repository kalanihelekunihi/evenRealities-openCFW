# Independent review 30009

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-inputten-fresh-byte-gate-event866-frame40-prefix-30408-map/001`. Candidate hashes and locked image hash match the receipt. Independent reassembly confirms all 92 bytes in `[0x4EB33C,0x4EB398)` decode contiguously as 32 Thumb instructions.

The entry pushes R7/LR and reserves 32 bytes. Incoming R0 is compared to ten; only equality reaches the fresh `4EB740` word and its byte-292 test. The nonzero-byte path queries bit1 for event866 with the decoded fresh literal/global words and current stack arguments. Distinct bit0 and bit2 queries gate `43CE9E`. `MOVS.W R0,#0x10000000` yields N=Z=C=0 and preserves V; the fallthrough sets R0=0 before branching outside the span. The six PC-relative references match the locked bytes.

This remains bounded partial evidence. The zero-byte and continuation targets are outside this prefix; no helper behavior, global coverage, source completeness, freeze, or byte equality is established.

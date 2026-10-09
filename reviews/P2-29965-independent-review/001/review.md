# Independent review 29965

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-fresh-byte-gate-event675-frame40-middle-30364-map/001`. Receipt and all five listed file hashes match. Independent reassembly confirms exact coverage of the 82 locked bytes and 27 instructions over `[0x4EAD72,0x4EADC4)`.

The fresh literal and byte-at-offset-292 test are correctly represented, with zero branching to the excluded boundary. Three separate `43D0CE` calls provide independent results: bit 1 gates event675, then bit 0, then bit 2 gate the later `43CE9E` call. The event stack values and fresh literal arguments match the encoded loads/stores. `MOVW R0,#675` is non-flag-setting; `MOVS R0,#2` sets N/Z. `MOVS.W R0,#0x08000000` sets N/Z to zero and C=0 from its rotated immediate expansion, preserving V. Actual helper return state is carried forward; no ABI or repeated-read equality assumption is made.

This is bounded partial evidence only. Both continuation targets are outside this span, and no helper closure, global coverage, source completeness, freeze, or byte equality is claimed.

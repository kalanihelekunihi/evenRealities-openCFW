# Independent review 30005

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-three-input-frame120-four-span-direct-branch-union-30404-map/001`. Union audit/replay/summary hashes match the receipt. All four pinned component maps are partial/unaccepted and their receipt/member hashes match the union component bindings. Independent locked-image replay and disassembly confirm exact tiling of `[0x4EB1C0,0x4EB31C)`: 348 bytes and 130 instructions. All 14 direct branch targets are decoded instruction starts within the union.

This is bounded connectivity evidence only. It does not establish helper behavior, incoming or indirect control flow, data accounting, global coverage, source completeness, freeze, or byte equality.

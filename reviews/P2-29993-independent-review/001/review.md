# Independent review 29993

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-six-value-dispatch-frame48-seven-span-direct-branch-union-30392-map/001`. Union audit/replay/summary hashes match the receipt. All seven pinned map attempts are partial/unaccepted and their receipt/member hashes match the component bindings. Independent locked-image comparison and full-span disassembly confirm exact tiling of `[0x4EAF76,0x4EB1B2)`: 572 bytes, 207 instructions. All 36 direct branches target instruction starts within the union.

This is bounded connectivity evidence only. It does not establish helper behavior, incoming or indirect control flow, data accounting, global coverage, source completeness, freeze, or byte equality.

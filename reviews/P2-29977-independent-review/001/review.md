# Independent review 29977

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-input-counter-frame40-seven-span-direct-branch-union-30376-map/001`. The audit, replay and summary hashes match the union receipt. All seven referenced map attempts are partial/unaccepted; their receipt and member hashes match the union's pinned component hashes. Independently checking their instruction records against the locked image establishes contiguous exact tiling of `[0x4EAD10,0x4EAF76)`: 614 instruction bytes across 216 instructions. A separate disassembly of the full locked interval reproduces the component stream and confirms all 37 direct branch targets are instruction starts within the union.

This is a bounded connectivity result only. It does not establish helper behavior, indirect or incoming control flow, data accounting, global coverage, source completeness, freeze, or byte equality.

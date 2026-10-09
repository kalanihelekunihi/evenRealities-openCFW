# Source-discovery track deliverable

Final result: two isolated official source acquisitions, verified pins and file hashes; bounded static branch constraints and owner-only submodule proposals. No canonical/index/source mutations, downloaded-code execution, Docker/device access or extra workers.

- `REPORT.md`: acquisition scope, provenance and exclusions.
- `search-inventory.json`: exact web queries, relevant searched sources, acquisition inventory and local references.
- `provenance.json`: acquired working-tree file hashes and Git pins/remotes.
- `nationalchip-comparison.json`, `static-diffs/`: existing KWS versus AIoT differences.
- `STATIC-COMPARISON.md`: source-line signatures and locked target candidates.
- `FINAL-CONSTRAINTS.md`: final bounded conclusions and incorporated independent-audit caveat; KWS PLL citation corrected to clock_board.c:118.
- `locked-target-candidates.json`, `locked-string-evidence.json`, `branch-constraint-evidence.json`, `vad-callsite-byte-checks.json`, `consumed-disassembly.json`: target identity, exact bytes and local executable-reference evidence.
- `PROPOSED-GITMODULES.txt`, `submodule-proposal-check.json`: exact proposed entries, current canonical duplicate check and pins. Both are absent from current canonical section/path/URL registry; no root modification performed.

Remaining questions: exact producing checkout and original build configuration; entry-point/indirect-root reachability of VAD call sites; image-bound board-structure field and SRAM alias binding; external ARC startup/ROM bytes. Existing references support no further restriction on those questions. Five-offset PLL and active local VAD call instructions constrain an unmodified source branch, not an entire modified checkout. Shared LOGFBANK logic does not distinguish the two public pins. embARC stays architecture analogy only. No global source-exhaustion or whole-firmware completion claim.

## Touch PDL follow-up

`pdl-history/REPORT.md` records official Configure history, six source snapshots, targeted historical header revisions, exact deltas and bounded translation-unit candidates. No alternate official copy loop/count was found. Source baseline 2.3-Beta2 through 2.21 shares the same Configure body; early 2.0 changes trim names, not loops. Historical source acquisition remains isolated and no new submodule is needed.

## Remaining P2 source-reference leads

P2-SOURCE-CANDIDATES.md ranks three provisional C-SKY candidate groups with exact source pointers and existing target extents; ownership scan and target hashes are in remaining-source-ownership-scan.json. No new ARM/ARC mapping is supported by this track’s acquired references. Coordinator ownership confirmation remains required; no reconstruction was performed.

# OpenCFW change scan — 2026-10-07 15:26 UTC

Compared with the saved 14:11 UTC scan. This scan reads files and existing receipts; it runs no builds, emulation or generators and changes no existing source, index, campaign state or shared checkpoint. Only this report and its snapshot were added.

Component source is unchanged: **295 bootloader + 89 foundation C/header/assembly files**, all 384 hashes identical to the baseline. No matching ignore rule hides these files. The startup analysis directory separately contains **45 C/header/assembly files**; these are reconstruction and test-support artifacts, not 45 newly recovered firmware functions. Their individual identities and Git visibility are in snapshot.json.

## What advanced

| Candidate/work | Current evidence | Remaining limit |
|---|---|---|
| `4b1fb750` | Final validation summary now PASS: seven integration cases and 53 additional receipts; 201 objects/230 current frozen inputs | Unpromoted bounded offline candidate |
| `687b0a4e` selector 17 | Seven exact-image integration cases PASS; 47 regression receipts PASS; 14 direct fixtures and 1,400 initialized-root comparisons PASS | Final frozen-input reconciliation still pending; see below |
| `525a8fdd` selector 3 | Source-installed callback pointer, seven direct fixtures and natural callback PASS; seven exact-image integration cases and 44 regression receipts PASS | Three further regression suites/root reconciliation not established by this scan; no final summary |
| Runtime action `0x416200` family | Reconstructed termination wrapper, task-state/delete/release helpers: 260 original-instruction comparisons PASS; native teardown callers: 512 PASS | These proofs cut allocator calls and use controlled scheduling boundaries |
| Allocator seam | Three ownership fixtures PASS using actual heap/free implementation | Bounded valid allocation fixtures; whole scheduler/idle cleanup remains unproven |
| Runtime-integrated `602cccc` | 207-object ELF exists and hash matches the recorded candidate | No completed candidate-specific validation summary; build existence alone is not proof |

Selector 17 and 3 extend the compiler-relocated initialized callback table, rather than adding script-only scaffolding. The runtime family explains ownership-dependent release: dynamically owned stack+TCB, TCB-only ownership, or neither. Teardown wrappers clear their stored handle even when termination returns an error; that observation is a tested bounded behavior, not a confirmed hardware leak.

## Provenance and status discrepancies

The selector-17 original durable manifest has **one source-copy mismatch**: `source/verify_integrated.py`. Its expected hash is `abb85421c048abd53bd6afcf48c9285aa403b6d7ca94f9d8a8ab9a982da6f719`; current hash is `120ac873b163f07189f916889d99d1329316fc5a5928f9ee458c120aceff7976`. This is a changed verifier snapshot, not evidence of changed linked firmware objects. Preserve and reconcile the original verifier lineage before declaring the entire frozen package reconciled. Existing test PASS results remain separately identifiable.

The lineage document still says selector-17 integration/regressions have not run; those statements are stale relative to the observed seven-case/47-receipt outputs. Selector-3 REPORT likewise predates full integration receipts. This scan leaves these shared documents untouched and records the distinction here.

The previous apparent `0x416200` decompiler conflict was an offset error: VA `0x416200` maps to file offset `0x6200` for load `0x410000`. The corrected bytes support the CMSIS termination wrapper; no actual corpus conflict was established.

## What has not changed

Shared offline ELF remains **`129a6b2f38f145f33e791874f52d722fb1715d5fff5c957a285644312f34a6f9`**. New startup candidates have not replaced it. Build outputs remain intentionally ignored; this is not hiding the inspected component source. Source completeness, physical peripheral timing, scheduling/drain behavior, external ROM dependencies, production firmware viability and byte-identical rebuilding remain separate unresolved requirements.

Next useful work is to finish candidate-specific validation and provenance reconciliation, then integrate the native runtime/allocator boundary against the exact successor. No new broad inventory is needed to do that. Exact source identities, receipt hashes and observed manifest mismatch are in [snapshot.json](snapshot.json).

# OpenCFW change scan — 2026-10-09 01:35 UTC

Compared with the 00:38 UTC snapshot, component C/header/assembly inventory grew **684 → 706: 22 added, 0 modified, 0 removed**. **654 indexed, 52 untracked**. All 22 additions are untracked. Git check-ignore matched **0** component source files. These counts measure files, not recovered function count or firmware completeness.

## New substantive work

| Batch | Added source files | Recorded PASS comparisons | What it establishes |
|---|---:|---:|---|
| [PCM registry](../audio-pcm-registry-interface-successor-2026-10-09/REPORT.md) | 2 | 64 | Correct callback slot identities; four new wrapper bodies, four repeated. Stock registration does not establish an active suspend child. |
| [Mutex priority](../audio-mutex-disinherit-closure-2026-10-09/REPORT.md) | 3 | 711 direct + 24 integrated | Priority inheritance, release and timeout disinherit behavior; separate integrated ELF receipt. |
| [ISR semaphore](../audio-semaphore-isr-closure-2026-10-09/REPORT.md) | 3 | 392 | ISR receive/give and CMSIS status/context routing; PendSV request rather than delivered switch. |
| [Semaphore take](../audio-semaphore-take-closure-2026-10-09/REPORT.md) | 4 | 250 | Take, recursive mutex and waiter-priority behavior; includes reused held-count helper cases. |
| [Memory pool / heap](../audio-cmsis-memory-pool-closure-2026-10-09/REPORT.md) | 7 | 484 | Pool layout, allocation/free ownership, constructor geometry, heap split/coalescing and fatal allocation failure. |
| [Main formatter](../audio-main-formatter-source-successor-2026-10-09/REPORT.md) | 3 | 88 | Selected integer/string/float formatting and fatal logging path with known synthetic sink. Adapted previously recovered formatter source. |

The earlier queue/CMSIS and early-PCM batches now have reports and manifests; both lacked these at the prior scan. The registry successor corrects misleading predecessor callback names without rewriting sealed evidence. All batches in the table are sealed and their recorded results bind to matching receipts and source hashes. The 24 integrated mutex cases correctly use the separate integration receipt. No tests were rerun for this scan; these are author-recorded offline results, not independent completion reviews.

Important new behavioral findings: pool free uses range/status/count checks without an allocation bitmap or slot-alignment check; duplicate/interior-free behavior is demonstrated only in synthetic invalid-use fixtures. The allocator has concrete alignment and split/coalescing rules; malloc failure reaches a fatal self-loop. Formatter behavior includes nonstandard negative string-width padding. Its float instruction comparisons use a scalar Thumb/VFP Cortex-A15 profile because Unicorn M33/M7 rejects a stock double-to-float instruction; this does not validate Cortex-M exceptions or task scheduling. An actual output-driver binding remains unestablished.

## Git visibility and preservation

New source is present on disk and visible as untracked Git content. A committed-only view omits it. Root ignore rules still exclude build trees, binaries, local SDKs and decompiler databases; no nested component ignore files or global excludes setting were found, and `.git/info/exclude` is absent. There is no evidence that .gitignore hides these source additions.

Verified **2,628 current dictionary-form sealed entries**, including all **2,490 originally preserved entries**: **0 mismatches**. All **110 audit inputs** and **4 preserved checkpoints** match. Git index unchanged during scan and matches the original preservation baseline. HEAD remains `36337d9b39ff36d318b0531f2968ca7e0554a7b1`. Non-dictionary manifest formats are listed separately in the snapshot and are not included in this integrity count.

Workflow state remains P2_EXECUTING; pseudocode completion, corpus freeze, source completeness and byte-identical firmware build gates remain not_run. This scan does not establish a complete buildable firmware, live hardware behavior or independent review.

[Full source delta, Git status, recorded-result checks and preservation evidence](snapshot.json). Only this scan directory was added; existing work, staging and campaign state were preserved.

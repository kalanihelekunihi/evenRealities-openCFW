# OpenCFW change scan — 2026-10-09 02:32 UTC

Compared with the 01:35 UTC snapshot, component C/header/assembly inventory grew **706 → 721: 15 added, 0 modified, 0 removed**. **654 indexed, 67 untracked**. All additions are untracked; git check-ignore matches **zero** component source files. Counts describe files, not complete firmware source or unique functions.

## New work and understanding

| Batch | New source files | Recorded passing cases | Concrete finding |
| --- | ---: | ---: | --- |
| [Stock logger providers](../audio-logger-stock-provider-closure-2026-10-09/REPORT.md) | 5 | 681 comparisons + 9 original-instruction checks | Actual UART sink installer recovered at 0x54171C despite failed decompiler output. Its sink uses UART channel 1. |
| [UART TX ownership](../audio-uart-tx-ownership-2026-10-09/REPORT.md) | 3 | 665 | Partial asynchronous TX borrows remaining source bytes; queue admission copies bytes. FIFO acceptance and completion are distinct. Default logger has no software TX queue; channel 3 has a 1,024-byte queue. |
| [UART RX stream ownership](../audio-uart-rx-stream-ownership-2026-10-09/REPORT.md) | 4 | 582 | RX callback copies into a 2,048-byte usable stream but ignores the accepted count; flush resets staging even if only a prefix fits. |
| UART power/configuration | 3 | None recorded | Unsealed work in progress: selected source and ABI/division adapters exist, with no completed report or result. Excluded from validated progress. |

Two additional sealed logger shutdown/composition evidence batches record 5 and 25 passing original-instruction fixtures without new component source files. The composition batch proves the first startup zero-fill over 461,552 bytes, not whole reset execution.

Controlled source mutation tests distinguish a live borrowed suffix from independently copied queue bytes. RX pressure fixtures demonstrate discarded suffixes, **not measured hardware loss**. Logger success can occur without its completion marker; it does not prove bytes left a physical pin. Actual task scheduling, peripheral timing, DMA and concurrent formatter reentrancy remain outside these offline validations.

Recorded results were inspected, not rerun. All three completed source batches have matching current source hashes, retained native ELF hashes and result/receipt ELF bindings where present. Original-only checks correctly have no native ELF binding. These are author validations, not independent corpus-completion review.

## Visibility and preservation

The new C/header files are on disk and visible as untracked Git content. A committed-only view misses them. No component source is ignored. Root .gitignore hash remains unchanged; no nested component ignores or configured global excludes were found; .git/info/exclude remains absent. Ignored build/SDK/database artifacts are separate from these source additions.

Verified **2,704 dictionary-form sealed entries: zero mismatches**. All **110 audit inputs**, all **four checkpoints**, and the Git index match the preservation baseline. HEAD remains `36337d9b39ff36d318b0531f2968ca7e0554a7b1`. Non-dictionary manifest formats are recorded separately and excluded from that seal count.

Workflow remains P2_EXECUTING. Completion, freeze, source completeness and byte-identical rebuild gates remain not_run. There is useful new source-backed behavior, but no complete source-built firmware claim.

[Full source delta, Git status, receipt checks and preservation evidence](snapshot.json). This scan only adds its own directory; existing sources, work in progress, staging and campaign state were preserved. Next concrete analysis is completing the currently unvalidated UART power/configuration comparisons, then channel-3 routing or the RX receiver/task-copy boundary.

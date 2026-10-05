# OpenCFW — fresh assessment, October 5

The full G2 firmware is **not yet proven completely disassembled/classified or semantically decompiled**, and **no blob-free source build reproduces the locked image**.

Fresh snapshot 15:33:22 UTC, compared with 00:13:53 UTC:

- Byte-matched assembly export footprint: **490,200 bytes (11.40% of stored bundle), +1,874 bytes**.
- Raw pseudocode footprint: **1,902,397 bytes (44.23%), unchanged**.
- Authenticated scoped reviews: **197,000 bytes (4.58%), unchanged**.
- Complete source-built payloads: **0/6**; source-identical bundles: **0/1**.

These percentages use stored bytes, not the unknown executable-code denominator. Codec/touch have assembly exports outside the unchanged parser's supported formats, so their true assembly percentage is unknown. Raw output exists for 11,359/11,428 catalogue candidates; 69 are missing, and the catalogue itself is incomplete.

There is current foundational work: recent RTOS tick/queue fixtures add original-instruction evidence (including 168 due-task cases). Partial-status fixture evidence, overlap with earlier reviewed ranges and nested-review schema gaps explain why unique reviewed coverage stays flat; that is not zero work.

Upstream attribution is useful but uneven. EM9305 has the strongest recorded archive match: 74.50% of its 210,888-byte app record. Other compiler/library identities generally lack a complete byte-match denominator. Public upstream source is not a verified compiled replacement.

The bounded data map has151,707 confirmed non-code bytes, 1,280 metadata/padding bytes, 1,570 observed CPU instruction bytes and 4,146,670 unresolved bytes. Resource extraction and semantic completion percentages remain unknown. Original blobs are still the active providers; historical hybrid outputs are missing/incompatible with the lock.

**Priority updated locally:** boot/memory/RTOS first; then all hardware drivers, buses and processor-to-processor protocols; **EvenHub SDK and higher application logic last**. Shared campaign state was preserved. The coordinator must confirm current worker ownership before redirecting overlapping work.

Full component/functionality tables, evidence, remaining gaps and independent checks: REPORT.md.

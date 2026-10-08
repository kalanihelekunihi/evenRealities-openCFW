# Source and integration rescan

Compared with the 2026-10-07 01:13:04 UTC scan. This inspection ran no builds, generators, emulation or hardware operations; only this scan directory was written. Concurrent campaign work was preserved.

Bootloader source/header/assembly files: **230 → 235**. Foundation: **89 → 89**. Changes: **5 added, 0 modified, 0 removed**. Git visibility: {'tracked': 312, 'untracked': 12}; ignored source files: 0.

Added:

- `g2/components/bootloader/initializer_callbacks/context_events.c`
- `g2/components/bootloader/initializer_callbacks/context_events.h`
- `g2/components/bootloader/initializer_callbacks/context_irq.c`
- `g2/components/bootloader/initializer_callbacks/context_nvic.c`
- `g2/components/bootloader/initializer_callbacks/semaphore_create.c`

Modified:


Latest complete reported checkpoint **92619ea6a927…** has normal 2, malformed 3 and interruption/reboot 2 cases PASS against the same image. Actual ELF hash matches the directory. Frozen inputs: 581 files/144 objects; current working-copy inputs changed since freezing: 3 (Makefile, linker script and context_events.h). This reflects newer work; it does not change the hashed immutable ELF or invalidate the historical receipt. The current progress record measures **35,468 original instruction bytes /148,599 = 23.86826%**, versus35,362/23.79693% previously. This is bounded modeled execution, not source completeness.

Newer candidate **4f111ccb9ed4…** exists with matching ELF hash, 584 frozen files/145 objects and 0 changed frozen inputs. Receipt status at scan time: {"comparison.json": {"status": "PASS", "cases": 2, "elf_sha256": "4f111ccb9ed4131499a99a47af126d83f4b56f8abb54a5e6073cbc6566e93e8a", "distinct_original_trace_bytes": 35022}, "failures.json": {"status": "PASS", "cases": 3, "elf_sha256": "4f111ccb9ed4131499a99a47af126d83f4b56f8abb54a5e6073cbc6566e93e8a", "distinct_original_trace_bytes": 33682}, "powerloss.json": {"status": "MISSING at scan time"}}. It must not be promoted as seven-case validated until the missing receipt is present and verified.

The added C implements NVIC enable, semaphore creation/cleanup, asynchronous IOM descriptor/CQ dispatch and IRQ status/clear/wrapper handling. These are actual source bodies, not solely scripts or metadata. Callback reentry and peripheral models remain synthetic; hardware execution and safe memory-management patches are unproved.

`.gitignore:15:build/` hides build-local ELF/receipts, none of the inspected source. Ordinary git diff omits untracked additions. No global exclude is configured; `.git/info/exclude` is absent. Detailed per-file hashes, ignored/tracked status and receipt provenance are in snapshot.json. A source-complete clean rebuild, whole-firmware operation and byte equality remain unproved.

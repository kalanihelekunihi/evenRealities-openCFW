# Source and integration rescan

Read-only comparison with the 2026-10-07 00:22 UTC scan. Only this scan directory was written; no build, emulator, generator, staging or hardware operation ran. Snapshot and hashes are in [snapshot.json](snapshot.json).

Bootloader C/header/assembly files increased **223 → 230**; foundation remains **89**. Seven files were added, one modified, none removed. Across both roots, **312 are tracked and seven untracked; none ignored**. The new files are `initializer_callbacks/context_claim.c`, `context_claim.h`, `context_clock.c`, `context_instance.c`, `context_queue.c`, `context_retry.c`, and `context_transaction.c`. These implement context allocation, configuration, clocks, enable, retry and command-queue adapters. `nor_mspi_queue/nor_mspi_queue.c` now preserves the original separate flag-store sequence. Counts do not measure source completeness.

The immutable **d983284c…** ELF hash matches its snapshot directory. Its normal two, malformed three, and interruption/reboot two cases all report PASS against that exact image. All **572 frozen input files and141 linked objects** still match their recorded hashes. The seven traces contain **35,362 deduplicated original instruction bytes**, up from the prior scan's complete checkpoint34,098: **23.80%** of the148,599-byte bootloader payload. This measures observed modeled execution, not implemented completion. Numerical linker bindings decreased74→68; that count likewise is not missing-function coverage.

Additional existing receipts report740 child-function cases,496 claim/transaction cases,52 interrupt cases and two conditional stable-subtype cases PASS. The partial ownership ledger maps13 IOM functions covering2242 original body bytes. Those sizes and case counts must not be added to seven-case coverage without deduplication.

A useful newly established failure behavior: failed enable can retain a claimed command queue; retry is bounded at1000 attempts. The stable-subtype test reaches the busy-queue error on repeated initialization, but explicitly uses synthetic subtype preservation and injected poll failure. It does not establish a hardware fault or safe cleanup patch.

**Reporting lag:** `integrated-status/REPORT.md` and `progress-percentage-current.json` still identify85d6eb/23.08%, despite the newer passing d98328 receipts. This scan records the newer evidence without modifying shared status files.

`.gitignore:15:build/` hides the ELF and build-local receipts. It hides none of the examined source files. No global exclude is configured and `.git/info/exclude` is absent. New source is visible as untracked files; ordinary `git diff` alone omits those additions.

The image remains a relocated test ELF using prepared objects, numerical/provider boundaries and synthetic MMIO, ROM and scheduling. Six original floating-point effects are modeled. A source-complete clean build, hardware boot, whole-firmware behavior and byte equality remain unproved. Existing staged and unstaged work was preserved.

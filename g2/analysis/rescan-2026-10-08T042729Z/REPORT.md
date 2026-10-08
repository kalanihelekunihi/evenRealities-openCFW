# OpenCFW rescan — 2026-10-08T04:27:29.636997+00:00

Compared with the 03:14:13 UTC scan. Inspection only: no builds, generators, tests or firmware changes were executed. Only this new scan directory was written. Existing test results are recorded evidence, not freshly rerun validation; concurrent work can continue after capture.

Canonical bootloader/foundation C, headers and assembly: **475 → 475**; **0 added, 0 modified, 0 removed**. **384 tracked/indexed, 91 untracked, 0 ignored**. Source hashes were freshly compared. This narrow inventory does not count analysis reconstructions or fetched vendor headers as integrated firmware source.

The four previously accepted integrated checkpoints were freshly hashed again (see snapshot). No larger checkpoint is inferred from the additional standalone analysis. All **110 sealed audit input files** were freshly hashed: **0 changed**.

Since that scan, dependency analysis delivered public-source reproduction of six touch FIFO functions: 254 exact compiled bytes, including 198 bytes newly attributed in that batch. Recorded tests include 39 I2C initialization cases, 480 dispatch cases with explicit helper cuts, 512 actual helper/critical-section cases with null callbacks, and 104 charging-case wake cases. See ../dependency-followup-2026-10-08/REPORT.md for source pins, ABI and limits. Imported public source is distinct from independently reconstructed C and from integrated firmware source.

The newer, still in-progress callback directory contains app_event.c: 336 recorded bounded callback comparisons and 96 composed IRQ/callback cases. It establishes callback rearming of static 16-byte RX/TX buffers; a synthetic interruption during a descriptor update demonstrates why buffer replacement needs serialization. This does not prove a stock hardware fault or complete callback coverage.

The new case-stop directory contains stop_mode.c and 216 recorded comparisons. The function at 0x080050e8 selects STOP0/STOP1 and sets SLEEPDEEP, despite its historical SLEEPMode label. WFI/WFE use controlled wake cuts; actual sleep, wake timing and clock restoration remain unverified. These two directories have no completed report/manifest at capture and remain work in progress.

New readable C is present in analysis directories even when the canonical component count is unchanged. These source files are not ignored; build ELFs remain hidden by build/ and *.elf rules. A tracked-only view still omits untracked files. No blanket ignore-rule change is needed.

This scan proves neither a complete source-built OTA nor byte equality with the official bundle. Whole-image pseudocode/source coverage, exact producing toolchain configuration and physical execution remain separate requirements.

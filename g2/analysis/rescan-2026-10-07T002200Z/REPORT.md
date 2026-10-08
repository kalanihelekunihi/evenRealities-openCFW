# Source and integration rescan

Compared with `g2/analysis/rescan-2026-10-06T234423Z`. Snapshot began 2026-10-07 00:22 UTC. Read-only inspection of existing work; only this scan directory was written. No build, generator, emulator, staging, commit or hardware action ran. Active campaign files can change after observation.

## What changed

Bootloader source: **222 → 223 files**. Foundation: **89 → 89**. Across those roots: one addition, two modifications, no removals; all **312 tracked**, **zero ignored**. Counts include headers, assembly and fixtures and are not source-completeness measures.

- Added `g2/components/bootloader/initializer_callbacks/context_interrupt.c`: reconstructed context interrupt helper. Its separate immutable source ELF has a **52-case PASS** receipt (`review-worker/initializer-callbacks/context-interrupt-0x42c63a.json`). This helper is not yet selected into the shared integration image.
- Modified `initializer_callbacks/platform_finish.c`: initializer now passes the context row's transfer field, matching the original call, rather than its instance field.
- Modified `nor_commands/nor_timing_wrapper.S`: explicit Thumb alignment.

Linker/build/test changes are outside the C/header/assembly file count: the shared linker now aligns object contributions and binds `opencfw_bl_kernel_state` to reconstructed `opencfw_boot_kernel_state`. Numerical bindings decreased **75 → 74**, unique numerical addresses **67 → 66**. This measures exposed linkage cuts, not whole-firmware missing functions.

## Verified advancement

The former `ac4b5688…` odd-address Thumb failure has been superseded by immutable **dceae3b56c3ef4b0572f4cd499230ca8f5eb20419cf1c4a0910d05d607389bee**. Its ELF hash matches the snapshot directory; alignment PASS and normal **2**, malformed **3**, power-loss **2** cases all report PASS for that exact image. The durable same-image summary records **34,098 deduplicated observed original instruction bytes**, up from prior checkpoint **31,344**: **22.95% of the 148,599-byte bootloader payload**. This is bounded modeled execution coverage, not implemented-source completion or whole-OTA coverage. Previous immutable checkpoints remain present and hash-consistent.

Newer immutable **4598040563d8f41b2fc71d430114b6b8564198b439e7225e9729d2f1c93acc2e** also has matching ELF identity and alignment PASS. At scan time normal **2** and malformed **3** cases PASS; **powerloss.json is absent**, so this scan does not promote it to seven-case validated. Independent bounded receipts on this exact image show **216 kernel-state cases** and **73 NOR wait/delay cases** PASS. These exercise the newly native query, including branches the immediate-ready integration fixture may not reach. Case counts must not be summed as unique instruction coverage.

## Limits and remaining gaps

Source-linked relocated test images still contain numerical/internal provider boundaries and resident-ROM dependencies. Runtime/task/ISR and mutex children, ADC/context/service children, logger/fatal and non-null power configuration paths remain significant gaps. Six original floating-point slots have modeled effects; ADC, scheduler and ROM-storage behavior remain synthetic. NOR comparison validates descriptor length, FIFO count and valid wire bytes while retaining raw differences in unused FIFO padding. No physical timing, real task delivery, hardware boot/recovery, source-complete build or byte equality is demonstrated.

`.gitignore:15:build/` hides generated ELFs/build-local receipts; it does **not** hide any source in the two scanned roots. No configured global excludes or local exclude file was found; the nested ignore is in unrelated shortcut resources. The observed advance is real source correction and integration validation, rather than ignored new source generation.

Full source hashes, current Git views, ignore configuration and pinned image/receipt status are in `snapshot.json` and `git-status.txt`. Last complete seven-case summary: `../bootloader-completion-2026-10-06/integrated-status/same-image-validation-dceae3.json`.

# OpenCFW change scan — 2026-10-08T00:57:13.340278+00:00

Read-only inspection relative to `g2/analysis/rescan-2026-10-07T235435Z`; only this scan directory was written. Tests were not rerun. Concurrent work may advance after capture.

Canonical bootloader/foundation C/header/assembly inventory: **449 → 453 files**, 4 added, 0 modified, 0 removed. File counts include reused variants and headers; they are not reconstructed-function counts. New canonical sources ignored: 0/4.

## Accepted progress

The previously pending **229-object candidate `0b80d612…` is now accepted as a bounded offline checkpoint**. Its ELF hashes to the receipt identity. Current receipts show seven integration cases and **76 regression jobs, 0 failures**. Fixture corrections and preserved earlier failure receipts are documented in `g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/bounded-format-native/FIXTURE-REPAIRS.md`; source/object reproduction and frozen relink are recorded in its completion receipt.

The successor ledger `g2/analysis/source-replacement-ledger-2026-10-08-runtime-format` admits **20 explicitly mapped C bodies, 4,932 original bytes**, versus 15/4,656 previously (+5 bodies/+276 bytes). This is a bounded mapped lower bound, not a whole-firmware replacement percentage. The accepted candidate still calls original formatter engine `0x41e47a`.

## Formatter work outside the accepted candidate

`g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/iar-format-parser` contains independent parser, integer cursor and integer renderer sources. Existing differential receipts report **937, 288 and 1,302 cases**, respectively. These helpers are not linked into the accepted 229-object candidate. Parser/cursor fragments lie inside the engine's extent and must not be added again to whole-engine byte counts.

`g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/iar-format-engine` now contains **7 C/header draft files**, including engine dispatch, floating rendering, native FP primitives, frame entry and termination behavior. The older 1,511-case nonfloating receipt **does not match the current engine.c hash**. A retained failure on `%%:%q:%` remains unresolved. Current QEMU log contains **130/130 equal rows** for floating formats, including full FPSCR comparisons. This uses unchanged stock bytes relocated to mapped test memory; it is bounded oracle evidence, not proof at the original firmware load address, full input coverage or accepted integrated closure. The observed 130-row log is not yet accompanied by a sealed reproduction manifest. No new accepted full-engine replacement is claimed.

## Visibility and preservation

All **110 sealed audit input hashes** checked; **0 changed**. Git's rule `.gitignore:15:build/	g2/build/bootloader-completion/bounded-format-native/0b80d612fe52fd296eae01d1e304daf8769df2a6847f8649ebfe787c3108d419/candidate.elf` hides generated ELF output. `.gitignore:45:*.log	g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/iar-format-engine/qemu/probe.log` hides the QEMU log. Readable analysis C/headers remain on disk outside the build tree; a tracked-only view misses untracked work. `.gitignore` explains missing build/log visibility, not absence of source generation. Nested ignore and local/global exclude checks are captured in snapshot.json; no ignore changes were made.

Production payload providers remain official blobs; this scan found no evidence establishing a complete source-built payload or byte-identical source-built OTA. The next formatter acceptance work is to resolve the differential failure, validate current-source nonfloating/FP/ABI/error paths, freeze reproducible evidence, then integrate and rerun checkpoint checks. Hardware behavior and remaining whole-image dependencies remain outside these bounded results.

## Canonical source delta

- `g2/components/bootloader/initializer_callbacks/bounded_format_native/bounded_format.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_runtime_native/pcm22_runtime_hooks.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_runtime_native/startup_events_a.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_runtime_native/startup_runtime.c`

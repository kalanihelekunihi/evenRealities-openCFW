# OpenCFW change scan — 2026-10-07T23:54:35.232922+00:00

Read-only inspection; only this report and snapshot were written. Existing tests were not rerun. Concurrent work can advance after this snapshot.

Against the23:02 UTC scan, canonical bootloader/foundation source inventory changed from433 to449 files: 16 added, 0 modified, 0 removed. These include headers and reused variants; they are not unique reconstructed-function counts.

All27 PCM selector slots now have source bindings. The preserved227-object candidate6e16ec94 has fifteen explicitly address-mapped PCM C bodies totaling4656 original bytes, up from the sealed audit's nine bodies/2656 bytes (+2000). The successor ownership ledger is `g2/analysis/source-replacement-ledger-2026-10-07-remaining/`. This remains a bounded lower bound; no whole-image percentage is established.

The newer229-object candidate0b80d612 adds profile application(0x42ab7c,54 bytes), temperature initialization(0x42ac54,80 bytes), snprintf/vsnprintf/writer wrappers(142 original bytes combined). Existing receipts show324 hook comparisons with stubbed child contracts,560 formatter-model comparisons and216 hybrid comparisons using the original formatter engine. These five bodies are not yet added to the accepted ownership ledger; the final delivery and all validation obligations remain pending. The formatter engine at0x41e47a remains an explicit executable dependency, so hybrid passing tests do not establish source-only formatting.

Checkpoint evidence and individual job failures are recorded in snapshot.json. Missing receipt files are pending/unavailable evidence, not a passing result. No firmware build, emulator job or shared-state edit was performed by this scan.

Frozen audit preservation: 110 selected input hashes checked, 0 changed. Newly added canonical sources ignored: 0/16. Build artifact visibility: `.gitignore:15:build/	g2/build/bootloader-completion/bounded-format-native/0b80d612fe52fd296eae01d1e304daf8769df2a6847f8649ebfe787c3108d419/candidate.elf`. A tracked-only view can omit untracked C sources; ignored ELF output does not imply absent reconstruction.

Production still uses official payload providers; no complete source-built payload or byte-identical source-built OTA bundle is demonstrated. Synthetic MMIO, resident-ROM stubs, hybrid original-code oracles and bounded scheduling fixtures do not certify hardware behavior. Source-only closure still requires original formatter and remaining indirect/runtime dependencies to be resolved or explicitly bounded.

New canonical source paths:

- `g2/components/bootloader/initializer_callbacks/pcm22_remaining_native/initialized_data.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_remaining_native/interfaces.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_remaining_native/pcm22_remaining.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_remaining_native/startup_events_a.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector10_native/initialized_data.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector10_native/interfaces.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector10_native/pcm22_sequence10.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector10_native/startup_events_a.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector13_native/initialized_data.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector13_native/interfaces.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector13_native/pcm22_sequence13.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector13_native/startup_events_a.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector9_native/initialized_data.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector9_native/interfaces.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector9_native/pcm22_sequence9.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector9_native/startup_events_a.h`

## Current validation blockers

The229-object candidate now has passing normal, malformed and power-loss integration receipts. Its regression suites still record failures: six job occurrences fail because native-selector-bindings.json is missing; dispatch-bindings comparison fails; the logging-output fixture encounters an unmapped memory read. These failures are unresolved in this read-only scan. They prevent treating229 as an accepted successor even though dedicated new-body comparisons pass. Next action is to restore the owned binding fixture, inspect the dispatch-table pointer comparison and formatter dependency boundary, then rerun affected checks and reproducibility before admitting the five new bodies to a successor ledger.

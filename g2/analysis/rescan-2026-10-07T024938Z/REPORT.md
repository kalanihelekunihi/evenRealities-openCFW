# Source and integration rescan

Compared with rescan-2026-10-07T020443Z. Read-only inspection; only this scan directory was written. No builds, emulation, generators, hardware operations or changes to campaign files.

Bootloader C/header/assembly: **235 → 242**. Foundation: **89 → 89**. **7 added, 2 modified, 0 removed**. Git visibility: {'tracked': 312, 'untracked': 19}; ignored inspected source: 0.

Added:

- `g2/components/bootloader/initializer_callbacks/adc_context.c`
- `g2/components/bootloader/initializer_callbacks/adc_context.h`
- `g2/components/bootloader/initializer_callbacks/adc_control.c`
- `g2/components/bootloader/initializer_callbacks/adc_control.h`
- `g2/components/bootloader/initializer_callbacks/gpio_descriptor_data.c`
- `g2/components/bootloader/initializer_callbacks/gpio_descriptors.c`
- `g2/components/bootloader/initializer_callbacks/gpio_descriptors.h`

Modified:

- `g2/components/bootloader/initializer_callbacks/initializer_callbacks.c`
- `g2/components/bootloader/initializer_callbacks/platform_bringup.c`

Current reported complete checkpoint: **8ec1fa00cae0c882dae79282e43736418537a942645ba185d7a6d6026f5618fb**. The report receipt hash matches: True. Observed original instruction footprint **35,468 → 36,160 / 148,599**, **23.86826% → 24.33395%**. This measures bounded modeled execution, not implementation completeness or byte equality.

- Image `8ec1fa00cae0`: actual ELF hash matches directory: True; frozen files/objects 592/148; working-copy inputs changed since freeze 3; receipts {"comparison.json": {"status": "PASS", "cases": 2, "elf_sha256": "8ec1fa00cae0c882dae79282e43736418537a942645ba185d7a6d6026f5618fb", "distinct_original_trace_bytes": 35714}, "failures.json": {"status": "PASS", "cases": 3, "elf_sha256": "8ec1fa00cae0c882dae79282e43736418537a942645ba185d7a6d6026f5618fb", "distinct_original_trace_bytes": 34374}, "powerloss.json": {"status": "PASS", "cases": 2, "elf_sha256": "8ec1fa00cae0c882dae79282e43736418537a942645ba185d7a6d6026f5618fb", "distinct_original_trace_bytes": 35674}}.
- Image `6bef4edbcece`: actual ELF hash matches directory: True; frozen files/objects 589/147; working-copy inputs changed since freeze 5; receipts {"comparison.json": {"status": "PASS", "cases": 2, "elf_sha256": "6bef4edbcece2022ee41b9670cd4eff295fc62bb697e00e180c4efce8812c259", "distinct_original_trace_bytes": 35220}, "failures.json": {"status": "PASS", "cases": 3, "elf_sha256": "6bef4edbcece2022ee41b9670cd4eff295fc62bb697e00e180c4efce8812c259", "distinct_original_trace_bytes": 33880}, "powerloss.json": {"status": "PASS", "cases": 2, "elf_sha256": "6bef4edbcece2022ee41b9670cd4eff295fc62bb697e00e180c4efce8812c259", "distinct_original_trace_bytes": 35180}}.
- Image `4f111ccb9ed4`: actual ELF hash matches directory: True; frozen files/objects 584/145; working-copy inputs changed since freeze 6; receipts {"comparison.json": {"status": "PASS", "cases": 2, "elf_sha256": "4f111ccb9ed4131499a99a47af126d83f4b56f8abb54a5e6073cbc6566e93e8a", "distinct_original_trace_bytes": 35022}, "failures.json": {"status": "PASS", "cases": 3, "elf_sha256": "4f111ccb9ed4131499a99a47af126d83f4b56f8abb54a5e6073cbc6566e93e8a", "distinct_original_trace_bytes": 33682}, "powerloss.json": {"status": "PASS", "cases": 2, "elf_sha256": "4f111ccb9ed4131499a99a47af126d83f4b56f8abb54a5e6073cbc6566e93e8a", "distinct_original_trace_bytes": 34982}}.
- Image `92619ea6a927`: actual ELF hash matches directory: True; frozen files/objects 581/144; working-copy inputs changed since freeze 7; receipts {"comparison.json": {"status": "PASS", "cases": 2, "elf_sha256": "92619ea6a92780848703d61cb91385c950b717089718aa6a82a13baf6fc1cda4", "distinct_original_trace_bytes": 35022}, "failures.json": {"status": "PASS", "cases": 3, "elf_sha256": "92619ea6a92780848703d61cb91385c950b717089718aa6a82a13baf6fc1cda4", "distinct_original_trace_bytes": 33682}, "powerloss.json": {"status": "PASS", "cases": 2, "elf_sha256": "92619ea6a92780848703d61cb91385c950b717089718aa6a82a13baf6fc1cda4", "distinct_original_trace_bytes": 34982}}.

New source includes GPIO descriptor/interrupt handling and ADC initialization/reset and control/getters. Presence of the new ADC control source does not prove it is integrated or validated; the current completed checkpoint report still identifies control/getters as next work. Historical frozen receipts remain distinct from mutable working-copy work.

Ignore configuration: {"global_excludes": null, "local_exclude_exists": false, "image_rule": ".gitignore:15:build/\tg2/build/bootloader-completion/source-image-compatible/snapshots/8ec1fa00cae0c882dae79282e43736418537a942645ba185d7a6d6026f5618fb/bootloader-source-test.elf"}. Build-local outputs are ignored; none of the inspected source files are ignored. Ordinary unstaged diff omits untracked additions and staged-only work. Full source reconstruction, real peripheral behavior and byte-identical reproduction remain unproved. Per-file hashes and receipt details are in snapshot.json.

# Follow-up scan: concrete changes since the previous inventory

Scan UTC: 2026-10-07T10:17:00.007427+00:00. Read-only inspection of sources, Git views and existing receipts; no generators or firmware execution rerun for this scan.

| Measurement | Previous scan | Current scan |
| --- | ---: | ---: |
| `g2/components` C files | 208 | 212 |
| `g2/components` headers | 139 | 142 |
| `g2/components` assembly files | 19 | 19 |
| R1 C / headers | 21 / 22 | 21 / 22 |
| Untracked files, excluding ignored | 4408 | 4532 |
| Frozen checkpoint inputs / linked objects | 670 / 172 | 681 / 175 |
| Alignment mappings | 493 | 496 |
| Selected numeric aliases | 17 | 17 |

New component C files: `startup_initialize_leaves.c`, `startup_runtime.c`, `startup_memory_config.c`, and `startup_spot_timer.c` in `g2/components/bootloader/initializer_callbacks/`. The first three are integrated into the checkpoint; the timer leaf is a separately validated pending prerequisite. New headers accompany the first three. File counts are inventory measurements, not source completeness.

## Checkpoint verified by scan

The current on-disk test ELF SHA-256 is `c6a3ac92c9a69b906b8b8f7c3ec1a12d79928f5a58ae7367f731600fd157b5e1`, matching [the c6a3 receipt](../bootloader-completion-2026-10-06/integrated-status/same-image-validation-c6a3.json). That receipt records seven PASS integration cases, 31 direct/regression receipts, and zero post-run input hash mismatches. The previous scan recorded checkpoint `761b…`. Thirteen newly linked startup prerequisites account for 2016 original body bytes covered by bounded direct suites. This scan confirms files/receipts and ELF identity; it does not independently rerun those suites.

## Additional recovered source beyond the integrated checkpoint

- [SPOT startup callbacks](../bootloader-completion-2026-10-06/inventory-worker/startup-spot-handlers/README.md): four original bodies, 722 bytes, 19 passing comparisons; all body bytes visited. INFO reads remain a controlled boundary in this suite.
- [Clock-mux initialization](../bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/README.md): 922-byte original body, 112 passing comparisons against compiled C; ten explicit child cuts. Ambient register carry must be handled before a drop-in initializer integration.
- [TON trim hooks](../bootloader-completion-2026-10-06/inventory-worker/startup-ton-hooks/README.md): two bodies, 470 bytes, 124 passing comparisons. Coverage is 152/152 and 296/318 bytes; 22 conditional-arm bytes remain unvisited with the locked table. Enable/delay helpers are explicit cuts.
- Event-dispatch work areas contain additional C under development. No completion result is counted here where a completed receipt is absent.

## Ignore rules and practical boundary

`git check-ignore -v` finds no ignore match for `startup_runtime.c` or `startup_memory_config.c`. The compiled ELF matches `.gitignore:15:build/`. Build products being ignored does not hide these reconstructed source files. Much of the source/analysis work is untracked or staged and therefore absent from a committed-files-only view.

The root startup initializer `0x41c4b4` remains an unresolved selected boundary. The runtime installer stores 29 authenticated callback addresses; storing an address is not executable source closure. Four initialization callbacks are still modeled in the integrated dispatch suite even though separate callback reconstruction has progressed. Seven integration cases retain startup/logger models. Native hardware timing, task drain, full-source closure and byte equality remain unproven. The unchanged 17-alias count is not evidence that no code was produced.

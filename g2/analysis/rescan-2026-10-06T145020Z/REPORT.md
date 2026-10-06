# Refreshed source scan

Compared with October 6 14:03 UTC. Current snapshot: 2026-10-06T14:50:20.645147+00:00.

Bootloader C/header/assembly files: **20 → 35**. Foundation: **89 → 89**. Current bootloader ignored source files: **0**.

New source files: 15; changed existing source files: 1. Counts include vendored code and declaration headers, not just reconstructed functions.

## Saved validation

| Artifact | Status | Cases | Original trace bytes | Source binding mismatches |
|---|---|---:|---:|---:|
| g2/build/bootloader-completion/allocator-compatible/comparison-first.json | PASS | 265 | 1994 | 0 / 9 |
| g2/build/bootloader-completion/dfu-context-compatible/comparison-first.json | PASS | 37 | 310 | 0 / 8 |
| g2/build/bootloader-completion/dfu-task-compatible/comparison-first.json | PASS | 213 | 734 | 0 / 4 |
| g2/build/bootloader-completion/filesystem-compatible/integration-final.json | PASS | — | — | 0 / 0 |
| g2/build/bootloader-completion/filesystem-compatible/integration-first.json | PASS | — | — | 0 / 0 |
| g2/build/bootloader-completion/filesystem-owned-compatible/integration-first.json | PASS | — | — | 2 / 35 |
| g2/build/bootloader-completion/platform-control-compatible/comparison-first.json | PASS | 496 | 270 | 1 / 4 |
| g2/build/bootloader-completion/platform-control-rom-compatible/comparison-first.json | PASS | 496 | 300 | 0 / 6 |
| g2/build/bootloader-completion/startup-compatible/comparison-final.json | PASS | 39 | 182 | 0 / 4 |
| g2/build/bootloader-completion/startup-compatible/comparison-first.json | PASS | 39 | 182 | 1 / 4 |
| g2/build/bootloader-completion/startup-compatible/itcm-comparison-first.json | PASS | 16 | — | 0 / 3 |
| g2/build/bootloader-completion/task-integrated-compatible/integration-first.json | PASS | — | — | 1 / 41 |
| g2/build/bootloader-completion/update-core-compatible/comparison-final.json | PASS | 4542 | 1208 | 2 / 5 |
| g2/build/bootloader-completion/update-core-compatible/comparison-first.json | PASS | 4514 | 1208 | 3 / 5 |
| g2/build/bootloader-completion/update-core-compatible/comparison-resources-final.json | PASS | 4542 | 1208 | 0 / 7 |

Saved results were inspected and source hashes checked; builds and emulation were not rerun. Superseded results appear separately and must not be added together. Source mismatch details and validation limits are in snapshot.json. A missing source manifest does not establish current source identity.

New meaningful implementation includes startup expansion/zeroing and ITCM assembly, TLSF allocation, DFU command processing/thread context, guarded MRAM programming and the local ROM bridge. The MSPI interrupt adapter currently has build evidence only. Runtime/kernel/ROM/flash providers remain synthetic where documented; there is no complete source-built bootloader or byte-identical bundle demonstrated.

Generated ELF/results live under ignored g2/build; reconstructed component source is visible under g2/components/bootloader. No global decompilation/review coverage claim was recomputed in this narrow source scan.

Index preserved by this scan: True. No staging, firmware modification, generator execution or hardware access.

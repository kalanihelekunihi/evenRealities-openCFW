# OpenCFW refreshed scan

Baseline: October 6 13:20 UTC assessment. Refreshed snapshot: 2026-10-06T14:03:25.724767+00:00. Same authenticated 4,301,227-byte official bundle and six payloads; no firmware changes or test execution during this scan.

| Evidence | Previous | Current | Change |
|---|---:|---:|---:|
| Exported assembly footprint | 599,718 | 602,226 | +2,508 |
| Generated pseudocode footprint | 1,902,397 | 1,902,397 | 0 |
| Authenticated scoped review footprint | 204,660 | 204,660 | +0 |
| Bounded compared source trace footprint | 8,418 | 9,626 | +1,208 |

Footprints count distinct stored payload addresses, not firmware completion. The new bootloader trace is disjoint from prior Apollo-main/touch traces; it includes 18 bytes of reconstructed assembly handoff, so the combined figure includes C and that assembly helper. Review counting uses the same repaired normalizer and its 12 passing fixtures; supplemental authenticated text disassembly is included consistently in both assembly totals.

## Concrete new source

Foundation remains 89 C/header files: no additions, changes or removals. New `g2/components/bootloader/` contains 19 C/header files and one assembly file, all untracked and visible to Git; none are ignored. Four files are vendored littlefs implementation/headers, one is a host test, three are freestanding declaration headers; this file count does not imply 20 recovered firmware functions.

- `update_core/update_core.c`, `update_core.h`, `handoff.S`, `rom_resources.c`: CRC, stream modes, alignment-sensitive comparison, erase/readback/image verification/programming, vector handoff and textual resources. Saved original/source comparison PASS **4,542 cases**, **1,208 distinct original instruction bytes**. All seven saved source hash bindings, ELF and original bytes match this checkout. Providers are synthetic; logger observation is partial. Cortex-M4 compatible build is the passing execution profile; default M55 generated loop instructions remain unsupported by the present emulator fixture. Not an exact IAR rebuild.
- `filesystem/`: pinned BSD-licensed littlefs 2.10.1, recovered NOR configuration/callbacks, file services and C runtime helpers. Saved ARM source integration PASS **16 calls**, format/mount/write/remount/verify/program/readback of a 9,001-byte payload. ELF hash matches. Real littlefs/file/update source executes, while heap, mutex, NOR and flash providers are synthetic. No full original filesystem differential comparison; this result has no complete source hash manifest, so ELF identity alone does not establish all current source bindings.
- `startup/initialize.c`, `initialize.h`: compressed-record expansion and zero-table reconstruction. Present source has **no saved passing validation result** in this snapshot; not credited as compared trace coverage.

## Visibility and remaining limits

`.gitignore:15:build/` hides generated ELF/results under `g2/build/`; it does not hide the new source. No complete blob-free payload or byte-identical source-built bundle is established: **0/6 payloads, 0/1 bundle**. Bootloader scheduler/platform providers, full reset/boot integration and matching original build remain open. The new source is meaningful partial implementation, not source-complete firmware.

HEAD remains 4ab13514dfcfd96f835784118cf580c48715c2d3. Existing index preserved during scan: True. Builds/emulation/hardware operations were not rerun. Saved validation is reported separately from freshly recomputed inventories. See `comparison.json`, `checkout-refresh.json`, fresh counting ledgers and `repaired/summary.json` for supporting evidence.

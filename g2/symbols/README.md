# G2 symbol seeds (s200_v2.2.6.10)

> **Citations.** Repository paths cited as `path` or `path:line` refer to the tree at commit `832137ec`. The 2026-09-29 cleanup retires many of those evidence files; after they are removed, `git show 832137ec:<path>` still shows them.


Address-sorted naming seeds for the six G2 payloads, consolidated from the
legacy G2 function maps, census tables, research reports and analysis
corpora before those were removed.

**These are naming seeds only.** They are not reviewed pseudocode, not a
statement that any function is understood or source-complete, and not
evidence toward byte equality. Names marked below `Proven` are hypotheses to
be confirmed or replaced during pseudocode review.

Regenerate (deterministic; no timestamps, sorted inputs and outputs):

```sh
python3 tools/consolidate_symbol_seeds.py --repo <repo root> --out symbols
```

The generator reads the legacy inputs from `g2/tools/manifests/`,
`g2/docs/research/` and `g2/research/corpus/`; it must be run against a
checkout (or git revision) that still contains them.

## Files

| File | Payload | Address space |
|---|---|---|
| `apollo_main.tsv` | Apollo510 main application | run addresses `[0x00438000,0x00794324)` (`run = file_offset + 0x00437FE0` for the OTA payload) |
| `bootloader.tsv` | Even Apollo bootloader | `[0x00410000,0x00434477)` |
| `ble_em9305.tsv` | EM9305 controller (ARCv2 EM) | `[0x00300000,0x00335BC8)`; application record at `0x00302400` |
| `codec.tsv` | GX8002 codec package | runtime addresses per image region (see below) |
| `touch.tsv` | PSoC 4000T touch application | linked flash addresses = payload offset + `0x3300` |
| `case.tsv` | STM32G0 charging-case application | `[0x08000000,0x0800D9C8)` |
| `conflicts.tsv` | all | addresses where sources disagree on the name |

Rows whose address falls outside the stock payload (for example appended
overlay code recorded in the legacy memory map) are dropped; 56 such rows were
rejected in the current generation.

## Columns

| Column | Meaning |
|---|---|
| `address` | Entry / start address, `0x%08X`. Deduplication key (codec: region + address). |
| `end` | Exclusive end if any source records one (best-ranked source first). |
| `size` | `end - address`, or the source's byte count. For touch rows it is the instruction byte count reported by the touch analyzers. |
| `name` | Best-ranked name. Empty when only a boundary is known. `FUN_xxxxxxxx`-style names are Ghidra placeholders. The legacy project prefix `open_cfw_` was stripped from descriptive names; upstream and retained names are unchanged. |
| `module` | Library, object or module: retained source path (backslashes turned into `/`), upstream archive/object, or the legacy manifest stem. Codec rows are prefixed with their image region (`uart_boot_stage1`, `uart_boot_stage2`, `image_a_stage1`, `image_a_xip`, `image_a_sram`, `image_b_stage1`, `image_b_sram`). |
| `confidence` | `Proven`, `Strong`, `Inferred`, `Unverified` (below). |
| `evidence` | `<source file>: [original confidence wording] original note`, then `also:` with the other sources that described the same address. |
| `stock_sha256` | SHA-256 recorded by the best source for the same extent: stock body bytes for most rows, Ghidra body bytes for corpus-only rows, instruction bytes for touch rows. Empty when no source records one. |

`conflicts.tsv` columns: `payload`, `address`, `name`, `confidence`,
`chosen` (`yes` for the name kept), `rival_rank` (`equal-or-higher` when a
rejected name has at least the chosen name's confidence, otherwise `lower`),
`source`.

## Confidence vocabulary

The legacy tables used dozens of phrasings; they are mapped as follows.

| Level | Assigned when the source says |
|---|---|
| `Proven` | the name string is retained in the image (exact retained diagnostic / function / assertion / symbol string), or the body matches an upstream object exactly after relocation normalization (EM9305 SDK archive comparisons, exact upstream definitions), or an exact official body hash corroborates a pinned upstream definition. |
| `Strong` | upstream-source correlation (linked Cordio/Ambiq/FreeRTOS definitions by source order and behavior), prior-firmware exact ordered symbol, exact semantic/name oracle, vector-table resolution, EM9305 link-order placement between exact anchors, relocation-free NationalChip SDK section match, `high` confidence, or entries from the legacy memory map's named rows. |
| `Inferred` | semantic, descriptive, lifecycle or proposed names derived from behavior, ABI or document titles; EM9305 vendor-modified partial matches; `medium` confidence. |
| `Unverified` | Ghidra address labels and placeholders, unresolved prefix entries, `low`/`none` confidence, codec stage1 rows whose runtime mapping is unresolved. |

For rows without a name the level describes the module/boundary attribution
rather than a name.

Deduplication: per address, the kept row maximizes (has a real name,
confidence, has an end address, source path). A missing end/hash/module is
filled from the next best source for the same address.

## Per-payload counts (current generation)

| Payload | Rows | Named | Proven | Strong | Inferred | Unverified | Unnamed / placeholder | Conflict addresses |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| apollo_main | 8,844 | 3,323 | 679 | 1,334 | 1,256 | 54 | 5,521 | 0 |
| bootloader | 292 | 292 | 0 | 62 | 230 | 0 | 0 | 106 |
| ble_em9305 | 1,835 | 1,695 | 1,444 | 206 | 12 | 33 | 140 | 48 |
| codec | 778 | 778 | 0 | 98 | 676 | 4 | 0 | 59 |
| touch | 298 | 236 | 0 | 76 | 160 | 0 | 62 | 7 |
| case | 435 | 315 | 0 | 34 | 281 | 0 | 120 | 0 |

Inputs: 1,035 source files, 48,966 raw rows.

Notes on the counts:

- Apollo main unnamed rows are mostly the authenticated Ghidra corpus
  boundaries (`g2/research/corpus/apollo-main/ghidra/decomp/functions.jsonl`,
  7,449 functions) and the unanchored/LVGL/Cordio-LL/FreeType census rows;
  they give boundaries and module attribution only.
- EM9305 conflicts are mostly identical-body aliases that match several SDK
  functions (for example `IRQHandler_SWI*`, `IRQHandler_ProtocolTimerOutCmp*`);
  the chosen alias is arbitrary among equals.
- Bootloader and codec conflicts are mostly a descriptive label versus an
  upstream or more specific name for the same entry.

## Sources

| Group | Inputs | Payloads |
|---|---|---|
| Function maps | `g2/tools/manifests/*-function-map.tsv` (303 files; column sets vary, dead-stripped/source-only rows without a stock address are skipped) | apollo_main, bootloader, case, touch |
| Apollo censuses | `g2-apollo-unanchored-census-functions.tsv`, `g2-lvgl-vendor-fork-census.tsv`, `g2-cordio-ll-sea-census.tsv`, `g2-freetype-engine-census.tsv`, `g2-freetype-*-function-map.json` | apollo_main |
| Retained source paths | the `source_path_anchor` / `retained_path` columns of the function maps (the embedded `__FILE__` path correlation of `apollo-embedded-source-path-*.md`; re-running that analyzer needs the official image) | apollo_main |
| Product test | `g2/research/corpus/apollo-main/ghidra/pt-protocol/{command-map.tsv,functions.jsonl}` (names `pt_cmd_XX_handler` are descriptive) | apollo_main |
| Ghidra boundaries | `g2/research/corpus/apollo-main/ghidra/decomp/functions.jsonl` (omit with `--no-ghidra-boundaries`) | apollo_main |
| Memory map | named rows of `g2/docs/memory-map.md` | apollo_main, bootloader |
| Bootloader | `g2-bootloader-*.tsv` (function/provider/caller rows), single-address `g2-bootloader-*-source-closure.md` titles (`bl_*` labels) | bootloader |
| EM9305 | SDK archive comparison reports under `g2/research/corpus/em9305/sdk-comparison/` (unique or expected-address matches), link-order / NOP-aware / vector placements and vendor-modified comparisons under `nop-aware/` and `size-delta/`, `em9305-controller-cluster-map.tsv`, `em9305-residual-provenance-map.tsv`, `em9305-*-boundary.tsv`, `em9305-qpc-hook-provider-closure.tsv`, `em9305-ghidra-*.tsv` | ble_em9305 |
| Codec | `g2/docs/research/gx8002-*.json` stock occurrences and `gx8002-upstream-object-candidates.json` (NationalChip `lvp_kws` `8bf9ee5c`) | codec |
| Touch | `g2-touch-prefix-function-map.tsv`, `g2-touch-relocated-*.tsv`, `g2-touch-*-admission*.tsv`, capsense/readiness/contract tables, `g2-touch-i2c-command-map.tsv` | touch |
| Case | `g2-box-function-map.tsv`, `g2-box-ghidra-functions.tsv`, `g2-box-task-*.tsv`, `g2-case-*-admission.tsv`, `g2-case-final-function-frontier.tsv` | case |

## Address-space details

- **Codec.** Package offsets are mapped by window: UART boot stage 1
  `0x50` -> `0x10000000`; stage 2 `0x2850` -> `0x10002800`; image A XIP text
  (main offset `0x3004`..`0xBE88`) -> `0x10200000 + flash offset` (public SDK
  XIP base, consistent with the recovered `0x102067DC` board-pin routine);
  image A SRAM (`0xBE88`..`0xF804`) -> `0x10023400`; image B SRAM
  (`0x323B4`..`0x46440`) -> `0x10003000`. Image A/B stage 1 blocks have no
  established runtime mapping and are placed at `0x10000000 + offset - 0x18`
  with confidence `Unverified`. Because images overlap in IRAM, codec rows are
  keyed by region and address.
- **Touch.** The payload is linked at flash `0x3300` (two independent
  correspondences: strings `0xAA5C`/`0x775C`, command table `0xB0C4`/`0x7DC4`).
  The evidence column keeps the original payload offset.
- **EM9305.** Addresses are controller addresses from the record table; EM9305
  SDK matches were accepted only when an archive function matched exactly one
  stock address or its expected address.

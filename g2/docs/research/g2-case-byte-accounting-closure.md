# G2 charging-case typed_external_or_unsupported byte accounting

Component: charging case / box (EVENOTA entry 4, `type 6`), range
`0x08000000..0x0800D9C8` (55,752 application bytes).
Image: `blobs/official/g2-2.2.6.10/firmware_box.bin`, SHA-256
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.

- Analyzer: `tools/analyze_g2_case_byte_accounting.py` (read-only, deterministic)
- Manifest: `tools/manifests/g2-case-byte-accounting.tsv` (1,135 rows)
- Machine summary: `tools/manifests/g2-case-byte-accounting-summary.json`
- Log-string manifest: `tools/manifests/g2-case-log-string-candidates.tsv`
- Residual shape manifest: `tools/manifests/g2-case-residual-shape.tsv`
- Residual recovery queue: `tools/manifests/g2-case-residual-recovery-queue.tsv`
- Residual recovery rows: `tools/manifests/g2-case-residual-recovery-rows.tsv`
- Residual non-target rows: `tools/manifests/g2-case-residual-non-target-rows.tsv`
- Residual entry candidates: `tools/manifests/g2-case-residual-entry-candidates.tsv`
- Fail-closed test: `tests/test_analyze_g2_case_byte_accounting.py` (10 tests)

## Why this exists

`g2-case-final-classification.md` proves the whole-blob split (32 B generated
wrapper + 14,886 B `project_source_candidate` + 40,866 B
`typed_external_or_unsupported`, zero unclassified) but treats the 40,866-byte
bucket as one opaque lump for whole-blob accounting purposes.
`g2-box-stm32g0-platform-recovery.md` separately names 1,202 bytes of it as
evidence-anchored upstream/first-party islands (CMSIS startup, FreeRTOS GCC
ARM_CM0 port fragments, STM32 HAL fragments, first-party G2 fragments) and
leaves a 54,550-byte "unresolved" aggregate that predates the final-frontier
function map, so it double-counts bytes the frontier later closed. Neither
record reconciles against the other, and neither says how much of the 40,866
bytes is genuine fill, how much is the compressed-log string corpus, and how
much is still undifferentiated code-or-data.

This closure reconciles both records against the pinned stock oracle into one
non-overlapping accounting of every byte in the range, in priority order:

1. `admitted_function_source_candidate` (14,886 B, excluded from the 40,866
   total) — the 222 final-frontier functions, cross-checked unchanged.
2. `platform_<ownership_category>` (1,104 B of the 40,866) — the
   evidence-anchored islands, wherever they don't overlap an admitted
   function (98 bytes of the platform doc's 1,202 fall inside functions the
   later Ghidra pass discovered independently, e.g. a semantic-leaf function
   at `0x08004B94` sits inside the platform doc's HAL-flash-credential
   island `0x08004B8C..0x08004C1C`; the function's clean-room source is the
   stronger claim there, so it wins the byte).
3. `function_map_<ownership_category>` (25,314 B of the 40,866) — the
   authenticated Ghidra function map's non-`unresolved` function rows, wherever
   they do not overlap an admitted source-candidate function or platform island.
   These bytes are named as upstream CMSIS/startup, FreeRTOS/CMSIS-RTOS2,
   STM32-HAL, or first-party G2 policy, but they are still not source-owned
   until routed to reviewed providers.
4. `function_map_gap_<ownership_category>` (12,328 B of the 40,866) — the
   authenticated function-map gap rows that carry positive non-`unresolved`
   evidence, primarily first-party log/status rodata plus the vector/pre-code
   gap. These bytes are evidence-attributed, not source-owned.
5. `gap_frontier_<classification>` (2,120 B of the 40,866) — the 229
   final-frontier inter-function gap spans, wherever they don't overlap a
   platform island (64 bytes of the 2,184 do; same tie-break).
6. No bytes remain in the content-only residual buckets:
   `residual_zero_fill`, `residual_ff_fill`,
   `residual_log_string_candidate`, and
   `residual_unresolved_code_or_data` are all 0 B.

Total: 14,886 + 1,104 + 25,314 + 12,328 + 2,120 = 55,752, conserving the
application image exactly; the typed_external_or_unsupported sub-total
(1,104 + 25,314 + 12,328 + 2,120 = 40,866) matches the pinned whole-blob
bucket. All figures are enforced as test assertions, not just observed once.

## Data tables, strings, identity windows, fill (this item's scope)

- **Strings.** The former residual string corpus is now attributed by the
  function-map gap layer as first-party log/status rodata. Those strings are
  real, human-legible debug/log strings —
  `Set SN:`, `1.2.57`, `%s reset GLS`, `B200 %s, %d`,
  `Standby, reason: cmd.`, `%s watchdog 4005`, `One-side charging: %s`,
  `Set PMIC chip id to 0x08`, the `{"vol":%d,...}` JSON status template, and
  the full `[OTA_BOX]`/`[AGING_*]` corpus already summarized by
  `_string_census` in the platform analyzer. They are genuinely understood
  (this and the platform doc identify their meaning), but **not yet
  source-authored**: the case component has no logging/formatting module in
  `components/shared/case/` or `components/case/source_image/` that would
  consume them, so emitting them as C string literals now would be inert
  data with no caller — a "candidate not production-routed" the hard rules
  explicitly do not count as completion. Reconstructing them into source
  requires first reconstructing (or explicitly stubbing) the logging
  call sites that reference them, which requires the log-ID scheme
  `g2-box-stm32g0-platform-recovery.md` flags as unresolved (most strings
  have no pointer literal; only a 34-pointer `0x0800Dxxx` page is directly
  referenced — consistent with an indexed `compress_log` strip whose ID
  encoding is unknown). `tools/analyze_g2_case_byte_accounting.py` now emits
  an empty residual string TSV with digest
  `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`;
  the strings are attributed, not source-owned.
  Flagged as follow-up, not attempted here.
- **Data tables.** No CRC/lookup table was found in the range (the platform
  doc already proved CRC-16/CRC-32 tables are absent — the CRC is bit-wise).
  The application task/timer descriptor table (`0x0800D2C0..0x0800D3A0`,
  224 B) and name-string block (`0x0800D8B8..0x0800D958`, 160 B) are the only
  structured tables identified; both are already in the `platform_first_
  party_g2` bucket above (evidence-anchored, not yet source-authored for the
  same production-routing reason as the strings).
- **Identity windows.** Confirmed **absent from this range.** The case
  updater's preserved per-device SN windows
  (`0x0803F000..0x0803F00F`/`0x0803F800..0x0803F807` and the bank-2 mirrors)
  are proven by `g2-box-stm32g0-platform-recovery.md` to sit far beyond this
  55,752-byte application image (`image_contains_preserved_windows: false`).
  `analyze_g2_case_byte_accounting.py`'s `identity_windows_in_range.count`
  is `0` and is pinned by test. There is nothing to reconstruct or
  divergence-document for identity windows inside `0x08000000..0x0800D9C8`;
  a future item touching the far-bank windows themselves is out of this
  range entirely.
- **Fill.** Only 428 bytes are unambiguous zero/0xFF fill runs *outside*
  everything already claimed by a function, platform island, or typed gap
  (most of the image's actual padding falls inside those, e.g. the 31
  `typed_zero_alignment_or_data` gap-frontier rows). This is a small,
  well-understood, low-value slice; not worth a dedicated source
  representation on its own.

## Source-image size/layout: intentional divergence, documented

The clean-room source image (`components/case/source_image/build_image.py`)
currently links 18,916 raw bytes against a fresh Cortex-M0+ linker layout; it
does not and will not reproduce the stock 55,752-byte layout address-for-
address. This is an **intentional divergence**, not an oversight:

1. The 222 admitted functions are independently authored clean-room C
   compiled with clang/lld, not the original toolchain (IAR/GCC-derived, per
   `g2-box-stm32g0-platform-recovery.md`'s newlib-style startup finding).
   Different compilers and code generators do not produce byte-identical
   output for equivalent source, and pursuing byte-identity would pressure
   toward copying disassembly rather than writing independent source — the
   opposite of this project's clean-room requirement.
2. `residual_unresolved_code_or_data` is now empty. The residual-shape
   analyzer still runs and emits authenticated header-only manifests with
   empty-list digest
   `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
   The recovery/non-target partition is also empty and pinned by digest
   `8b8a0fb3dfaf65d7b832fa22e87151d7d6dbc06266643848b58dc61cded876df`.
   There is still no
   reviewed source to place at a matching offset for the majority of the image;
   an exact-layout linker script today could only be populated by copying stock
   bytes, which `source-only-goal.md` explicitly excludes ("binary bytes
   encoded as C arrays... do not satisfy this goal").
3. The completion conditions require functionality to be produced from
   reviewed source, not exact size/layout; layout matching is useful for
   differential testing against the stock oracle, not a hard gate this
   project's own goal document imposes.

Closing this divergence for real (rather than continuing to document it)
needs, in order: (a) the log-ID/`compress_log` scheme resolved so the string
corpus can be wired to real call sites, (b) a full Ghidra function map of the
`residual_unresolved_code_or_data` bytes (the platform doc's own "highest-
value next action"), and (c) production routing of the 222 already-admitted
functions (tracked separately as CS-001, in progress concurrently with this
item).

## What this closure does not do

Naming a byte range here is a precondition for routing reviewed source at
those addresses, not source ownership itself. No bytes moved from
`typed_external_or_unsupported` into `project_source_candidate`; the pinned
whole-blob split is unchanged and re-verified, not altered.
`production_routed` remains `false`. No hardware operation was used or is
implied; battery/charging/thermal/option-byte behavior stays hardware-gated
throughout, consistent with `hardware-validation-policy.md`.

## Verification

```
cd g2 && PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \
  -m unittest -v tests.test_analyze_g2_case_byte_accounting
# 10 tests, OK

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \
  tools/analyze_g2_case_byte_accounting.py --write-manifests

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \
  tools/analyze_g2_case_residual_shape.py --write-manifests
```

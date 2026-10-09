# Eight residual source/build discriminators

Bounded official-source discovery; no compilation, source editing, linker edits, byte fitting or canonical ledger changes.

## Positive flash history discriminator

Official Infineon/mtb-pdl-cat2 full history already acquired as isolated bare clone. Enumerated every change to cy_flash.c/cy_sysclk.c/cy_syspm.c and fetched27 changed-file snapshots, hashes in provenance.json. These are source change points rather than every release tag; inherited unchanged files are represented by their last change.

Flash PDL2.16 commit `16aaf1d3d764ca3c426234c90cdeb6f19cb2d091` has explicit __NOP immediately before ProcessStatusCode in ClockBackup:755+, ClockConfig:786+, ClockRestore:815+. PDL2.17 commit `6951433aa12bedcd1226fc97086182448f6a767e` removes those NOPs and ProcessStatusCode starts with WaitForSysCallFinish rather than directly reading CPUSS_SYSARG. Exact diffs are saved here. This authentic source-history change directly explains the reported structural NOP/status distinction and supplies a bounded older-source candidate. It does NOT prove target byte equality. WriteRow has three normalized source variants across history; ProcessStatusCode two; ClockBackup two; ClockConfig/Restore three. function-variants.json contains exact bodies/line numbers/pins. The 2.16 header set is acquired too, so owner must avoid mixing incompatible current/old flash interfaces blindly.

## Authentic variable-section contract

Official https://github.com/Infineon/recipe-make-cat2.git acquired at `f9cf7bcbc28688cc012ad9bb9392b5516256d262`. make/toolchains/GCC_ARM.mk:107–116 defines common flags including -mthumb, -ffunction-sections, -fdata-sections, -ffat-lto-objects, -g, -Wall, -pipe. Release selects -Os:99; CM0P selects -mcpu=cortex-m0plus and nano.specs:132+. Historical first release `1a75035214b5dcda4c39dcbd9133e750f250ba2e` (2020) and2.2 `22e2ac01e93c4080a74fd81fc21c4c0a3302af36` (2024) independently retain both section flags. Exact historical recipe files and hashes in header-recipe-provenance.json. This is public manufacturer build-contract support for testing -fdata-sections with fixed GNU14.2.1. It does not identify stock flags, variable addresses or source/link order. No full flag bundle adoption or compiler sweep is implied.

Official core-make `aefe7ff6ff59de2cb357362638231f701f7a220c` documents requiring device-specific recipes (README:9); it delegates recipe toolchain setup. Neither make repository was executed. Both Apache-2.0 licenses retained; file inventory/hash provenance in build-acquisition-provenance.json.

Current cy_sysclk.c:586–587 declares two separate bool objects, iloMeasurment and preventIloMeasurment, with no explicit section attribute. Both have static false initializers. Recipe section flag can discriminate aggregate .bss-offset addressing from individual variable sections; exact target addresses still need authenticated linker/layout evidence. ILO start/stop each have three normalized source variants, compensation four. These include conditional source text and are NOT preprocessed device-specific variants; owner should use unchanged source and actual device headers when evaluating.

## PM source-history boundary

Six cy_syspm.c change-point snapshots spanning1.0 through2.20 yield ONE normalized ExecuteCallback body (comment/whitespace removed), SHA256 `66f5982e935562c3364489ae1bdb093fd2862cbd44a675a5a190c3bceb696278`. Latest2.21 inherits this file. Thus no body revision in the checked official history explains the69 mismatches. Global pmCallbackRoot and failedCallback are static three-element pointer arrays (2.20 source43,46), without explicit section attributes. Per-variable sections could affect their addresses/loads, but cannot alone be asserted to explain all control-flow lowering.

cy_stc_syspm_callback_params_t and cy_stc_syspm_callback_t declarations normalize identically between2.16 and2.21 headers; hashes/text in discriminators.json. This is only a two-version header comparison, not full header-history exhaustion. Target compiler flags/preprocessing and relocation/link contract remain open; matching registration/wrappers do not resolve ExecuteCallback.

## Defensible limits

Exhausted distinct tracked function bodies in this official PDL repository history for these three source files, subject to source-extraction heuristic review. Did not search private SDKs, deleted/unreachable upstream commits, other official repository families or target-producing proprietary changes. No stock build recipe/map is authenticated. No exact matches newly claimed. Useful next owner experiments are fixed-compiler historical flash source comparison and independently supported per-variable section comparison, keeping raw mismatch receipts and relocation handling intact.

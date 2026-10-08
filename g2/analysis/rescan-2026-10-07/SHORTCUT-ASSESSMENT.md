# Source and analysis shortcuts — October 7

Recommendation: finish the bootloader plain-printf source comparison first, then use IAR objects to identify the separate bounded-formatting backend. For whole firmware, prioritize EM debug/type transfer and codec model extents over more generic decompilation. These are hypotheses with rejection tests, not newly recovered firmware coverage.

## 1. Ambiq generic printf: available source, small testable closure

**Target:** stock plain logger entry `0x415fae`, parser `0x415bf6` (952 bytes), float conversion `0x415ab6` (320 bytes), and helpers at `415900/415924/415936/41595c/4159a0/415a08/415a7c/415a94`. Prior disassembly identifies 11 bodies / 1,754 bytes. Do not confuse this with IAR `_Printf` below.

**Asset:** `third-party/local-vendor/sources/AmbiqSuite_R3.2.0/utils/am_util_stdio.c`, including `am_util_stdio_printf`, `am_util_stdio_vsprintf`, `divu64_10`, integer/hex conversion and float formatting. Its printf checks the sink, formats a global buffer, calls the sink and returns the count: a strong structural lead for the stock callback at `0x200270cc` and buffer `0x20024cd0`. Available BSD-3-Clause C is more useful here than another raw archive scan. The downloaded SDK is Apollo3/3P, release `release_sdk_3_2_0-dd5f40c14b`; it is not the Apollo510 HAL. Generic utility correspondence is plausible, producing-source identity/configuration remains unproven.

**Cheap rejection:** compile only these utility functions under the recovered calling convention with controlled sink; compare original instructions on `%d/%u/%x`, 64-bit values, width/padding, star precision, `%f`, negatives, special floats, newline conversion and missing sink. Compare return counts and callback bytes/order. A failed edge case means adapt/reconstruct that behavior, not declare a library match. Budget estimate: 1–2 hours for the initial matrix; potentially saves several hours to a day of parser reconstruction if it passes. Neither estimate is measured progress.

**New versus prior:** available local source and structural correspondence are a fresh shortcut lead. No exact stock byte match or source implementation credit is claimed by this assessment.

## 2. IAR runtime: large opaque formatter, binary/type references now available

**Target:** stock bounded formatting entry `snprintf` at `0x41b218` (62 bytes), `vsnprintf` near `0x41b25c`, and backend `0x41e47a` (3,256 bytes, 20 identified callees). The latter is among the largest bootloader bodies still relevant to this closure. Already recovered MSPI bodies can be larger; size alone does not make them current opaque targets.

**Asset:** installed IAR Arm 10.10.2.27058 Base tree, 675 `.a` archives. A data-only `arm-none-eabi-ar` probe of `arm/lib/dl7M_tlng.a` extracted `snprintf.o`, `xprintfdefault.o`, `xprintffull.o`, `xprintflarge.o`, `xprintfsmall.o`, `xprintftiny.o` and `vsnprintf_s.o`. Full evidence hashes/sections/symbols are in `sdk-probe-evidence.json`. Installed `snprintf` is 68 bytes; `_PrintfFull` is 2,988 bytes (`0xbac`), so these are already negative exact-size checks against the stock candidates. IAR `.rtmodel`, stack-usage and debug-frame metadata can still identify ABI/helper roles; do not assume full C types from those sections.

**Confidence/limits:** stock compiler candidate is EWARM 9.60.2, not installed 10.10.2. Relocation-normalized fingerprints survive relocation changes, not arbitrary compiler/code-generation changes. These archives supply compiled implementations, not C source for the full formatter. The supplied runtime source license limits its use to IAR products; do not import it into independent Clang code. Licensed compilation is blocked by authentication; reading reference object metadata does not require activating the compiler.

**Cheap rejection:** select 20–50 formatter/memory/float helper bodies, compare normalized relocations, instruction/control-flow shape and argument roles against stock; reject mismatches explicitly. Use recognized names to recover call contracts, then reconstruct unsupported code. Budget estimate: under two hours for a first bounded match report; may save days on runtime-helper identification, but will not itself close source or byte equality.

## 3. Apollo510 startup HAL: use the correct source family

**Target:** startup children `0x41c4b4` (810 bytes), `0x41c86c` (282), `0x41ca2c` (48), `0x4222a0` (50), `0x422416` (26), plus remaining conditional children. These are lower dependencies of the newly recovered orchestrators, not yet native source closure.

**Asset:** public Apollo510 HAL 5.1.0 replay pin `5efc0228528a8adce5eae0d226fac85d2551eb3b`, BSD-3-Clause, consolidated in `g2/docs/reference/libraries.md`. Its private prerelease producing checkout remains unavailable; the gitlink is not a guarantee that the complete local source tree is initialized. Reuse already fetched owned leaves and narrowly retrieve missing pinned files if needed. Do not substitute downloaded Ambiq 3.2.0 HAL.

**Cheap rejection:** match one descriptor/layout and one error branch per child, compile a bounded leaf, compare ordered MMIO/call arguments using existing fixtures. Budget: a few hours for this family, likely faster than independent HAL reconstruction. Existing recovered MSPI/GPIO bodies are not counted again.

## 4. EM9305 controller: debug-backed interfaces, version mismatch to resolve

**Scale:** historical v4.2 archive matching attributed 1,494 functions / 157,122 of 210,888 application bytes (74.50%); provenance-inclusive accounting was 167,684 bytes (79.51%). These are prior compiled-binary attribution numbers, not public-source or new v4.6 matches. Focus remaining modified/vendor glue and HCI/PAL contracts rather than redecompiling all matched functions.

**New local assets:** safely extracted SDK v4.6 has 109 archives, 238 C files and 1,235 headers. `libs/third_party/emb/lib_emb_controller_iso.a` has 342 archive members. Six ARC `EM_ARC_COMPACT2` ELFs contain `.debug_info`, `.debug_abbrev`, `.debug_line` and related sections:

| ELF family / revision | Bytes | Symbols |
|---|---:|---:|
| `emcore_standard_fpga_di03` | 982,480 | 2,316 |
| `emcore_standard_fpga_di04` | 758,432 | 1,816 |
| `emcore_standard_fpga_di05` | 733,340 | 1,793 |
| `nvm_bootloader_base_di03` | 35,764 | 262 |
| `nvm_bootloader_base_di04` | 43,144 | 466 |
| `nvm_bootloader_base_di05` | 43,664 | 480 |

Full paths and SHA-256 values are in `sdk-probe-evidence.json`. Symbol counts include data/local symbols, not recovered functions. Debug ELFs target SDK/FPGA configurations and are not the locked product image.

**Cheap rejection:** compare ten already attributed v4.2 PAL/QPC functions and associated structure offsets against v4.6, then import only validated type layouts/names. Separate unchanged code, changed code and new layouts. Budget estimate: 1–3 hours; potentially converts days of structure inference into hours. EM agreement acceptance is recorded, but confidentiality/use/redistribution restrictions remain; no blanket right to distribute extracted SDK content follows. MetaWare compilation is not available locally. Debug inspection is useful without installing it.

## 5. GX8002 codec: model interfaces prevent misdirected decompilation

**Asset:** initialized NationalChip LVP KWS pin `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, `include/vui/ctc_model.h` getters `LvpModelGetOpsSize/DataSize/TmpSize/CmdSize/WeightSize`, task initializer and model dimensions; GXDNN GRUS `gx_snpu.h` supplies task/layout candidates. Use the GRUS variant, not the differently configured LEO structure. Component licenses vary; headers marked all-rights-reserved are not permissive source imports.

**Scale:** codec image A has 36,484 XIP bytes, 12,516 SRAM-code bytes and 2,196 data bytes; model commands are 9,164 bytes at `[0xf804,0x11bd0)`, weights 120,800 at `[0x11bd0,0x2f3b0)`. The combined 129,964 bytes must not be treated as ordinary MCU functions. Commands are NPU executable content, weights model data: neither automatically satisfies the blob-free goal. Historical SDK matches cover 102 of 151 eligible sections, 68 symbols / 5,374 bytes; no new attribution here.

**Cheap rejection:** follow stock task initialization/getter literals, compare five size/pointer fields and staged destinations `0x20003304/0x200056d0`; test wrong extents as negative cases. C-SKY GCC 6.3.0 / ABIv2 toolchain 3.10.15 already executes an isolated CK804 probe, but is not a GX8002 device SDK or established stock compiler configuration. Budget: 1–2 hours for task/extents proof; major savings come from excluding model weights from MCU decompilation, not recovering a missing trained-model source pipeline.

## 6. Display, LC3 and resource family reuse

LVGL core comparison pin `344c7c318047b7348e1be8572a9fd4260c251cfa` is a hybrid 9.3-development baseline; exact Ambiq draw-backend subtree `1e774257495fa43177e04fc5c8a42a77c2d7d619` is already vendored under MIT with recovered ABI. Google liblc3 v1.1.3 pin `96a3af0beb5487aca3b98a4b992a539a1f6d80d1` supplies Apache-2.0 source for the encoder family. These are established prior leads, not newly discovered source coverage. Prefer one held-out renderer/encoder contract test over manually decompiling every library entry.

NemaGFX 1.4.12 / NemaVG 1.1.8 headers explain GPU interfaces; available public GCC archives differ from stock IAR objects and do not supply complete C. Renderer/cache/buffer ownership remains product-specific. Six previously validated L8 resources round-trip over 28,872 unique bytes, with zero newly classified bytes in that earlier export batch. Test a new constructor/consumer and format before extrapolating to 422 unresolved candidates. Missing external NOR content requires the corresponding authorized image. Estimate: hours for a held-out contract/resource test; savings depend on whether it generalizes.

## Bootloader-first execution order and stopping rules

Run the Ambiq printf behavioral matrix; use IAR archive fingerprints for its separate bounded formatter dependencies; then close the specific Apollo510 startup children. Move to EM ABI/type transfer and GX task extents for whole-firmware knowledge. Do not add mixed byte counts into a completion percentage, transfer unvalidated v4.6 types to stock v4.2, infer asset formats from one example, or equate library identification with C reconstruction.

The source candidate `be4ede3b…` now has seven existing passing profiles and a fresh 635-input/161-object hash reconciliation with zero mismatches. Candidate-specific alignment/manifest/setter reconciliation is still required before promotion. No compiler activation, new dependency setup, device access or patch implementation is part of this assessment.

## Follow-through after assessment

The bounded Ambiq integer formatter probe now passes14/14 original-instruction comparisons plus changed-argument/count negative controls; see `../bootloader-completion-2026-10-06/upstream-worker/ambiq-printf-probe/REPORT.md`. Floats/64-bit/sink/translation remain untested. The be4ede candidate passed192 setter tests,454 alignment checks and manifest reconciliation (34 aliases,42 segments,zero source mismatches), and is now the verified offline checkpoint. Previous checkpoint/snapshot preserved. These later results supersede the earlier promotion-pending note above without changing its hypothesis limits.

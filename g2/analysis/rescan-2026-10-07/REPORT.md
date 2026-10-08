# OpenCFW rescan — 2026-10-07

Read-only inspection of existing firmware work and local SDKs, with this report and inventory as the only new artifacts. No generators, compilers, emulators, activation, firmware writes, commits or shared campaign changes. Counts are current observations, not a historical file-by-file delta.

## Changes supported by artifacts

The bootloader now contains concrete reconstructed source in `g2/components/bootloader/initializer_callbacks/elog_output.c`, `elog_uart_tx.c` and `startup_alternatives.c`. Existing focused receipts under `g2/analysis/bootloader-completion-2026-10-06/integrated-status/elog-output/` report PASS for 494 output cases, 222 UART TX cases and 64 startup cases on candidate SHA-256 `be4ede3b0288899ff661ddca1c949b4e5b24db393d4277c6acc7f75da0d04608`.

That immutable candidate's `comparison.json`, `failures.json` and `powerloss.json` now all exist and report PASS for 2 normal, 3 malformed and 2 interruption/reboot cases. This scan reads those receipts; it does not independently rerun or audit all frozen inputs. The integration REPORT still names the older `9affaa59…` checkpoint: there is a documentation/promotion lag, not evidence that these new files do not exist.

Tests remain bounded: direct output tests inject IAR formatting, metadata and sink behavior; startup tests inject HAL children and model the original descriptor copy; UART fixtures synthesize FIFO readiness/delay. Seven integration cases retain logger/startup provider models. Passing them does not prove physical UART drain, real scheduling, standalone source completeness or byte equality.

## Current SDK inventory

| Local distribution | Files | C | Headers | Archives | ELF |
|---|---:|---:|---:|---:|---:|
| AmbiqSuite 3.2.0 | 7,903 | 1,011 | 794 | 26 | 0 |
| EM9305 v4.6 SDK subtree | 7,437 | 238 | 1,235 | 109 | 6 |
| IAR Arm 10.10.2 | 2,405 | 29 | 939 | 675 | 0 |

Exact inspected roots and method are in `inventory.json`. The EM count is scoped to the SDK subtree, whereas setup records 7,439 unique archive paths; these are different scopes, not a demonstrated missing-file failure. All three inspected roots have zero `.map` files. Existing prior probes identify DWARF in the six EM ELFs. Symbol/debug availability does not prove stock-version correspondence.

`.gitignore:150` explicitly ignores `/third-party/local-vendor/`. Thus SDK content is deliberately absent from ordinary Git status. That rule does not hide the reconstructed C under `g2/components/bootloader/`. The checkout has substantial staged and unstaged work; it was preserved.

## Highest-yield next probes

1. **Bootloader plain printf family.** Available Ambiq `utils/am_util_stdio.c` supplies `am_util_stdio_printf`, `am_util_stdio_vsprintf`, integer and float helpers. Prior analysis identifies a candidate stock family of 11 bodies / 1,754 bytes around `0x415900..0x415fae`. Apollo3/3P SDK provenance does not make its HAL suitable for Apollo510, but this generic utility is a credible source comparison. Compare bounded formatting cases, callback order and newline behavior before adopting it. This can avoid reconstructing the parser from scratch; savings remain an estimate, not measured.
2. **IAR runtime identification.** Use the 675 archives as relocation-aware reference objects without activation. Prior probes already show size differences for `snprintf` and `_PrintfFull`; do not claim an exact match between installed 10.10.2 and the stock 9.60.2 candidate. This could identify helper contracts while the licensed compilation boundary remains unresolved. Preserve the IAR source-license restriction; no vendor source was copied here.
3. **EM controller types and interfaces.** Six debug-bearing ELFs and 109 archives are useful for bounded ABI/type comparisons. The consolidated reference attributes 1,494 functions / 157,122 bytes to older v4.2 archives; this is historical binary matching, not new v4.6 source recovery. Compare a small known function/layout set before transferring types or names.
4. **GX8002 model boundary.** Existing model getter/task headers can explain command/data extents. The 9,164-byte NPU command stream and 120,800-byte weights are distinct from MCU instructions. Preserve their identities and trace their consumers rather than feeding weights to a CPU decompiler. Closed/model-generation content still blocks a blob-free rebuild.

The newly usable material strengthens source attribution and interface recovery. It does not remove the remaining compiler/configuration, closed-library, resource, scheduling or whole-image equality gaps. No source-completion percentage is inferred from these counts.

The requested ranked theory-crafting assessment is in [SHORTCUT-ASSESSMENT.md](SHORTCUT-ASSESSMENT.md), with seven data-only IAR object probes and six EM ELF identities in `sdk-probe-evidence.json`. New post-run reconciliation also confirms all635 recorded inputs and161 linked objects remain unchanged for the newer candidate; it is still awaiting candidate-specific promotion checks.

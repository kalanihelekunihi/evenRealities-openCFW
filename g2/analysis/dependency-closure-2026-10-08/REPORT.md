# Completed bounded dependency closure

Native delay, five terminal/fatal paths, complete allocator/DFU diagnostic interfaces, fixed readonly diagnostic data and internal IAR memory-helper contracts were advanced. No commits/index/flash/device writes or shared campaign changes. All110 sealed audit inputs and accepted predecessor deliverables verify unchanged. No source-complete or byte-identical payload/OTA claim.

| Accepted checkpoint | Candidate SHA256 | New execution evidence |
| --- | --- | --- |
| Native delay238 | e5aeae5297c6aa35c78a5f4c558365d2d47a0f8f6505f3ed2431914278ef6c32 | 768 native scheduler/list cases,270 body cases,73 NOR boundary cases;7 integration/13 affected; exact object/relink |
| Terminal239 | 15d222c4f550da090e0893905111771b5e3cabd07948f4be082863851f1fdd32 | 120 body/48 actual mask/exit-child cases;7 integration/76 fresh jobs; exact object/relink |
| Logger240 | 1cdf1d63cc01590235139d85caea25e518e3cb9b8fcf4c4bed3c15e5c14c20fd | 213 installed full-task-log,88 native elog/IAR-packaging,48 real time producer;7 integration/76 fresh jobs;2 objects/relink |
| Readonly242 | fe6b6c464c4f884965ce75fe2e6925adc8ee773bf49c4a34c86b34ff270429d3 | 36 strings+ADC2 words,1166 exact readonly bytes;97 update-core full-log cases on241 with identical code/data inherited;7 fresh integration/13 affected;24076-job suite inherited;2 data objects/relink |

Standalone internal IAR fill/aligned-copy source executes840 real-instruction Cortex-M55 QEMU comparisons (504fill/336copy), including full guard buffers, raw return, seededR4-R11,SP,masks, no semantic child stubs.2 mutants rejected. Source object/fixture ELF9836dacab743cbc75d6bd1e3624bf045a461084cec8855f3b94a4538b65168c0 reproduce exactly. It is not installed into242 and does not relabel older Unicorn helper-model receipts as real execution.

The final ownership ledger g2/analysis/source-replacement-ledger-2026-10-08-readonly separates38 nonoverlapping original body footprints9,472B from37 readonly ranges1,166B. Existing/refined DFU task and timestamp were admitted after stronger coupling evidence; four new log bridges receive no fabricated stock-function byte credit. Standalone memory helpers164 original bytes are deliberately outside that integrated ledger. File/object counts do not measure source completeness. validate.py checks source/object/original hashes and110 inputs.

Read KNOWLEDGE.md for recovered behavior, image-header offsets, tick/CRC/install/log semantics and explicit test limits. Key practical facts: CMSIS0 skips yield; UINTMAX is finite ticks; log time%d becomes negative aboveINTMAX; short-read log needs actual count; magicNum is only the low byte; CRC/install skip different header lengths; final install log has no varargs; internal copy raw cursor isout+(count&~1), not memcpy's out. Readonly logging gaps were hidden by severity/line-only or pointer-only fixture cuts. Real hardware UART/locking/scheduling/trap effects remain unverified.

## Navigation

All following analysis directories are under g2/analysis/bootloader-completion-2026-10-06/inventory-worker/:

- startup-initialize/iar-format-native-integrated/: preserved237 formatter checkpoint;5062 M55/1511 nonfloat/216 wrappers/7integration/76jobs; source/objects/relink, fullFPSCR and limits.
- startup-initialize/startup-caller-root-native/: preserved237 initializer alias;64 caller/root comparisons,7integration/13affected; frozen2-object reproduction.
- task-delay-native/ and startup-initialize/runtime-delay-native-integrated/: delay body/scheduler source and accepted238 receipt.
- terminal-paths-native/ and startup-initialize/terminal-native-integrated/: five readable terminal functions and accepted239 receipt.
- logger-call-metadata/ and startup-initialize/logger-native-integrated/:18 original caller lines, full argument/layout recovery, original-only capture clearly separated, accepted240 receipt.
- update-log-literals/ and startup-initialize/platform-log-literals-integrated/: literal manifests/data ownership and final accepted242 receipt. update-log-literals-integrated/ is the unaccepted241 intermediate used for97 scoped tests.
- iar-memory-native/: independent source/header, stock byte provenance,840 actual M55 cases and controls/reproduction.

Canonical source is under g2/components/bootloader/thread_creation/{task_delay_native,terminal_paths_native}/, log_call_adapters/, update_core/log_literals/, initializer_callbacks/{platform_log_literals,iar_memory_native}/. Sources are outside ignored build paths; no blanket unignore or staging performed.

## Exact remaining boundary

Named synthetic logger aliases and five named raw terminal executable aliases in this bounded link were replaced. This does not prove a complete direct/indirect bootloader graph: static scans retain source-local/zero-size assembly and linker-veneer attribution limits, and dynamic callback/peripheral/state coverage is incomplete. No unsupported static graph conclusion is promoted to source completeness.

Authentic resident ROM bytes or matching vendor source are needed to recover/emulate external routines40,48 and0200ff20. They are outside OTA and their absence does not prevent accounting/reconstructing known call instructions inside OTA. Physical correctness needs real scheduler/interrupt/clock/peripheral/UART/factory/calibration traces/state for the respective paths. Producing IAR compiler/configuration and remaining whole-image reviewed source coverage are separate prerequisites for complete source-defined byte-identical OTA. Existing coherent/controlled fixtures cannot substitute for those inputs. Further arbitrary-input/hardware lifetime claims stop here; the bounded recovered code/interfaces remain usable offline.

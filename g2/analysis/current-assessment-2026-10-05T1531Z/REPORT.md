# Current OpenCFW assessment — 2026-10-05

**The complete locked firmware is not proven fully disassembled/classified, not semantically decompiled, and not recreated as a blob-free compilable source build.** There is substantial raw output and useful bounded understanding, but these are different completion claims.

This is a **new scan of the original MacBook checkout** `/Users/kalani/Repo/evenRealities-openCFW`, cutoff **15:33:22 UTC**, not a replay of the earlier assessment. Scope is the locked G2 `s200_v2.2.6.10` EVENOTA artifact: six payloads, 4,301,227 bytes, SHA-256 `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`. R1's separate firmware/SoftDevice, absent ROM/resident loaders and external NOR/font contents are not part of this denominator.

## What changed since 00:13:53 UTC

| Same-definition measure | Earlier | Fresh | Change |
|---|---:|---:|---:|
| Recognized candidate bodies | 1,912,325 | 1,912,325 | 0 |
| Raw pseudocode-addressed bytes | 1,902,397 | 1,902,397 | 0 |
| Source-byte-matched assembly exports | 488,326 | 490,200 | +1,874 |
| Authenticated scoped-review union | 197,000 | 197,000 | 0 |

The fresh measures address 44.46%, 44.23%, 11.40% and 4.58% of **stored bundle bytes**, respectively. None is a percentage of all executable code or complete semantics. The assembly gain is entirely Apollo main. Definitions and regression checks are unchanged; baseline records are the saved immutable audit. Upstream/functionality/classification views are additional dimensions, not credited as methodology progress.

There are 710 first-observed receipt paths under the unchanged scanner, no changed receipt hashes, and no new top-level review paths. This does **not** mean no new reviews: the scanner excludes newer nested fixture reviews and unsupported schemas. Fresh activity snapshot records 7,153 files changed after the old cutoff (mtime evidence, not success). At15:31, new RTOS tick wrap/due-task fixtures and independent reviews were written. The due-task review reports **168 original-instruction calls** with varied priorities/event membership/cursors/ready counts and guards. Packets remain `accepted:false`, `status:partial`; multi-task batches, future deadlines, inter-read mutation and physical tick delivery are outside that proof. Earlier review scopes already cover the relevant tick/queue code, so richer tests add understanding without increasing the unique reviewed-byte union. Nested review globs and receipt formats are a second limitation. “No added unique review footprint” is not “no work.”

`state.json` still registers old108–110 P2 assignments while artifacts show120xx fixtures. Recent writes do not identify live worker owners. The campaign records P2_EXECUTING, G1 passed, G2–G6 not run, and no C implementation assignments.

## Per payload and processor

All percentages below divide by the **payload's stored byte count**. “Outside footprint” includes unmeasured code, data, assets and packaging; it is not a missing-C-code count.

| Payload | Stored bytes | Byte-matched assembly footprint | Raw catalogue pseudocode footprint | Authenticated scoped-review footprint | Blob-free complete payload |
|---|---:|---:|---:|---:|---:|
| codec | 326,092 | unknown* | 92,560 (28.38%) | 2,170 (0.67%) | 0/1 |
| ble_em9305 | 211,948 | 208,840 (98.53%) | uncatalogued* | 1,530 (0.72%) | 0/1 |
| touch | 34,464 | unknown* | 27,879 (80.89%) | 15,926 (46.21%) | 0/1 |
| case | 55,784 | 41,082 (73.64%) | 43,072 (77.21%) | 22,814 (40.90%) | 0/1 |
| apollo_bootloader | 148,599 | 123,960 (83.42%) | 112,506 (75.71%) | 101,936 (68.60%) | 0/1 |
| apollo_main | 3,523,396 | 116,318 (3.30%) | 1,626,380 (46.16%) | 52,624 (1.49%) | 0/1 |

*Codec/C-SKY and touch have disassembly text, but the unchanged matcher cannot count relevant manifest-indirected receipts or text without byte columns. Therefore assembly availability/completeness is **unknown**, not zero. EM9305 has bounded manual recovery outside the Ghidra function catalogue; its zero catalogue numerator is not zero actual pseudocode. ARC instruction streams and NPU commands are not interchangeable with CPU source.

| Payload | Consumer/processor | Role |
|---|---|---|
| Apollo bootloader | Apollo510B / Cortex-M55 | reset/scatter, update/recovery, image and flash handling |
| Apollo main | Apollo510B / Cortex-M55 | RTOS/memory, drivers and buses, BLE host, display/audio, application services |
| BLE controller | EM9305 / ARCv2 EM | link layer, baseband, radio/PAL, HCI/vendor records |
| Codec | GX8002B / C-SKY CK804ef + proprietary NPU | voice DSP/KWS/VAD, control/DFU UART and I2S audio |
| Touch | PSoC CY8C4046FNI / Cortex-M0+ | touch/proximity, calibration/power and I2C reports |
| Case | STM32G0B1 / Cortex-M0+ | UART protocol, charging/thermal/watchdog and dual-bank update |

### Raw-output denominator and remaining work

| Payload | Raw decompiler output / catalogued candidates | Missing candidate outputs | Raw addressed bytes / catalogue bytes | Catalogue bytes without raw output |
|---|---:|---:|---:|---:|
| codec | 929/929 | 0 | 100.00% | 0 |
| touch | 308/308 | 0 | 100.00% | 0 |
| case | 435/435 | 0 | 100.00% | 0 |
| apollo_bootloader | 849/903 | 54 | 93.42% | 7,926 |
| apollo_main | 8,838/8,853 | 15 | 99.88% | 2,002 |

Totals: **11,359/11,428 catalogue candidates have raw output; 69 do not.** The catalogue is incomplete, particularly for ARC/nested/decoded regions, and may include data in bodies. A .c suffix on a Ghidra export is not compilable firmware C. Semantic acceptance and fully reviewed-function counts are **unknown**; a scoped review can cover bytes or paths without closing all callers, branches, indirect dependencies and hardware behavior.

Machine matrix `component-phase-matrix.json` records every phase denominator, complements and nulls. Assembly complement is stored payload bytes minus its measured export union; pseudocode complement is both catalogue bytes minus addressed bytes and stored bytes outside footprint; review complement is stored bytes outside review union. They must not be summed across phases. No complete semantic-pseudocode, actual-executable-disassembly or partial-compilable-C percentage is supported.

## Assets, data, metadata and unresolved storage

The earlier bounded typed map is **reused after fresh source identity checks**, not advertised as new classification work:

| Disjoint class | Bytes |
|---|---:|
| Actually observed original CPU instructions | 1,570 |
| Confirmed typed non-code | 151,707 |
| Metadata | 1,276 |
| Proven padding | 4 |
| Unresolved, including static code candidates | 4,146,670 |
| Conflicts | 0 |
| **Total** | **4,301,227** |

Observed PCs are a conservative code-role lower bound, not all statically recognized code. The executable denominator remains bounded only by [1,570,4,148,240]; no useful semantic completion interval follows. Non-code comprises120,800 codec weights,1,792 vector/control bytes,40 FHDR fields,7 version-string bytes,4 checksum bytes,28,872 consumer-attributed L8 storage,168 descriptor bytes and24 pointer-literal bytes. The NPU's adjacent 9,164-byte command stream remains code-bearing unresolved. RAM/BSS/decoded expansions do not inflate stored-byte totals. Broad compressed/resource-like spans are not blindly subtracted.

The 120,800-byte weight leaf exists separately and its hash verifies in the 33-image inventory. Six of 428 display descriptor candidates have attributable typed storage; the other 422 remain unresolved. Those proofs validate storage admission and geometry, not renderer pixels/global decoder activation. No complete standalone stock bitmap/font/audio resource export corpus is evidenced; indexed pixel ranges are not extracted artwork. External fonts/NOR contents are absent. **Whole-bundle resource extraction percentage is unknown.**

## Upstream versus unique/closed logic

Attribution is evidence-graded. Selected source commits are generally compatibility baselines, not the historical producing checkout. Most key submodule directories are uninitialized. Presence of public source, matching function names or a known version does not prove a compiled replacement.

| Payload | Strongest supported attribution | Remaining distinction |
|---|---|---|
| Apollo main | Strong FreeRTOS 10.5.1/IAR CM55 lineage + TCB patch; CMSIS wrappers; Ambiq 5.1 lineage; Cordio r20.05-family; hybrid LVGL 9.3-development fork; filesystem/font/utility families | Historical generating commits unresolved; product adapters/custom application logic and closed GoMore/Goodix/NemaGFX remain separate gaps. No image-wide library/unique split % |
| Bootloader | IAR/DLIB, FreeRTOS, littlefs, TLSF, EasyLogger and Ambiq family evidence | Exact toolchain/release/link configuration and source replacement unproven |
| EM9305 | Documented SDK archive audit: 1,494 functions / 157,122 bytes of a 210,888-byte app record (**74.50%**); broader provenance 167,684 bytes (**79.51%**) | Historical scoped archive attribution, not new complete relink/source recovery; unmatched portion is not automatically unique app code |
| Codec |102 matches / 151 eligible SDK object sections;68 symbols / 5,374 bytes | SDK-object denominator, not firmware-wide percent; DSP/NPU contents and private logic remain opaque |
| Touch | Exact 56-byte Infineon PDL unit matching release-v2.21.0/GCC 10.3–13.3 -Og | One function match; broad PDL/ModusToolbox attribution not proved |
| Case | Strong Keil armclang/armlink/Arm C runtime, STM32HAL/FreeRTOS lineage and one exact handler | Exact versions, broad byte coverage and product charging/control policy source unknown |

These are documented evidence claims checked against current references/checkout availability, not a new FunctionID/archive experiment. Some citations refer to retired files available in Git history, and older summaries conflict with newer matching evidence. `upstream-attribution.json` preserves those qualifications. There is no defensible all-firmware upstream-versus-unique percentage.

## Compilable source, linking and image reproduction

**0/6 complete blob-free payloads; 0/1 demonstrated source-identical bundle.** Per payload, completion is0/1, rather than an assertion that no partial source exists. Compilable-source byte/function percentage is unknown. Whole-system behavioral equivalence is unverified.

All six active manifest providers are `official_blob`. The matching official inputs or their repacked container demonstrate input identity/container round trip, not compilation. The cached reference-build path recorded in target.json is now absent; target.json itself describes a historical cached verification with no package build.

Historical core-source manifests describe hybrid overlays. Their provider outputs are absent and declared sizes/hashes differ from the lock; region ledgers retain 81,187 bootloader, 3,028,096 main and 210,584 controller official bytes. Those ledgers cannot establish today's verified source-built byte percentage. EM record packagers accept supplied binaries; they are not controller implementations.

Nine existing Apollo-only model/helper batches document 269 instruction scenarios. They are useful pseudocode/host interfaces/synthetic tests, not six processor firmware links or a production image. The bounded typed-map replays are additional evidence, not new firmware modules. Exact licensed toolchain releases, linker/object/section order, runtime configuration, all unique/closed code, resource reconstruction and external dependencies remain blocking gaps. ARC/C-SKY tool-build receipts establish analysis tools, not firmware builds. No complete production link/relink receipt was found.

## Foundations-first actionable plan

**EvenHub SDK and similar higher-level application logic are last.** New local plan files `PRIORITIES.md` / `priority-plan.json` record this instruction without editing shared campaign state.

| Priority | Functionality | Consumers | Interface | Next bounded gap |
|---|---|---|---|---|
| P0 | Boot chain / reset / vectors | Apollo bootloader + main; EM9305; GX8002; touch; case | ROM/SBL → image entry → scatter/copy/zero → vector/IRQ registration | Reset reachability and initialization ownership for every image; constructor/ISR scheduling contracts |
| P0 | Memory / allocator / DMA / MPU-cache | Apollo main + all secondary processors | NOR/XIP, SRAM/TCM, heap/pools, buffers and DMA | Pool/heap lifetime, DMA/copy boundaries, allocation failures, IRQ/cache coherence |
| P0 | RTOS / tick / task / queues / ISR | Apollo main; case; codec RTOS lineage | Scheduler, tick/tickless, task/event lists, mutexes and queues | Multi-task due batches, future deadlines, critical section/inter-read mutation, actual interrupt delivery |
| P1 | Apollo ↔ EM9305 / BLE host-controller | Apollo main + EM9305 ARC | HCI packet driver, controller LL/BB/PAL and vendor reset/NVDS | HCI enqueue/copy/ownership, controller records, RF sequencing and host↔controller failure recovery |
| P1 | Apollo ↔ codec / audio hardware | Apollo main + GX8002 C-SKY/NPU | UART3 BUXX control/DFU; I2S/DMA PCM input | Reset/start/stop/DFU handshakes, PCM timing/metadata producer, frame faults and DMA buffer ownership |
| P1 | Apollo ↔ touch | Apollo main + PSoC Cortex-M0+ | I2C bus5 slave0x0C; attention GPIO; reports/DFU mailbox | Command/report layout, IRQ/attention ordering, power transitions, calibration and resident-loader boundary |
| P1 | Apollo ↔ charging case | Apollo main + STM32G0 Cortex-M0+ | Pogo UART 5A A5 FF; charging/thermal/watchdog; dual-bank OTA | Frame/resync/checksum, bank swap, charger/watchdog buses and disconnect behavior |
| P1 | Temples ↔ each other | Apollo main per temple | UART/TinyFrame and sync framework | Synchronization state ownership, framing/CRC, retransmission and device-role boot configuration |
| P1 | Display hardware / draw buffers | Apollo main; JBD4010/A6N-G + NemaGFX | MSPI0 QSPI, panel command variants, DMA/render buffer handoffs | Panel command/register sequences, framebuffer stride/format, GPU ownership/cache/DMA and scanout lifecycle |
| P1 | NOR / filesystem / persistent update | Apollo bootloader + main; MX25U25643G | MSPI1 quad/XIP; littlefs/FlashDB; OTA flash backends | Flash transaction state, erase/program safety, filesystem recovery, authenticated image install boundaries |
| P1 | Sensors / power / board configuration | Apollo main; ICM45608 + mag, OPT3007, nPM1300/BQ25180/BQ27427 | I2C/IOM, GPIO/ADC/interrupts; battery/brightness/sleep policy | Board variant dispatch, register transactions, IRQ/power timing, sensing↔scheduler interactions |
| P1 | Security / crypto / update trust | Apollo bootloader + main; EM9305 | Image checks, BLE SMP/security, compiler/runtime and hardware AES interfaces | Trust boundary and recovery paths using synthetic inputs; no credential/device access |
| P2 | G2 ↔ R1 ring transport | Apollo main; external nRF52840 R1 | BLE central discovery, notifications/write, queue/ATT ownership | Finish transport/lifecycle contracts before app actions; R1firmware is a separate locked artifact, not these six payloads |
| LAST | EvenHub / SDK / product feature services | Apollo main application layer | Protobuf/RPC service logic, custom screens, UI features and app semantics | Defer new work until foundations/buses/drivers/IPC contracts reviewed; retain interfaces needed to explain hardware consumers |

All functionality-specific completeness percentages remain **unknown**: no exhaustive subsystem byte/function denominators have been independently admitted. The matrix records interfaces, evidence and next gaps instead of inventing them. Hardware reference grades distinguish firmware evidence from datasheet identity and inferred board wiring; in particular physical Apollo↔EM bus/pins and several sensor bus/pad assignments remain unverified.

**Coordination needed:** identify active owners through the campaign parent before reserving overlaps or changing assignments. If an RTOS owner is confirmed active, preserve its current bounded work and relay this plan. This assessment neither cancels unknown workers nor alters state/gates. Avoid new higher-level feature/SDK work; retain only application interfaces necessary to explain foundational consumers. Pseudocode freeze still precedes firmware C implementation.

## Evidence, reproduction and independent checks

Readable summary: `SUMMARY.md`. Structured component/functionality matrices, class and phase intervals, current-activity evidence, build/upstream assessments, comparisons and priority plan are alongside this report. The large immutable audit is `g2/build/audits/2026-10-05T1531Z-current/` with 45,187 verified file captures, 56 missing references and 5 hash mismatches reported rather than accepted silently; supplemental app-text files have separate pins.

Reproduce the saved metric definitions on this Mac into a **new** directory:

```sh
python3 g2/analysis/current-assessment-2026-10-05T1531Z/assess.py --output g2/build/audits/NEW-ASSESSMENT
```

The new scan was executed stepwise with those methods. `methods/` and `method-manifest.json` pin implementations; the driver composes those steps. Twelve review-repair fixtures and five instruction fixtures pass; all 33 inventory image hashes / six root payloads authenticate. Source-byte instruction matching and interval unions reproduce baseline definitions. The bounded class map partition/hash checks pass. Independent reviewers verified totals/deltas, schema limitations, upstream/source-build distinctions and ownership caveats. No decompilation or firmware-build/generation job was started; no commit, reset, staging, flashing or hardware write occurred.

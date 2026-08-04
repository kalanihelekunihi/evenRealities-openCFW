# Peripheral open-source library provenance audit

Status: read-only provenance and source-close audit. This report does not
change an overlay, manifest, build input, test, package artifact, or device.

Scope: the official G2 `2.2.6.10` codec, EM9305, touch-controller, and
charging-case payloads, with the Apollo bootloader used as a control case for
the upstream-identification method. Package offsets are offsets in the
official component file. Installed addresses are shown only where the record
table, vector table, or existing updater analysis supports them.

## Decision

The peripheral blobs are not equally opaque:

| Payload | Defensible identity | Confidence | Source-use decision |
|---|---|---|---|
| Codec | NationalChip LVP firmware for `grus_gx8002b_dev_1v` | Certain vendor identity | Proprietary boundary; retain the two blobs unless licensed NationalChip source is obtained |
| Codec stage 1 | U-Boot-derived simple CLI core | High family confidence; exact fork/release unknown | A focused source replacement is plausible, but no U-Boot revision is yet authorized |
| EM9305 application | Quantum Leaps QP/C framework with QK and the QF/QEP modules | High family confidence; exact release/configuration unknown | Best new peripheral OSS source-close candidate; retain the controller blob until the QP ABI, port, version, and license choice are pinned |
| EM9305 application | `WsfOs` integration label, consistent with the Cordio/Packetcraft WSF runtime | Lead only | Do not import Cordio controller source from this one label or from the Apollo host-stack identity |
| Touch application | No authenticated OSS library | No positive identity | Keep blob-backed and recover the MCU/port contract first |
| Case application | FreeRTOS Cortex-M0 kernel, with software timers enabled | Certain family; exact release/configuration unknown | Use official FreeRTOS as the algorithmic reference after tag/config fingerprinting; do not assume Apollo's V10.5.1 pin |
| Case application | STM32G0 HAL | Target family proven, HAL provenance unproven | Compare complete HAL bodies against STM32CubeG0 tags before importing source |
| Apollo bootloader | littlefs v2.10.1-equivalent, EasyLogger 2.2.99-equivalent, and one exact AmbiqSuite MSPI leaf | Authenticated/source-equivalent | These are already defensible upstream reuse boundaries |
| Apollo bootloader | TLSF v3.1 family/source-equivalent candidate | Strong | Reuse the vendored source only after the boot-specific executable closure is bounded |
| Apollo bootloader | FreeRTOS plus a CMSIS-RTOS2-style wrapper | Certain family; exact boot revision unknown | Fingerprint the boot copy independently; do not inherit the main-application version by association |

The immediate result is therefore not “decompile every peripheral.” The
EM9305 QP/C framework, case FreeRTOS kernel, and codec CLI should be handled as
upstream-configuration recovery problems. The NationalChip DSP/application,
EM9305 radio/controller glue, complete touch application, and charging-case
board/application logic remain genuine binary or clean-room boundaries.

## Evidence and confidence rules

### Official inputs

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `firmware_codec.bin` | 326,092 | `b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0` |
| `firmware_ble_em9305.bin` | 211,948 | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` |
| `firmware_touch.bin` | 34,464 | `0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d` |
| `firmware_box.bin` | 55,784 | `36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374` |
| `ota_s200_bootloader.bin` | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |

The region layout and address status are already fail-closed in
[`manifests/g2-2.2.6.10.json`](../../manifests/g2-2.2.6.10.json) and summarized
in [`docs/memory-map.md`](../memory-map.md). This audit does not strengthen an
`unknown` or `inferred` address merely because a library family was found.

Confidence terms used here are:

- **Authenticated/source-equivalent**: source revision or a set of
  object-equivalent source states is fixed by binary discriminators, and the
  local snapshot/license is pinned.
- **Certain family**: multiple independent and distinctive implementation
  markers identify a project or kernel, but not one source revision.
- **High family confidence**: an exact project-specific module/string corpus
  matches official source; a tag-level instruction comparison is still
  required.
- **Lead only**: the evidence is useful for directing disassembly but is not
  enough to select or license source.

A family match never silently becomes an exact-version claim. Likewise, an
application, board, or SDK version string is not promoted to a third-party
library version.

## Codec: proprietary NationalChip image with a U-Boot-derived CLI

### Container and vendor identity

The FWPK contains metadata at `[0x00000000,0x00000030)`, stage 1 at
`[0x00000030,0x0000958C)`, and stage 2 at
`[0x0000958C,0x0004F9CC)`. The stages are 38,236 and 287,808 bytes, with
declared CRC-32 values `0x307E8A10` and `0xC2DA6C45`. Their target addresses
remain unresolved.

Stage 2 contains two independently built copies of this exact vendor corpus:

| Evidence | Package offset | Stage-2-relative offset |
|---|---:|---:|
| `[LVP]Copyright (C) 2001-2020 NationalChip Co., Ltd` | `0x00014467` | `0x0000AEDB` |
| `grus_gx8002b_dev_1v` | `0x000144B6` | `0x0000AF2A` |
| `2026-03-26, 17:07:25` | `0x00014514` | `0x0000AF88` |
| same LVP copyright | `0x0004BCA0` | `0x00042714` |
| same board/model string | `0x0004BCF0` | `0x00042764` |
| `2026-03-26, 17:07:19` | `0x0004BD50` | `0x000427C4` |

This is definitive NationalChip LVP/GX8002-family firmware, not evidence of
an open-source audio, NPU, or DSP implementation. The embedded notice says
“All Rights Reserved.” Public availability of a GX8002 SDK or documentation
does not by itself provide a redistribution or source license. The repeated
`0.0.2.3` strings at package offsets `0x00012C40` and `0x00044D30` are not
assigned to an SDK release without an authenticated vendor manifest.

### U-Boot-derived command line

Stage 1 contains a distinctive cluster from U-Boot's simple CLI and command
dispatcher:

| String | Package offset | Stage-1-relative offset |
|---|---:|---:|
| `alias for 'help'` | `0x00008364` | `0x00008334` |
| `No CLI available` | `0x00008568` | `0x00008538` |
| `** Too many args (max. %d) **` | `0x0000857C` | `0x0000854C` |
| `## Command too long!` | `0x0000859C` | `0x0000856C` |
| `boot> ` | `0x000085B4` | `0x00008584` |
| `<INTERRUPT>` | `0x000085BC` | `0x0000858C` |
| `%-*s- %s` | `0x000085E0` | `0x000085B0` |
| full unknown-command/help diagnostic | `0x000085F8` | `0x000085C8` |
| short unknown-command diagnostic | `0x00008650` | `0x00008620` |

The combined wording and formatting correspond to `common/main.c`,
`common/cli_simple.c`, and `common/command.c` in official
[U-Boot](https://github.com/u-boot/u-boot), whose relevant files carry
`GPL-2.0+`/`GPL-2.0-or-later` terms. A read-only comparison against upstream
commit `100e12ea78c73071b9710f08b32fd4590019266f` found the same corpus, but
that current comparator commit is **not** a G2 version candidate. These
strings have existed across many U-Boot releases and vendor forks.

This supports the family-level label **U-Boot-derived simple CLI core**. It
does not establish that the surrounding boot code, board port, environment,
or NationalChip fork is upstream U-Boot.

Focused disassembly should recover:

- `CONFIG_SYS_MAXARGS`, command-buffer size, prompt length, and tokenizer
  limits;
- command-table descriptor layout, repeatability, aliases, help, completion,
  and environment feature gates;
- input/edit/history behavior and the console read/write hooks;
- allocator/environment ownership and every jump from the CLI into
  NationalChip services; and
- complete entry/interior/stored-pointer topology for the small CLI closure.

Even a perfect instruction match might not distinguish two source-identical
fork states. The exact fork archive or source manifest is needed to settle
historical provenance. Any source reuse must preserve U-Boot notices and
comply with the applicable GPL corresponding-source obligations; the
proprietary LVP body cannot be relabeled under U-Boot's license.

## EM9305: QP/C is present; the controller source is not yet pinned

### Record/address boundary

The EM package is record-based rather than one flat image:

| Package range | Target range | Role |
|---|---|---|
| `[0x00000000,0x0000007C)` | container only | record metadata |
| `[0x0000007C,0x0000015C)` | `0x00300000...0x003000E0` | record 0 |
| `[0x0000015C,0x000003EC)` | `0x00300400...0x00300690` | record 1 |
| `[0x000003EC,0x00000424)` | `0x00302000...0x00302038` | FHDR; entry `0x00302028` |
| `[0x00000424,0x00033BEC)` | `0x00302400...0x00335BC8` | controller application |

The raw package version word is `0x04040200`, and the FHDR declares 206,848
code bytes. Neither value is assigned to an upstream library.

### Quantum Leaps QP/C and QK

The application has a contiguous assertion/module-name table:

| String | Package offset | Installed address |
|---|---:|---:|
| `MyApp` | `0x00032538` | `0x00334514` |
| `qk` | `0x00032540` | `0x0033451C` |
| `qf_dyn` | `0x00032544` | `0x00334520` |
| `qf_act` | `0x0003254C` | `0x00334528` |
| `qep_hsm` | `0x00032554` | `0x00334530` |
| `qf_actq` | `0x0003255C` | `0x00334538` |
| `qf_mem` | `0x00032564` | `0x00334540` |
| `WsfOs` | `0x0003256C` | `0x00334548` |

Official [Quantum Leaps QP/C](https://github.com/QuantumLeaps/qpc) source
defines exactly the project-specific module names `qk`, `qf_dyn`, `qf_act`,
`qep_hsm`, `qf_actq`, and `qf_mem` in the correspondingly named QK/QF/QEP
translation units. This six-module corpus is strong evidence for QP/C, not a
match inferred from generic state-machine function names. It proves at least:

- the QK preemptive run-to-completion kernel;
- QF active objects and active-object event queues;
- dynamic event allocation and fixed-block event pools; and
- QEP hierarchical state machines.

A read-only official-source comparator at commit
`7ee296892198cb980bfa64959044a8080cdc5669` contains the exact module
definitions. That commit is only a family comparator, not the controller's
version. The names span multiple QP/C generations, and no QP release/version
literal was recovered.

Current official QP/C is dual-licensed as
`GPL-3.0-or-later OR LicenseRef-QL-commercial`. Because the embedded release
is unpinned, this audit does not claim an exact historical QP license. Before
source enters an EM9305 image, openCFW must select a clearly licensed release,
preserve its notices, and review the GPL effect on the complete linked
controller image or obtain a commercial license. A module-name match is not a
license grant for the existing binary.

Focused comparison should now recover, per candidate QP tag:

- `QF_MAX_ACTIVE`, `QF_MAX_EPOOL`, and `QF_MAX_TICK_RATE`;
- event-signal, event-size, queue-counter, and memory-pool counter widths;
- QP object layouts, event reference counts, pool tables, and active-object
  registry layout;
- assertion IDs and whether `Q_NASSERT` or tracing/Q-SPY was enabled;
- QK ready-set width, priority ceiling, interrupt nesting, scheduler lock,
  and the exact EM9305 CPU-port critical-section ABI; and
- normalized function hashes for the six named modules, followed by a
  complete caller/pointer closure.

QP/C is the strongest new peripheral source-close candidate, but not yet a
safe drop-in. Its portable algorithms should be separated from the EM9305
startup, radio, ROM imports, flash records, interrupt controller, clock, and
vendor BLE/link-layer glue.

### `WsfOs` and the BLE stack boundary

`WsfOs` is consistent with the Wireless Software Foundation OS layer used by
the Packetcraft/Arm Cordio stack. A read-only official Cordio comparator at
commit `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` exposes the `WsfOs*` API and
uses Apache-2.0 at repository level. This is a useful lead, not an exact
controller-stack identity:

- the string alone does not select a Cordio/Packetcraft revision or source
  file;
- the Apollo image's authenticated Cordio **host** stack does not prove the
  EM9305 controller's provenance; and
- a WSF adaptation can coexist with proprietary EM radio/link-layer code.

Do not vendor a controller stack from this marker alone. First recover the
HCI Read Local Version constants or `LlGetVersion` equivalent, WSF handler and
timer layouts, ROM import table, supported LL feature masks, transport ABI,
and the vendor radio/patch boundary. Then compare complete normalized bodies
against authenticated Cordio/controller SDK releases.

## Touch controller: no authenticated upstream library

The FWPK wrapper is `[0x00000000,0x00000020)`. Its 34,432-byte Cortex-M
application is `[0x00000020,0x000086A0)`. The vector table gives initial SP
`0x20002000` and reset vector `0x00004675`, making logical base `0x00000000`
a strong inference rather than a confirmed updater destination.

The useful retained text is application-specific: EEPROM initialization and
save failures, proximity-baseline and gesture settings, click/slide/long-press
state, and ANSI-colored diagnostics. `2.2.0.1` at package offset `0x00007AC4`
(raw/application address `0x00007AA4`) is the touch application version, not
an RTOS or library version.

No source path, license/version banner, project-specific module corpus,
standard FreeRTOS task name, or other discriminating OSS marker was found.
ARM Cortex-M code and generic EEPROM/logging behavior are not library
identities. The full application remains blob-backed.

The next focused pass should:

1. identify the MCU from CPUID, peripheral bases, flash geometry, and updater
   protocol;
2. bound reset, IRQ, clock, watchdog, EEPROM/flash, CRC, host transport, and
   touch-sensor interfaces;
3. establish bare-metal versus scheduler/event-loop control flow; and
4. replace small protocol/CRC/configuration seams only after golden host
   traces exist.

## Charging case: FreeRTOS family is certain, version is not

The 32-byte EVEN wrapper declares case application `1.2.57`. The application
occupies package range `[0x00000020,0x0000D9E8)` and installed range
`[0x08000000,0x0800D9C8)`; the updater can program the same bytes at
inactive-bank alias `0x08040000` before `nSWAP_BANK` changes the logical bank
mapping.

### FreeRTOS evidence

The case vector table selects PendSV `0x08000103`. Its complete handler at
`[0x08000102,0x08000140)` is 62 bytes with SHA-256
`6093899cb710c7c4528991e47a9fd21cc8e4099f36f51ecaebadcc5f6998309c`.
It has the canonical Cortex-M0 FreeRTOS context switch:

- read PSP;
- load `pxCurrentTCB` through the literal at `0x08000140`, whose value is
  `0x20000128`;
- save and restore software context `r4-r11` around the current task stack;
- mask interrupts around the call to `vTaskSwitchContext` at `0x0800C390`;
- write PSP and exception-return.

The SysTick vector is `0x08008421`; its 20-byte handler at
`[0x08008420,0x08008434)` has SHA-256
`f79a96ddb1c4afa97ba3edf88a956b8444ce29b77bf7bca38399530173619504`
and reaches the RTOS tick path after an application/HAL gate. Standard kernel
task names are present at:

| Task name | Package offset | Run address |
|---|---:|---:|
| `IDLE` | `0x0000C308` | `0x0800C2E8` |
| `Tmr Svc` | `0x0000CD94` | `0x0800CD74` |

The handler plus both standard task names unequivocally identifies the
FreeRTOS Cortex-M0 kernel. `Tmr Svc` proves `configUSE_TIMERS == 1`. It does
not identify V10.5.1, the compiler port revision, or a complete
`FreeRTOSConfig.h`; the same markers exist across many releases.

The exact release must be pinned before assigning the embedded copy's
license. Older FreeRTOS generations used GPL terms with an exception, while
modern FreeRTOS Kernel releases use MIT. Importing the authenticated Apollo
V10.5.1 snapshot merely because both images use FreeRTOS would be an
unsupported provenance claim.

Focused tag comparison should recover:

- tick frequency/source, CPU clock, preemption, time slicing, idle/tick
  hooks, and tickless-idle policy;
- maximum priorities, stack growth/alignment, TCB/list/queue/timer layouts,
  and the exact Cortex-M0 compiler port;
- dynamic/static allocation and heap scheme;
- mutex, recursive mutex, semaphore, event-group, notification, queue
  registry, overflow, assert, and `INCLUDE_*` switches;
- timer task priority, queue length, and stack depth; and
- every board/HAL call around SysTick, SVC/startup, low power, and the
  scheduler start.

Once tag discrimination is complete, use the matching official kernel and a
small case-specific port/config layer rather than decompiling scheduler,
list, queue, and timer algorithms.

### STM32G0 HAL non-claim

The vector/peripheral/update behavior establishes an STM32G0 Cortex-M0+
target and a dual-bank 512-KiB logical flash plan. It does not identify a
specific STM32CubeG0 release, exact part number, or prove that the application
uses unmodified ST HAL rather than LL or generated/local code.

Before any source import, recover the DBGMCU/device ID or exact peripheral
map, normalize complete candidate functions against official STM32CubeG0
tags, and pin the selected device header plus `stm32g0xx_hal_conf.h` feature
set. Preserve the case updater's 2-KiB page, eight-byte doubleword,
option-byte, bank-swap, and protected calibration/device windows as
case-specific policy, not generic HAL behavior.

## Apollo bootloader control case: identities already strong enough for reuse

The bootloader demonstrates the standard required before a peripheral family
match is promoted to source.

### littlefs v2.10.1 source-equivalent

The defensible source pin is release `v2.10.1`, commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`, tree
`06dd0162169d3cb550cd24a3e34d0e4d02983ad3`, BSD-3-Clause. Three upstream
source states are object-equivalent under the recovered configuration, so
this is not a historical-checkout claim. The complete proof is
[`littlefs-version-audit.md`](littlefs-version-audit.md).

Boot evidence includes source path string at file offset `0x0002168C`
(run `0x0043168C`) and an 84-byte configuration at `0x00431070`, SHA-256
`724c351d2136e3c2f10b59ad84d547da4632739ea1f20eb839e9af2cfbd5b6e8`.
Its exact port/configuration is:

| Field | Value |
|---|---:|
| read / program / erase / sync | `0x004212D9` / `0x00421311` / `0x00421349` / `0x004213D5` |
| read / program / block size | 16 / 256 / 4,096 bytes |
| block count / cycles | 3,008 / 500 |
| cache / lookahead | 4,096 / 256 bytes |
| compact threshold | 0 |
| optional buffers and limit overrides | null / zero |
| threading / multiversion / trace | disabled |
| assert/debug/warn/error | enabled |
| buffer allocation | dynamic |

This source is reusable now for source-equivalent core and utility work. Full
mutating filesystem ownership is still blocked on a golden external-flash
capture and disposable power-loss tests because the board MSPI port, flash
contents, and failure policy are not upstream littlefs.

### EasyLogger 2.2.99 source-equivalent

The exact source-equivalent core set is
`cd93d9c768415f4b7279f2d3ef2366ce15ea087c`,
`34cc1717825c799979a1b4b3739be1e5668a7322`, and selected reproducible
snapshot `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`, MIT. Relevant source
blobs are identical across those commits; upstream has no `2.2.99` tag. See
[`easylogger-version-audit.md`](easylogger-version-audit.md) and
[`easylogger-boot-port-audit.md`](easylogger-boot-port-audit.md).

Boot evidence includes:

- `elog_utils.c` at file `0x00020DA0` / run `0x00430DA0`;
- `elog.c` at file `0x00020EC0` / run `0x00430EC0`;
- version `2.2.99` at file `0x00024074` / run `0x00434074`;
- logger object `0x20026700`, padded size `0xF8`;
- output buffer `0x200258D0`, 1,024 bytes;
- six levels, maximum global level verbose, ANSI colors, line/tag/keyword
  maxima 5/30/16, and five tag-level slots;
- assert mask `0xFF`, error-through-verbose mask `0xD7`, LF newline, and
  directory/function/line formatting enabled; and
- boot-specific static 80-byte CMSIS mutex, 1,000-tick wait, synchronous
  channel-1 sink, 56-byte transfer descriptor, 1,000 polls, and ten-unit
  inter-poll wait.

The upstream formatter/filter core is reusable. The sink, wait/interrupt
policy, assertion hook, CMSIS object storage, and downstream transfer are G2
boot ports. No upstream EasyLogger async worker is proven in this image.

### AmbiqSuite exact reusable leaf

`am_hal_mspi_interrupt_clear` is an exact source-equivalent leaf from
AmbiqSuite SDK 5.1.0 commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`, tree
`02b79dbf428a8cded053c65c92cc58fa5fdb8e78`, BSD-3-Clause. Reached CMSIS
Core headers are pinned at `d23a6949a0331ca96853bcd98b0fdcc4db47184c`
under Apache-2.0.

The complete stock boot body is `[0x00426506,0x00426536)`, 48 bytes, SHA-256
`4b01a25a8075cf158eb59da277f8730e36c751ee01c67bae86bc172ec877bd48`.
It has callers at `0x0041FE1A` and `0x004203CC`, API validation enabled,
handle prefix `0x01BEBEBE`, module index at `+4`, base `0x40060000`, stride
`0x1000`, `INTSTAT`/`INTCLR` offsets `0x204`/`0x208`, and interrupt mask
`0x1A80`.

The same function also exists in SDK 5.0.0, so the bytes alone do not prove
that Even historically used the 5.1.0 checkout. The authenticated 5.1.0
source is nevertheless a valid reusable implementation. Larger HAL imports
still require function-level proof because the G2
`am_hal_mspi_control` request ordinals differ from the selected public SDK.

### TLSF and boot FreeRTOS

The boot paths `tlsf_init.c` at file `0x000215C8` / run `0x004315C8` and
`tlsf.c` at file `0x00021A04` / run `0x00431A04`, together with the
diagnostic/assertion corpus and allocator behavior, strongly identify
Matthew Conte TLSF v3.1 source-equivalent code. The defensible local source
range is
`a1f743ffac0305408b39e791e0ffb45f6d9bc777...deff9ab509341f264addbd3c8ada533678591905`,
with selected BSD-3-Clause snapshot `deff9ab`. Recovered target choices are
32-bit pointers/`size_t`, four-byte alignment, `TLSF_64BIT` off, second-level
log2 of 5, maximum first level 30, `0xC74` control size, assertions enabled,
and generic bit operations. Bound the boot executable closure and coordinator
lock/arena before redirecting it wholesale.

Boot strings `IDLE`, `Tmr Svc`, `osMessageQueueNew`, `osTimerNew`,
`osThreadNew`, and task-overflow diagnostics prove FreeRTOS with a
CMSIS-RTOS2-style wrapper and software timers. They do not pin the boot copy
to the Apollo main application's authenticated FreeRTOS V10.5.1 release.
Function-hash the boot task/queue/timer/port bodies independently and recover
its `FreeRTOSConfig.h` before importing the main snapshot.

## Ranked next source-close work

1. **EM9305 QP/C:** enumerate QP assertion call sites and IDs, recover the
   object/configuration widths, and diff normalized QK/QF/QEP bodies across
   official tags. This can replace portable scheduler/event/state-machine
   logic while preserving the EM radio and ROM-import seams.
2. **Case FreeRTOS:** fingerprint `vTaskSwitchContext`, tick, queue/list, and
   timer bodies across official kernel tags; recover a complete
   `FreeRTOSConfig.h` and Cortex-M0 port contract.
3. **Codec CLI:** bound the small U-Boot-derived command-line closure and
   recover command-table/configuration constants. Treat the GPL boundary and
   NationalChip calls explicitly.
4. **EM WSF/controller:** recover HCI/LL version and feature constants, WSF
   handler/timer ABI, and radio/ROM seams before selecting Cordio source.
5. **Case STM32 HAL:** identify the exact G0 part and compare complete HAL/LL
   functions against STM32CubeG0 tags.
6. **Touch:** identify the MCU and protocol/peripheral seams first. There is
   currently no upstream body worth guessing.

For every promoted library, the acceptance gate should require a pinned
official repository/ref, per-file hashes, retained license/notice, recovered
configuration header, host oracle, target object/relocation inspection,
complete entry/interior/stored-pointer topology, and a golden hardware or
captured-protocol test appropriate to the component.

## Hard limitations and explicit non-claims

- This was static, read-only analysis. No G2, case, touch controller, codec,
  EM9305, external flash, or updater was accessed.
- The images are stripped and optimized. Source-inlined bodies, unused
  modules, compiler revision, and source-identical commits can be impossible
  to distinguish from executable bytes.
- Codec stage destinations remain unknown; the touch base remains inferred.
  Library identity does not improve those address classifications.
- QP/C is not assigned a release. `WsfOs` is not promoted to an exact Cordio
  controller identity. FreeRTOS in the case and bootloader is not assigned
  V10.5.1. STM32G0 target identity is not an STM32Cube HAL version.
- The NationalChip `0.0.2.3`, touch `2.2.0.1`, case `1.2.57`, EM raw version
  word, and package version are not third-party library versions.
- Public source availability and a family match do not license proprietary
  vendor glue or the official binary. GPL, MIT, BSD, Apache, vendor SDK, and
  commercial components must remain separately attributed.
- The exact-source bootloader results are a methodological control, not
  evidence that the same versions were used in another processor's image.

The earlier broad inventory's conservative “unattributed peripheral” status
should therefore be refined only for the three proven families above:
U-Boot-derived CLI in the codec, QP/C in the EM9305 application, and FreeRTOS
in the case. Everything else stays blob-backed until a discriminator stronger
than a generic API name or platform association is recovered.

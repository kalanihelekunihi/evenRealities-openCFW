# Ranked upstream-library source-reuse audit

Status: production evidence for the integrated FreeRTOS NTZ/littlefs
increments, bounded `heap_4`/`vQueueDelete`, and bounded CMSIS-FreeRTOS
`osMessageQueueNew`/`osMutexNew`/`osSemaphoreNew` adapters, plus the
dual-image EasyLogger helper quartet and image-specific seam providers, and
the Apollo-main FreeRTOS tick-count getter pair with a source-owned state
provider, plus the exact FreeRTOS `vTaskMissedYield` store;
research-only evidence for the remaining broad CMSIS constructor and
EasyLogger output/core closures; no hardware state changed

Scope: remaining unequivocal or strongly authenticated upstream-library
boundaries in the official G2 `2.2.6.10` Apollo-main and S200 bootloader
images

Out of scope: the separately audited `pcTaskGetName` increment and the
already integrated littlefs utility, fallback-bitops, and disk-version-parts
tranches

## Decision

The remaining firmware should not be approached as one undifferentiated
decompilation target. Several stock boundaries are released open-source
functions whose algorithms can be reused directly. Focused disassembly is
still required, but only to recover the selected compile-time paths, target
ABI, fixed-address state, G2 port adaptations, caller topology, and safe
redirect or in-place ownership.

The first five recommendations below are now completed. The remaining
implementation order is:

1. completed: source-integrate the authenticated FreeRTOS V10.5.1 `heap_4`
   closure and `vQueueDelete`;
2. completed: close `osSemaphoreNew` over those production dependencies;
3. completed: source-integrate the shared EasyLogger helper quartet in both
   Apollo images with distinct source-owned logger/assertion bindings;
4. completed: source-integrate the exact FreeRTOS V10.5.1 tick-count getter
   pair behind a bounded G2 `xTickCount` provider;
5. completed: source-integrate exact FreeRTOS V10.5.1 `vTaskMissedYield`
   behind the recovered G2 `xYieldPending` word;
6. extend the Apollo-main EasyLogger output/formatting cluster beyond those
   helpers;
7. close the remainder of the S200 bootloader EasyLogger core;
8. begin a read-only-first complete littlefs phase after a golden external-flash
   capture; and
9. vendor the now configuration-recovered FlashDB 2.1.1 KVDB/FAL closure
   production-excluded, then build its read-only storage oracle.

The five FreeRTOS Cortex-M55 NTZ assembly leaves formerly ranked second are
now source-integrated in place. The remaining ranked tranches avoid reverse
engineering released algorithms. They
still require bounded G2 adapters where the stock behavior intentionally
differs from pristine upstream.

LVGL, nanopb, TinyFrame, FreeType, Cordio, and the remaining broad LZ4
provenance question are not eligible for an exact-version import claim yet.
Their current evidence is recorded explicitly below.

## Methodology and qualifications

### Official inputs

| Image | Bytes | Load mapping | SHA-256 |
|---|---:|---|---|
| `ota_s200_firmware_ota.bin` | 3,523,396 | 32-byte wrapper, installed payload at `0x00438000` | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Apollo-main installed payload | 3,523,364 | wrapper bytes `32...end` | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| `ota_s200_bootloader.bin` | 148,599 | raw image at `0x00410000` | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |

Every stock span in this report is end-exclusive and is hashed directly from
one of those authenticated inputs.

### Source authentication

An upstream identity is described as **exact release** only when an official
tag, peeled commit, tree, selected source file, and license can be pinned and
the G2 code shape positively selects that release or released alternative.

An identity is described as **source-equivalent** when the stripped G2
binary selects a source generation but cannot distinguish byte- or
object-equivalent official source states. A source-equivalent pin is a
reproducible baseline, not a claim about Even Realities' historical checkout.

The analysis used:

- authenticated upstream tags, commits, trees, Git blobs, and copied-file
  SHA-256 values;
- exact stock function boundaries and neighboring instructions;
- Thumb-2 `BL` and `B.W` decoding at every halfword;
- narrow `B`, conditional branch, `CBZ`, and `CBNZ` decoding;
- an every-byte scan for stored odd Thumb pointers;
- Ghidra function/reference cross-checks for ambiguous byte-window hits;
- outgoing-call, literal, fixed-RAM, object-offset, and callback review; and
- existing source-oracle, target-layout, and offline package evidence where
  already available.

A raw four-byte window that numerically resembles a code pointer is not
treated as control flow without an aligned data use, code reference, or
semantic consumer. The FlashDB and `heap_4` findings below call out the
remaining false-positive windows explicitly.

### What “reuse upstream” means

Reuse does not imply that an entire pristine translation unit can always be
linked without adaptation.

- Authenticated, unmodified CMSIS-FreeRTOS can be candidate-compiled as a
  complete translation unit with function sections and garbage collection,
  retaining only the reviewed constructor closure; that proof is not a
  production integration.
- The FreeRTOS port assembly should be syntax-adapted without changing its
  instruction sequence and installed in place where timing and vector entry
  addresses matter.
- `heap_4` should keep the pristine allocation/coalescing algorithm while a
  small G2 layer binds the recovered fixed RAM and scheduler seams.
- EasyLogger requires explicit G2 port adaptations around an authenticated
  upstream core.
- littlefs and FlashDB require source-owned board/storage ports, not guessed
  copies of upstream example ports.

## Upstream identity and license matrix

| Library | Reusable identity | Authentication qualification | License |
|---|---|---|---|
| CMSIS-FreeRTOS | tag `v10.5.1`, annotated tag object `34e6e4c403c17de35ec0acf29610e374dc938604`, commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`, tree `d3689a816acc77a3f0b7d35439d666ad8434b6ba` | Exact official tagged CMSIS-RTOS2 wrapper source. `cmsis_os2.c` is 70,106 bytes, Git blob `88dca1d881f1a960872572a8a0efd94cde19dcea`, SHA-256 `8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36`. | Apache-2.0 for `cmsis_os2.c`; the linked FreeRTOS kernel remains MIT |
| FreeRTOS-Kernel | tag `V10.5.1`, annotated tag object `d7b40dbed508c305c2a32ccf3982045ec9ba8734`, commit `def7d2df2b0506d3d249334974f51e427c17a41c`, tree `7496dfa815c3cea2f45a090c6e92d113f494b930` | Exact official release snapshot. The annotated tag is not cryptographically signed; the tag, commit, tree, Git blobs, and copied bytes are pinned. | MIT |
| EasyLogger | declared `2.2.99`; source-equivalent set from `cd93d9c768415f4b7279f2d3ef2366ce15ea087c` through selected commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`, tree `dc9ceb7202c5dd2d58e5e5a9b408b1c05a5ec4f3` | No upstream `2.2.99` tag exists. The three proven core-equivalent commits have identical `elog.c`, `elog_utils.c`, `elog.h`, and `elog_cfg.h` blobs. Selected `elog.c` is 28,740 bytes, SHA-256 `d4291ab1314a34cf940c8e0d7246e05570f8d32ae0704b498cf6fbacab76acb1`. | MIT |
| littlefs | source-equivalent release `v2.10.1`, commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`, tree `06dd0162169d3cb550cd24a3e34d0e4d02983ad3` | The complete 38-assertion fingerprint selects the v2.10.1 generation. Three official source states are object-equivalent under the recovered configuration, so the pin is not a historical-checkout claim. | BSD-3-Clause |
| FlashDB | tag and commit `2.1.1` / `714d6159e7e6afb267a3953756abca445c350e61`, tree `3410ae8111e4dbf6ae22d995bfcf37274abf89ea` | Exact official tagged source and an in-image `2.1.1` version literal referenced by the stock initializer. | Apache-2.0 |

The authenticated local source records for FreeRTOS, CMSIS-FreeRTOS,
EasyLogger, and littlefs are:

- `third_party/freertos-kernel/PROVENANCE.json`;
- `third_party/cmsis-freertos/PROVENANCE.json`;
- `third_party/easylogger/PROVENANCE.json`; and
- `third_party/littlefs/PROVENANCE.json`.

The CMSIS-FreeRTOS snapshot and broad candidate closure are authenticated;
the bounded `osMessageQueueNew`, `osMutexNew`, and `osSemaphoreNew`
algorithms are production-integrated. FlashDB still requires
a production vendor snapshot with the same per-file verification discipline
before its first build is accepted.

## Rank 1: CMSIS-FreeRTOS v10.5.1 constructors

### Why this is first

The constructor algorithms and wrapper policies are released upstream,
their G2 object ABI is recovered, and all three complete stock entries have
closed external-reference topology. They add no private writable state.

The preferred internal order is:

1. `osMessageQueueNew`;
2. `osMutexNew`; and
3. `osSemaphoreNew`.

All three constructors have now shipped as separately bounded production
leaves. `osSemaphoreNew` closes over source-owned `vQueueDelete`, which in
turn closes over source-owned `heap_4` free and interrupt masking.

### Exact stock bodies and topology

| Function | Stock range | Bytes | Stock SHA-256 | External direct `BL` callers | Caller-address SHA-256 |
|---|---|---:|---|---:|---|
| `osMessageQueueNew` | `[0x00449A32,0x00449ABE)` | 140 | `52d0abf097914cc84b2cdfe7f628dc61f9efb40bac880112062315d2b1bfba47` | 15 | `7974f375f4b38120a6df7ce5416cef9fa65031d5768226b8785d2916d0f96f18` |
| `osMutexNew` | `[0x0044971C,0x004497B6)` | 154 | `09f88d8a6a64730936a52aa0c2f90d9bcb0152f6e2439919f6409110148999ec` | 30 | `14d18197e409351bfa6ded1310c61c1f27246ebd93ecf86452d19ac0bdadbfd0` |
| `osSemaphoreNew` | `[0x0044989A,0x0044994E)` | 180 | `ebdcf69b866e35e468ba9ce84d7e7ac9b58377b5ffcc439762d729f7d99a098c` | 5 | `b1bff9196e2fecc8b466bd89718cfb0bf0f3e825e4d220f08bbdd6e6d6598bcb` |

The ordered noncontiguous concatenation is 474 bytes with SHA-256
`fc3d9e163b0d029829f3f4d9b78155d0c0559e6d4633863769e5d27cbb5495eb`.

For all three entries, complete-image scanning found:

- no external `B.W` caller;
- no narrow entry branch;
- no external branch into an interior instruction; and
- no stored entry or interior Thumb pointer.

### Recovered configuration and ABI

The stock constructors select the following upstream branches:

| Item | Recovered G2 value |
|---|---|
| static allocation | enabled |
| dynamic allocation | enabled |
| `StaticQueue_t` / `StaticSemaphore_t` control block | 80 bytes |
| queue registry | disabled (`configQUEUE_REGISTRY_SIZE == 0`) |
| recursive mutexes | enabled |
| robust mutexes | rejected |
| CMSIS recursive-mutex ID convention | low bit of successful handle is set |
| message-queue static validation | control and message storage must both be present and large enough |
| semaphore validation | `maximum > 0` and unsigned `initial <= maximum` |
| interrupt policy | object construction is rejected in `IRQ_Context()` |

The selected outgoing calls are:

```text
osMessageQueueNew
  0x00449A3C -> IRQ_Context                 0x0044900E
  0x00449AA2 -> static generic creator     0x004415CA
  0x00449AB4 -> dynamic generic creator    0x00441636

osMutexNew
  0x00449722 -> IRQ_Context                 0x0044900E
  0x00449778 -> static mutex creator        0x004416F0
  0x00449784 -> static mutex creator        0x004416F0
  0x00449796 -> dynamic mutex creator       0x004416D6
  0x004497A0 -> dynamic mutex creator       0x004416D6

osSemaphoreNew
  0x004498A4 -> IRQ_Context                 0x0044900E
  0x004498F8 -> static generic creator      0x004415CA
  0x00449906 -> dynamic generic creator     0x00441636
  0x0044991C -> generic send/give           0x004417EE
  0x00449926 -> queue delete                0x00441EA2
  0x00449938 -> static counting creator     0x00441790
  0x00449944 -> dynamic counting creator    0x004417C2
```

The queue creators, mutex creators, counting wrappers, generic send/give,
`vQueueDelete`, and heap free paths are source-owned. Binary-semaphore
give-failure cleanup therefore stays within the reviewed production closure.

### Implementation gate

The compile inputs are now vendored under `third_party/cmsis-freertos`.
CMSIS-FreeRTOS tag `v10.5.1` is pinned at unsigned annotated tag object
`34e6e4c403c17de35ec0acf29610e374dc938604`, peeled commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`, tree
`d3689a816acc77a3f0b7d35439d666ad8434b6ba`. Its package-declared CMSIS_5
`5.9.0` dependency is pinned at unsigned annotated tag object
`61e36449f53c25ef7825c40f7dd93685736f457f`, peeled commit
`2b7495b8535bdcb306dac29b9ded4cfb679d7e5c`, tree
`b88e747b2a2309b81ea77831481a58393465cd7b`. `cmsis_os2.c` is 70,106
bytes, Git blob `88dca1d881f1a960872572a8a0efd94cde19dcea`, SHA-256
`8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36`.
The wrapper and CMSIS headers retain Apache-2.0 terms; the separately
supplied FreeRTOS kernel remains MIT.

Candidate-only shims at
`components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/`
provide `{FreeRTOSConfig.h,portmacro.h,cmsis_freertos_target.h,string.h}`.
They compile the authenticated, unmodified `cmsis_os2.c` for Cortex-M55 with
`-Oz -Werror`. Function-section garbage collection retains 370 text bytes:

| Candidate-retained function | Text bytes |
|---|---:|
| `IRQ_Context` | 46 |
| `osMessageQueueNew` | 88 |
| `osMutexNew` | 98 |
| `osSemaphoreNew` | 138 |
| **Total** | **370** |

The candidate retains zero read-only or writable data and four 8-byte EHABI
`.ARM.exidx` sections. Its isolated gate passes 6/6 tests in 0.231 seconds.

This broad proof does not establish Even's historical checkout or stock byte
identity and does not make `osSemaphoreNew` or unrelated CMSIS services
production-ready. There is
no authenticated G2 RTE/device header; the `SystemCoreClock` seam and MVE
selection remain unresolved; broad `INCLUDE_*` switches are compile-only
assumptions; assert, NVIC, and libc seams remain outside the retained root;
and candidate `StaticTask_t` is 108 bytes versus the 112-byte stock G2 TCB.
Reject any production build that retains unrelated CMSIS services, writable
state, an unexpected undefined symbol, or a configuration branch outside its
bounded evidence.

The target test must inspect every retained call relocation and bind
source-owned queue dependencies directly rather than through unnecessary
source-to-stock-to-source trampolines.

### Production `osMessageQueueNew` result

The admitted source is the 8,427-byte
`components/apollo_main/core_overlay/runtime_cmsis_message_queue_new.c`,
SHA-256
`8897019aa7a2beca32a88dc60808fb1f99b1538933b8ab4fbd9ed4fed38d433c`.
It ports the exact `osMessageQueueNew` algorithm from authenticated
CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`, retaining Apache-2.0 terms.
Its separately reached FreeRTOS V10.5.1 dependencies remain MIT.

Focused disassembly closes static and dynamic allocation, disabled queue
registry, the 80-byte `StaticQueue_t` ABI, the 24-byte 32-bit attribute
layout, and the `IPSR`/`PRIMASK`/`BASEPRI` IRQ-context policy. The exact
140-byte stock span `[0x00449A32,0x00449ABE)` has SHA-256
`52d0abf097914cc84b2cdfe7f628dc61f9efb40bac880112062315d2b1bfba47`.
Its 15 direct callers have ordered digest
`7974f375f4b38120a6df7ce5416cef9fa65031d5768226b8785d2916d0f96f18`;
there is no alternate, interior, or stored entry.

The raw 124-byte function hashes to
`543fb1ef418aeadd05e2f3b3e60c3f48c0f3521dfa995a3079a86b86ccc58eee`.
Its exact relocation allowlist is:

| Offset | Type | Source-owned target |
|---:|---|---|
| `+0x10` | `R_ARM_THM_CALL` | `open_cfw_freertos_task_get_scheduler_state` |
| `+0x44` | `R_ARM_THM_CALL` | `open_cfw_freertos_queue_generic_create_static` |
| `+0x78` | `R_ARM_THM_JUMP24` | `open_cfw_freertos_queue_generic_create` |

Two zero bytes at `[0x007B0202,0x007B0204)` align the final relocated leaf
at `[0x007B0204,0x007B0280)`, SHA-256
`afbba4f9f08b2df17a4350d7a7e83d99b8439283ee40c1a1604bd879dff75f04`.
The complete 140-byte entry replacement has SHA-256
`b9e761042539e109acea61b03a522bb5795539850f0751906c6e06d0da198a47`.

The main overlay/provider are 114,524 and 3,637,920 bytes with SHA-256
`de76f5db2f04f48c81ea480c348a3c9151d4441c522eba68621ad812290153e2`
and
`874bdc621a6cd91848dee66038c3ba97d7e4b7c7ab1fb5063739bf69fc3047e1`.
The 4,416,102-byte package has SHA-256
`c7baf50cd5386a5e27b4c284cc0084e8cf5d0b83d74eb08b8d4a997bf66474f4`;
the 552,937-byte flash plan has SHA-256
`79da631918503c668516e1af5d3844e3dab65c9e63d8add4834a43536ef69407`.
The focused production gate passes 10/10 tests. All validation was offline;
no physical device, serial endpoint, debugger, or flasher was accessed.

### Production `osMutexNew` result

The admitted source is the 9,798-byte
`components/apollo_main/core_overlay/runtime_cmsis_mutex_new.c`, SHA-256
`28081734a384c089635681014ed028414b75d375c22f0a52a64f53e22842cf2d`.
It preserves the exact 2,169-byte `osMutexNew` algorithm block, SHA-256
`c928d16d21e4c016836b54f3a3780609c567e6484adcb297bc1b9f733ed47b15`,
from the authenticated 70,106-byte CMSIS-FreeRTOS v10.5.1
`cmsis_os2.c`, commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`, file SHA-256
`8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36`.
The adapter retains Arm's Apache-2.0 terms. Its separately reached
FreeRTOS-Kernel V10.5.1 dependencies are pinned to commit
`def7d2df2b0506d3d249334974f51e427c17a41c` and retain MIT terms.

Focused disassembly selects enabled static and dynamic allocation, enabled
recursive mutexes, disabled queue registry, rejection of robust mutexes,
and the upstream rule that priority-inheritance bit `0x2` needs no special
constructor branch. `osMutexRecursive` is bit `0x1`; successful recursive
handles are returned with their low bit set, while `osMutexRobust` bit `0x8`
returns null. The 32-bit `osMutexAttr_t` ABI is 16 bytes with
`name/attr_bits/cb_mem/cb_size` at `+0x00/+0x04/+0x08/+0x0C`, and
`StaticSemaphore_t` is 80 bytes. Null attributes and an all-zero attribute
record select dynamic ordinary-mutex creation; a non-null control block
requires at least 80 bytes; mixed control-block fields are rejected. The
inlined `IPSR`/`PRIMASK`/`BASEPRI` policy rejects handler mode immediately
and rejects masked thread mode after the scheduler has started.

The complete stock span is `[0x0044971C,0x004497B6)`, 154 bytes with
SHA-256
`09f88d8a6a64730936a52aa0c2f90d9bcb0152f6e2439919f6409110148999ec`.
Its 30 direct `BL` callers have ordered address/instruction digest
`14d18197e409351bfa6ded1310c61c1f27246ebd93ecf86452d19ac0bdadbfd0`.
Whole-image scanning finds no external `B.W`, narrow entry branch, interior
branch, or stored entry/interior Thumb pointer. The stock outgoing topology
is `0x00449722 -> IRQ_Context 0x0044900E`,
`0x00449778/0x00449784 -> xQueueCreateMutexStatic 0x004416F0`, and
`0x00449796/0x004497A0 -> xQueueCreateMutex 0x004416D6`.

The raw target section is 116 bytes, four-byte aligned, with SHA-256
`59e1d787a4beaa36b01d932672e43893331fc5d22a46e2371cc111ec4dacb192`.
Two generated zero bytes occupy `[0x007B02A6,0x007B02A8)` and the relocated
leaf occupies `[0x007B02A8,0x007B031C)`, with final SHA-256
`4b404daca19132875236099c06bd18ab6441ade2d61a7f3c855210ddd2a28863`.
Its complete relocation allowlist is:

| Offset | Type | Source-owned target | Runtime target |
|---:|---|---|---:|
| `+0x0E` | `R_ARM_THM_CALL` | `open_cfw_freertos_task_get_scheduler_state` | `0x007AECFC` |
| `+0x32` | `R_ARM_THM_JUMP24` | `open_cfw_freertos_queue_create_mutex_static` | `0x007AEEBC` |
| `+0x56` | `R_ARM_THM_JUMP24` | `open_cfw_freertos_queue_create_mutex` | `0x007AE100` |
| `+0x5C` | `R_ARM_THM_CALL` | `open_cfw_freertos_queue_create_mutex_static` | `0x007AEEBC` |
| `+0x64` | `R_ARM_THM_CALL` | `open_cfw_freertos_queue_create_mutex` | `0x007AE100` |

That mutex release's main overlay was 114,680 bytes with SHA-256
`7603cf2a0de6e8b05d66dc356bf3e0701f6157536d29bdac8ad692dc56e0362c`.
The 3,638,076-byte Apollo-main component has SHA-256
`f696c6dfbd8ab1f7b5cc44fdc06fcdc5baf44f368ad55130e7571d82ee31ec82`;
the 4,416,258-byte package has SHA-256
`11d40cd1b3648f96b5ec98c9fa2dff6de121e878978206a0a9694ede38d3a0ff`.
The focused production gate passes 10/10 tests. These are offline structural,
semantic, topology, and artifact results only; no device, serial endpoint,
debugger, flasher, reset, or external-flash operation was accessed.

The broad complete-translation-unit constructor proof remains candidate-only
for unrelated CMSIS services. The separately bounded production
`osSemaphoreNew` adapter is 11,566 bytes with SHA-256
`a947868d3fbcfc7f41d021210355e0ff777d49d3db84fa0da71a255d319c1527`.
Its complete 180-byte stock span redirects to a 178-byte relocated leaf at
`[0x007B05A8,0x007B065A)`, closed over source-owned scheduler state, static
and dynamic generic creation, generic send, counting-semaphore creation, and
`vQueueDelete`. Its focused production gate passes 8/8 tests.

## Integrated FreeRTOS NTZ port assembly

### Identity and stock bodies

The G2 context-frame, SVC, PendSV, FPU, and MPU behavior positively selects:

```text
FreeRTOS-Kernel V10.5.1
portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s
configENABLE_MPU = 0
configENABLE_TRUSTZONE = 0
configENABLE_FPU = 1
```

The authenticated upstream `portasm.s` is 11,686 bytes with SHA-256
`eaa83b3867edec5560c69f2a21facd7aff3c0f3bfcdfc5751722375ae328ee8f`.

The already integrated interrupt-mask pair is not duplicated here. The
remaining exact assembly leaves are:

| Function | Stock range | Bytes | SHA-256 | Entry topology |
|---|---|---:|---|---|
| `vRestoreContextOfFirstTask` | `[0x005FA058,0x005FA07E)` | 38 | `10edd4871b5f0c829e38618f1003ef0c45ec3629219317e23c62a2e255b0f4f8` | one `BL` at `0x00442146`; caller digest `db283daff74045a6fe9702c346c6000e03061e8eb49ec86fdfa6357782cb7fdc` |
| `vRaisePrivilege` | `[0x005FA07E,0x005FA08C)` | 14 | `29bceedf776515c291813e4eecd9a836378b81550c42d08aee35cf15df3bd8db` | no external direct caller or stored pointer |
| `vStartFirstTask` | `[0x005FA08C,0x005FA0A4)` | 24 | `44ba0097fbbc1d0691837d5c51bee83e6b61509c9d89efffee9c202d930e6347` | one `BL` at `0x00442200`; caller digest `638abbe988f572d43825de249ca173ddb82fa4b9c6f6b4af988211cd59837d20` |
| `PendSV_Handler` | `[0x005FA0C8,0x005FA120)` | 88 | `d8e234bfa34805ad160e41ef54801973c9c871b36cf7ac0f365b56fe503253e3` | vector pointer `0x005FA0C9` at `0x00438038` |
| `SVC_Handler` | `[0x005FA120,0x005FA132)` | 18 | `d0fac197473b52d6ed466462d237ddb20dd8096a6507ea559e75d4bd9d88da94` | vector pointer `0x005FA121` at `0x0043802C` |

Their ordered noncontiguous concatenation is 182 bytes with SHA-256
`ca6be773f86c12eea198872e73541d97ce6bb806e2d03c57c1f540ad43c1e2fd`.
There are no additional wide, narrow, interior, or stored references.

### Fixed seams

The exact source-generated in-place form must preserve:

- `pxCurrentTCB` at `0x20074A20`;
- the vector-table offset register address `0xE000ED08`;
- the literal/alignment pool at `[0x005FA132,0x005FA13C)`;
- `BL vTaskSwitchContext` to `0x004551B4`;
- `B.W vPortSVCHandler_C` to `0x00442134`;
- conditional `s16...s31` save/restore;
- `PSPLIM`, `EXC_RETURN`, and `r4...r11` frame ordering; and
- the released BASEPRI, DSB, and ISB ordering already established by the
  integrated mask pair.

### Production integration and gates

The implementation is
`components/apollo_main/core_overlay/runtime_freertos_ntz_port.S`, 5,487
bytes with SHA-256
`38c6a259ca2fbfbefb373ef5a80216f2e5f1cad998173ca2b4c9cfde6c01aee8`.
Apple Clang 21.0.0 compiles it for `arm-none-eabi` with the reviewed
Cortex-M55, Thumb, freestanding, no-builtin, function/data-section,
no-unwind, warning, and error flags. The target ELF contains five independent
two-byte-aligned executable sections with no tails:

| Section | Bytes | Raw pre-relocation SHA-256 |
|---|---:|---|
| `.text.vRestoreContextOfFirstTask` | 38 | `6cd49195f965664fa52a501576fafc8f84a77f4719cf755515ef7606b3a1d8be` |
| `.text.vRaisePrivilege` | 14 | `29bceedf776515c291813e4eecd9a836378b81550c42d08aee35cf15df3bd8db` |
| `.text.vStartFirstTask` | 24 | `28d1d6e471df04ae8476e1355225e2d4d3673d4af90b68338fc8589441ae16b7` |
| `.text.PendSV_Handler` | 88 | `12c7f208de16f3d5636cd00d8307847552937eb484b86b185b45b686553953ee` |
| `.text.SVC_Handler` | 18 | `1807cfce5ab3df565e585de5dd35011f18e5994e748363f15cb7376aa796e1c4` |

The exact allowlist is four `R_ARM_THM_PC8` relocations:
`vRestoreContextOfFirstTask+0x00`, `vStartFirstTask+0x00`, and
`PendSV_Handler+0x18/+0x3A`. The three `pxCurrentTCB` sites target
`0x005FA134` and require `204a0720`; the VTOR site targets `0x005FA138`
and requires `08ed00e0`. The remaining records are
`PendSV_Handler+0x2E R_ARM_THM_CALL vTaskSwitchContext -> 0x004551B4`
and
`SVC_Handler+0x0E R_ARM_THM_JUMP24 vPortSVCHandler_C -> 0x00442134`.
Relocation reproduces the five exact stock hashes in the table above.

The production `in_place_leaves` contract keeps these functions outside the
appended overlay ABI and `patch_sites`. It authenticates source/compiler/body
pins, requires the complete ordered relocation list, verifies literal words
and original stock bytes, and rejects overlapping or out-of-range writes.
SVC/PendSV vectors remain `0x005FA121`/`0x005FA0C9`; the literal pool remains
`[0x005FA132,0x005FA13C)`.

At the FreeRTOS NTZ integration milestone, the appended
overlay/provider/package bytes were unchanged, with SHA-256 values
`00318de9ff51e19f77d889fa691a3a2a54e035b1287843bda857f944af58e065`,
`f0da043e234dc38481059459755e091622d689313cd12e5c8d5155c7b4ba3202`,
and
`058782604ab6cb946aff0acedbbef7d367bb1d82114f28c9a70276bcdf178e9a`.
The report records 182 in-place source bytes, 114,506 total source-owned
bytes, and 3,443,066 opaque base bytes. The 750/2/5 manifest has flash-plan
SHA-256
`eda45c2cc276bd70bc123267d9fbdc09b0ae4aa030a7557f874c259ca7f5fee8`;
ownership is 114,820 source, 81,477 generated, 4,219,537 opaque, and 196,297
controlled bytes, or 2.600188%, 1.845110%, 95.554702%, and 4.445298%.

The focused production gate passes 23/23 tests in 18.333 seconds, and the
linker plus inherited focused gate passes 21/21 in 0.705 seconds. Standard
source and manifest verification pass. Three output-isolated lanes at
`build/repro-freertos-ntz-output-{a,b,c}` reproduce both overlays, both
providers, the package, and the flash plan byte-for-byte; lane-local temporary
manifests were moved to Trash. All 248 Apollo-main tests passed in 582.904
seconds. `./make.sh test` passed all 1,838 tests in 1,038.709 seconds,
including all six CMSIS constructor compile-closure tests. All validation
was offline and no hardware was accessed.

Those artifact and accounting pins are historical and are superseded by the
current littlefs disk-version-parts promotion below.

## Completed former Rank 3: FreeRTOS V10.5.1 `heap_4`

### Source identity

The official V10.5.1 `portable/MemMang/heap_4.c` is 20,608 CRLF bytes with
SHA-256
`d48a51e34caed771e6650d95f6c2527e52fde2a6ebc6f83b49d003aef0135e05`.
Its LF-normalized 20,071-byte form has SHA-256
`025bc24c6fff0115d83e5ab496efc4e7bf02803683ec57cf11225d6f71b28eb6`.
The normalization changes line endings only.

The 49-file authenticated FreeRTOS vendor snapshot now retains this exact
`portable/MemMang/heap_4.c` at its upstream path. Provenance additionally
pins Git blob `3af0caf2b60fc4adfb103a115fefbf1b09b21dd8`; the file retains the
FreeRTOS MIT license. It is the authenticated algorithm reference for the
selected bounded production adapter; the pristine snapshot does not itself
provide G2 heap placement or allocator selection. Focused disassembly supplies
the fixed-address state, configuration, and scheduler/hook seams below. The
separate application TLSF allocator is not substituted.

### Exact stock closure and topology

| Function | Stock range | Bytes | SHA-256 | Direct callers / topology |
|---|---|---:|---|---|
| `pvPortMalloc` | `[0x00456110,0x00456210)` | 256 | `8d86a7daf341ad836729e4abdd25b66b45f97a56d6d1077c07bf0c5718f8dc57` | 11 external `BL` callers; digest `d462d089b939012d13528427b3f788d2339ad392617849ab9305e3fe9302e77b` |
| `vPortFree` | `[0x00456210,0x00456280)` | 112 | `d754aec282080b2deafeb6756cbacc156af70a311499ee4d73eeb7497f12b032` | 10 external `BL` callers; digest `962e1ea2286d11969de5f736bfffe8f940bfe168ef72318272102ed99676d96a` |
| `prvHeapInit` | `[0x00456280,0x004562DA)` | 90 | `0b6c69c306e3a8e734f524f0cc38146cf761f996a14bd61ef81651fd6ebd6b0f` | one internal caller at `0x00456128` |
| `prvInsertBlockIntoFreeList` | `[0x004562DA,0x00456338)` | 94 | `88820119c56a0487020dceef91194de8299b056d25f887ff87badb84c0806a10` | two internal callers at `0x004561BA` and `0x0045626E` |

The contiguous 552-byte closure has SHA-256
`a805cb30f37d145d55e1785435f941a850b85b5ab3af7d1a21752fe75130d266`.
No true external `B.W`, narrow, interior, or stored-pointer reference was
found. The raw every-byte scan sees a numeric `0x004562C0` window at odd
address `0x005A6C69`; it is unaligned data, has no Ghidra control-flow
reference, and is not an allocator entry.

### Recovered configuration and state

| Item | Recovered value |
|---|---:|
| heap base | `0x20004558` |
| `configTOTAL_HEAP_SIZE` | `0x2F000` bytes |
| nominal heap end | `0x20033558` |
| alignment | 8 bytes |
| block header | 8 bytes |
| allocation bit | `0x80000000` |
| free-list policy | address sorted, adjacent-block coalescing |
| `configHEAP_CLEAR_MEMORY_ON_FREE` | `0` |
| scheduler locking | `vTaskSuspendAll` / `xTaskResumeAll` |
| malloc-failed hook | enabled, stock entry `0x0046D85E` |

The fixed compatibility globals are:

| Address | Role |
|---:|---|
| `0x20074158` | start-list sentinel |
| `0x2007465C` | end marker pointer |
| `0x20074660` | current free bytes |
| `0x20074664` | minimum-ever free bytes |
| `0x20074668` | successful allocation count |
| `0x2007466C` | successful free count |

The remaining typed scheduler seams are `vTaskSuspendAll` at `0x00454D7C`
and `xTaskResumeAll` at `0x00454DCC`. The interrupt-mask fail-stop path can
bind to the source-owned mask leaf.

### Completed implementation gate

The bounded adapter preserves the upstream algorithm while binding the
authenticated heap and globals through reviewed fixed-address compatibility
pointers; it adds no writable section.

All four functions moved atomically, so no old and new allocator bodies can
mutate the same free list through different structure definitions. Host tests
cover alignment, splitting, both-direction coalescing, exact-fit allocation,
overflow rejection, double-free assertion, free-byte accounting,
minimum-ever accounting, and allocation/free counters.

The 16,885-byte MIT adapter has SHA-256
`d848b90a00da24db963c49dbff2472314b2a76c6cf269efef46e6cac56889986`.
Its source leaves occupy `[0x007B031C,0x007B057E)` with four generated
alignment bytes, and the complete 552-byte stock closure redirects to them.
The dedicated production gate passes 13/13 tests.

Together with the source-owned `vQueueDelete` and `osSemaphoreNew` leaves,
that historical overlay was 115,510 bytes with SHA-256
`6359e4e8c824af3cea36280a1aabd6ad671027e38fb3263fe9ac0cbb292660b4`.
The 3,638,906-byte Apollo-main component hashes to
`00d112e265f40dd8bf98fc9021bba54b3bcc94f159111b2f4815d5484e91c67c`;
the 4,417,088-byte package hashes to
`064c9429352132cee2a5dfe45c2bf52349e10111b89db91f093b1ce16ed0c2b0`.
The 570,697-byte flash plan hashes to
`8334c9308a7ae7f03d7a2a214cca946063963b1636a9088fe730a15303dd2975`.

## Partially completed former Rank 4: Apollo-main EasyLogger output/formatting cluster

### Source identity and required adaptation

The thread-mode formatting and filtering algorithm is source-equivalent to
the authenticated EasyLogger core. Three small format helpers are direct
upstream logic. The main output function contains two deliberate G2 changes:

1. it reads `IPSR` immediately after entry and silently returns from every
   exception context before dereferencing an argument or touching state; and
2. it submits `(buffer, length, level)` to G2 asynchronous glue, while
   pristine upstream uses `(level, buffer, length)`.

This tranche is therefore an MIT-licensed bounded G2 adaptation of
authenticated upstream source, not an unmodified transplant.

### Exact stock bodies and topology

| Function | Stock range | Bytes | SHA-256 | Direct callers / topology |
|---|---|---:|---|---|
| `elog_output` | `[0x0043D574,0x0043D976)` | 1,026 | `d7c5fd89997fc677ecce543af7c33cd08614b832a47602f1fd895bb7ab45f90c` | 6,239 `BL` callers; digest `2d4e701757c3ec84ae6c6b53b2638728c3da6d6121eb95579f3b4e13843be2a2` |
| `get_fmt_enabled` | `[0x0043D97C,0x0043D9E6)` | 106 | `d0a18c1e6bc1a42e8a91b37c891aaf3425b98f6bc56741211512d871056b136d` | 10 `BL` callers; digest `dfeaf0c883a7e9e23c2eb09e5f14f934da56e4a9d3ea5972bccccd3406d9612c` |
| line-aware format helper | `[0x0043D9F0,0x0043DA0A)` | 26 | `95bba933ae9e65022ef0ff0daa76324678aa539c2ba79435b80181ce34a23db7` | 3 `BL` callers; digest `2dfdd9b59819f72c56f2bc6a7d86889d2306f364ed9ac385a1ee1ffe5d5ec491` |
| pointer-aware format helper | `[0x0043DA0A,0x0043DA24)` | 26 | `3af2631ad7a44be557a9454da2df68862b6458bf2359f58d41c3d6d2ff86c8a2` | 6 `BL` callers; digest `a1b68901945b68e29b7994d29c0299af9f472d4eb4ba08dd747b3af671d5cec2` |

The ordered noncontiguous 1,184-byte cluster has SHA-256
`19e46435c144691ec4c9d9779241c3faf08d15329eb6fb7075b92963d74b0709`.
No entry has a `B.W`, narrow, external-interior, or stored-pointer reference.
The helper quartet has now been reviewed and source-linked. The retained
`elog_output` body remains the larger boundary for the next tranche.

### Recovered G2 configuration

| Item | Value |
|---|---:|
| logger object | `0x20070BE8`, field extent `0xF6`, padded size `0xF8` |
| shared output buffer | `0x2006BD30`, 1,024 bytes |
| maximum level | verbose (`5`) |
| tag filter | 30 characters plus terminator |
| keyword filter | 16 characters plus terminator |
| tag-level slots | 5 × 33 bytes |
| color output | enabled |
| assertion-hook pointer | `0x2007456C` |
| G2 async event handle | `0x20074570` |
| downstream output wrapper | `[0x0044AA80,0x0044AA98)`, SHA-256 `787d13cfe59fad83061379298387393fa94266c9b31420e7f67e8e07d63f7356` |

The existing EasyLogger source-owned lock/unlock and tag-filter functions
are available for direct linking. The next output tranche should retain:

- the early `IPSR != 0` no-op gate;
- the fixed logger and buffer ABI;
- the G2 assertion identity and returning-hook behavior;
- the typed `(buffer, length, level)` async seam;
- the G2 time/process/thread port seams; and
- the pinned IAR `vsnprintf` seam for arbitrary application format strings.

Replacing IAR formatting with the existing mpaland-derived formatter is a
separate compatibility decision. It requires an oracle across the format
corpus used by all 6,239 current call sites.

### Completed dual-image helper tranche

The completed atomic helper tranche source-owns `get_fmt_enabled`, its
unsigned-argument and pointer-argument predicates, and `elog_strcpy` in
Apollo main and the bootloader. Each image retires 320 authenticated stock
bytes with complete non-linking `B.W` redirects and NOP fill. The helper
callers remain at their original entry points.

The shared 4,975-byte MIT source and 6,505-byte header have SHA-256 values
`8f2850f789fba3b08bdc3e1fa8f3a4646aaef7e4b16862f3be53478071aa22b5`
and
`f3a7e9bce0f136a2ff4a76929c317aef7bbc7c29dfc60d58311d94e58f6e2393`.
The 7,068-byte MIT seam source hashes to
`78dc5aa9a7eb4f072b3169ae1837855007f25e1adccec7deaefecc486c8f0823`.
It source-binds the same algorithms to the Apollo-main logger/hook pair
`0x20070BE8`/`0x2007456C` and boot pair
`0x20026700`/`0x200270E4`. Both profiles fix 32-bit `size_t`, six levels, a
1,024-byte line buffer, and the authenticated tag record layout
`level +0`, `tag +1`, `tag_use_flag +0x20`.

The official assertion strings, main/boot `elog_output` entries
`0x0043D574`/`0x004176CE`, and wait wrappers
`0x0044B0AE`/`0x0041AC8A` remain explicit binary seams. The helper algorithms
and image binding are source-owned.

Apollo main appends 390 source bytes plus ten alignment bytes. Its
115,910-byte overlay and 3,639,306-byte component hash to
`e59da6e6753c0c8a9fa73bad8cd555313d0e2ae6ed95006c818e6697e4fbe32d`
and
`00f5f11dd18c13c56137d0f527da3ecd8ae850a9ae35dc96d671a4b998d79b61`.
Boot appends 270 source bytes plus two alignment bytes. Its 622-byte overlay
and 149,222-byte provider hash to
`fc02cf66854adace4d213e08764e435e27c8c2bc7cc4f7caac6ff286f3adf813`
and
`b4a5b0f2028842a2d6fde9424fff05fac2db3bf0e26e7f01d16a990e67ed9052`.

The 4,417,760-byte package hashes to
`fb662322f26e06aa04eb1d3f55f8c8f18606e510fac9c35885de3e4f92864c4d`.
Its 592,687-byte flash plan hashes to
`c06c84e277bad2160479e0ec1f7a626abb804574f42ecee0709f0978657cd1b3`
and records 822 placed, two unresolved, five container-only, and six
protected regions. Ownership is 116,718 source bytes, 83,395 generated
bytes, and 4,217,647 opaque bytes; 200,113 bytes are controlled.

## Partially completed former Rank 5: S200 bootloader EasyLogger core

### Exact source-equivalent boundary

The bootloader identifies the same EasyLogger source generation and
`0xF8`-byte object ABI as Apollo main. The contiguous core is:

| Boundary | Range | Bytes | SHA-256 |
|---|---|---:|---|
| complete boot EasyLogger core | `[0x0041733C,0x00417BB8)` | 2,172 | `89263d626619d8348f7e9a1f47e5664acb13d812bc039565b380858568f7d7d1` |
| `elog_output` within the core | `[0x004176CE,0x00417AD0)` | 1,026 | `97645514643e4e4e3e5e04a8d14a08c5c714df3cfd64e764b7b73ab95860e021` |
| boot EasyLogger setup | `[0x0043194C,0x0043198A)` | 62 | `3d057acab6aa34a7443a18c5f1a7a63133a12944656603585df0f08982d41316` |

The boot `elog_output` has 115 direct `BL` callers. The ordered caller list
has SHA-256
`47456628984211dc924d9cd6fa0c011711b7195537c8e3f0729a2894cdbed481`.
There is no direct `B.W`, narrow entry, external interior branch, or stored
pointer to the core or port functions.

The separate boot setup function is reached through one stored Thumb pointer:

```text
0x00433448 -> 0x0043194D
```

### Boot-specific configuration

The boot port must not be replaced with the Apollo-main port:

| Area | Bootloader behavior |
|---|---|
| logger object | `0x20026700` |
| line buffer | `0x200258D0`, 1,024 bytes |
| filter after setup | verbose |
| assert format mask | `0xFF` |
| error-through-verbose mask | `0xD7` |
| time string | decimal RTOS tick count in a 28-byte buffer |
| mutex | normal CMSIS mutex, static 80-byte control block, acquire timeout 1,000, ignored result |
| interrupt output | silent early return |
| sink | discard level and submit buffer/length on downstream channel 1 |
| transport | 56-byte descriptor, one transfer start, at most 1,000 polls, ten-unit delay |

The boot image does not prove an upstream EasyLogger async worker. Its sink is
G2 downstream glue and must remain separate from pristine `elog_async.c`.

### Implementation gate

The helper quartet and boot-specific logger/assertion seam providers are now
production-integrated. Closing the remaining authenticated EasyLogger core
still requires a boot-specific configuration and port adapter that preserves
the stored setup pointer, all 115 output callers, the boot assertion policy,
and the channel-1 submission contract. It must not share absolute logger,
buffer, mutex, time, or sink state with Apollo main.

## Rank 6: complete littlefs, read-only first

### Exact source-equivalent evidence

The selected upstream files are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `lfs.c` | 196,753 | `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |
| `lfs.h` | 26,439 | `ee44e99d6b19119b3e577b969b80c9d5e6f96410c9593794afddf6d4b314c486` |
| `lfs_util.c` | 988 | `f2fbde533670560434bd9f5a547174cc7c5a4670a02c47b4bd85180dced8b2ec` |
| `lfs_util.h` | 7,954 | `f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e` |

The complete public wrapper clusters currently occupy:

| Image | Stock range | Bytes | SHA-256 |
|---|---|---:|---|
| Apollo main | `[0x004CFA58,0x004CFD0C)` | 692 | `8fac514f80a47d951c7d25b2912e10d20054e527113767caa8570ab0b346ea3d` |
| bootloader | `[0x00415128,0x0041531C)` | 500 | `f12c429a59dd8fd2285f6a254b55b789f1442523334a2e14190ae70e00823180` |

These aggregate hashes authenticate the current public veneer clusters; a
production redirect still needs an entry-by-entry, interior-reference, and
stored-pointer topology pin for the selected read-only API subset.

### Recovered configuration

Both images use a standard 84-byte non-threadsafe `lfs_config`:

| Item | Value |
|---|---:|
| read size | 16 |
| program size | 256 |
| block size | 4,096 |
| block count | 3,008 |
| partition | `0x01400000...0x01FC0000` |
| block cycles | 500 |
| cache size | 4,096 |
| lookahead size | 256 |
| compact threshold | 0 |
| static optional buffers | null |
| `LFS_THREADSAFE` | disabled |
| `LFS_MULTIVERSION` | disabled |
| dynamic allocation | enabled |
| assertions/debug/warn/error | enabled |
| trace | disabled |

The config objects are:

| Image | Address | SHA-256 |
|---|---:|---|
| Apollo main | `0x006E83A4` | `f38bd899e180d29ee60609a2452d25c2d2d6c6fef4eb455064e23a6ca7c6e813` |
| bootloader | `0x00431070` | `724c351d2136e3c2f10b59ad84d547da4632739ea1f20eb839e9af2cfbd5b6e8` |

The standard callback mapping is:

```text
external address = 0x01400000 + block * 0x1000 + offset
driver success    = 0
driver failure    = -5
sync              = no-op
```

### Remaining blocker and tranche policy

Source identity and basic geometry are not the blockers. The required gate is
a complete external-flash capture:

1. capture and hash the external flash without mutation;
2. mount a copy read-only with the pinned v2.10.1 source;
3. validate superblock, disk version, directory tree, and file contents
   against stock behavior;
4. source-own only mount/stat/read/directory-read paths first;
5. keep format/program/erase and stock auto-format recovery unreachable; and
6. run mutating and power-loss tests only on disposable copies before any
   write-capable integration.

The Apollo510 MSPI parameters are already substantially recovered, but board
initialization, XIP, calibration, mutex, timeout, and retained-power policy
remain in a G2 adapter rather than the littlefs library.

## Rank 7: FlashDB 2.1.1 after configuration recovery

### Exact upstream evidence

The official `2.1.1` source pin is:

| File | SHA-256 |
|---|---|
| `src/fdb.c` | `bd880bdfc33cb81368236a90a2508f69e9da25bae2a47804e16cb728272d087f` |
| `src/fdb_kvdb.c` | `96e09b3f7b8b0dc77b51cb387701e4e9ef7a5cbce2eaa606380962aff25582ac` |
| `src/fdb_utils.c` | `f3ec5d0ec094ceb16f9ad4c73b277d29029b1b3f1b8c7699ddc9ee8ce0efc9a7` |
| `LICENSE` | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` |

The G2 `2.1.1` string is at `0x0078D60C` and has one code reference from
`_fdb_init_ex` at `0x00585BF2`.

Two exact initializer anchors are:

| Function | Stock range | Bytes | SHA-256 | Topology |
|---|---|---:|---|---|
| `fdb_kvdb_init` | `[0x005453FE,0x0054552C)` | 302 | `c40571f5f8710c17ca10a713ec7dd6fa7a32da2fac0e2c1571806ff33cd03aad` | two `BL` callers at `0x004D9776` and `0x005107F0`; caller digest `d8243428fac9957d7eb50c095e2fc9ffdb6e20f17ded4f9c5c2332f3188ccf4d` |
| `_fdb_init_ex` | `[0x00585BC8,0x00585C46)` | 126 | `dcf189562e2516bdc6a47f4975b16f01c15d0250990e2d51745f14cb604ce4aa` | one caller at `0x00545520`; caller digest `b368053ab0ce7bbd61ccc3b5e6c99fac45886086fe55b44eb35ee51632bef684` |

Ghidra reports no external reference into either interior. The raw byte-window
scan finds repeated numeric value `0x00545441` and one `0x0054544C` window.
Neither target has a Ghidra reference, neither is a function entry, and the
windows are data rather than control flow. A production analyzer should pin
that classification instead of weakening the stored-pointer check.

### Recovered configuration

The fail-closed analyzer now proves:

- FAL-backed KVDB mode, not file mode;
- database `sysenv` on partition `kvdb`;
- database `factory` on partition `NVdb`;
- `FDB_WRITE_GRAN=1` and a 24-byte KV header;
- 64 KV-cache entries;
- 64 sector-cache entries;
- 4-KiB sectors inherited from the FAL device block size;
- the two partitions (`kvdb`: `0x01FC0000+0x38000`; `NVdb`:
  `0x01FF8000+0x8000`);
- a single `norflash` device with 1-bit write granularity and exact callback
  slots;
- two static short-enum database objects at `0x2005DFFC`, stride `0x8AC`;
- KV auto update, FlashDB debug logging, and file mode are off; no
  live/retained TSDB subsystem is present, while the original
  `FDB_USING_TSDB` macro state is not statically proven; and
- callers install lock/unlock without overriding sector size.

The selected vendor package is the exact 14-file closure enumerated in
`flashdb-configuration-recovery-audit.md`: `fdb.c`, `fdb_kvdb.c`,
`fdb_utils.c`, public headers, and the generic FAL core/headers. It omits
TSDB source, file, RT-Thread, shell, demo, and sample-port code. Its offline
verifier reconstructs all seven required Git tree objects and proves
commit-to-path-to-blob membership for the 14 selected files.

### Unresolved configuration

The compile-time parameter gaps are closed. Do not link write-capable core
code until focused recovery and oracle work pins:

- the garbage-collection and auto-format policy on corrupt media;
- default KV tables;
- flash read/write/erase callbacks and error mapping;
- the mutex object and callback policy;
- magic/version migration and factory-reset behavior; and
- the exact blob, delete, control, iteration, and service API surface.

The authenticated upstream core can now be compiled as a production-excluded
host/read-only oracle. It is not yet a safe write-capable source tranche
because its outgoing closure reaches the unrecovered Even port and policy.

## Full FreeRTOS kernel: reusable base, not a pristine drop-in

The ranked FreeRTOS assembly and allocator increments are intentionally
bounded. A later complete kernel link can reuse the authenticated V10.5.1
source, but it must carry the recovered G2 compatibility layer.

Proven or strongly constrained values include:

- `ARM_CM55_NTZ/non_secure`, MPU off, TrustZone task contexts off, FPU on;
- `BASEPRI=0x30`;
- 56 priorities;
- 32-byte task names;
- 1,024-Hz Apollo STIMER compare-A tick;
- tickless idle;
- static and dynamic allocation;
- timers, mutexes, recursive mutexes, trace fields, and one notification;
- 80-byte `Queue_t`;
- 44-byte `Timer_t`;
- 32-byte `EventGroup_t`; and
- 112-byte G2 `TCB_t`.

Pristine `tasks.c` is not ABI-compatible by itself. G2 stores a vendor
stack-depth word at TCB offset `+0x54`, followed by trace, priority, mutex,
and notification fields. A complete source port must retain that field,
provide the Apollo STIMER/tickless glue and application hooks, and keep all
object offsets under compile-time assertions.

Still unresolved are MVE selection, unrelated `INCLUDE_*` switches,
device-wide secure attribution, and a few complete hook/build choices. Those
do not block the ranked assembly, allocator, or CMSIS constructor tranches.

## Explicitly non-eligible exact-version claims

The following families are real and useful identification leads, but their
current evidence does not justify an exact upstream revision import:

| Family | What is proven | Why exact-version source reuse is not yet authorized |
|---|---|---|
| LVGL | v9.3-compatible source family, 76 source paths, core ABI/configuration anchors | exact commit and local/Ambiq patches are unknown; large-library append-only duplication also needs a reclamation/link strategy |
| nanopb | 0.4 compact-descriptor ABI, 16-bit field descriptors, callback streams, error strings, 64-bit values, packed repeated fields, no dynamic allocation | exact 0.4.x release, `PB_CONVERT_DOUBLE_FLOAT`, UTF-8 policy, required-field limit, and complete generated descriptor set remain unresolved |
| TinyFrame | unmistakable TinyFrame source paths, public names, and parser diagnostics | ID/length/type widths, SOF, checksums, timeout, payload limit, listener counts, object layout, and exact upstream revision are unresolved |
| FreeType | linked FreeType and LVGL FreeType glue with a used API surface | release, compiled module table, and `FT_CONFIG_OPTION_*` choices are not pinned |
| Packetcraft/Ambiq Cordio | Cordio/Ambiq host-stack family | normalize against AmbiqSuite 5.1.0 and separate application-database modifications before selecting source |
| LZ4 | stock boundary is unequivocally `LZ4_decompress_safe` | point release remains ambiguous between LZ4 1.9.4 semantics and the 1.10.0 copy bundled with LVGL 9.3; the bounded decoder is already source-integrated |

IAR DLIB runtime, application services, audio algorithms, codec/touch/
EM9305 images, and case-controller HAL remain proprietary, unattributed, or
insufficiently identified. They stay blob-backed or are re-created only from
a separately reviewed behavioral contract.

## Already integrated and not duplicated here

This ranking deliberately omits:

- TLSF v3.1 source-equivalent integration;
- the FreeRTOS queue/list/task getter, interrupt-mask, and fixed-address NTZ
  context/exception increments already source-owned;
- the littlefs utility quartet and the other integrated littlefs private
  leaves;
- `am_hal_mspi_interrupt_clear` from authenticated AmbiqSuite 5.1.0;
- the current bounded LZ4 decoder; and
- the separately planned `pcTaskGetName` boundary.

Their existing source, provenance, and tests remain the authoritative record.

## Historical littlefs disk-version-parts promotion

The littlefs reuse program now includes the exact v2.10.1
`lfs_fs_disk_version_major` and `lfs_fs_disk_version_minor` bodies from
`lfs.c` at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. They are compiled for both
official images from the shared 1,734-byte
`components/apollo_main/core_overlay/runtime_littlefs_disk_version_parts.c`,
SHA-256
`920d03e80c9d16a1d0b4299f8151eefe4d9f3ac1ba89c2d40bcc5830335eb5a7`.
The source retains the upstream copyright and BSD-3-Clause SPDX identifier;
the complete license is retained at `third_party/littlefs/LICENSE.md`.

This promotion required focused disassembly only to close the configuration,
entry topology, and link boundary. Both authenticated 84-byte G2
configuration objects disable `LFS_MULTIVERSION`; the exact upstream
wrappers therefore ignore `lfs_t *`. Complete dual-image scans find only
the retained `lfs_mount_` validation/diagnostic callers, with no non-linking
branch, stored pointer, or interior entry. Each emitted leaf has exactly one
ordered `R_ARM_THM_CALL` at function offset `+0x02` to the already
source-owned `lfs_fs_disk_version` provider.

| Image/leaf | Relocated span | Call site and target | Relocated SHA-256 |
|---|---|---|---|
| Apollo main major | `[0x007B01B8,0x007B01C2)` | `0x007B01BA -> 0x007AED1C` | `cffc852c2243f51e8a52543b4f2410b192e2365c25f161cfd12f69cae8544122` |
| Apollo main minor | `[0x007B01C4,0x007B01CE)` | `0x007B01C6 -> 0x007AED1C` | `e0494044bcf077ed5b67a33cf3eb526bb9b8b6f31dcfefb5ce347a197b100012` |
| bootloader major | `[0x00434592,0x0043459C)` | `0x00434594 -> 0x00434490` | `15251b134de5617995984b9d8140d6fb88dca904ef8ef72e480b99f3c0250b2a` |
| bootloader minor | `[0x0043459C,0x004345A6)` | `0x0043459E -> 0x00434490` | `685d7f3e70053272d9a3920aaf7867d0a84e8adb402bbccd4ef3afc76195b2b7` |

The raw major/minor section SHA-256 values are respectively
`ebb72edfdb508cbf5b617452eb60cbceb58bfdfc879dcece076544efa75c092f`
and
`da349b05b3a26d6a22ba3f707c4c21e1591915aeb8451e21f7509905926a4b9d`.
Apollo main inserts only the declared two-byte generated alignment interval
at `[0x007B01C2,0x007B01C4)`; the bootloader needs no relocated padding.
No upstream algorithm was decompiled or recreated.

That build and manifest used these historical pins:

- Apollo-main overlay: 114,346 bytes, SHA-256
  `bdc1e353d1adcb0075231afb6c423616dcc0da8335b4b430afe51763a0b9df20`;
- Apollo-main provider: 3,637,742 bytes, SHA-256
  `d69c4834f65b0661834f990da8167ca6989a1b1c97fda838edc488a4ed0b3e8e`;
- bootloader overlay: 302 bytes, SHA-256
  `e94e33658aca89d3830182bc6c17c656256a194262835c041fecc93e1d72dc59`;
- bootloader provider: 148,902 bytes, SHA-256
  `abc583d976a01e237ffa4ed29e4be1b6ff0e5ae2d9756bccec58d1779fe20239`;
- package: 4,415,876 bytes, SHA-256
  `60cd913a716266b349ce18295064f2484749a7dbad2ab9244c923c927bd56c2f`;
- boot/main CRC-32C/MSB: `0x12EAC8F8`/`0x7E9838B8`; and
- flash plan: 546,404 bytes, SHA-256
  `52124c17205ae10e47f0b02d0cd6bae7c2b30e10d65d787aa34201a53fe0dc68`.

The manifest contains 757 placed, two deliberately unresolved, five
container-only, and six protected regions. Package ownership is 114,860
source bytes (2.601069%), 81,523 generated bytes (1.846134%), and 4,219,493
opaque bytes (95.552796%), for 196,383 controlled bytes (4.447204%).
`./make.sh source` and core-source manifest verification pass.

## Recommended validation matrix

Each admitted tranche should add:

1. upstream tag/commit/tree/blob/license verification;
2. package, installed-image, stock-span, neighbor, and aggregate hashes;
3. complete `BL`, `B.W`, narrow, interior, and stored-pointer topology;
4. target object function sizes, symbol visibility, and relocation review;
5. compile-time target ABI assertions;
6. a pristine-upstream behavioral oracle plus G2-adaptation tests;
7. fixed-state and callback ordering tests;
8. fail-closed patch authentication and redirect decoding, or exact in-place
   byte comparison;
9. aggregate ownership, flash-layout, CRC, package, and headroom pins;
10. full project regression and three output-isolated reproducibility builds;
11. independent EVENOTA and offline flasher inspection; and
12. a documented hardware gate separate from structural flashability.

The CMSIS and upstream-translation-unit builds must prove garbage collection
retains only the reviewed closure. The FreeRTOS assembly build must prove
byte-exact in-place output. The allocator and storage libraries must prove
that all writable-state owners move atomically.

## Completed FreeRTOS V10.5.1 tick-query source reuse

The normal and ISR tick queries are unequivocal pristine-source reuse
targets. FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` supplies the MIT algorithms;
its pinned 223,695-byte `tasks.c` hashes to
`14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`.
The G2-specific adapter is deliberately limited to a source provider for the
recovered kernel state seam and two leaf getters. Its 3,412-byte source and
1,186-byte header hash to
`948d1b2de6026adc7cf84a34a359c859c32126b3afcafe92c2347f5f7ab56363`
and
`adc4065b3504a7eacb2e29e2d357636917e2b690afc49b265689e36d66171dae`.

Focused disassembly established the exact production boundary:

| Function | Official span | Bytes | Official SHA-256 |
|---|---|---:|---|
| `xTaskGetTickCount` | `[0x00454EFE,0x00454F06)` | 8 | `6dbb234e35fb86f883529c083fed0e1cabdca99d6647a95568ed1a5522310ac0` |
| `xTaskGetTickCountFromISR` | `[0x00454F06,0x00454F10)` | 10 | `8fe0a4f494b20b340d1126b2da725919f86c53cc3c1cabf5031fffc03f6de63a` |

The aggregate 18-byte stock SHA-256 is
`d0b93ff29439d26b92dcd56fd012a9dab842364f7c5f4b4f7f39a27ed8cfe077`.
`0x00454F08` is the ISR function's second instruction, not a function entry,
and has no direct or stored reference. The normal getter has nine direct
callers, whose ordered digest is
`3b032511b7c47b3afe47149262380345e354dea6d00f2b9dda369d10ce89abcd`;
the ISR getter has the sole caller `0x004490D6`.

Production places two generated alignment bytes at
`[0x007B07EA,0x007B07EC)`, the relocation-free source provider at
`[0x007B07EC,0x007B07F8)`, and four-byte normal and ISR leaves at
`[0x007B07F8,0x007B07FC)` and `[0x007B07FC,0x007B0800)`. The provider
binds `xTickCount` at `0x20074A34`; each getter has exactly one
`R_ARM_THM_JUMP24` relocation to it. Complete `B.W` redirects plus NOP fill
own the full stock spans.

The resulting 115,932-byte overlay hashes to
`272ba0e0492b0c6b721adec53a007809158d6871ccdb7ec52d4b6ceadd4b4529`;
the 3,639,328-byte main component hashes to
`615304858150f5ee6b7b4c62a714629375010c6f4ab20bea1b6958daa6a5b4af`
and accounts for 116,114 source-owned bytes including 182 in place, 81,626
generated patch-site bytes, 81,808 replaced-stock bytes, 3,441,556 opaque
base bytes, and the 32-byte wrapper. The manifest's raw installed-application
partition is 116,118 source, 81,622 generated, and 3,441,556 opaque bytes.

The 4,417,782-byte package hashes to
`3bf635fb81439451e67642dc5ce11dde47a1773bda8ef11c12b35cd9bbbec01d`.
It contains 116,738 source bytes (2.642457%), 83,415 generated bytes
(1.888165%), and 4,217,629 opaque bytes (95.469378%); 200,153 bytes
(4.530622%) are controlled. Its 596,957-byte flash plan hashes to
`2b89447a0a867d1ec34f51e5798a4da7b28effe8bc5d7e27b1b7f24ce1c9cd3c`,
with 828 placed, two unresolved, five container-only, and six protected
regions. The placed inventory includes 53 source-compiled regions, 574
generated source-entry replacements, and 18 generated alignments.

This source reuse does not claim the Apollo STIMER increment path, tickless
idle, scheduler core, or full kernel state ownership. Those remain separately
bounded compatibility work.

## Completed FreeRTOS V10.5.1 missed-yield source reuse

`vTaskMissedYield` is another unequivocal pristine-source target.
FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` defines its complete behavior
as `xYieldPending = pdTRUE`. Focused disassembly adds only the G2 boundary:
the official ten-byte span is `[0x004555E6,0x004555F0)`, its SHA-256 is
`8cada1af8ad4973f2ad647d45c8a0ac9c56fdf2d8b270607844b7940eb7d5d2d`,
and `xYieldPending` is the word at `0x20074A44`. The complete direct caller
set is `0x00441FA2` and `0x00441FD8`; no alternate entry or stored pointer
exists.

The bounded 1,749-byte source and 1,055-byte header hash to
`1f7ec93d00e35dcc4cf156d4559924493e46f6cc89c30de1ed7e53442177013c`
and
`0008f68d1196ea92a33a8cfa7bee339733354ccf8d64b96279acf6a43a1a21af`.
Apple clang 21 and Homebrew clang 22.1.8 produce the same relocation-free
14-byte leaf, SHA-256
`2b028e0c4aa84ce41bfe4b4164a397ae4d5ba9f177900cefb3b71c5d5d339ba9`.
Canonical placement is `[0x007B0800,0x007B080E)`; Linux places it at
`[0x007B0F38,0x007B0F46)` after two alignment bytes.

The canonical overlay, component, and package are 115,946, 3,639,342, and
4,417,796 bytes, with SHA-256 values
`a24cd67ac1d308b8812c329a294f3f07cbe9db4bc815be3fe081ba0c2fd9008c`,
`f037745e9b85d16fc048ba2fedb282f7fc498a524a90b803b652556e286cf77d`,
and
`f06fdc7a1e9034e72321680b35fbd542b12dad06135e6f01f701d670dba676ae`.
The overlay contains 592 functions and 559 patch sites. Builder accounting
is 116,128 source-owned bytes including 182 in place, 81,636 generated patch
bytes, 81,818 replaced-stock bytes, and 3,441,546 opaque bytes.

Linux independently pins a 117,794-byte overlay, 3,641,190-byte component,
and 4,419,644-byte package. Aggregate Linux reproducibility currently
requires the reviewed checkout spelling
`/Users/kalani/Repo/SybilSightABCD`, because unrelated TLSF diagnostics embed
absolute `__FILE__`; the missed-yield leaf itself is byte-identical across
both reviewed toolchains. Complete evidence is in
[`freertos-missed-yield-source-boundary-audit.md`](freertos-missed-yield-source-boundary-audit.md).

## Preceding FreeRTOS event-item reset and mutex-held source reuse

The next two adjacent task leaves are also exact FreeRTOS-Kernel V10.5.1
source reuse from commit
`def7d2df2b0506d3d249334974f51e427c17a41c`:

| Function | Official span | Bytes | Official SHA-256 | Direct caller |
|---|---|---:|---|---|
| `uxTaskResetEventItemValue` | `[0x00455ACA,0x00455AE0)` | 22 | `76463ec53fbc06884c159bf5b7d01708c06e404e9b51bdcaab307b219179c049` | `0x0047ECCE` |
| `pvTaskIncrementMutexHeldCount` | `[0x00455AE0,0x00455AF6)` | 22 | `3cca7b821687976e59eccd737dc20b2064b86d66195c6f60f6a7cc2353f40d2f` | `0x00441D46` |

Focused disassembly supplies only the G2 ABI seams. Both leaves preserve
volatile evaluations through `pxCurrentTCB=0x20074A20`.
`uxTaskResetEventItemValue` binds event-list item value offset `+0x18`,
priority offset `+0x2C`, and `configMAX_PRIORITIES=56`.
`pvTaskIncrementMutexHeldCount` binds held-mutex offset `+0x64` under
`configUSE_MUTEXES=1`.

Apple clang 21 emits a relocation-free 26-byte reset leaf at
`[0x007B0810,0x007B082A)`, SHA-256
`04fee613f7c2fb46a3e6f5832f7ea61875543a30160757ffd63579b58f0c45c6`,
and a relocation-free 24-byte mutex-held leaf at
`[0x007B082C,0x007B0844)`, SHA-256
`494b41afb48389988e2678920ae7e1796b41a3d568e5c01c35c12c48bf7b57bf`.
Two generated alignment bytes precede each leaf.

The combined canonical overlay, component, and package are 116,000,
3,639,396, and 4,417,850 bytes, with SHA-256 values
`203b31ea09e03c919da51b4d194cab2c3325ad5d5eed3efc7464018af90e2059`,
`78375130a88e6ec0d14bc936b8f16f4535056344288419baba83d81fd4f3bdc3`,
and
`9ffe927fdb587db9fae07043d7dc0938d2519c95d29e71cd0dca021cadf31d85`.
The overlay contains 594 functions and 561 patch sites. Builder accounting
is 116,182 source-owned bytes including 182 in place, 81,680 generated patch
bytes, 81,862 replaced-stock bytes, and 3,441,502 opaque bytes.

The package contains 116,802 source, 83,473 generated, and 4,217,575 opaque
bytes; 200,275 bytes are controlled. Its 604,237-byte flash plan hashes to
`c25b80e357274ee25903c74d6472cb0a3ab30d6f5d702a053b88c145e3ddd521`
and records 838 placed, two unresolved, and five container-only regions.

Linux places the leaves at `[0x007B0F48,0x007B0F62)` and
`[0x007B0F64,0x007B0F7C)`. Its overlay, component, and package are 117,848,
3,641,244, and 4,419,698 bytes, with SHA-256 values
`12e592da338cbcf99ee81ec3551ff5ae22410f34387ba35dcbdfbf38294f8cc9`,
`a81f7ca5c4219f9f31820a9f3e18aa6f5bb85004b7bedc9f25f9083dbdfd14e6`,
and
`e86eb0003e5b9f7f15c416ab9485e3457ce2082b17720d85ef59b6f198efe4b2`.
Aggregate reproduction retains the reviewed source-root spelling
`/Users/kalani/Repo/SybilSightABCD`. Complete evidence is in
[`freertos-reset-event-item-value-source-boundary-audit.md`](freertos-reset-event-item-value-source-boundary-audit.md)
and
[`freertos-mutex-held-source-boundary-audit.md`](freertos-mutex-held-source-boundary-audit.md).

## Completed FreeRTOS scheduler-suspend and timeout-state source reuse

The production Apollo-main graph now also reuses authenticated
FreeRTOS-Kernel V10.5.1 `vTaskSuspendAll` and
`vTaskInternalSetTimeOutState` from commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. These are upstream source
ports, not clean-room decompilations; focused disassembly is limited to G2
configuration and ABI recovery.

| Function | Official span | Bytes | Official SHA-256 | G2 seam |
|---|---|---:|---|---|
| `vTaskSuspendAll` | `[0x00454D7C,0x00454D88)` | 12 | `3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2` | `uxSchedulerSuspended=0x20074A58`, 32-bit wrapping increment and barrier order |
| `vTaskInternalSetTimeOutState` | `[0x00455556,0x00455566)` | 16 | `6ff12b123d1647953300d002a439daf4df52f96e369eebbb0b183a1a4fb3e862` | `xNumOfOverflows=0x20074A48`, `xTickCount=0x20074A34`, 8-byte `TimeOut_t` with fields at `+0`/`+4` |

The timeout source preserves the released overflow-read/store then
tick-read/store ordering. Its exact four direct callers are `0x00441886`,
`0x00441B90`, `0x00441CBC`, and `0x004555D0`, with no alternate entry or
stored pointer. Both reviewed compilers emit the same relocation-free
18-byte timeout leaf, SHA-256
`8319202babe42ee571774682793c4c4c1a54c3a72826a92ba5c60273ba451c6a`.

Apple clang 21 places the 16-byte suspend leaf at
`[0x007B0844,0x007B0854)` and the timeout leaf immediately after it at
`[0x007B0854,0x007B0866)`. Homebrew clang 22.1.8 places their byte-identical
bodies at `[0x007B0F7C,0x007B0F8C)` and
`[0x007B0F8C,0x007B0F9E)`.

| Profile / artifact | Bytes | SHA-256 |
|---|---:|---|
| canonical overlay | 116,034 | `d0b36ab3661f3b3487e3962bfe58d9f588f6a6f1ea14e1d9389f7e45d98094bd` |
| canonical Apollo-main component | 3,639,430 | `8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc` |
| canonical core-source package | 4,417,884 | `e3b7f29a19a4b3c19a14377a8ea8a77d14458a48678955d406ef7eea274dd6e7` |
| Linux overlay | 117,882 | `5c3c381342bb57ec4f33192ea89c2d40e8f0018c39c7092551243be7159dc326` |
| Linux Apollo-main component | 3,641,278 | `6bead197d657c26fa6ba84210949c8e28b266fbf63a8f908edda1d64516a3163` |
| Linux core-source package | 4,419,732 | `a801d1ecbf83780701cbb7fdc1ae14401a656ba79102877458a3a88c73bc3fc4` |

The combined overlay contains 596 functions and 563 patch sites. Main
builder accounting is 116,216 source-owned bytes including 182 in place,
81,708 generated patch bytes, 81,890 replaced-stock bytes, and 3,441,474
opaque bytes. The package contains 116,836 source, 83,501 generated, and
4,217,547 opaque bytes; 200,337 bytes are controlled. Its 608,608-byte flash
plan hashes to
`c6cde87716d8ff407e06998aadaaa0da6e78e5689ea1ac2963f104178447cae2`
and records 844 placed, two unresolved, and five container-only regions.

Aggregate Linux reproduction retains the reviewed source-root spelling
`/Users/kalani/Repo/SybilSightABCD` because unrelated TLSF diagnostics embed
absolute `__FILE__`. The complete timeout proof is in
[`freertos-timeout-state-source-boundary-audit.md`](freertos-timeout-state-source-boundary-audit.md).

## Hardware caveat

All findings in this report are offline. No serial endpoint, SWD debugger,
flashing interface, signing service, or physical G2 hardware was used.

Source provenance, deterministic compilation, closed topology, valid package
checksums, and offline flasher acceptance establish structural readiness
only. They do not establish successful boot, display behavior, storage
durability, power-loss safety, interrupt latency, or rollback on physical
hardware.

The Apollo-main update remains experimentally high risk because no autonomous
single-slot rollback has been proven. littlefs and FlashDB write-capable
integration remains prohibited until read-only captures and disposable-copy
tests pass. Physical installation and behavioral validation require a
separate, explicitly authorized hardware plan.

## Prior completed FreeRTOS queue/task closure reuse

The production graph now reuses authenticated FreeRTOS-Kernel V10.5.1
`xTaskRemoveFromEventList`, `xQueueGiveFromISR`, and
`prvTaskCheckFreeStackSpace`. Their maintained source implementations replace
468 complete stock bytes and add 490 compiled bytes plus two alignment bytes.
Focused disassembly supplies only the G2-specific ABI, topology, structure,
global-address, and stack-configuration parameters; the algorithms and MIT
license come from upstream commit
`def7d2df2b0506d3d249334974f51e427c17a41c`.

The canonical overlay/component/package are 119,066 / 3,642,462 / 4,420,916
bytes. The qualified Linux artifacts are 120,942 / 3,644,338 / 4,422,792
bytes. The exact-root Linux profile reproduced the full package in two normal
fail-closed builds. Source reuse and package assembly were validated offline;
no firmware was signed, flashed, reset, or executed on hardware.

## Current completed FreeRTOS timeout-check reuse

The production graph now also reuses authenticated FreeRTOS-Kernel V10.5.1
`xTaskCheckForTimeOut` from commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. This is an upstream MIT source
adaptation with focused G2 configuration recovery, not a re-created private
algorithm. The admitted source is 3,506 bytes with SHA-256
`d0d84996ae7ab897cf53655962e86574577b98bf367df52c9ae8ac076a8dc89e`.

The complete 128-byte stock span `[0x00455566,0x004555E6)` is redirected to
a four-byte-aligned, relocation-free 136-byte source leaf. Apple places it at
`[0x007B1440,0x007B14C8)` with SHA-256
`33f0782fa8af468bccf78b558cc010a9f7a89f30c7c76abced9a799feb6a93f5`;
Linux places it at `[0x007B1B94,0x007B1C1C)` with SHA-256
`486515dfdbdb1e175321445df167dca27357f270421b2d00492268e8da7c815c`.
Two generated alignment bytes precede each leaf.

The canonical overlay/component/package are 119,204 / 3,642,600 /
4,421,054 bytes and the Linux equivalents are 121,080 / 3,644,476 /
4,422,930 bytes. Package SHA-256 values are
`4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37`
and
`22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab`.
The canonical manifest contains 821 main regions and 884 whole-package
regions, with 877 placed, two unresolved, and five container-only. All
source reuse, compilation, package assembly, and verification remained
offline; no device was connected or operated.

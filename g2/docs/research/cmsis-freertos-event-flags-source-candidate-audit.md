# CMSIS-FreeRTOS event-flags source-candidate audit

Status: production-integrated and dual-toolchain replayed  
Target: official G2 `s200_v2.2.6.10` Apollo-main application  
Scope: `osEventFlagsNew`, `osEventFlagsSet`, `osEventFlagsClear`, and
`osEventFlagsWait`

## Result

The complete linked event-flags family is source-owned over existing FreeRTOS
event-group providers:

| Wrapper | Stock span | Bytes | SHA-256 | External callers |
|---|---|---:|---|---:|
| `osEventFlagsNew` | `[0x00449590,0x004495E4)` | 84 | `6dfae64ebf472c51d4105d50434acfccd26b723a6d6da790eee981a529f4ed83` | 3 |
| `osEventFlagsSet` | `[0x004495E4,0x00449642)` | 94 | `11de6c596381befd11300bd6383f97b334847c3eafc74a7392bfe956629acce7` | 24 |
| `osEventFlagsClear` | `[0x00449642,0x00449694)` | 82 | `40de3905b1832d076c51eed224d82c791e472d36de1ec4307b57cd518e54e647` | 7 |
| `osEventFlagsWait` | `[0x0044969C,0x0044971C)` | 128 | `55efe563c27f16d40c0488e9a86351c934313b894a1428c89ddde96194ea8a08` | 4 |

Together they cover 388 stock bytes and 38 external call sites. The selected
oracle is Arm CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`; its exact `cmsis_os2.c` blob was
first introduced by `13acfbef7be85119fc6bc56832c455d4547d92c7`.

## Dependency and behavior closure

- `New` preserves the 32-byte `StaticEventGroup_t` threshold, invalid mixed
  memory rejection, dynamic/static selection, and ISR rejection.
- `Set` and `Clear` preserve the 24-bit flag mask, task/ISR provider split,
  ISR command-queue failure mapping, returned pre/post-operation bits, and
  PendSV behavior. Clear forces a yield after successful ISR submission.
- `Wait` preserves `WaitAll`/`NoClear`, task timeout/resource mapping, and the
  distinct zero/nonzero ISR errors used by this release.

Every fixed callee is already source-owned: private `IRQ_Context`, both event
group constructors, task and ISR set/clear, ISR bit retrieval, and wait. No TCB
field, WSF hook, opaque queue receive, or callback-record layout is introduced.

## Qualification and production pins

The source and host fixture are pinned at 6,667 bytes / SHA-256
`7b1aedf76715b46870aea818eb1391221dfae5f290d09af32fa038297c4c7c03`
and 3,220 bytes / SHA-256
`83f80921c5f55b6a17e408d6360adad7cfaa494ec4d2ca54d98089b636e28caf`.
Host tests cover constructor selection, validation, task/ISR set and clear,
PendSV, wait options, timeout/resource mapping, and both ISR wait errors.

| Toolchain | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple clang 21 | `132556` / `6f9179762e490de0b52edaa9614900a3f3fd64304431ca7f89fa1f46d11866f9` | `3655952` / `758df9fe9099227c581e93c3186d72a3592e608bffe7036b52799464af2184eb` | `4434446` / `83cbeefbc9e10fae4c8ed0c7bc934356fc7b93e9e06149a9357a5c74410c7778` |
| Homebrew clang 22.1.8 | `134424` / `13f18ac6920db4f508f3b10e88d6d27f6e5bc4fc15544bc8f20737f3e37d1378` | `3657820` / `86838ca2e62199132e0510eb6df73ef59de4af8ceaec6b09e3c60466f6725c27` | `4436314` / `626142e8553c80f40a25fd28af35eca5064d281ae78194e5c70c900bdd57ae93` |

Both profiles were recorded once and replayed through ordinary fail-closed
component and package builds. No signing, flashing, reset, boot, or hardware
operation was performed.

## Reproduction

```sh
make -C openCFW cmsis-freertos-event-flags
```

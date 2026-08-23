# FreeRTOS Apollo `xPortStartScheduler` source-candidate audit

Status: production-routed authenticated MIT source adaptation; offline and
dual-profile complete; hardware timer/transfer validation blocked by
unavailable physical evidence

## Result

The complete stock `xPortStartScheduler` at
`[0x004421E2,0x00442210)` is 46 bytes with SHA-256
`66bacaafa2fa8e76a548eb9da62c2d3e1f058a471efe0bdfa072f59bf38ae1c0`.
Its control flow exactly follows FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c`, selected
`portable/IAR/ARM_CM55_NTZ/non_secure/port.c`, with the G2 timer setup kept as
an explicit Apollo seam.

## Recovered contract

The function performs two distinct volatile read/OR/write operations on
System Handler Priority Register 3 at `0xE000ED20`, setting PendSV bits
`0x00FF0000` and SysTick bits `0xFF000000` while preserving unrelated bits.
It then:

1. calls G2 `vPortSetupTimerInterrupt` at `0x0045643E`;
2. clears global `ulCriticalNesting` at `0x2000309C`;
3. calls the authenticated first-task assembly entry at `0x005FA08C`;
4. retains the nominally unreachable `vTaskSwitchContext` call at
   `0x004551B4` and `prvTaskExitError` call at `0x0044207C`; and
5. returns zero if the first-task entry unexpectedly returns.

The only direct caller is `vTaskStartScheduler` at `0x00454D5A`. Whole-image
scans find no stored entry/interior word and all four outgoing calls are
exactly pinned.

## Qualification

The host oracle proves both volatile priority updates, preservation of lower
bits, timer-before-nesting ordering, zero critical depth before first-task
entry, and the two unreachable-tail calls. The target test authenticates the
stock span/topology, fixed register/global literals, upstream source tokens,
and FreeRTOS commit.

Apple and Linux emit the same 58-byte function (SHA-256
`c02d239a4f345d45184ae3f9720abd43d28fff09c6b8ae5e51db75940cf51a88`)
and the same eight relocations. Apple object size/hash is 1,476 /
`e25055c8d089f9fadd723fc6602e2903b6732d205b72aec529fb190d52fcc52c`;
Linux is 1,456 /
`57a7bc93f879c18de6de0864ef866181ad440ec71d4802653cae8449e13150a7`.

## Production boundary

The 46-byte stock entry now redirects to the source-owned 58-byte leaf in both
profiles. It is admitted atomically with source-owned `vTaskStartScheduler`,
`vTaskSwitchContext`, and the scheduler-start fail-stop. Strict relocations
bind SHPR3, `ulCriticalNesting`, retained timer/first-task/exit providers, and
the overlay-local switch-context leaf. Manifest regions and both package
profiles account for the redirect and appended text.

Real STIMER interrupt latency and first-task context transfer are still a
hardware-dependent evidence tail. No authorized G2 or probe was present in the
2026-08-22 audit, so that tail is explicitly blocked.

Verification:

```sh
make freertos-scheduler-start-core-closure
```

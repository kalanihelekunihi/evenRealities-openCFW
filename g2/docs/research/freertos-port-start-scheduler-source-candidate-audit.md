# FreeRTOS Apollo `xPortStartScheduler` source-candidate audit

Status: authenticated MIT source adaptation; production-excluded pending
STIMER and boot-critical port integration

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
and the same eight relocations. Apple object size/hash is 1,484 /
`a7accfc2d0e6f3b92c7705cd61e7a233f45a5e35c091f9764841ddd03c64e790`;
Linux is 1,464 /
`2fb45e4c57f9fedbdbfb15813a891c2ecca7c256b0f387c39988785ad6304cf7`.

## Production boundary

This closes semantic opacity in the V10.5.1 scheduler-port start function but
does not redirect it. The first-task context transfer is already separately
authenticated. A companion candidate now closes the G2 Apollo STIMER setup;
companion candidates now close the elapsed-tick/compare-A ISR dispatcher and
tickless-idle path while retaining the power hooks explicitly. Production
admission of this function should remain atomic with `vTaskStartScheduler`
and hardware timer/sleep validation.

Verification:

```sh
python3 -m unittest -v tests.test_runtime_freertos_port_start_scheduler
```

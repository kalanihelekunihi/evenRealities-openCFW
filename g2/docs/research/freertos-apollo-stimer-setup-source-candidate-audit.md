# FreeRTOS Apollo STIMER setup source-candidate audit

Status: production-excluded G2 clean-room candidate with authenticated
AmbiqSuite constants; hardware timer validation remains mandatory

## Result

The complete G2 `vPortSetupTimerInterrupt` override at
`[0x0045643E,0x00456496)` is 88 bytes with SHA-256
`5a54cfc80b658ae5b645ac53b60f0e3098f0fd24fd4b5bedcfb0f822007b30ae`.
Its FreeRTOS-facing role is downstream G2 port code, while the register/API
constants are corroborated by authenticated AmbiqSuite Apollo510 5.1.0 commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`.

## Recovered contract

The function selects 32 STIMER counts per kernel tick. With the 32.768-kHz
XTAL clock this is exactly 1,024 Hz. It computes maximum suppressed ticks as
`(UINT32_MAX / 32) - 4 = 0x07FFFFFB`, where four is Ambiq's minimum safe
compare delta. It then performs the exact sequence:

1. enable STIMER compare-A interrupt bit `1`;
2. set external IRQ 32 priority with raw argument `255`;
3. enable external IRQ 32;
4. call `am_hal_stimer_config(0x80000000)` to clear and capture prior config;
5. capture the wrapping counter in `0x20074884`;
6. program compare A (`index 0`) at delta 32;
7. clear the saved clear/clock bits with `0x7FFFFFF0`; and
8. select compare-A enable plus XTAL 32 kHz with `0x103` and restore config.

The other two globals are counts-per-tick at `0x20074888` and maximum
suppressed ticks at `0x2007488C`. The only caller is authenticated
`xPortStartScheduler` at `0x004421F6`; all seven outgoing calls and the absence
of stored entry/interior words are pinned.

## Qualification

The host oracle verifies exact call/argument ordering, all three globals,
counter capture, compare index/delta, arithmetic, and four representative
saved-configuration masks. The focused target test authenticates the stock
span/topology/literals, the AmbiqSuite macro names and commit, both compiler
objects, the identical 110-byte function, all 13 relocations, and every
undefined seam.

Apple object size/hash is 1,780 /
`ff492566a9d8c4ad3fc5c37db5f767c9fd1642c339834803221cac0155d25050`;
Linux is 1,760 /
`e72114eadafc5f007650123154fd3d5e72590a375d0a5a129cecd82e91d7c545`.

## Boundary

This closes local opacity in scheduler timer setup without claiming it came
from pristine FreeRTOS or Ambiq source. Production remains unchanged. The
elapsed-tick/compare-A ISR dispatcher and tickless-idle path are now closed by
companion dual-profile candidates. Their first-party power hooks remain
explicit, and the combined timer closure still needs hardware timing/sleep
validation.

Verification:

```sh
python3 -m unittest -v tests.test_runtime_freertos_apollo_stimer_setup_candidate
```

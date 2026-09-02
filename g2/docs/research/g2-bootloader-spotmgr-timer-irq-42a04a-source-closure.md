# G2 bootloader SPOT-manager timer interrupt source closure

Date: 2026-09-01

## Result

The corrected timer-service extent is `[0x0042A04A,0x0042A078)`, 46 bytes;
the prior boundary at `0x0042A074` incorrectly excluded `msr primask` and the
terminal pop. `runtime_spotmgr_timer_irq_service_42a04a.c` is BSD-3-Clause
production C grounded in Ambiq's Apollo510 boost-timer service.

Both reviewed profiles reproduce the exact body after four strict call
relocations to `0x0041B8EC`, `0x00428378`, `0x00428A94`, and `0x0041CCD6`.
The linked SHA-256 is
`2ce0019a9c986275a9d5c9ea8d04c05e055c163e2802417c4ee68be2fd2b7fd4`;
the unrelocated SHA-256 is
`fbeda6f0cc785f369e1ecc2da2a580a954b3c705058d8f32c3137dd609ae7e79`.
The stored entry pointer is at `0x0041D160`; all 24 direct call sites and the
shared ongoing-sequence literal are authenticated.

The portable form passes 100,000 randomized states, including critical-token
save/restore, sequence-2b/7b dispatch, and unconditional timer finalization.

Interrupt delivery, preemption, MMIO ordering, timer expiry, rail behavior,
reset, and cold-boot qualification are **blocked by unavailable physical
evidence**. No hardware operation or firmware-wide completeness claim
occurred.

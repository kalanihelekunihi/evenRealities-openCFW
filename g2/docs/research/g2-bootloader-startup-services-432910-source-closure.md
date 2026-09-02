# G2 bootloader Cortex-M startup services source closure

Date: 2026-09-01

Four startup services at `0x00432910`, `0x0043291A`, `0x0043293C`, and
`0x00432958` are MIT production C in `runtime_startup_services_432910.c`.
Their complete extents are 10, 16, 24, and 34 bytes. Both reviewed compilers
reproduce each body exactly after three strict internal call relocations.
All four Apollo-main analogues at `0x005E4228`, `0x005E4232`, `0x005E4254`,
and `0x005E4270` are byte-for-byte exact.

The services relocate VTOR to `0x00410000`, establish MSPLIM and PSPLIM,
initialize PSP before the runtime handoff, enable CP10/CP11 access, issue the
required DSB/ISB barriers, and initialize FPSCR to `0x02040000`. A portable
model verifies the complete state transition. The census corrects two prior
prefix-only boundaries and retains the external literals separately.

Actual exception entry, stack-limit faults, FPU execution, reset, and runtime
handoff are **blocked by unavailable physical evidence**. No MMIO, flashing,
reset, or completeness claim occurred.

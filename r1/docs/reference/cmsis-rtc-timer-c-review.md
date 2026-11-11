# CMSIS system timer on the R1 RTC1 backend

`r1/src/application/rtos/system_timer.c` provides osKernelGetSysTimerCount and
osKernelGetSysTimerFreq for the selected R1 FreeRTOS RTC1 configuration. The
manifest generates a copy of the pinned CMSIS-FreeRTOS frontend with only its
SysTick-specific timer pair removed. Other devices retain the upstream source.
There is one definition of each API in the R1 composition.

The old frontend assumed a SysTick sub-counter and reported configCPU_CLOCK_HZ,
leaving OS_Tick_GetCount/Interval unresolved. That assumption does not match the
selected 1024-Hz RTC1 kernel port. The new implementation reports 1024 Hz and
extends the RTC's 24-bit value using the kernel's 32-bit epoch:

```
count = kernel_ticks + ((rtc_counter - kernel_ticks) & 0x00ffffff)
```

The kernel snapshot and RTC read run with PRIMASK set; the previous PRIMASK is
restored exactly, including when BASEPRI was already nonzero. BASEPRI is not
changed by the timer provider. The actual kernel getter is reused. This avoids
counting pending RTC ticks twice when the interrupt handler catches up.

This is a platform C port, not stock entry-address identity. Its resolution is
one configured RTC tick (1/1024 second), not CPU-cycle resolution. The existing
RTC initialization and privileged FreeRTOS port are prerequisites. The kernel
must lag the free-running RTC by less than one full 24-bit wrap; multiple missed
wraps or independent counter reset are outside this extension rule. It adds no
clock ownership, initialization, persistent state or interrupt handler.

## Executed verification

`build/goal-r1-cmsis-rtc-timer-c/verify.py` passes 8944 calls:

- 7208 snapshot cases cover selected/random 32-bit kernel epochs, RTC lags,
  24-/32-bit wrap, autonomous counter advance during sampling, PRIMASK 0/1 and
  BASEPRI 0/32/64/128. The actual compiled kernel tick getter executes exactly
  once per count query with IRQs masked. Independent arithmetic checks the
  resulting extended counter and frequency; unchanged RTC/tick memory is checked
  when the test does not inject an autonomous advance.
- 288 scenarios execute the actual RTC1 handler twice each, for 576 invocations.
  System-timer queries before and after catch-up return the same timestamp;
  a later three-tick RTC advance produces the next expected timestamp. The real
  kernel tick getter and scheduler-state query execute. xTaskIncrementTick is a
  controlled mock that advances the shared native tick word and returns no
  context-switch request; scheduler lists/context switching are not tested.
- Final R4-R11, SP, PRIMASK and BASEPRI are preserved. RTC/SCB are mapped emulator
  registers and counter progression is supplied by the test. Physical clock,
  real IRQ entry/return and sleep/wake timing are not exercised.

Five compiled defects (wrong frequency, lost epoch, wrong wrap width, unprotected
snapshot and lost interrupt mask) are detected; a final clean run passes. Three
configuration changes (tick rate, LF clock and tick source) fail the intended
static assertions.

## Composition and scope

`build/sources-goal-r1-cmsis-rtc-timer-c/report.json`: 780/780 units compile,
698 application and 82 bootloader, with zero failures or duplicate strong
symbols. Application imports drop from 122 to 120, removing exactly the two
OS_Tick imports. The new provider uses only the existing xTaskGetTickCount.
The bootloader retains 22 linker imports before its strict layout link, which
still succeeds without undefined symbols.

All 154 remaining allocated sections of the CMSIS frontend have identical
bytes and allocated-section relocations. The prior common objects retain 776
identical hashes; two generated boot objects differ in debug-path metadata
with matching allocated bytes/relocations. The vector, kernel and RTC driver
implementations are unchanged. No source-plan qualification is added.

R1 validation passes (780 units, 578 source files, zero excluded units). Global
sources-check still fails on the existing unlisted G2 assembly file. Full
application linking, physical clocks/interrupts and complete firmware startup
remain unproved. No device or firmware was written.

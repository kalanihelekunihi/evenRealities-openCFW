# RTC1 app-timer counter dependency closure

`r1/src/application/rtos/app_timer_counter.c` supplies the two counter APIs
missing from the pinned FreeRTOS timer lifecycle provider. It reads the existing
RTC1 COUNTER and computes `(ticks_to - ticks_from) & 0x00ffffff`, retaining the
SDK header's RTC1/24-bit counter contract. It does not initialize, clear, start,
stop or reconfigure the peripheral and installs no interrupt handler or state.

This is an SDK-contract C port for the selected open firmware configuration.
It is not a recovered stock entry-address identity claim. The earlier dependency
note correctly withheld an unqualified kernel-tick alias; this adapter instead
reads the peripheral named by the pinned API and qualifies the actual unit route:

- The peer-manager consumer compiles with FREERTOS, so APP_TIMER_TICKS uses
  configTICK_RATE_HZ, currently 1024.
- The selected FreeRTOS RTC source uses NRF_RTC1, a 32768-Hz input and prescaler
  31, producing 1024 counter increments per second.
- The actual consumer's initial/max penalty and reward periods compile to
  4096, 65536 and 10240 ticks, all below one 24-bit wrap.

The provider has compile-time checks for this RTC backend, tick rate, input
clock/prescaler, one-second APP_TIMER_TICKS conversion and counter mask. It
requires the existing RTC initialization before meaningful elapsed-time use.
Like the SDK API, a wrapped difference does not distinguish multiple full wraps.

## Executed evidence

`build/goal-r1-app-timer-counter-c/verify.py` passes 2708 calls:

- 264 selected/random valid counter values and 1073 selected/random difference
  pairs match both an independent arithmetic expectation and the actual pinned
  SDK app_timer.c counter implementations. The SDK oracle is compiled separately
  without FREERTOS, linked only for its two counter functions, and is never
  linked into the product alongside the FreeRTOS timer lifecycle provider.
- The selected compiled `vPortSetupTimerInterrupt` executes and establishes
  prescaler 31 plus RTC clear/start tasks in mapped registers. Clock-request
  completion is modeled. Getter calls do not modify the RTC register page.
- The real compiled peer-manager `auth_status_tracker.c` executes across RTC
  rollover, two-peer staggered expiry, repeated authentication failures,
  capped penalties and reward decay. Its actual APP_TIMER_TICKS constants are
  checked through a probe compiled with the consumer profile. Timer lifecycle,
  address lookup and logging are modeled; memcpy/memcmp and counter APIs execute.
- Tests preserve the consumer's existing minimum-timeout scheduling during
  escalation; no new scheduling/error policy is substituted. The single-shot
  timer model consumes its pending timeout before invoking the real callback.
- SP, R4-R11 and interrupt masks are checked at calls. RTC/NVIC registers are
  ordinary emulator memory; hardware clock progression is supplied by the test.

Four compiled defects—wrong RTC instance, omitted wrap mask, reversed difference
and wrong tick units—are detected, followed by a passing baseline. Three altered
configuration probes (tick rate, LF clock and tick source) fail their intended
static assertions.

## Composition and limits

`build/sources-goal-r1-app-timer-counter-c/report.json` compiles 779/779 units
without failures or duplicate strong symbols: 697 application and 82 bootloader.
Application imports drop from 124 to 122, removing exactly app_timer_cnt_get and
app_timer_cnt_diff_compute. No imports or persistent state are added by the new
provider. All 776 unchanged prior object hashes match; two generated boot
objects differ only in debug-path metadata with matching allocated bytes and
relocations. The strict bootloader link still succeeds without undefined symbols.

R1 source validation passes (779 units, 577 source files, zero excluded units).
Global sources-check retains the existing unlisted G2 assembly file. No source
qualification or source-plan entry is added. Physical oscillator behavior, real
radio authorization/timer delivery, multiple-wrap scheduling delays and full
application linking remain unproved. No device was flashed.

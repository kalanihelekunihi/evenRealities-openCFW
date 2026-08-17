# Clock-production correlation

## Scope

Local wall-clock time production: how the ring keeps and advances Unix epoch time between
phone synchronizations, and how broken-down calendar time is derived for health/activity
bucketing.

## Stock evidence

- The stock application keeps time through the B210 platform `sys rtc` named-record layer
  (`unknown_rtc_device_provider_candidate`, 10 functions / 608 bytes, blocked): an nrfx RTC at
  8 Hz (prescaler 0xFFF), epoch accumulation with a signed int16 UTC offset applied in
  minutes ×60, a 256-entry named 88-byte alarm/calendar record table, and a snapshot that
  emits `epoch*1000 + tick` milliseconds. Instruction-level detail:
  [`../boundaries/unknown_rtc_device_provider_candidate-ATTRIBUTION-2026-08.md`](../boundaries/unknown_rtc_device_provider_candidate-ATTRIBUTION-2026-08.md).
- Calendar conversion beside toolchain `gmtime` (`0x000276C8`, attributed Arm toolchain
  runtime) exists as a private seconds↔Gregorian pair
  (`unknown_time_calendar_provider_candidate`, 16 functions, blocked). The 2026-08
  re-examination proved the seconds→tm direction behaviorally identical to the old-newlib
  `_mktm_r` idiom on the whole product domain, and the inverse converter's 1970–2029
  validating bound unique to this firmware:
  [`../boundaries/unknown_time_calendar_provider_candidate-ATTRIBUTION-2026-08.md`](../boundaries/unknown_time_calendar_provider_candidate-ATTRIBUTION-2026-08.md).
- The BLE time-set command (`0x05`) carries Unix epoch seconds plus a signed timezone-minutes
  field (`src/r1_dispatch.c`), so the phone performs the calendar→epoch conversion.

## OpenR1 replacement and source-built adoption

The product-owned monotonic clock remains independent of the RTC-device
hardware/backend family. The original route decision is recorded in
[`../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md`](../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md):

- `r1/include/openr1/r1_clock.h` / `r1/src/r1_clock.c` — portable, R1-owned epoch clock:
  phone-synchronized epoch + validated signed UTC offset (±720/840 minutes), wrap-safe tick
  arithmetic, saturation instead of epoch wrap, zero-clamped local time, and no reported time
  before first synchronization (never fabricated).
- `r1/platform/nrf52840/sdk/openr1_clock.c` — platform glue: adopts phone time-sets from the
  portable device state within one 1024-tick cadence, advances the epoch from the RTC-backed
  (tickless-idle-correct) FreeRTOS kernel tick, and exposes epoch, UTC-offset, and
  local-calendar access via toolchain `gmtime_r`.
- `r1/platform/nrf52840/zephyr/src/openr1_clock_zephyr.c` — the source-built
  target now uses the owner-authorized reconstructed
  `time_calendar_unix_to_broken_down` body for local-calendar queries. The
  health-database adapter uses the same exact converter to calculate local-day
  boundaries. Neither path binds the reconstructed hardware RTC/backend or
  exposes the validating inverse converter, because time arrives as epoch
  seconds from the phone.

## Tests

`test_clock_production` in `r1/tests/test_openr1.c` covers synchronization validation
(offset range, NULL), unsynchronized and zero-frequency refusal, partial-second behavior,
exact advance, tick-counter wraparound, epoch saturation, and local-offset clamping.

## Hardware gates

Physical RTC drift, tickless-idle accuracy, and phone-sync convergence require owned-hardware
validation; nothing here fabricates timestamps when unsynchronized.

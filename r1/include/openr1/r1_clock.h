#ifndef OPENR1_R1_CLOCK_H
#define OPENR1_R1_CLOCK_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

/*
 * R1-owned local time production.
 *
 * The stock firmware produced local time through the blocked B210 platform
 * `sys rtc` named-record layer and its private validating calendar converters
 * (family `unknown_rtc_device_provider_candidate` /
 * `unknown_time_calendar_provider_candidate`, both
 * `clean_room_reimplementation_owner_authorized`).  OpenR1 replaces the
 * hardware/backend portion of that layer with this small product-owned clock:
 * the phone synchronizes Unix epoch
 * seconds plus a signed UTC offset over BLE (command 0x05), and the platform
 * supplies a monotonic tick so the epoch keeps advancing between
 * synchronizations.  The source-built target delegates broken-down calendar
 * conversion to the separately reconstructed exact calendar family.
 *
 * The module is pure: no hardware access, no hidden globals, and wrap-safe
 * tick arithmetic.  A clock that has never been synchronized reports no time
 * rather than fabricating one.
 */

#define R1_CLOCK_UTC_OFFSET_MINUTES_MIN (-720)
#define R1_CLOCK_UTC_OFFSET_MINUTES_MAX (840)

typedef struct {
    uint32_t epoch_seconds;
    int16_t utc_offset_minutes;
    uint32_t reference_ticks;
    uint32_t tick_frequency_hz;
    bool synchronized;
} r1_clock;

void r1_clock_initialize(r1_clock *clock, uint32_t tick_frequency_hz);

/* Records a phone-synchronized epoch.  The offset must be a real UTC offset;
 * an out-of-range offset leaves the previous state untouched. */
r1_error r1_clock_synchronize(r1_clock *clock, uint32_t epoch_seconds,
                              int16_t utc_offset_minutes,
                              uint32_t reference_ticks);

/* Reports the current epoch.  Returns false when the clock is unsynchronized
 * or was initialized with a zero tick frequency.  Elapsed ticks use unsigned
 * wrap-safe subtraction, so a single tick-counter wraparound is handled. */
bool r1_clock_now(const r1_clock *clock, uint32_t now_ticks,
                  uint32_t *epoch_seconds);

/* Reports the current local epoch (UTC epoch plus the signed offset).  The
 * result is clamped to zero rather than wrapping below the epoch. */
bool r1_clock_local_now(const r1_clock *clock, uint32_t now_ticks,
                        uint32_t *local_seconds);

#endif

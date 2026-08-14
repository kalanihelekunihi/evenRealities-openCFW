#ifndef OPENR1_CLOCK_H
#define OPENR1_CLOCK_H

#include <stdbool.h>
#include <stdint.h>

#include "nrf.h"
#include "app_error.h"

/*
 * Platform clock glue: adopts the phone-synchronized epoch from the portable
 * device state into the R1-owned r1_clock, keeps it advancing from the
 * (RTC-backed, sleep-correct) FreeRTOS kernel tick, and exposes the current
 * epoch and local calendar to other platform modules.
 *
 * The Nordic nRF52 FreeRTOS port drives the kernel tick from RTC1 with
 * tickless idle, so xTaskGetTickCount() remains monotonic across sleep; no
 * additional nrfx_rtc instance is allocated.  This module contains no code
 * from the blocked stock `sys rtc` layer; see
 * docs/boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md.
 */

ret_code_t openr1_clock_initialize(void);

/* Adopts a phone-synchronized epoch.  Called when the portable device state
 * gains a new time-set; also polled by the worker so a direct state write is
 * picked up within one cadence. */
void openr1_clock_adopt_phone_time(uint32_t epoch_seconds,
                                   int16_t utc_offset_minutes);

/* Current synchronized epoch, or false when never synchronized. */
bool openr1_clock_epoch(uint32_t *epoch_seconds);

/* Current local broken-down time via the toolchain C library.  Returns false
 * when never synchronized.  `struct tm` is the toolchain's. */
struct tm;
bool openr1_clock_local_tm(struct tm *out);

#endif

/*
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded clean-room candidate for the G2 Apollo STIMER
 * tickless-idle override.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_APOLLO_TICKLESS_CANDIDATE_H
#define OPEN_CFW_RUNTIME_FREERTOS_APOLLO_TICKLESS_CANDIDATE_H

typedef unsigned int open_cfw_freertos_tickless_u32;
typedef int open_cfw_freertos_tickless_base_type;

extern volatile open_cfw_freertos_tickless_u32
    open_cfw_retained_freertos_stimer_last_compare;
extern volatile open_cfw_freertos_tickless_u32
    open_cfw_retained_freertos_stimer_counts_per_tick;
extern volatile open_cfw_freertos_tickless_u32
    open_cfw_retained_freertos_stimer_max_suppressed_ticks;

void open_cfw_freertos_apollo_suppress_ticks_and_sleep(
    open_cfw_freertos_tickless_u32 expected_idle_ticks
);

#endif

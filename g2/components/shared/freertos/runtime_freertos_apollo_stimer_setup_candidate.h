/*
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded clean-room candidate for the G2 Apollo STIMER tick
 * setup used by the authenticated FreeRTOS V10.5.1 port.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_APOLLO_STIMER_SETUP_CANDIDATE_H
#define OPEN_CFW_RUNTIME_FREERTOS_APOLLO_STIMER_SETUP_CANDIDATE_H

typedef unsigned int open_cfw_freertos_stimer_u32;

extern volatile open_cfw_freertos_stimer_u32
    open_cfw_retained_freertos_stimer_last_compare;
extern volatile open_cfw_freertos_stimer_u32
    open_cfw_retained_freertos_stimer_counts_per_tick;
extern volatile open_cfw_freertos_stimer_u32
    open_cfw_retained_freertos_stimer_max_suppressed_ticks;

void open_cfw_freertos_apollo_stimer_setup(void);

#endif

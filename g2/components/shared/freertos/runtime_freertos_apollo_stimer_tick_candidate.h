/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded clean-room candidate for the G2 Apollo STIMER elapsed
 * tick dispatcher and compare-A interrupt wrapper.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_APOLLO_STIMER_TICK_CANDIDATE_H
#define OPEN_CFW_RUNTIME_FREERTOS_APOLLO_STIMER_TICK_CANDIDATE_H

typedef unsigned int open_cfw_freertos_stimer_tick_u32;
typedef int open_cfw_freertos_stimer_tick_base_type;

extern volatile open_cfw_freertos_stimer_tick_u32
    open_cfw_retained_freertos_stimer_last_compare;
extern volatile open_cfw_freertos_stimer_tick_u32
    open_cfw_retained_freertos_stimer_counts_per_tick;
extern volatile open_cfw_freertos_stimer_tick_u32
    open_cfw_retained_freertos_interrupt_control_state;

void open_cfw_freertos_apollo_stimer_elapsed_ticks_dispatch(void);
void open_cfw_freertos_apollo_stimer_compare_a_interrupt(void);

#endif

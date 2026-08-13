/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room reconstruction of the G2 Apollo510 elapsed-tick dispatcher and
 * compare-A ISR at [0x004563B4,0x0045643E). Not a production input.
 */

#include "runtime_freertos_apollo_stimer_tick_candidate.h"

enum {
    OPEN_CFW_FREERTOS_STIMER_COMPARE_A = 0U,
    OPEN_CFW_FREERTOS_STIMER_COMPARE_A_INTERRUPT = 1U,
    OPEN_CFW_FREERTOS_STIMER_PENDSV_SET = 0x10000000U,
};

extern open_cfw_freertos_stimer_tick_u32
open_cfw_retained_freertos_stimer_counter_get(void);
extern void open_cfw_retained_freertos_stimer_compare_delta_set(
    open_cfw_freertos_stimer_tick_u32 compare,
    open_cfw_freertos_stimer_tick_u32 delta
);
extern open_cfw_freertos_stimer_tick_u32
open_cfw_retained_freertos_interrupt_mask_set(void);
extern void open_cfw_retained_freertos_interrupt_mask_clear(
    open_cfw_freertos_stimer_tick_u32 mask
);
extern open_cfw_freertos_stimer_tick_base_type
open_cfw_freertos_task_increment_tick(void);
extern open_cfw_freertos_stimer_tick_u32
open_cfw_retained_freertos_stimer_interrupt_status_get(
    open_cfw_freertos_stimer_tick_u32 enabled_only
);
extern void open_cfw_retained_freertos_stimer_interrupt_clear(
    open_cfw_freertos_stimer_tick_u32 interrupts
);

__attribute__((used, noinline))
void open_cfw_freertos_apollo_stimer_elapsed_ticks_dispatch(void)
{
    open_cfw_freertos_stimer_tick_u32 current =
        open_cfw_retained_freertos_stimer_counter_get();
    open_cfw_freertos_stimer_tick_u32 elapsed;
    open_cfw_freertos_stimer_tick_u32 elapsed_ticks;
    open_cfw_freertos_stimer_tick_u32 quotient;
    open_cfw_freertos_stimer_tick_u32 remainder;
    open_cfw_freertos_stimer_tick_base_type switch_required = 0;

    if (current < open_cfw_retained_freertos_stimer_last_compare) {
        elapsed = current +
            (0xFFFFFFFFU - open_cfw_retained_freertos_stimer_last_compare);
    } else {
        elapsed = current - open_cfw_retained_freertos_stimer_last_compare;
    }

    elapsed_ticks = elapsed /
        open_cfw_retained_freertos_stimer_counts_per_tick;
    quotient = elapsed /
        open_cfw_retained_freertos_stimer_counts_per_tick;
    remainder = elapsed -
        (open_cfw_retained_freertos_stimer_counts_per_tick * quotient);

    open_cfw_retained_freertos_stimer_last_compare = current - remainder;
    open_cfw_retained_freertos_stimer_compare_delta_set(
        OPEN_CFW_FREERTOS_STIMER_COMPARE_A,
        open_cfw_retained_freertos_stimer_counts_per_tick - remainder
    );

    (void)open_cfw_retained_freertos_interrupt_mask_set();
    while (elapsed_ticks != 0U) {
        elapsed_ticks--;
        if (open_cfw_freertos_task_increment_tick() != 0) {
            switch_required = 1;
        }
    }

    if (switch_required != 0) {
        open_cfw_retained_freertos_interrupt_control_state =
            OPEN_CFW_FREERTOS_STIMER_PENDSV_SET;
    }
    open_cfw_retained_freertos_interrupt_mask_clear(0U);
}

__attribute__((used, noinline))
void open_cfw_freertos_apollo_stimer_compare_a_interrupt(void)
{
    open_cfw_freertos_stimer_tick_u32 status =
        open_cfw_retained_freertos_stimer_interrupt_status_get(0U);

    if ((status & OPEN_CFW_FREERTOS_STIMER_COMPARE_A_INTERRUPT) != 0U) {
        open_cfw_retained_freertos_stimer_interrupt_clear(
            OPEN_CFW_FREERTOS_STIMER_COMPARE_A_INTERRUPT
        );
        open_cfw_freertos_apollo_stimer_elapsed_ticks_dispatch();
    }
}

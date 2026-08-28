/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the G2 Apollo510 tickless-idle override at
 * [0x00456498,0x0045655C). This candidate is not a production input.
 */

#include "runtime_freertos_apollo_tickless_candidate.h"

enum {
    OPEN_CFW_FREERTOS_TICKLESS_ABORT_SLEEP = 0,
    OPEN_CFW_FREERTOS_TICKLESS_COMPARE_A = 0U,
    OPEN_CFW_FREERTOS_TICKLESS_COMPARE_A_INTERRUPT = 1U,
    OPEN_CFW_FREERTOS_TICKLESS_STIMER_IRQ = 32U,
};

extern void open_cfw_retained_freertos_global_interrupt_disable(void);
extern void open_cfw_retained_freertos_global_interrupt_enable(void);
extern open_cfw_freertos_tickless_base_type
open_cfw_retained_freertos_confirm_sleep_mode_status(void);
extern open_cfw_freertos_tickless_u32
open_cfw_retained_freertos_stimer_counter_get(void);
extern void open_cfw_retained_freertos_stimer_compare_delta_set(
    open_cfw_freertos_tickless_u32 compare,
    open_cfw_freertos_tickless_u32 delta
);
extern open_cfw_freertos_tickless_u32
open_cfw_retained_freertos_pre_sleep_processing(
    open_cfw_freertos_tickless_u32 expected_idle_ticks
);
extern void open_cfw_retained_freertos_wait_for_interrupt(void);
extern void open_cfw_retained_freertos_post_sleep_processing(
    open_cfw_freertos_tickless_u32 expected_idle_ticks
);
extern void open_cfw_retained_freertos_stimer_interrupt_clear(
    open_cfw_freertos_tickless_u32 interrupts
);
extern void open_cfw_retained_freertos_nvic_pending_clear(
    open_cfw_freertos_tickless_u32 interrupt
);
extern void open_cfw_freertos_task_step_tick(
    open_cfw_freertos_tickless_u32 ticks
);

static open_cfw_freertos_tickless_u32
open_cfw_freertos_tickless_elapsed(
    open_cfw_freertos_tickless_u32 current
)
{
    if (current < open_cfw_retained_freertos_stimer_last_compare) {
        return current +
            (0xFFFFFFFFU - open_cfw_retained_freertos_stimer_last_compare);
    }
    return current - open_cfw_retained_freertos_stimer_last_compare;
}

__attribute__((used, noinline))
void open_cfw_freertos_apollo_suppress_ticks_and_sleep(
    open_cfw_freertos_tickless_u32 expected_idle_ticks
)
{
    open_cfw_freertos_tickless_u32 current;
    open_cfw_freertos_tickless_u32 elapsed;
    open_cfw_freertos_tickless_u32 complete_ticks;
    open_cfw_freertos_tickless_u32 quotient;
    open_cfw_freertos_tickless_u32 remainder;

    if (expected_idle_ticks >
        open_cfw_retained_freertos_stimer_max_suppressed_ticks) {
        expected_idle_ticks =
            open_cfw_retained_freertos_stimer_max_suppressed_ticks;
    }

    open_cfw_retained_freertos_global_interrupt_disable();
    if (open_cfw_retained_freertos_confirm_sleep_mode_status() ==
        OPEN_CFW_FREERTOS_TICKLESS_ABORT_SLEEP) {
        open_cfw_retained_freertos_global_interrupt_enable();
        return;
    }

    current = open_cfw_retained_freertos_stimer_counter_get();
    elapsed = open_cfw_freertos_tickless_elapsed(current);
    open_cfw_retained_freertos_stimer_compare_delta_set(
        OPEN_CFW_FREERTOS_TICKLESS_COMPARE_A,
        (expected_idle_ticks *
            open_cfw_retained_freertos_stimer_counts_per_tick) - elapsed
    );

    if (open_cfw_retained_freertos_pre_sleep_processing(
        expected_idle_ticks
    ) != 0U) {
        open_cfw_retained_freertos_wait_for_interrupt();
    }
    open_cfw_retained_freertos_post_sleep_processing(expected_idle_ticks);

    current = open_cfw_retained_freertos_stimer_counter_get();
    elapsed = open_cfw_freertos_tickless_elapsed(current);
    complete_ticks = elapsed /
        open_cfw_retained_freertos_stimer_counts_per_tick;
    quotient = elapsed /
        open_cfw_retained_freertos_stimer_counts_per_tick;
    remainder = elapsed -
        (open_cfw_retained_freertos_stimer_counts_per_tick * quotient);
    open_cfw_retained_freertos_stimer_last_compare = current - remainder;

    open_cfw_retained_freertos_stimer_interrupt_clear(
        OPEN_CFW_FREERTOS_TICKLESS_COMPARE_A_INTERRUPT
    );
    open_cfw_retained_freertos_nvic_pending_clear(
        OPEN_CFW_FREERTOS_TICKLESS_STIMER_IRQ
    );
    open_cfw_retained_freertos_stimer_compare_delta_set(
        OPEN_CFW_FREERTOS_TICKLESS_COMPARE_A,
        open_cfw_retained_freertos_stimer_counts_per_tick - remainder
    );

    if (complete_ticks > expected_idle_ticks) {
        complete_ticks = expected_idle_ticks;
    }
    open_cfw_freertos_task_step_tick(complete_ticks);
    open_cfw_retained_freertos_global_interrupt_enable();
}

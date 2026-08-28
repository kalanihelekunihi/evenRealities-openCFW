/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the G2 Apollo510 vPortSetupTimerInterrupt
 * override at [0x0045643E,0x00456496). This is not a production input.
 */

#include "runtime_freertos_apollo_stimer_setup_candidate.h"

enum {
    OPEN_CFW_FREERTOS_STIMER_COUNTS_PER_TICK = 32U,
    OPEN_CFW_FREERTOS_STIMER_MINIMUM_COMPARE_DELTA = 4U,
    OPEN_CFW_FREERTOS_STIMER_COMPARE_A_INTERRUPT = 1U,
    OPEN_CFW_FREERTOS_STIMER_IRQ = 32U,
    OPEN_CFW_FREERTOS_STIMER_IRQ_PRIORITY = 255U,
    OPEN_CFW_FREERTOS_STIMER_CONFIG_CLEAR = 0x80000000U,
    OPEN_CFW_FREERTOS_STIMER_CONFIG_PRESERVE_MASK = 0x7FFFFFF0U,
    OPEN_CFW_FREERTOS_STIMER_COMPARE_A_XTAL_32KHZ = 0x00000103U,
};

extern void open_cfw_retained_freertos_stimer_interrupt_enable(
    open_cfw_freertos_stimer_u32 interrupts
);
extern void open_cfw_retained_freertos_nvic_priority_set(
    open_cfw_freertos_stimer_u32 interrupt,
    open_cfw_freertos_stimer_u32 priority
);
extern void open_cfw_retained_freertos_nvic_enable(
    open_cfw_freertos_stimer_u32 interrupt
);
extern open_cfw_freertos_stimer_u32
open_cfw_retained_freertos_stimer_config(
    open_cfw_freertos_stimer_u32 configuration
);
extern open_cfw_freertos_stimer_u32
open_cfw_retained_freertos_stimer_counter_get(void);
extern void open_cfw_retained_freertos_stimer_compare_delta_set(
    open_cfw_freertos_stimer_u32 compare,
    open_cfw_freertos_stimer_u32 delta
);

__attribute__((used, noinline))
void open_cfw_freertos_apollo_stimer_setup(void)
{
    open_cfw_freertos_stimer_u32 saved_configuration;

    open_cfw_retained_freertos_stimer_counts_per_tick =
        OPEN_CFW_FREERTOS_STIMER_COUNTS_PER_TICK;
    open_cfw_retained_freertos_stimer_max_suppressed_ticks =
        (0xFFFFFFFFU / open_cfw_retained_freertos_stimer_counts_per_tick) -
        OPEN_CFW_FREERTOS_STIMER_MINIMUM_COMPARE_DELTA;

    open_cfw_retained_freertos_stimer_interrupt_enable(
        OPEN_CFW_FREERTOS_STIMER_COMPARE_A_INTERRUPT
    );
    open_cfw_retained_freertos_nvic_priority_set(
        OPEN_CFW_FREERTOS_STIMER_IRQ,
        OPEN_CFW_FREERTOS_STIMER_IRQ_PRIORITY
    );
    open_cfw_retained_freertos_nvic_enable(OPEN_CFW_FREERTOS_STIMER_IRQ);

    saved_configuration = open_cfw_retained_freertos_stimer_config(
        OPEN_CFW_FREERTOS_STIMER_CONFIG_CLEAR
    );
    open_cfw_retained_freertos_stimer_last_compare =
        open_cfw_retained_freertos_stimer_counter_get();
    open_cfw_retained_freertos_stimer_compare_delta_set(
        0U,
        open_cfw_retained_freertos_stimer_counts_per_tick
    );

    saved_configuration &=
        OPEN_CFW_FREERTOS_STIMER_CONFIG_PRESERVE_MASK;
    saved_configuration |=
        OPEN_CFW_FREERTOS_STIMER_COMPARE_A_XTAL_32KHZ;
    (void)open_cfw_retained_freertos_stimer_config(saved_configuration);
}

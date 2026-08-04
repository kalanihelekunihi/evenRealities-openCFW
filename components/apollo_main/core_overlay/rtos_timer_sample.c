/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS tick/list-switch sampler matched to stock entry 0x0047E916.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_sample_uintptr;

typedef unsigned int (*open_cfw_rtos_timer_sample_tick_function)(void);

void open_cfw_rtos_timer_switch_lists(void);

#ifndef OPEN_CFW_RTOS_TIMER_SAMPLE_TICK
#define OPEN_CFW_RTOS_TIMER_SAMPLE_TICK() \
    (((open_cfw_rtos_timer_sample_tick_function) \
        (open_cfw_rtos_timer_sample_uintptr)0x00454EFFU)())
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SAMPLE_READ_LAST_TICK
#define OPEN_CFW_RTOS_TIMER_SAMPLE_READ_LAST_TICK() \
    (*(volatile unsigned int *)( \
        open_cfw_rtos_timer_sample_uintptr)0x20074AB8U)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SAMPLE_WRITE_LAST_TICK
#define OPEN_CFW_RTOS_TIMER_SAMPLE_WRITE_LAST_TICK(value) \
    ((*(volatile unsigned int *)( \
        open_cfw_rtos_timer_sample_uintptr)0x20074AB8U) = (value))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SAMPLE_SWITCH_LISTS
#define OPEN_CFW_RTOS_TIMER_SAMPLE_SWITCH_LISTS() \
    open_cfw_rtos_timer_switch_lists()
#endif

__attribute__((used, noinline))
unsigned int open_cfw_rtos_timer_sample(unsigned int *lists_switched)
{
    unsigned int time_now = OPEN_CFW_RTOS_TIMER_SAMPLE_TICK();

    if (time_now < OPEN_CFW_RTOS_TIMER_SAMPLE_READ_LAST_TICK()) {
        OPEN_CFW_RTOS_TIMER_SAMPLE_SWITCH_LISTS();
        *lists_switched = 1U;
    } else {
        *lists_switched = 0U;
    }
    OPEN_CFW_RTOS_TIMER_SAMPLE_WRITE_LAST_TICK(time_now);
    return time_now;
}

#undef OPEN_CFW_RTOS_TIMER_SAMPLE_SWITCH_LISTS
#undef OPEN_CFW_RTOS_TIMER_SAMPLE_WRITE_LAST_TICK
#undef OPEN_CFW_RTOS_TIMER_SAMPLE_READ_LAST_TICK
#undef OPEN_CFW_RTOS_TIMER_SAMPLE_TICK

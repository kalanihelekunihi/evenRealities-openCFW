/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacements for the G2 2.2.6.10 LVGL tick increment, getter, and
 * wrap-safe elapsed-time helpers at 0x00473474...0x004734BB.
 */

typedef unsigned int (*open_cfw_lv_tick_callback)(void);

struct open_cfw_lv_tick_state {
    volatile unsigned int counter;
    volatile unsigned char stable;
    unsigned char reserved[3];
    open_cfw_lv_tick_callback volatile callback;
};

#ifndef OPEN_CFW_LV_TICK_STATE
#define OPEN_CFW_LV_TICK_STATE \
    ((struct open_cfw_lv_tick_state *)(void *)0x2006F600U)
#endif

__attribute__((used, noinline))
void open_cfw_lv_tick_increment(unsigned int milliseconds)
{
    struct open_cfw_lv_tick_state *state = OPEN_CFW_LV_TICK_STATE;

    state->stable = 0U;
    state->counter += milliseconds;
}

__attribute__((used, noinline))
unsigned int open_cfw_lv_tick_get(void)
{
    struct open_cfw_lv_tick_state *state = OPEN_CFW_LV_TICK_STATE;
    unsigned int value;

    if (state->callback != (open_cfw_lv_tick_callback)0) {
        return state->callback();
    }
#if defined(__clang__)
#pragma clang loop unroll(disable)
#endif
    do {
        state->stable = 1U;
        value = state->counter;
    } while (state->stable == 0U);
    return value;
}

__attribute__((used, noinline))
unsigned int open_cfw_lv_tick_elapsed(unsigned int previous)
{
    return open_cfw_lv_tick_get() - previous;
}

#undef OPEN_CFW_LV_TICK_STATE

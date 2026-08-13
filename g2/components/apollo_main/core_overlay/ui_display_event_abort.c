/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 Apollo event-side abort/reset
 * helper at 0x0058DFB2. Exact stock behavior is recorded in EVIDENCE.md.
 */

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_ABORT_CRITICAL_ENTER
static inline unsigned int open_cfw_ui_display_event_abort_critical_enter(void)
{
    unsigned int interrupt_mask;

    __asm__ volatile(
        "mrs %0, primask\n"
        "cpsid i"
        : "=r"(interrupt_mask)
        :
        : "memory"
    );
    return interrupt_mask;
}
#define OPEN_CFW_UI_DISPLAY_EVENT_ABORT_CRITICAL_ENTER() \
    open_cfw_ui_display_event_abort_critical_enter()
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_ABORT_CRITICAL_EXIT
static inline void open_cfw_ui_display_event_abort_critical_exit(
    unsigned int interrupt_mask
)
{
    __asm__ volatile(
        "msr primask, %0"
        :
        : "r"(interrupt_mask)
        : "memory"
    );
}
#define OPEN_CFW_UI_DISPLAY_EVENT_ABORT_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_ui_display_event_abort_critical_exit(interrupt_mask)
#endif

__attribute__((used, noinline))
unsigned int open_cfw_ui_display_event_abort(void *handle)
{
    volatile unsigned char *state = handle;
    unsigned int interrupt_mask;
    unsigned int index;
    unsigned int result;

    interrupt_mask = OPEN_CFW_UI_DISPLAY_EVENT_ABORT_CRITICAL_ENTER();
    if (state[0x11AU] == 1U) {
        state[0x11AU] = 0U;
        for (index = 0U; index < 14U; ++index) {
            *(volatile unsigned int *)(void *)(
                state + 0x64U + index * 4U
            ) = 0U;
        }
        *(volatile unsigned int *)(void *)(state + 0x9CU) = 0U;
        result = 0U;
    } else {
        result = 7U;
    }
    OPEN_CFW_UI_DISPLAY_EVENT_ABORT_CRITICAL_EXIT(interrupt_mask);
    return result;
}

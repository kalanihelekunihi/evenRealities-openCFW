/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 Apollo event-side display-operation
 * begin routine at 0x0058DF5C. The exact stock boundary, state layout, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_BEGIN_CRITICAL_ENTER
static inline unsigned int open_cfw_ui_display_event_begin_critical_enter(void)
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
#define OPEN_CFW_UI_DISPLAY_EVENT_BEGIN_CRITICAL_ENTER() \
    open_cfw_ui_display_event_begin_critical_enter()
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_BEGIN_CRITICAL_EXIT
static inline void open_cfw_ui_display_event_begin_critical_exit(
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
#define OPEN_CFW_UI_DISPLAY_EVENT_BEGIN_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_ui_display_event_begin_critical_exit(interrupt_mask)
#endif

#define OPEN_CFW_UI_DISPLAY_EVENT_BEGIN_BUSY_RESULT 0x08000005U

/*
 * Stock ABI at 0x0058DF5C. This is the receive/event-side counterpart to the
 * source-owned transmit begin routine at 0x0058DEF2.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_event_begin(
    void *handle,
    const void *descriptor
)
{
    volatile unsigned char *state = handle;
    const unsigned char *descriptor_bytes = descriptor;
    const unsigned int *descriptor_words = descriptor;
    unsigned int interrupt_mask;
    unsigned int index;
    unsigned int result;

    interrupt_mask = OPEN_CFW_UI_DISPLAY_EVENT_BEGIN_CRITICAL_ENTER();
    if (state[0x11AU] == 0U) {
        state[0x11AU] = 1U;
        state[0x98U] = descriptor_bytes[0x34U];
        for (index = 0U; index < 7U; ++index) {
            *(volatile unsigned int *)(void *)(
                state + 0x64U + index * 4U
            ) = descriptor_words[index];
        }
        *(volatile unsigned int *)(void *)(state + 0x9CU) = 0U;
        result = 0U;
    } else {
        result = OPEN_CFW_UI_DISPLAY_EVENT_BEGIN_BUSY_RESULT;
    }
    OPEN_CFW_UI_DISPLAY_EVENT_BEGIN_CRITICAL_EXIT(interrupt_mask);
    return result;
}

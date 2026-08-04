/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 Apollo lower-level display-operation
 * begin routine at 0x0058DEF2. The exact stock boundary, state layout, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_BEGIN_CRITICAL_ENTER
static inline unsigned int
open_cfw_ui_display_operation_begin_critical_enter(void)
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
#define OPEN_CFW_UI_DISPLAY_OPERATION_BEGIN_CRITICAL_ENTER() \
    open_cfw_ui_display_operation_begin_critical_enter()
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_BEGIN_CRITICAL_EXIT
static inline void open_cfw_ui_display_operation_begin_critical_exit(
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
#define OPEN_CFW_UI_DISPLAY_OPERATION_BEGIN_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_ui_display_operation_begin_critical_exit(interrupt_mask)
#endif

#define OPEN_CFW_UI_DISPLAY_OPERATION_BEGIN_BUSY_RESULT 0x08000004U

/*
 * Stock ABI at 0x0058DEF2. The descriptor pointer remains live in r1 at the
 * stock call site and is therefore an explicit second source-level argument.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_operation_begin(
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

    interrupt_mask =
        OPEN_CFW_UI_DISPLAY_OPERATION_BEGIN_CRITICAL_ENTER();
    if (state[0x119U] == 0U) {
        state[0x119U] = 1U;
        state[0xD4U] = descriptor_bytes[0x34U];
        for (index = 0U; index < 7U; ++index) {
            *(volatile unsigned int *)(void *)(
                state + 0xA0U + index * 4U
            ) = descriptor_words[index];
        }
        *(volatile unsigned int *)(void *)(state + 0xD8U) = 0U;
        state[0xDEU] = 0U;
        result = 0U;
    } else {
        result = OPEN_CFW_UI_DISPLAY_OPERATION_BEGIN_BUSY_RESULT;
    }
    OPEN_CFW_UI_DISPLAY_OPERATION_BEGIN_CRITICAL_EXIT(interrupt_mask);
    return result;
}

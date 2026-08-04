/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacements for the G2 2.2.6.10 Apollo display transport IRQ
 * special-transfer helpers at 0x0058DD30, 0x0058DD5C, 0x0058DD8A, and
 * 0x0058DFEE. Exact stock boundaries and behavior are recorded in
 * EVIDENCE.md.
 */

unsigned int open_cfw_ui_display_fifo_discard(void *handle);
unsigned int open_cfw_ui_display_event_abort(void *handle);

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_HELPER_INSTANCE
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_INSTANCE(handle) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0x28U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, offset) \
    (*(volatile unsigned int *)(void *)( \
        0x40039000U + (instance) * 0x1000U + (offset) \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_HELPER_CLOCK
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_CLOCK(handle) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0x30U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_HELPER_SPECIAL
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_SPECIAL(handle) \
    (((const volatile unsigned char *)(handle))[0x11BU])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_HELPER_DELAY
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_DELAY(ticks) \
    (((void (*)(unsigned int))0x004807A1U)(ticks))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_HELPER_FIFO_DISCARD
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_FIFO_DISCARD(handle) \
    ((void)open_cfw_ui_display_fifo_discard(handle))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_HELPER_EVENT_ABORT
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_EVENT_ABORT(handle) \
    ((void)open_cfw_ui_display_event_abort(handle))
#endif

__attribute__((used, noinline))
void open_cfw_ui_display_irq_finish(void *handle)
{
    unsigned int instance;

    instance = OPEN_CFW_UI_DISPLAY_IRQ_HELPER_INSTANCE(handle);
    OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x48U) = 0U;
    OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x04U) &=
        ~0x10U;
    OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x04U) &=
        ~0x20U;
}

__attribute__((used, noinline))
void open_cfw_ui_display_irq_bit12(void *handle)
{
    unsigned int instance;

    instance = OPEN_CFW_UI_DISPLAY_IRQ_HELPER_INSTANCE(handle);
    OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x48U) = 0U;
    OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x04U) &=
        ~0x20U;
    OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x50U) &=
        ~0x00000FFFU;
}

__attribute__((used, noinline))
unsigned int open_cfw_ui_display_irq_result(
    unsigned int instance,
    unsigned int status
)
{
    unsigned int observed;

    observed =
        status
        | OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x3CU);
    if ((observed & (1U << 6)) != 0U) {
        return 0x08000006U;
    }
    if ((observed & (1U << 7)) != 0U) {
        return 0x08000007U;
    }
    if ((observed & (1U << 8)) != 0U) {
        return 0x08000008U;
    }
    if ((observed & (1U << 9)) != 0U) {
        return 0x08000009U;
    }
    if ((observed & (1U << 10)) != 0U) {
        return 0x0800000AU;
    }
    if ((observed & (1U << 12)) != 0U) {
        return 0x0800000BU;
    }
    return 0U;
}

__attribute__((used, noinline))
void open_cfw_ui_display_irq_bit6(void *handle)
{
    unsigned int instance;
    unsigned int restore_bit14;

    instance = OPEN_CFW_UI_DISPLAY_IRQ_HELPER_INSTANCE(handle);
    restore_bit14 =
        (
            OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x30U)
            >> 14
        )
        & 1U;

    if (restore_bit14 != 0U) {
        OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x30U) &=
            ~0x4000U;
        OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x30U) &=
            ~0x0800U;
    }
    OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x30U) &=
        ~0x0200U;

    if (
        (
            OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x18U)
            & 0x08U
        )
            != 0U
    ) {
        OPEN_CFW_UI_DISPLAY_IRQ_HELPER_DELAY(
            0x00989680U
                / OPEN_CFW_UI_DISPLAY_IRQ_HELPER_CLOCK(handle)
                + 1U
        );
    }

    if (OPEN_CFW_UI_DISPLAY_IRQ_HELPER_SPECIAL(handle) != 0U) {
        open_cfw_ui_display_irq_bit12(handle);
    }
    OPEN_CFW_UI_DISPLAY_IRQ_HELPER_FIFO_DISCARD(handle);
    OPEN_CFW_UI_DISPLAY_IRQ_HELPER_EVENT_ABORT(handle);

    if (restore_bit14 != 0U) {
        OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x30U) |=
            0x4000U;
    }
    OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, 0x30U) |=
        0x0200U;
}

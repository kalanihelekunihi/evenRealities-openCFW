/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 Apollo display ring-drain helper at
 * 0x0058E3A0. The exact stock boundary, state layout, and behavioral evidence
 * are recorded in EVIDENCE.md.
 */

unsigned int open_cfw_ring_read(
    void *ring,
    void *destination,
    unsigned int count
);

unsigned int open_cfw_ui_display_direct_write(
    void *handle,
    const void *source,
    unsigned int count,
    unsigned int *written
);

#ifndef OPEN_CFW_UI_DISPLAY_RING_DRAIN_CRITICAL_ENTER
static inline unsigned int open_cfw_ui_display_ring_drain_critical_enter(void)
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
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_CRITICAL_ENTER() \
    open_cfw_ui_display_ring_drain_critical_enter()
#endif

#ifndef OPEN_CFW_UI_DISPLAY_RING_DRAIN_CRITICAL_EXIT
static inline void open_cfw_ui_display_ring_drain_critical_exit(
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
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_ui_display_ring_drain_critical_exit(interrupt_mask)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_RING_DRAIN_INSTANCE
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_INSTANCE(handle) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0x28U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_RING_DRAIN_FIFO_FULL
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_FIFO_FULL(instance) \
    ( \
        ( \
            *(const volatile unsigned int *)(const void *)( \
                0x40039018U + ((instance) << 12U) \
            ) \
            & (1U << 5U) \
        ) \
        != 0U \
    )
#endif

#ifndef OPEN_CFW_UI_DISPLAY_RING_DRAIN_RING
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_RING(handle) \
    ((void *)((unsigned char *)(handle) + 0x34U))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_RING_DRAIN_READ
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_READ(ring, destination, count) \
    (open_cfw_ring_read( \
        (ring), \
        (destination), \
        (count) \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_RING_DRAIN_DIRECT_WRITE
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_DIRECT_WRITE( \
    handle, \
    source, \
    count, \
    written \
) \
    (open_cfw_ui_display_direct_write( \
        (handle), \
        (source), \
        (count), \
        (written) \
    ))
#endif

/*
 * Stock ABI at 0x0058E3A0. Its sole caller ignores the return value, but the
 * routine propagates a nonzero direct-writer status after restoring PRIMASK.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_ring_drain(void *handle)
{
    unsigned int instance =
        OPEN_CFW_UI_DISPLAY_RING_DRAIN_INSTANCE(handle);
    unsigned int status = 0U;
    unsigned int written;
    unsigned int interrupt_mask;
    unsigned char value;

    interrupt_mask = OPEN_CFW_UI_DISPLAY_RING_DRAIN_CRITICAL_ENTER();
    while (!OPEN_CFW_UI_DISPLAY_RING_DRAIN_FIFO_FULL(instance)) {
        if (
            OPEN_CFW_UI_DISPLAY_RING_DRAIN_READ(
                OPEN_CFW_UI_DISPLAY_RING_DRAIN_RING(handle),
                &value,
                1U
            )
                == 0U
        ) {
            break;
        }
        status = OPEN_CFW_UI_DISPLAY_RING_DRAIN_DIRECT_WRITE(
            handle,
            &value,
            1U,
            &written
        );
        if (status != 0U) {
            break;
        }
    }
    OPEN_CFW_UI_DISPLAY_RING_DRAIN_CRITICAL_EXIT(interrupt_mask);
    return status;
}

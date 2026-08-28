/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 Apollo display FIFO-to-ring fill
 * helper at 0x0058E360. The exact stock boundary, sole caller, and behavioral
 * evidence are recorded in EVIDENCE.md.
 */

unsigned int open_cfw_ui_display_direct_read(
    void *handle,
    void *destination,
    unsigned int count,
    unsigned int *read_count
);

unsigned int open_cfw_ring_write(
    void *ring,
    const void *source,
    unsigned int count
);

#ifndef OPEN_CFW_UI_DISPLAY_RING_FILL_CRITICAL_ENTER
static inline unsigned int
open_cfw_ui_display_ring_fill_critical_enter(void)
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
#define OPEN_CFW_UI_DISPLAY_RING_FILL_CRITICAL_ENTER() \
    open_cfw_ui_display_ring_fill_critical_enter()
#endif

#ifndef OPEN_CFW_UI_DISPLAY_RING_FILL_CRITICAL_EXIT
static inline void open_cfw_ui_display_ring_fill_critical_exit(
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
#define OPEN_CFW_UI_DISPLAY_RING_FILL_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_ui_display_ring_fill_critical_exit(interrupt_mask)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_RING_FILL_READ
#define OPEN_CFW_UI_DISPLAY_RING_FILL_READ( \
    handle, \
    destination, \
    capacity, \
    read_count \
) \
    (open_cfw_ui_display_direct_read( \
        (handle), \
        (destination), \
        (capacity), \
        (read_count) \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_RING_FILL_RING
#define OPEN_CFW_UI_DISPLAY_RING_FILL_RING(handle) \
    ((void *)((unsigned char *)(handle) + 0x4CU))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_RING_FILL_WRITE
#define OPEN_CFW_UI_DISPLAY_RING_FILL_WRITE(ring, source, count) \
    (open_cfw_ring_write((ring), (source), (count)))
#endif

/*
 * Stock ABI at 0x0058E360. The lower FIFO reader owns read_count on every
 * result path. A zero ring-write result maps to the stock ring-full status.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_ring_fill(void *handle)
{
    unsigned char buffer[32];
    unsigned int read_count;
    unsigned int interrupt_mask;
    unsigned int result;

    interrupt_mask = OPEN_CFW_UI_DISPLAY_RING_FILL_CRITICAL_ENTER();
    result = OPEN_CFW_UI_DISPLAY_RING_FILL_READ(
        handle,
        buffer,
        sizeof(buffer),
        &read_count
    );
    if (
        result == 0U
            && OPEN_CFW_UI_DISPLAY_RING_FILL_WRITE(
                OPEN_CFW_UI_DISPLAY_RING_FILL_RING(handle),
                buffer,
                read_count
            )
                == 0U
    ) {
        result = 0x08000001U;
    }
    OPEN_CFW_UI_DISPLAY_RING_FILL_CRITICAL_EXIT(interrupt_mask);
    return result;
}

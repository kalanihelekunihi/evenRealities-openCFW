/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 Apollo direct display FIFO writer
 * at 0x0058E31E. The exact stock boundary, MMIO layout, and behavioral
 * evidence are recorded in EVIDENCE.md.
 */

#ifndef OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_INSTANCE
#define OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_INSTANCE(handle) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0x28U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_FIFO_FULL
#define OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_FIFO_FULL(instance) \
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

#ifndef OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_BYTE
#define OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_BYTE(instance, value) \
    do { \
        *(volatile unsigned int *)(void *)( \
            0x40039000U + ((instance) << 12U) \
        ) = (unsigned int)(value); \
    } while (0)
#endif

/*
 * Stock ABI at 0x0058E31E. The routine always returns zero, optionally
 * reports the number of bytes accepted, and never waits for a full FIFO.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_direct_write(
    void *handle,
    const void *source,
    unsigned int count,
    unsigned int *written
)
{
    const unsigned char *bytes = (const unsigned char *)source;
    unsigned int instance =
        OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_INSTANCE(handle);
    unsigned int accepted = 0U;

    while (
        accepted < count
            && !OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_FIFO_FULL(instance)
    ) {
        OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_BYTE(
            instance,
            bytes[accepted]
        );
        ++accepted;
    }

    if (written != (unsigned int *)0) {
        *written = accepted;
    }
    return 0U;
}

/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 Apollo direct display FIFO reader
 * at 0x0058E2D8. The exact stock boundary, MMIO layout, callers, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

#ifndef OPEN_CFW_UI_DISPLAY_DIRECT_READ_INSTANCE
#define OPEN_CFW_UI_DISPLAY_DIRECT_READ_INSTANCE(handle) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0x28U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_DIRECT_READ_FIFO_EMPTY
#define OPEN_CFW_UI_DISPLAY_DIRECT_READ_FIFO_EMPTY(instance) \
    ( \
        ( \
            *(const volatile unsigned int *)(const void *)( \
                0x40039018U + ((instance) << 12U) \
            ) \
            & (1U << 4U) \
        ) \
        != 0U \
    )
#endif

#ifndef OPEN_CFW_UI_DISPLAY_DIRECT_READ_WORD
#define OPEN_CFW_UI_DISPLAY_DIRECT_READ_WORD(instance) \
    (*(const volatile unsigned int *)(const void *)( \
        0x40039000U + ((instance) << 12U) \
    ))
#endif

/*
 * Stock ABI at 0x0058E2D8. A null destination intentionally discards FIFO
 * bytes. The optional read count is published on empty, complete, and error
 * exits; data words with any status bit in 0x00000F00 set are not accepted.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_direct_read(
    void *handle,
    void *destination,
    unsigned int count,
    unsigned int *read_count
)
{
    unsigned char *bytes = (unsigned char *)destination;
    unsigned int instance =
        OPEN_CFW_UI_DISPLAY_DIRECT_READ_INSTANCE(handle);
    unsigned int accepted = 0U;
    unsigned int result = 0U;
    unsigned int word;

    while (
        accepted < count
            && !OPEN_CFW_UI_DISPLAY_DIRECT_READ_FIFO_EMPTY(instance)
    ) {
        word = OPEN_CFW_UI_DISPLAY_DIRECT_READ_WORD(instance);
        if ((word & 0x00000F00U) != 0U) {
            result = 0x08000000U;
            break;
        }
        if (bytes != (unsigned char *)0) {
            bytes[accepted] = (unsigned char)word;
        }
        ++accepted;
    }

    if (read_count != (unsigned int *)0) {
        *read_count = accepted;
    }
    return result;
}

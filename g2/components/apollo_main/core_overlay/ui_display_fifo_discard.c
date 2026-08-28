/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 Apollo display FIFO discard helper
 * at 0x0058E352. The exact stock boundary and callers are recorded in
 * EVIDENCE.md.
 */

unsigned int open_cfw_ui_display_direct_read(
    void *handle,
    void *destination,
    unsigned int count,
    unsigned int *read_count
);

#ifndef OPEN_CFW_UI_DISPLAY_FIFO_DISCARD_READ
#define OPEN_CFW_UI_DISPLAY_FIFO_DISCARD_READ( \
    handle, \
    destination, \
    count, \
    read_count \
) \
    (open_cfw_ui_display_direct_read( \
        (handle), \
        (destination), \
        (count), \
        (read_count) \
    ))
#endif

/*
 * Stock ABI at 0x0058E352. The helper requests 32 bytes with both optional
 * outputs omitted and returns the direct reader's result unchanged.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_fifo_discard(void *handle)
{
    return OPEN_CFW_UI_DISPLAY_FIFO_DISCARD_READ(
        handle,
        (void *)0,
        32U,
        (unsigned int *)0
    );
}

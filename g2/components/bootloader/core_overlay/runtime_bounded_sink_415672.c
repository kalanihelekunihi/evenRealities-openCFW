/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader bounded-output character
 * sink retained between the authenticated Arm EABI byte-fill (memset) and
 * forward-copy (memcpy) primitives. Callers hold a three-word context: a
 * cursor into the destination buffer, the remaining free byte count, and
 * the running total of characters offered to the sink (matching the
 * classic counted-sprintf pattern also used by the neighboring numeric
 * formatting primitives). Every call increments the running total; a byte
 * is written and the remaining count decremented only while space remains,
 * so overflowing callers still learn how many characters they asked for.
 */

typedef __UINT32_TYPE__ open_cfw_bootloader_sink_u32;

typedef struct open_cfw_bootloader_bounded_sink {
    unsigned char *cursor;
    open_cfw_bootloader_sink_u32 remaining;
    open_cfw_bootloader_sink_u32 total;
} open_cfw_bootloader_bounded_sink_t;

__attribute__((used, noinline))
void open_cfw_bootloader_bounded_sink_putc_415672(
    open_cfw_bootloader_bounded_sink_t *sink, unsigned char value)
{
    sink->total++;
    if (sink->remaining == 0U) {
        return;
    }
    *sink->cursor++ = value;
    sink->remaining--;
}

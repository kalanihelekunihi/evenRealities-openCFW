/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 LVGL zero-fill wrapper at
 * 0x004734C0.
 */

__attribute__((used, noinline))
void open_cfw_lv_memory_zero(void *destination, unsigned int size)
{
    unsigned char *cursor = (unsigned char *)destination;

#if defined(__clang__)
#pragma clang loop unroll(disable)
#endif
    while (size != 0U) {
        *cursor = 0U;
        cursor += 1;
        size -= 1U;
    }
}

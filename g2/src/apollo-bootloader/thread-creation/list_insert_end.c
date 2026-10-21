/* SPDX-License-Identifier: MIT
 * Stock 0x41b55a..0x41b572: append a FreeRTOS list item immediately before
 * the list index node, update both links and ownership, then increment count.
 * The list and item are five-word native structures with 32-bit pointers.
 */
#include "list_insert_end.h"

void opencfw_boot_list_insert_end(uint32_t *list, uint32_t *item)
{
    uint32_t *const index = (uint32_t *)(uintptr_t)list[1];
    uint32_t *const previous = (uint32_t *)(uintptr_t)index[2];
    item[1] = (uint32_t)(uintptr_t)index;
    item[2] = (uint32_t)(uintptr_t)previous;
    previous[1] = (uint32_t)(uintptr_t)item;
    index[2] = (uint32_t)(uintptr_t)item;
    item[4] = (uint32_t)(uintptr_t)list;
    list[0] += 1u;
}

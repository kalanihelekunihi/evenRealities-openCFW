/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800bf8c: timer-daemon callback forwarding its two ABI
 * arguments to the task-context event-set provider at 0x0800c4de.
 */
#include <stdint.h>

extern uint32_t xEventGroupSetBits(void *event_group, uint32_t bits);

void vEventGroupSetBitsCallback(void *event_group, uint32_t bits)
{
    (void)xEventGroupSetBits(event_group, bits);
}

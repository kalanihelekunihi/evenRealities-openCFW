/* SPDX-License-Identifier: MIT. Private scheduler waiter wake ABI. */
#ifndef OPENCFW_BOOT_EVENT_WAITER_WAKE_H
#define OPENCFW_BOOT_EVENT_WAITER_WAKE_H

#include <stdint.h>

/* Remove the first owner of a nonempty event list, transferring it to ready
 * or pending-ready state. Input is the list header (queue+0x24 / +0x10). */
uint32_t opencfw_bl_remove_event_waiter(uint32_t *list);

/* Set the scheduler's pending-yield word. */
void opencfw_bl_missed_yield(void);

#endif

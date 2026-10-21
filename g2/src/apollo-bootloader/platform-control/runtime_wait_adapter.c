/* SPDX-License-Identifier: MIT. Stock41d21c equality wait shares the tested
 *41d246 loop semantics with equal=1. No hardware elapsed-time assertion. */
#include <stdint.h>
extern uint32_t opencfw_hal_status_poll(uint32_t, uintptr_t, uint32_t, uint32_t, uint32_t);
uint32_t opencfw_boot_control_delay_status_change(uint32_t count,
    volatile uint32_t *address, uint32_t mask, uint32_t expected) {
    return opencfw_hal_status_poll(count, (uintptr_t)address, mask, expected, 1u);
}

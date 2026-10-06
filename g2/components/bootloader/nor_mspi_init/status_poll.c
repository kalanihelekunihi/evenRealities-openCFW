/* SPDX-License-Identifier: MIT. Stock41d246 timeout is a count of delay(1)
 * calls. Physical time depends on the unclosed delay implementation/clock. */
#include <stdint.h>
extern void opencfw_hal_delay_us(uint32_t);
uint32_t opencfw_hal_status_poll(uint32_t count, uintptr_t address,
                                uint32_t mask, uint32_t expected,
                                uint32_t equal) {
    for (;;) {
        uint32_t value = *(volatile uint32_t *)address & mask;
        if ((uint8_t)equal == 0u ? value != expected : value == expected) return 0;
        if (count == 0u) return 4;
        opencfw_hal_delay_us(1u);
        --count;
    }
}

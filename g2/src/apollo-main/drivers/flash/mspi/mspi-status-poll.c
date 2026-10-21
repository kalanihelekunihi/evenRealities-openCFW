/* SPDX-License-Identifier: MIT. Main 0x480826 timeout is a count of delay(1)
 * calls. Physical time depends on the unclosed delay implementation/clock. */
#include <stdint.h>
extern void audio_delay_us_selected(uint32_t);
uint32_t g2_main_mspi_status_poll_480826(uint32_t count, uintptr_t address,
                                uint32_t mask, uint32_t expected,
                                uint32_t equal) {
    for (;;) {
        uint32_t value = *(volatile uint32_t *)address & mask;
        if ((uint8_t)equal == 0u ? value != expected : value == expected) return 0;
        if (count == 0u) return 4;
        audio_delay_us_selected(1u);
        --count;
    }
}

/* Apollo uLED power controls 0x4d391e and 0x4d3938. Candidate. */
#include <stdint.h>

uint32_t display_driver_uled_power_set_4d391e(uint32_t enabled) {
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x40004044u;
    uint32_t bit=((uint8_t)enabled != 0u) ? 1u : 0u;
    *control=(*control & ~1u) | bit;
    return 0u;
}

uint32_t display_driver_uled_power_apply_4d3938(uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)0x40004020u=value | 1u;
    return 0u;
}

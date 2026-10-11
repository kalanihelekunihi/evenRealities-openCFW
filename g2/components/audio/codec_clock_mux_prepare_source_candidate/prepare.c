#include <stdint.h>

/* Native 0x00539c9a..0x00539d75 reads the clock control register and
 * returns the currently selected source code through an output byte. */
uint32_t g2_clock_mux_prepare(uint8_t group, uint8_t *selection) {
    uint32_t const control =
        *(volatile const uint32_t *)(uintptr_t)0x400204e8u;
    uint32_t current;
    uint8_t base;
    switch (group) {
    case 0u: current = control & 3u; base = 0u; break;
    case 1u: current = (control >> 2) & 3u; base = 3u; break;
    case 2u: current = (control >> 4) & 1u; base = 6u; break;
    case 3u: current = (control >> 5) & 3u; base = 8u; break;
    case 4u: current = (control >> 7) & 3u; base = 11u; break;
    case 5u: return 6u;
    default: return 0u;
    }
    if (current < 3u)
        *selection = (uint8_t)(base + current);
    return 0u;
}

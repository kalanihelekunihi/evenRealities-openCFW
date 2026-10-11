#include <stdint.h>

/* Apollo MAIN 0x58fd1c. The subtraction sequence intentionally wraps at 32 bits. */
uint32_t audio_i2s_clock_source(uint32_t value) {
    if (value == 0) return 6;
    value -= 0x100u;
    if (value == 0) return 6;
    value -= 0x100u;
    if (value <= 7u) return 5;
    value -= 8u;
    if (value <= 6u) return 4;
    value -= 7u;
    if (value <= 6u)
        return ((*(volatile const uint32_t *)(uintptr_t)0x40004048u >> 30) & 1u) ? 3u : 2u;
    value -= 7u;
    if (value == 0) return 4;
    value -= 0xffeau;
    if (value <= 1u) return 4;
    value -= 2u;
    if (value == 0) return 2;
    value -= 1u;
    return value == 0 ? 5u : 7u;
}

uint32_t audio_power_clock_source(uint32_t) __attribute__((alias("audio_i2s_clock_source")));

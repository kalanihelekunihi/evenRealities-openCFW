/* SPDX-License-Identifier: MIT */
/* Source reconstruction of the shipped byte-normalizing memset and the
 * NationalChip SDK fast-fill algorithm. See NATIONALCHIP-LIBC-NOTICE.txt.
 * Volatile stores preserve recovered store widths/order. The signed block
 * comparisons and three-byte tail intentionally preserve stock behavior;
 * this is not a promise of valid storage for arbitrary 32-bit sizes. */
#include <stdint.h>
#include <stddef.h>
typedef uint32_t alias_word __attribute__((may_alias));
void *open_cfw_gx8002_memset(void *destination, int value, size_t count)
{
    uintptr_t cursor = (uintptr_t)destination;
    uint8_t byte = (uint8_t)value;
    if (!count)
        return destination;
    while (cursor & 3u) {
        *(volatile uint8_t *)cursor = byte;
        if (!--count)
            return destination;
        cursor++;
    }
    uint32_t word = byte;
    word |= word << 8;
    word |= word << 16;
    while ((int32_t)count >= 16) {
        *(volatile alias_word *)(cursor + 0) = word;
        *(volatile alias_word *)(cursor + 4) = word;
        *(volatile alias_word *)(cursor + 8) = word;
        *(volatile alias_word *)(cursor + 12) = word;
        count -= 16;
        cursor += 16;
    }
    while ((int32_t)count >= 4) {
        count -= 4;
        *(volatile alias_word *)cursor = word;
        cursor += 4;
    }
    if (count) {
        *(volatile uint8_t *)cursor = byte;
        if (--count) {
            *(volatile uint8_t *)(cursor + 1) = byte;
            if (--count)
                *(volatile uint8_t *)(cursor + 2) = byte;
        }
    }
    return destination;
}

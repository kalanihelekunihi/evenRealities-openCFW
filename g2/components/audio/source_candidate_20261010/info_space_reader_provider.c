/* Apollo510 INFO reader, reconstructed from pinned Ambiq HAL infoX_read.
 * Pinned source: am_hal_info.c at 5efc0228528a8adce5eae0d226fac85d2551eb3b.
 * The original uses an 8-bit info-space selector on this image.
 * Source admission requires the companion stock/source execution receipt.
 */
#include <stdint.h>

extern uint32_t platform_copy_words(uint32_t source, uint32_t *destination,
                                    uint32_t words);

uint32_t audio_info_space_read(uint32_t raw_space, uint32_t offset,
                               uint32_t words, uint32_t *destination) {
    const uint32_t shadow = *(volatile uint32_t *)(uintptr_t)0x400201bcu;
    const uint32_t power = *(volatile uint32_t *)(uintptr_t)0x40021008u;
    const uint32_t space = (uint8_t)raw_space;
    uint32_t capacity;
    uint32_t source;

    if (!destination) return 6u;
    switch (space) {
    case 0: capacity = (shadow & 0x10u) ? 64u : 512u; break;
    case 1: capacity = (shadow & 0x08u) ? 704u : 1536u; break;
    case 2: capacity = 64u; break;
    case 3: capacity = 704u; break;
    case 4: capacity = 512u; break;
    case 5: capacity = 1536u; break;
    default: return 6u;
    }
    if (offset + words > capacity) return 5u;

    switch (space) {
    case 0:
        if (shadow & 0x10u) {
            if (!(power & 0x08000000u)) return 9u;
            source = 0x42004000u + offset * 4u;
        } else {
            source = 0x42000000u + offset * 4u;
        }
        break;
    case 1:
        if (shadow & 0x08u) {
            if (!(power & 0x08000000u)) return 9u;
            source = 0x42006000u + offset * 4u;
        } else {
            source = 0x42002000u + (offset < 512u ? offset : offset + 640u) * 4u;
        }
        break;
    case 2:
        if (!(power & 0x08000000u)) return 9u;
        source = 0x42004000u + offset * 4u;
        break;
    case 3:
        if (!(power & 0x08000000u)) return 9u;
        source = 0x42006000u + offset * 4u;
        break;
    case 4:
        source = 0x42000000u + offset * 4u;
        break;
    default:
        source = 0x42002000u + offset * 4u;
        break;
    }
    (void)platform_copy_words(source, destination, words);
    return 0u;
}

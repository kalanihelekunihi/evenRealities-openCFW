/* Native image-B 0x1000f824..0x1000f849, directly attributable to pinned
 * NationalChip libdsp csky_bitreversal2.S csky_bitreversal_16. Expressed
 * as C so the loaded image remains C-compilable. The native loop reads
 * successive two-byte table offsets, divides by two, then swaps 32-bit
 * complex Q15 records. Stock caller uses an even length of 240.
 */
#include <stdint.h>

void gx8002_image_b_bit_reverse_1000f824(
    uint16_t *data, uint16_t length, const uint16_t *table)
{
    uint8_t *bytes = (uint8_t *)(void *)data;
    uint32_t pairs = ((uint32_t)length + 1u) >> 1;
    for (uint32_t i = 0; i < pairs; ++i) {
        uint32_t left_offset = (uint32_t)table[2u * i] >> 1;
        uint32_t right_offset = (uint32_t)table[2u * i + 1u] >> 1;
        uint32_t *left = (uint32_t *)(void *)(bytes + left_offset);
        uint32_t *right = (uint32_t *)(void *)(bytes + right_offset);
        uint32_t old_left = *left;
        uint32_t old_right = *right;
        *left = old_right;
        *right = old_left;
    }
}

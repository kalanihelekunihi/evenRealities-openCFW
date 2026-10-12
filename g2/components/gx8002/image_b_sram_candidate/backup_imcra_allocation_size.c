/* Native 0x1000c6a4, called by image-B IMCRA setup at 0x1000b89e.
 * Unsigned operations retain C-SKY 32-bit register wraparound.
 */
#include <stdint.h>

uint32_t gx8002_image_b_imcra_allocation_size_1000c6a4(
    uint32_t channels, uint32_t stages, uint32_t bins, uint32_t history)
{
    /* The retained decompiler expression is independently grounded by the
     * full 0xc6a4..0xc6e6 arithmetic instruction sequence. */
    uint32_t total = stages * channels * 522u;
    total += stages * 522u;
    total += bins * 4u;
    total += (stages - 1u) * history;
    total -= history * 3u;
    total += 0x806u;
    return total << 1;
}

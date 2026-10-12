/* Native 0x1000c5d0: in-place 64-by-32 unsigned quotient and remainder.
 * The sole observed image-B caller at 0x100050c0 supplies divisor 1024.
 * Zero-divisor behavior is outside this source contract pending native proof.
 */
#include <stdint.h>

uint32_t gx8002_image_b_divide_u64_u32_1000c5d0(
    uint64_t *value, uint32_t divisor)
{
    uint64_t dividend = *value;
    uint32_t remainder = (uint32_t)(dividend % divisor);
    *value = dividend / divisor;
    return remainder;
}

/* SPDX-License-Identifier: MIT
 * Stock 0x08002f60 and 0x08002f88 copy runtime flash-resident data.
 * The data at these addresses is external to the pinned CASE image.
 */
#include <stdint.h>
/* Stock 0x08002F60 (case_binary_fill51) */
uint8_t *case_binary_fill51(uint8_t *out)
{
    volatile const uint8_t *source=(volatile const uint8_t *)(uintptr_t)0x0803f800u;
    for(uint32_t i=0;i<8u;i++) out[i]=source[7u-i];
    return out;
}
/* Stock 0x08002F88 (case_binary_fill5f) */
uint8_t *case_binary_fill5f(uint8_t *out)
{
    volatile const uint8_t *source=(volatile const uint8_t *)(uintptr_t)0x0803f000u;
    for(uint32_t i=0;i<8u;i++) out[i]=source[7u-i];
    for(uint32_t i=0;i<8u;i++) out[8u+i]=source[15u-i];
    return out;
}

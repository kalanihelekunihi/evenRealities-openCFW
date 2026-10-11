/* SPDX-License-Identifier: MIT
 * Native CASE 0x080001fc little-endian reader. Called from transfer parser 0x2194/0x21aa.
 */
#include <stdint.h>

uint32_t case_boot_read_le32(const uint8_t *input)
{
    uint32_t value=0u;
    for(uint32_t i=0u;i<4u;++i)
        value|=(uint32_t)input[i]<<(i*8u);
    return value;
}

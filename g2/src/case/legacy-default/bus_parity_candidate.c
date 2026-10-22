/* SPDX-License-Identifier: MIT
 * Stock 0x0800c412 eight-bit xor parity used by output transaction.
 */
#include <stdint.h>
/* Stock 0x0800C412 (case_parity8_alt) */
uint32_t case_bus_read(uint32_t value)
{
    uint32_t parity=0u;
    for(uint32_t bit=0;bit<8u;++bit) parity^=(value>>bit)&1u;
    return parity;
}

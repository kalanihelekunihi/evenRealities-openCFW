/* SPDX-License-Identifier: MIT
 * Stock 0x415844 unsigned 64-bit decimal quotient helper. The shift/add
 * correction is arithmetic source, with no compiler division service import.
 */
#include <stdint.h>

uint64_t opencfw_boot_u64_div10(uint64_t value)
{
    uint64_t quotient = (value >> 1) + (value >> 2);
    quotient += quotient >> 4;
    quotient += quotient >> 8;
    quotient += quotient >> 16;
    quotient += quotient >> 32;
    quotient >>= 3;
    const uint64_t remainder = value - (quotient << 3) - (quotient << 1);
    return quotient + ((remainder + 6u) >> 4);
}

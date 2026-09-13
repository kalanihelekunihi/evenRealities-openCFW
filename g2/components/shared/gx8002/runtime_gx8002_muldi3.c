/* SPDX-License-Identifier: MIT
 * Recovered low-64-bit product using 16-bit limbs; no 64-bit multiply helper.
 */
#include <stdint.h>
uint64_t open_cfw_gx8002_muldi3(uint64_t a,uint64_t b)
{
    uint32_t al=(uint32_t)a, bl=(uint32_t)b;
    uint32_t a0=al&65535, a1=al>>16, b0=bl&65535, b1=bl>>16;
    /* Empty constraints select compact low registers; normal C prologue
     * preserves r4-r6. No instruction or call-preservation override is used. */
    register uint32_t low __asm__("r6")=a0*b0;
    register uint32_t cross __asm__("r5")=a1*b0;
    uint32_t other=a0*b1;
    register uint32_t high __asm__("r4")=a1*b1;
    __asm__("" : "+r"(low), "+r"(cross), "+r"(high));
    uint32_t middle=(low>>16)+cross+other;
    if (middle<cross) high+=65536;
    high+=middle>>16;
    high+=al*(uint32_t)(b>>32)+(uint32_t)(a>>32)*bl;
    /* Target ABI is little-endian: low word precedes high word. */
    union { uint64_t value; struct { uint32_t low, high; } words; } result;
    result.words.low=(middle<<16)|(low&65535);
    result.words.high=high;
    return result.value;
}

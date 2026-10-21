#include <stdint.h>
/* This native conversion discards sign, inserts the implicit significand bit
 * even for exponent 2047, and delegates shifts to the recovered register-shift
 * contracts. A language double-to-uint64 cast would change its behavior. */
extern uint64_t __aeabi_llsl(uint64_t,uint32_t);
extern uint64_t __aeabi_llsr(uint64_t,uint32_t);
uint64_t r1_format_double_to_unsigned_bits(uint64_t bits)
{
    uint32_t high=(uint32_t)(bits>>32),exponent=(high>>20)&2047u;
    uint64_t significand=((uint64_t)((high&UINT32_C(0xfffff))|UINT32_C(0x100000))<<32)|(uint32_t)bits;
    if (exponent<1023u) return 0;
    if (exponent<=1075u) return __aeabi_llsr(significand,1075u-exponent);
    return __aeabi_llsl(significand,exponent-1075u);
}

#include <stdint.h>
extern uint64_t __aeabi_llsr(uint64_t,uint32_t);
extern uint64_t r1_format_double_round_bits(uint64_t,uint64_t);
/* Raw R0/R1 binary64 contract at native0x2820a, not a generic IEEE sqrt.
 * Nonpositive signed encodings return +0. Positive exceptional/subnormal
 * encodings follow the same forced-significand integer recurrence as normals.
 * Native instructions, not decompiler carry/overflow expressions, establish
 * the entry signed comparison and final unsigned remainder comparison. */
uint64_t r1_binary64_square_root_bits(uint64_t bits)
{
    if ((int64_t)bits<=0) return 0;
    uint32_t exponent=(uint32_t)(bits>>52)&2047u;
    uint64_t remainder=(bits&UINT64_C(0xfffffffffffff))|UINT64_C(0x10000000000000);
    if (!(exponent&1u)) { remainder<<=1;--exponent; }
    uint32_t encoded_exponent=(uint32_t)((int32_t)exponent>>1)+511u;
    uint64_t root=0;
    for (uint32_t index=0;index<53u;++index) {
        uint64_t bit=__aeabi_llsr(UINT64_C(0x10000000000000),index);
        uint64_t trial=bit+root+root;
        if (remainder>=trial) { remainder-=trial;root+=bit; }
        remainder<<=1;
    }
    uint64_t round_remainder=remainder>(root<<1) ? UINT64_MAX : 0;
    return r1_format_double_round_bits(root+((uint64_t)encoded_exponent<<52),round_remainder);
}

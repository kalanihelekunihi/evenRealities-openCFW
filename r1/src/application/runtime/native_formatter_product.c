#include <stdint.h>
extern uint64_t r1_format_double_normalize_bits(uint64_t,uint64_t,uint64_t,uint32_t);
extern uint64_t r1_format_double_round_bits(uint64_t,uint64_t);
/* Native arithmetic always inserts the hidden bit for nonzero operands. There
 * are no IEEE special-value substitutions. Retain the complete integer product
 * and its discarded bits before the recovered normalization/rounding step. */
uint64_t r1_format_double_multiply_bits(uint64_t a,uint64_t b)
{
    const uint64_t signbit=UINT64_C(0x8000000000000000);
    if (!(a&~signbit) || !(b&~signbit)) return 0;
    uint32_t ah=((uint32_t)(a>>32)&UINT32_C(0xfffff))|UINT32_C(0x100000);
    uint32_t bh=((uint32_t)(b>>32)&UINT32_C(0xfffff))|UINT32_C(0x100000);
    uint32_t al=(uint32_t)a,bl=(uint32_t)b;
    uint64_t p00=(uint64_t)al*bl,p01=(uint64_t)al*bh,p10=(uint64_t)ah*bl,p11=(uint64_t)ah*bh;
    uint64_t middle=(p00>>32)+(uint32_t)p01+(uint32_t)p10;
    uint64_t upper=(p01>>32)+(p10>>32)+(uint32_t)p11+(middle>>32);
    uint32_t limb1=(uint32_t)middle,limb2=(uint32_t)upper,limb3=(uint32_t)((p11>>32)+(upper>>32));
    uint64_t significand=((uint64_t)limb1>>20)|((uint64_t)limb2<<12)|((uint64_t)limb3<<44);
    uint64_t remainder=(((uint64_t)limb1<<32)|(uint32_t)p00)<<12;
    uint32_t exponent=(uint32_t)((a>>52)&2047u)+(uint32_t)((b>>52)&2047u)-1023u;
    return r1_format_double_normalize_bits(significand,remainder,(a^b)&signbit,exponent);
}
/* Native restoring division emits 53 quotient bits. The doubled final
 * remainder determines below-half, exact-half and above-half rounding. */
uint64_t r1_format_double_divide_bits(uint64_t a,uint64_t b)
{
    const uint64_t signbit=UINT64_C(0x8000000000000000),hidden=UINT64_C(0x10000000000000);
    if (!(a&~signbit) || !(b&~signbit)) return 0;
    uint64_t numerator=(a&UINT64_C(0xfffffffffffff))|hidden;
    uint64_t denominator=(b&UINT64_C(0xfffffffffffff))|hidden;
    uint32_t exponent=(uint32_t)((a>>52)&2047u)-(uint32_t)((b>>52)&2047u)+1021u;
    if (numerator>=denominator) ++exponent;
    else numerator<<=1;
    if ((int32_t)exponent<0) return 0;
    uint64_t quotient=0;
    for (uint64_t bit=hidden;bit;bit>>=1) {
        if (numerator>=denominator) { numerator-=denominator;quotient|=bit; }
        numerator<<=1;
    }
    uint64_t remainder=0;
    if (numerator) {
        if (numerator==denominator) remainder=signbit;
        else remainder=numerator>denominator ? UINT64_MAX-1u : 1;
    }
    return r1_format_double_round_bits(quotient+((uint64_t)exponent<<52)+((a^b)&signbit),remainder);
}

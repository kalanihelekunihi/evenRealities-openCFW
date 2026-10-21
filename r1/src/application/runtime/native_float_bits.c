#include "native_float_bits.h"
extern uint64_t __aeabi_llsr(uint64_t,uint32_t);
extern uint64_t r1_format_double_normalize_bits(uint64_t,uint64_t,uint64_t,uint32_t);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
static uint32_t lsl32(uint32_t x,uint32_t count)
{ count&=255u;return count<32 ? x<<count : 0; }
/* Native classifier tags: zero0, subnormal4, normal5, infinity3, NaN7.
 * These are encoded tags, not host FP_* enumeration values. */
uint32_t r1_binary64_classify_bits(uint64_t bits,uint32_t unused2 __attribute__((unused)),uint32_t saved3)
{
    register uint32_t incoming3 __asm__("r3")=saved3;
    uint32_t high=(uint32_t)(bits>>32),exponent=(high>>20)&2047u;
    uint32_t tag=((uint32_t)bits || (high&0xfffffu)) ? 4u : 0u;
    if (exponent) tag|=1;
    if (exponent==2047u) tag|=2;
    if (tag==1) tag=5;
    register uint32_t out0 __asm__("r0")=tag,out1 __asm__("r1")=high<<1;
    register uint32_t out2 __asm__("r2")=2047u;
    __asm__ volatile("" : "+r"(out0),"+r"(out1),"+r"(out2),"+r"(incoming3) : : "memory");
    return out0;
}
uint32_t r1_binary32_classify_bits(uint32_t bits,uint32_t unused1 __attribute__((unused)),uint32_t unused2 __attribute__((unused)),uint32_t saved3)
{
    register uint32_t incoming3 __asm__("r3")=saved3;
    uint32_t exponent=(bits>>23)&255u,tag=(bits&0x7fffffu) ? 4u : 0u;
    if (exponent) tag|=1;
    if (exponent==255u) tag|=2;
    if (tag==1) tag=5;
    register uint32_t out0 __asm__("r0")=tag,out1 __asm__("r1")=~(bits<<1)&UINT32_C(0xff000000);
    register uint32_t out2 __asm__("r2")=UINT32_C(0xff000000);
    __asm__ volatile("" : "+r"(out0),"+r"(out1),"+r"(out2),"+r"(incoming3) : : "memory");
    return out0;
}
uint64_t r1_signed32_to_binary64_bits(uint32_t word)
{
    uint32_t negative=word>>31,magnitude=negative ? 0u-word : word;
    return r1_format_double_normalize_bits(magnitude,0,(uint64_t)negative<<63,1075);
}
uint64_t r1_unsigned32_to_binary64_bits(uint32_t word)
{ return r1_format_double_normalize_bits(word,0,0,1075); }
static uint32_t to_word(uint64_t bits)
{
    uint32_t exponent=(uint32_t)(bits>>52)&2047u;
    if (exponent<1023u) return 0;
    if (exponent>1075u) return lsl32((uint32_t)bits,exponent-1075u);
    uint64_t significand=(bits&UINT64_C(0xfffffffffffff))|UINT64_C(0x10000000000000);
    return (uint32_t)__aeabi_llsr(significand,1075u-exponent);
}
uint32_t r1_binary64_to_signed32_bits(uint64_t bits)
{
    uint32_t value=to_word(bits);
    return bits>>63 ? 0u-value : value;
}
uint32_t r1_binary64_to_unsigned32_bits(uint64_t bits)
{ return to_word(bits); }
uint64_t r1_binary32_to_binary64_bits(uint32_t bits)
{
    uint32_t magnitude=bits&UINT32_C(0x7fffffff);
    if (!magnitude) return 0;
    uint32_t exponent=(magnitude>>23)+896u;
    return ((uint64_t)(bits&UINT32_C(0x80000000))<<32)|((uint64_t)exponent<<52)|((uint64_t)(magnitude&0x7fffffu)<<29);
}
uint64_t r1_binary64_subtract_bits(uint64_t a,uint64_t b)
{ return r1_format_double_add_bits(a,b^UINT64_C(0x8000000000000000)); }
uint64_t r1_binary64_reverse_subtract_bits(uint64_t a,uint64_t b)
{ return r1_format_double_add_bits(a^UINT64_C(0x8000000000000000),b); }
uint64_t r1_binary64_scale_power2_bits(uint64_t bits,uint32_t scale)
{
    if (!(bits&UINT64_C(0x7fffffffffffffff))) return bits;
    int64_t exponent=(int64_t)((bits>>52)&2047u)+(int32_t)scale;
    if (exponent<=0) return 0;
    return bits+((uint64_t)scale<<52);
}
/* Authenticated native 0x2839a is literally a zero-return control leaf. */
uint32_t r1_native_floating_environment_control(void)
{ return 0; }

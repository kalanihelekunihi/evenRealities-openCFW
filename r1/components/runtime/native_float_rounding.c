#include <stdint.h>
extern uint64_t __aeabi_llsl(uint64_t,uint32_t);
extern uint64_t __aeabi_llsr(uint64_t,uint32_t);
extern uint64_t r1_format_double_round_bits(uint64_t,uint64_t);
static uint32_t lsl32(uint32_t x,uint32_t n)
{ n&=255u;return n<32 ? x<<n : 0; }
static uint32_t lsr32(uint32_t x,uint32_t n)
{ n&=255u;return n<32 ? x>>n : 0; }
/* Reuse the already-tested native0x28078 provider from structured-float. */
extern uint32_t r1_log_round_float_bits(uint32_t,uint32_t);
/* 0x2808a is a shared interior entry in the 0x27e0c function body.
 * high/low here are normalized source words, not a uint64_t ABI argument. */
uint32_t r1_binary32_pack_words(uint32_t high,uint32_t low,uint32_t sign,uint32_t exponent)
{
    uint32_t leading=high ? (uint32_t)__builtin_clz(high) : 32u;
    high=lsl32(high,leading);
    if (!(high|low)) return high;
    if (low) high|=lsr32(low,32u-leading)|(lsl32(low,leading)!=0);
    uint32_t adjusted=exponent-leading+7u;
    if ((int32_t)adjusted<0) return 0;
    uint32_t encoded=(high>>8)+(adjusted<<23)+sign;
    return r1_log_round_float_bits(encoded,high<<24);
}
uint32_t r1_signed64_to_binary32_bits(uint64_t word)
{
    uint32_t sign=(uint32_t)(word>>63)<<31;
    uint64_t magnitude=sign ? 0u-word : word;
    uint32_t high=(uint32_t)(magnitude>>32),low=(uint32_t)magnitude;
    return high ? r1_binary32_pack_words(high,low,sign,182u) : r1_binary32_pack_words(low,0,sign,150u);
}
uint32_t r1_binary32_round_integral_bits(uint32_t bits)
{
    if (!(bits&0x7fffffffu)) return bits;
    uint32_t exponent=(bits>>23)&255u;
    if (exponent>150u) return bits;
    if (exponent>126u) {
        uint32_t shift=150u-exponent;
        return lsl32(r1_log_round_float_bits(lsr32(bits,shift),lsl32(bits,32u-shift)),shift);
    }
    if (exponent<126u || !(bits&0x7fffffu)) return 0;
    return (bits&0x80000000u)|0x3f800000u;
}
/* Native 0x28330 literal is the high word of encoded binary64 one. */
__attribute__((section(".r1.float.round_one"),used))
const uint32_t r1_binary64_round_one_high=0x3ff00000u;
uint64_t r1_binary64_round_integral_bits(uint64_t bits)
{
    if (!(bits&UINT64_C(0x7fffffffffffffff))) return bits;
    uint32_t exponent=(uint32_t)(bits>>52)&2047u;
    if (exponent>1075u) return bits;
    if (exponent>1022u) {
        uint32_t shift=1075u-exponent;
        uint64_t remainder=__aeabi_llsl(bits,64u-shift);
        uint64_t rounded=r1_format_double_round_bits(__aeabi_llsr(bits,shift),remainder);
        return __aeabi_llsl(rounded,shift);
    }
    if (exponent<1022u || !(bits&UINT64_C(0xfffffffffffff))) return 0;
    return (bits&UINT64_C(0x8000000000000000))|((uint64_t)r1_binary64_round_one_high<<32);
}

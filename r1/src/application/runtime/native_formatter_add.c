#include <stdint.h>
extern uint64_t __aeabi_llsl(uint64_t,uint32_t);
extern uint64_t __aeabi_llsr(uint64_t,uint32_t);
static uint32_t lsl32(uint32_t x,uint32_t n)
{ n&=255u;return n<32 ? x<<n : 0; }
static uint32_t lsr32(uint32_t x,uint32_t n)
{ n&=255u;return n<32 ? x>>n : 0; }
static uint32_t asr32(uint32_t x,uint32_t n)
{ n&=255u;return n<32 ? (uint32_t)((int32_t)x>>n) : (uint32_t)((int32_t)x>>31); }
uint64_t r1_format_signed_shift_bits(uint64_t x,uint32_t n)
{
    uint32_t low=(uint32_t)x,high=(uint32_t)(x>>32);
    if ((int32_t)n>=32) { low=asr32(high,n-32u);high=(uint32_t)((int32_t)high>>31); }
    else { low=lsr32(low,n)|lsl32(high,32u-n);high=asr32(high,n); }
    return ((uint64_t)high<<32)|low;
}
/* Native guard/remainder rounding, including tie-to-even carry. */
uint64_t r1_format_double_round_bits(uint64_t encoded,uint64_t remainder)
{
    if (remainder>>63) {
        ++encoded;
        if (!(remainder<<1)) encoded&=~UINT64_C(1);
    }
    return encoded;
}
uint64_t r1_format_double_normalize_bits(uint64_t significand,uint64_t remainder,
                                       uint64_t sign,uint32_t exponent)
{
    uint32_t high=(uint32_t)(significand>>32),low=(uint32_t)significand;
    uint32_t leading=high ? (uint32_t)__builtin_clz(high) : 32u+(low ? (uint32_t)__builtin_clz(low) : 32u);
    uint64_t normalized=__aeabi_llsl(significand,leading);
    if (!(normalized|remainder)) return normalized;
    if (remainder) {
        uint64_t carry=__aeabi_llsr(remainder,64u-leading);
        if (__aeabi_llsl(remainder,leading)) carry|=1;
        normalized|=carry;
    }
    uint32_t adjusted=exponent-leading+10u;
    if ((int32_t)adjusted<0) return 0;
    uint64_t encoded=((uint64_t)adjusted<<52)+(normalized>>11)+sign;
    return r1_format_double_round_bits(encoded,normalized<<53);
}
/* Recovered encoded-significand addition. It intentionally does not substitute
 * IEEE infinity/NaN/subnormal handling from a generic standard runtime. */
uint64_t r1_format_double_add_bits(uint64_t a,uint64_t b)
{
    const uint64_t signmask=UINT64_C(0x8000000000000000),implicit=UINT64_C(0x10000000000000);
    uint32_t different=(uint32_t)((a^b)>>63);
    if ((a&~signmask)<(b&~signmask)) { uint64_t swap=a;a=b;b=swap; }
    if (!(b&~signmask)) return a;
    uint32_t top=(uint32_t)(a>>52),exponent=top&2047u;
    uint32_t distance=exponent-(uint32_t)((b>>52)&2047u);
    uint64_t encoded,remainder;
    if (distance>=64u) {
        encoded=a-different;
        remainder=different ? UINT64_MAX : 1;
    } else {
        uint64_t smaller=(b&UINT64_C(0xfffffffffffff))|implicit;
        if (different) smaller=0u-smaller;
        remainder=__aeabi_llsl(smaller,64u-distance);
        encoded=a+r1_format_signed_shift_bits(smaller,distance);
        uint64_t base=(uint64_t)top<<52;
        if ((encoded>>52)!=top) {
            if (!different) {
                remainder=(remainder>>1)|(encoded<<63);
                encoded=((encoded-base+implicit)>>1)+base;
            } else if (distance<=1u) {
                return r1_format_double_normalize_bits(encoded-base+implicit,remainder,(uint64_t)(top&2048u)<<52,exponent);
            } else {
                encoded=((encoded<<1)-base)|(remainder>>63);
                remainder<<=1;
            }
        }
    }
    return r1_format_double_round_bits(encoded,remainder);
}

/* SPDX-License-Identifier: MIT. Stock42c222,42c256,42c26a arithmetic. */
#include <stdint.h>
static uint32_t lshift(uint32_t value,uint32_t amount) {return (amount&255u)<32u?value<<(amount&255u):0u;}
static uint32_t divide(uint32_t n,uint32_t d) {return d?n/d:0u;}
static uint32_t clz(uint32_t value) {return value?(uint32_t)__builtin_clz(value):32u;}
__attribute__((noinline)) uint32_t opencfw_boot_iom_frequency(uint32_t base,uint32_t select,
    uint32_t div3,uint32_t div_enable,uint32_t period)
{
    uint32_t denominator=(2u*div3+1u)*lshift(1u,select-1u)*(period*div_enable+1u);
    uint32_t result=divide(base,denominator);
    uint32_t remainder=base-denominator*result;
    if ((denominator>>1)<remainder) ++result;
    return result;
}
__attribute__((noinline)) uint32_t opencfw_boot_iom_onebit(uint32_t value) {return value && !(value&(value-1u));}
uint64_t opencfw_boot_iom_clock_config(uint32_t hz,uint32_t phase)
{
    const uint32_t base=96000000u;
    if (!hz) return 0;
    uint32_t divisor=base/hz+(base%hz!=0u);
    int32_t n=31-(int32_t)clz(divisor&(0u-divisor));
    if (n>=7) n=6;
    uint32_t div3=(hz<(base>>14) || (hz>=base/3u && hz<=(base>>1)-1u));
    uint32_t denominator=(2u*div3+1u)*lshift(1u,(uint32_t)n);
    uint32_t total=divide(divisor,denominator)+(divisor-denominator*divide(divisor,denominator)!=0u);
    uint32_t v=31u-clz(total);
    if (v>=8u) n=n+(int32_t)v-7;
    ++n;
    if ((uint32_t)n>=8u) return 0;
    if (v>=8u) {
        uint32_t divisor2=lshift(1u,v-7u);
        total=divide(total,divisor2)+(total-divisor2*divide(total,divisor2)!=0u);
    }
    uint32_t enabled=(hz<(base>>2) && lshift(1u,(uint32_t)n-1u)!=divisor);
    uint32_t low=(total-(phase==1u?2u:1u))>>1;
    uint32_t config=(((uint32_t)n<<8)&0xf00u)|((div3<<12)&0x1000u)|
        ((enabled<<13)&0x2000u)|((low<<16)&0xff0000u)|((total-1u)<<24);
    uint32_t actual=opencfw_boot_iom_frequency(base,(uint32_t)n,div3,enabled,total-1u);
    if (actual%250000u==0u && opencfw_boot_iom_onebit(actual/250000u)) {
        actual=opencfw_boot_iom_frequency(base,(uint32_t)n,1u,0u,0u);
        config=(((uint32_t)n<<8)&0xf00u)|0x1000u;
    }
    return ((uint64_t)actual<<32)|config;
}

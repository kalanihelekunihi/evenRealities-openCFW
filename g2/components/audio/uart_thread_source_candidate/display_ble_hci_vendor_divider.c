/* Native vendor clock divider 0x55bf64 and arithmetic children
 * 0x55bf1c/0x55bf50. ROM 0x55c7e0/e4: 0x05b8d800 and 0x0003d090. */
#include <stdint.h>
static uint32_t lz(uint32_t v) {return v==0u?32u:(uint32_t)__builtin_clz(v);}
static uint32_t shift(uint32_t v,uint32_t n) {return n>=32u?0u:v>>n;}
static uint32_t lshift(uint32_t v,uint32_t n) {return n>=32u?0u:v<<n;}

uint32_t audio_ble_vendor_divider_frequency_55bf1c(uint32_t clock,uint32_t divider,
        uint32_t odd,uint32_t fractional,uint32_t multiplier) {
    uint32_t quantum=(multiplier*fractional+1u)*(odd*2u+1u)*
        lshift(1u,(divider-1u)&0xffu);
    uint32_t quotient=clock/quantum;
    if((quantum>>1)<clock-quantum*quotient)quotient++;
    return quotient;
}
uint32_t audio_ble_vendor_divider_is_power2_55bf50(uint32_t value) {
    return value!=0u&&(value&(value-1u))==0u;
}

uint64_t audio_ble_vendor_clock_divider_body(uint32_t frequency,uint32_t mode,
                                              uint32_t unused,uint32_t high) {
    (void)unused;(void)high;
    const uint32_t clock=0x05b8d800u;
    uint32_t result=0u,actual=0u;
    if(frequency!=0u) {
        uint32_t count=clock/frequency+(clock!=frequency*(clock/frequency));
        uint32_t divider=31u-lz((0u-count)&count);
        if(divider>6u)divider=6u;
        uint32_t odd=(frequency<(clock>>14)||
            ((clock/3u)<=frequency&&frequency<=((clock>>1)-1u)))?1u:0u;
        uint32_t scale=(odd*2u+1u)*lshift(1u,divider&0xffu);
        uint32_t units=count/scale+(count!=scale*(count/scale));
        int32_t neg_lz=-(int32_t)lz(units);
        uint32_t width=(uint32_t)(neg_lz+31);
        if(width>7u)divider=divider+width-7u;
        uint32_t encoded=divider+1u;
        if(encoded<8u) {
            uint32_t rounded=units;
            if(width>7u) {
                uint32_t bits=(uint32_t)(neg_lz+0x118)&0xffu;
                rounded=shift(units,bits);
                uint32_t quantum=lshift(1u,(uint32_t)(neg_lz+0x18)&0xffu);
                if(units!=quantum*(units/quantum))rounded++;
            }
            uint32_t fractional=(frequency<(clock>>2)&&lshift(1u,divider&0xffu)!=count)?1u:0u;
            int32_t bias=(mode==1u)?-2:-1;
            result=(((rounded+(uint32_t)bias)>>1)&0xffu)<<16 |
                ((encoded*0x100u)&0xf00u) | odd<<12 | fractional<<13 |
                (rounded-1u)*0x1000000u;
            actual=audio_ble_vendor_divider_frequency_55bf1c(clock,encoded,odd,
                                                               fractional,rounded-1u);
            if(actual==0x0003d090u*(actual/0x0003d090u)&&
               audio_ble_vendor_divider_is_power2_55bf50(actual/0x0003d090u)!=0u) {
                actual=audio_ble_vendor_divider_frequency_55bf1c(clock,encoded,1u,0u,0u);
                result=((encoded*0x100u)&0xf00u)|0x1000u;
            }
        }
    }
    return ((uint64_t)actual<<32)|result;
}
__attribute__((naked)) uint64_t audio_ble_vendor_clock_divider_55bf64(uint32_t frequency,
                                                                          uint32_t mode) {
    __asm volatile("b audio_ble_vendor_clock_divider_body");
}

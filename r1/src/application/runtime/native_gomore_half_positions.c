#include <stdint.h>
#include "native_float_bits.h"
extern double r1_native_round(double);
static __attribute__((noinline,noclone)) float mul(float a,float b){return a*b;}
static __attribute__((noinline,noclone)) float sub(float a,float b){return a-b;}
static __attribute__((noinline,noclone)) float divide(float a,float b){return a/b;}
static __attribute__((noinline,noclone)) float madd(float acc,float a,float b){return acc+a*b;}
static __attribute__((noinline,noclone)) float signed_float(uint32_t value){return (float)(int32_t)value;}
static __attribute__((noinline,noclone)) float unsigned_float(uint32_t value){return (float)value;}
static uint32_t halfword(uint32_t at){return *(volatile uint16_t *)(uintptr_t)at;}
static float sample(uint32_t at){return *(volatile float *)(uintptr_t)at;}
static uint32_t rounded(float value)
{
    union {float value;uint32_t bits;} input={.value=value};
    union {double value;uint64_t bits;} result={.bits=r1_binary32_to_binary64_bits(input.bits)};
    result.value=r1_native_round(result.value);
    return r1_binary64_to_signed32_bits(result.bits);
}
uint32_t r1_gomore_fill_float_progression_native(uint32_t values,uint32_t first,uint32_t end,float initial,float step)
{
    for(uint32_t offset=0;(int32_t)first<(int32_t)end;first++,offset++) {
        float value=madd(initial,signed_float(offset),step);
        *(volatile float *)(uintptr_t)(values+first*4u)=value;
    }
    return values;
}
uint32_t r1_gomore_expand_half_positions_native(uint32_t positions,uint32_t values,uint32_t count,uint32_t output,uint32_t capacity)
{
    uint32_t prefix=rounded(mul(unsigned_float(halfword(positions)),0.5f));
    if((int32_t)prefix>(int32_t)capacity)return 1;
    r1_gomore_fill_float_progression_native(output,0,prefix,sample(values),0.0f);
    uint32_t last=count-1u;
    for(uint32_t i=0;(int32_t)i<(int32_t)last;i++) {
        uint32_t current=halfword(positions+i*2u),next=halfword(positions+(i+1u)*2u);
        uint32_t span=rounded(mul(signed_float(next-current),0.5f));
        float slope=0.0f;
        if(span) {
            float right=sample(values+(i+1u)*4u),left=sample(values+i*4u);
            slope=divide(sub(right,left),signed_float(span));
        }
        uint32_t end=prefix+span;
        if((int32_t)end>(int32_t)capacity || (int32_t)span<=0)return 1;
        r1_gomore_fill_float_progression_native(output,prefix,end,sample(values+i*4u),slope);
        prefix=end;
    }
    if((int32_t)prefix<(int32_t)capacity)r1_gomore_fill_float_progression_native(output,prefix,capacity,sample(values+last*4u),0.0f);
    return 0;
}

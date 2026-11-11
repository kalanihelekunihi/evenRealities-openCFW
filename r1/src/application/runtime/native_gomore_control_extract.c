#include <stdint.h>
#include "native_float_bits.h"
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern void __aeabi_memclr(void *,uint32_t);
extern uint32_t r1_gomore_expand_half_positions_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_locomotion_feature_reduce_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
static __attribute__((noinline,noclone)) float sub(float a,float b){return a-b;}
static __attribute__((noinline,noclone)) float mul(float a,float b){return a*b;}
static __attribute__((noinline,noclone)) float divide(float a,float b){return a/b;}
static __attribute__((noinline,noclone)) float convert(uint32_t value){return (float)(int32_t)value;}
static __attribute__((noinline,noclone)) uint32_t greater(float a,float b){return a>b;}
static uint32_t bits(float value){union {float value;uint32_t bits;} x={.value=value};return x.bits;}
static uint32_t byte(uint32_t at){return *(volatile uint8_t *)(uintptr_t)at;}
static uint32_t halfword(uint32_t at){return *(volatile uint16_t *)(uintptr_t)at;}
static float sample(uint32_t at){return *(volatile float *)(uintptr_t)at;}
static void store(uint32_t at,float value){*(volatile float *)(uintptr_t)at=value;}
static uint32_t carry(uint64_t a,uint64_t b)
{
    uint64_t ka=a>>63?a:UINT64_C(0x8000000000000000)-a;
    uint64_t kb=b>>63?b:UINT64_C(0x8000000000000000)-b;
    return kb>=ka;
}
static uint64_t scale(uint32_t value,uint64_t factor)
{return r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(value),factor);}
uint32_t r1_gomore_locomotion_control_extract_native(uint32_t state,uint32_t expanded,uint32_t maxima,uint32_t minima,volatile uint32_t incoming_controls,volatile uint32_t incoming_primary,volatile uint32_t secondary,volatile uint32_t mode)
{
    /* Preserve the native caller frame for reducer-owned stack publications. */
    volatile uint32_t frame_reservation[4];frame_reservation[0]=0;(void)frame_reservation;
    uint32_t controls=incoming_controls,primary=incoming_primary;
    volatile uint16_t positions[40];
    store(primary,-1.0f);store(secondary,0.0f);
    __aeabi_memclr((void *)positions,80);
    uint32_t retained=0;
    for(uint32_t i=0;(int32_t)i<(int32_t)(byte(state+81u)-1u);i++) {
        uint32_t next=halfword(state+(i+1u)*16u+92u),current=halfword(state+i*16u+92u);
        uint32_t delta=next-current;
        uint64_t distance=r1_signed32_to_binary64_bits(delta);
        if(carry(scale(*(volatile uint32_t *)(uintptr_t)(state+1728u),UINT64_C(0x3fe3333333333333)),distance))continue;
        if(carry(distance,scale(*(volatile uint32_t *)(uintptr_t)(state+1728u),UINT64_C(0x3ff8000000000000))))continue;
        positions[retained]=(uint16_t)halfword(state+i*16u+92u);
        if(mode==1u)store(controls+retained*4u,convert(delta));
        else {
            float first=sample(state+i*16u+96u),second=sample(state+i*16u+100u);
            float difference=sub(first,second);
            uint64_t raw_difference=r1_binary32_to_binary64_bits(bits(difference));
            uint64_t floor=scale(*(volatile uint32_t *)(uintptr_t)(state+1732u),UINT64_C(0x3fd0000000000000));
            if(carry(floor,raw_difference))difference=sample(state+1732u);
            else if(!greater(mul(sample(state+1732u),2.0f),difference))difference=sample(state+1732u);
            store(controls+retained*4u,difference);
        }
        retained++;
    }
    float period=sample(state+1728u),required=0.0f;
    if(greater(period,0.0f))required=divide(500.0f,period);
    uint64_t threshold=scale(bits(required),UINT64_C(0x3fe6666666666666));
    if(!carry(r1_signed32_to_binary64_bits(retained),threshold))return 1;
    if(r1_gomore_expand_half_positions_native((uint32_t)(uintptr_t)positions,controls,retained&255u,expanded,250)) {
        store(primary,-1.0f);store(secondary,0.0f);return 0;
    }
    r1_gomore_locomotion_feature_reduce_native(expanded,maxima,minima,controls,primary,secondary);
    return 0;
}

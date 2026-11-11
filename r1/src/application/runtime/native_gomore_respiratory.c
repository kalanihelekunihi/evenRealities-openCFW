#include "native_gomore_stages.h"
#include <stdint.h>
#include "native_gomore_history_record.h"
#include "native_gomore_respiratory_stats.h"
extern uint32_t r1_gomore_optical_estimate_native(uint32_t,uint32_t,uint32_t,uint32_t,volatile float *,volatile float *);
#include "native_gomore_clear_two.h"
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_binary64_subtract_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern double r1_native_sqrt(double);
static __attribute__((noinline,noclone)) float add(float a,float b){return a+b;}
static __attribute__((noinline,noclone)) float mul(float a,float b){return a*b;}
static __attribute__((noinline,noclone)) float divide(float a,float b){return a/b;}
static __attribute__((noinline,noclone)) int positive(float a){return a>0.0f;}
static __attribute__((noinline,noclone)) int negative(float a){return a<0.0f;}
static uint32_t bits(float value){union {float f;uint32_t u;} v={.f=value};return v.u;}
static float value(uint32_t word){union {float f;uint32_t u;} v={.u=word};return v.f;}
static uint32_t word(uint32_t at){return *(volatile uint32_t *)(uintptr_t)at;}
static void put(uint32_t at,uint32_t v){*(volatile uint32_t *)(uintptr_t)at=v;}
static uint8_t byte(uint32_t at){return *(volatile uint8_t *)(uintptr_t)at;}
static float from_double(uint64_t v){return value(r1_log_double_to_float_bits(v));}
static uint64_t promote(float v){return r1_binary32_to_binary64_bits(bits(v));}
static uint64_t square_root(uint64_t v){union {double f;uint64_t u;} x={.u=v};x.f=r1_native_sqrt(x.f);return x.u;}
static float adjusted(float confidence,float mean)
{
    uint64_t adjustment=square_root(promote(mean));
    adjustment=r1_format_double_multiply_bits(adjustment,UINT64_C(0x3fd0000000000000));
    adjustment=r1_format_double_multiply_bits(adjustment,UINT64_C(0x3fd3333340000000));
    return from_double(r1_binary64_subtract_bits(promote(confidence),adjustment));
}
uint32_t r1_gomore_stage_60680_native(uint32_t state,uint32_t elapsed,uint32_t input,uint32_t codes,uint32_t output)
{
    volatile struct {float confidence,rate;uint32_t reserved[9];} frame;
    _Static_assert(sizeof(frame)==44,"native estimator scratch reservation");
    frame.rate=0.0f;frame.confidence=0.0f;
    uint32_t flags=0;
    if(elapsed>1) {
        uint32_t missing=elapsed-1u;if(missing>20)missing=20;
        for(uint32_t i=0;i<missing;i++)(void)r1_gomore_modulo5_native((volatile void *)(uintptr_t)state,2,2);
    }
    uint32_t primary=byte(codes+2u),secondary=byte(codes+1u);
    (void)r1_gomore_modulo5_native((volatile void *)(uintptr_t)state,secondary,primary);
    float sum_primary=0.0f,sum_secondary=0.0f;
    for(uint32_t i=0;i<4;i++) {
        if(i<2){uint32_t code=byte(state+45u+i);sum_secondary=add((float)(code*code),sum_secondary);}
        uint32_t code=byte(state+41u+i);sum_primary=add((float)(code*code),sum_primary);
    }
    float primary_mean=mul(sum_primary,0.25f),secondary_mean=mul(sum_secondary,0.5f);
    if(byte(input+4u))flags=64;
    if(r1_gomore_optical_estimate_native(state+48u,elapsed,input,flags,&frame.rate,&frame.confidence))flags|=8;
    if(bits(frame.rate)+0xbf200000u>0xe80000u) {
        if(positive(frame.rate)&&positive(frame.confidence)) {
            if((int32_t)bits(frame.rate)>(int32_t)0x41c80000u)frame.rate=25.0f;
            else if((int32_t)bits(frame.rate)<(int32_t)0x40e00000u)frame.rate=7.0f;
        } else if(bits(frame.rate)!=0xbf800000u)frame.rate=-1.0f;
        flags|=16;
    }
    if(elapsed>1){r1_gomore_clear_two_native((volatile void *)(uintptr_t)state);flags|=32;}
    if((int32_t)bits(secondary_mean)>0x3f800000)frame.confidence=adjusted(frame.confidence,secondary_mean);
    if((int32_t)bits(primary_mean)>0x3f000000)frame.confidence=adjusted(frame.confidence,primary_mean);
    if(negative(frame.confidence)){frame.confidence=0.0f;frame.rate=-1.0f;}
    for(uint32_t i=1;i<5;i++) {
        put(state+(i-1u)*4u,word(state+i*4u));
        put(state+20u+(i-1u)*4u,word(state+20u+i*4u));
    }
    put(state+16u,bits(frame.rate));put(state+36u,bits(frame.confidence));
    if((int32_t)r1_gomore_encoded_count_native((volatile void *)(uintptr_t)state,5)<1) {
        put(output,bits(frame.rate));put(output+4u,bits(frame.confidence));
    } else {
        uint32_t selected=state+r1_gomore_argmax_native((volatile float *)(uintptr_t)(state+20u),5)*4u;
        uint32_t confidence=word(selected+20u);float threshold;
        if((int32_t)confidence>0x3f000000)threshold=0.5f;
        else threshold=from_double(r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(confidence),UINT64_C(0x3fe999999999999a)));
        uint32_t included=r1_gomore_threshold5_native(threshold,(volatile float *)(uintptr_t)state,(volatile float *)(uintptr_t)(state+20u),(volatile float *)(uintptr_t)output);
        float share=mul(divide((float)(int32_t)included,5.0f),value(0x3e99999a));
        uint64_t share64=promote(share);
        uint64_t weighted=r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(word(selected+20u)),UINT64_C(0x3fe6666666666666));
        put(output+4u,r1_log_double_to_float_bits(r1_format_double_add_bits(weighted,share64)));
    }
    return flags;
}

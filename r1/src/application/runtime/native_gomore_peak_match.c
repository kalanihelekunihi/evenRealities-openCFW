#include <stdint.h>
#include "native_float_bits.h"
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern void __aeabi_memclr(void *,uint32_t);
extern void *r1_native_memory_move(void *,const void *,uint32_t);
extern float r1_gomore_mean_native(uint32_t,uint32_t),r1_gomore_deviation_native(uint32_t,uint32_t),r1_gomore_median_native(uint32_t,uint32_t);
extern void r1_gomore_sort_float_subrange_native(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_quantized_argmin_native(uint32_t,uint32_t,uint32_t);
static __attribute__((noinline,noclone)) float add(float a,float b){return a+b;}
static __attribute__((noinline,noclone)) float sub(float a,float b){return a-b;}
static __attribute__((noinline,noclone)) float divide(float a,float b){return a/b;}
static __attribute__((noinline,noclone)) float madd(float acc,float a,float b){return acc+a*b;}
static __attribute__((noinline,noclone)) float convert(uint32_t value){return (float)(int32_t)value;}
static __attribute__((noinline,noclone)) uint32_t greater(float a,float b){return a>b;}
static __attribute__((noinline,noclone)) uint32_t less(float a,float b){return a<b;}
static uint32_t byte(uint32_t at){return *(volatile uint8_t *)(uintptr_t)at;}
static void put(uint32_t at,uint32_t value){*(volatile uint8_t *)(uintptr_t)at=(uint8_t)value;}
static float sample(uint32_t at){return *(volatile float *)(uintptr_t)at;}
static void store(uint32_t at,float value){*(volatile float *)(uintptr_t)at=value;}
static uint32_t bits(float value){union {float value;uint32_t bits;} x={.value=value};return x.bits;}
/* Native 0x27f0c carry: encoded ordering, including non-IEEE NaN encodings. */
static uint32_t carry(uint64_t a,uint64_t b)
{
    uint64_t ka=a>>63?a:UINT64_C(0x8000000000000000)-a;
    uint64_t kb=b>>63?b:UINT64_C(0x8000000000000000)-b;
    return kb>=ka;
}
static uint64_t scaled(float median,uint64_t factor)
{return r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(bits(median)),factor);}
uint32_t r1_gomore_peak_candidate_match_native(uint32_t signal,uint32_t candidates,uint32_t references,uint32_t candidate_count,volatile uint32_t reference_count,volatile uint32_t output,volatile uint32_t incoming_workspace)
{
    uint32_t workspace=incoming_workspace;
    volatile uint8_t local_refs[20],filtered[20];
    uint32_t filtered_count=0,a=0,b=0,n=0,result;
    store(output,0.0f);
    __aeabi_memclr((void *)filtered,20);__aeabi_memclr((void *)local_refs,20);
    if(byte(candidate_count)<2u)goto failure;
    uint32_t reference_size=byte(reference_count);
    if(reference_size<2u)goto failure;
    r1_native_memory_move((void *)local_refs,(const void *)(uintptr_t)references,reference_size);
    uint32_t original_refs=byte(reference_count);
    for(uint32_t i=0;i<25;i++) {
        if(i<byte(candidate_count))store(workspace+i*4u,sample(signal+byte(candidates+i)*4u));
        else store(workspace+i*4u,0.0f);
    }
    float deviation=r1_gomore_deviation_native(workspace,byte(candidate_count));
    float mean=r1_gomore_mean_native(workspace,byte(candidate_count));
    if(greater(deviation,mean)) {
        r1_gomore_sort_float_subrange_native(workspace,0,byte(candidate_count)-1u);
        uint64_t count=r1_unsigned32_to_binary64_bits(byte(candidate_count));
        uint32_t lower=r1_binary64_to_signed32_bits(r1_format_double_multiply_bits(count,UINT64_C(0x3fd0000000000000)));
        uint32_t upper=r1_binary64_to_signed32_bits(r1_format_double_multiply_bits(count,UINT64_C(0x3fe8000000000000)));
        float high=sample(workspace+upper*4u),low=sample(workspace+lower*4u);
        float difference=sub(high,low),sum=0.0f;
        for(uint32_t i=lower;(int32_t)i<=(int32_t)upper;i++)sum=add(sample(workspace+i*4u),sum);
        float threshold=madd(divide(sum,convert(upper-lower+1u)),difference,3.0f);
        for(uint32_t i=0;i<byte(candidate_count);i++) {
            uint32_t index=byte(candidates+i);
            if(less(sample(signal+index*4u),threshold))filtered[filtered_count++&255u]=(uint8_t)index;
        }
        filtered_count&=255u;
    } else {
        r1_native_memory_move((void *)filtered,(const void *)(uintptr_t)candidates,byte(candidate_count));
        filtered_count=byte(candidate_count);
    }
    if(filtered_count<2u)goto failure;
    __aeabi_memclr((void *)(uintptr_t)candidates,20);__aeabi_memclr((void *)(uintptr_t)references,20);
    for(uint32_t i=0;i<filtered_count-1u;i++)store(workspace+i*4u,convert((uint32_t)filtered[i+1]-(uint32_t)filtered[i]));
    float median=r1_gomore_median_native(workspace,filtered_count-1u);
    for(;a<filtered_count;a=(a+1u)&255u) {
        while(local_refs[b]<filtered[a]) {
            uint32_t diff=(uint32_t)filtered[a]-(uint32_t)local_refs[b];
            if(!carry(r1_signed32_to_binary64_bits(diff),scaled(median,UINT64_C(0x3fe8000000000000))))break;
            b=(b+1u)&255u;if(b>=original_refs)break;
        }
        if(b>=original_refs)break;
        uint32_t diff=(uint32_t)filtered[a]-(uint32_t)local_refs[b];
        if((int32_t)diff>0 && !carry(r1_signed32_to_binary64_bits(diff),scaled(median,UINT64_C(0x3fe8000000000000)))) {
            if(local_refs[b] && filtered[a]>12u) {
                put(candidates+n,filtered[a]);put(references+n,local_refs[b]);
                b=(b+1u)&255u;n=(n+1u)&255u;
            }
            continue;
        }
        uint32_t previous=n?byte(candidates+n-1u):0;
        uint32_t spacing=(uint32_t)filtered[a]-previous;
        if(carry(scaled(median,UINT64_C(0x3fe8000000000000)),r1_signed32_to_binary64_bits(spacing)))continue;
        if(carry(r1_signed32_to_binary64_bits((uint32_t)filtered[a]-previous),scaled(median,UINT64_C(0x3ff4000000000000))))continue;
        uint32_t valley=r1_gomore_quantized_argmin_native(signal,(previous+1u)&255u,filtered[a])&255u;
        uint32_t tail=(uint32_t)filtered[a]-valley;
        if(carry(scaled(median,UINT64_C(0x3fb999999999999a)),r1_signed32_to_binary64_bits(tail)))continue;
        if(carry(r1_signed32_to_binary64_bits((uint32_t)filtered[a]-valley),scaled(median,UINT64_C(0x3fe0000000000000))))continue;
        put(candidates+n,filtered[a]);put(references+n,valley);n=(n+1u)&255u;
    }
    if(n<2u)goto failure;
    put(reference_count,n);put(candidate_count,n);
    for(uint32_t i=0;i<n-1u;i++) {
        uint32_t left=byte(candidates+i),right=byte(candidates+i+1u);
        store(workspace+i*4u,convert(right-left));
    }
    store(output,r1_gomore_median_native(workspace,n-1u));result=0;goto publish_padding;
failure:
    put(reference_count,0);put(candidate_count,0);store(output,0.0f);result=1;
publish_padding:
    /* The following stock interval merger publishes these two reference bytes
       from entry SP-114 as record padding. Preserve that inter-call footprint
       with the compiler CFA rather than an uninitialized C object or SP asm. */
    *(volatile uint16_t *)(uintptr_t)((uint32_t)(uintptr_t)__builtin_dwarf_cfa()-114u)=
        (uint16_t)((uint32_t)local_refs[14]|((uint32_t)local_refs[15]<<8));
    return result;
}

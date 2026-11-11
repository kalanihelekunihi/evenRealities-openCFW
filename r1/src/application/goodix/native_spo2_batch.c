#include <stdint.h>
#include <stddef.h>
extern void __aeabi_memclr(void *,size_t);
static uint32_t word(uintptr_t p,uint32_t offset){return *(const volatile uint32_t *)(p+offset);}
static void put(uintptr_t p,uint32_t offset,uint32_t value){*(volatile uint32_t *)(p+offset)=value;}
static float load_float(uintptr_t p){return *(const volatile float *)p;}
static void store_float(uintptr_t p,float value){*(volatile float *)p=value;}
/* A separate ordinary C call keeps the accumulator as the first NaN operand. */
__attribute__((noinline)) static float ordered_add(float accumulator,float sample){return accumulator+sample;}
static uint32_t quotient(uint32_t n,uint32_t d){return d?n/d:0;}
static uint32_t signed_quotient(uint32_t n,uint32_t d)
{
    if(!d)return 0;
    uint32_t a=n>>31?0u-n:n,b=d>>31?0u-d:d;
    uint32_t q=a/b;return (n^d)>>31?0u-q:q;
}
uint32_t r1_goodix_spo2_batch(void *input,const void *descriptor,void *output)
{
    uintptr_t in=(uintptr_t)input,desc=(uintptr_t)descriptor,out=(uintptr_t)output;
    uint32_t period=word(desc,76),sequence=word(in,0);
    if(sequence-period*quotient(sequence,period)==0){
        __aeabi_memclr((void *)(uintptr_t)word(out,8),word(desc,0)*24u);
        __aeabi_memclr((void *)(uintptr_t)word(out,24),24);
        put(out,12,0);put(out,16,0);put(out,20,0);
    }
    for(uint32_t i=0;i<word(desc,0);++i){
        for(uint32_t off=8;off<=16;off+=8){
            uintptr_t src=(uintptr_t)word(in,8)+i*24u+off;
            uintptr_t dst=(uintptr_t)word(out,8)+i*24u+off;
            float sample=load_float(src),accumulator=load_float(dst);
            store_float(dst,ordered_add(accumulator,sample));
            accumulator=load_float(dst+4);sample=load_float(src+4);
            store_float(dst+4,ordered_add(accumulator,sample));
        }
    }
    put(out,12,word(out,12)+word(in,12));
    put(out,16,word(out,16)+word(in,16));
    put(out,20,word(out,20)+word(in,20));
    sequence=word(in,0);
    if(sequence-period*quotient(sequence,period)!=period-1u)return 3;
    *(volatile uint8_t *)(out+4)=*(const volatile uint8_t *)(in+4);
    put(out,0,quotient(word(in,0),period));
    for(uint32_t i=0;i<word(desc,0);++i){
        uintptr_t p=(uintptr_t)word(out,8)+i*24u+8;
        store_float(p,load_float(p)/(float)(int32_t)period);
        store_float(p+4,load_float(p+4)/(float)(int32_t)period);
        p=(uintptr_t)word(out,8)+i*24u+16;
        store_float(p,load_float(p)/(float)(int32_t)period);
        store_float(p+4,load_float(p+4)/(float)(int32_t)period);
    }
    uint32_t i=0,count;
    while((count=word(desc,0))>i){
        uintptr_t src=(uintptr_t)word(out,8)+i*24u+8;
        uintptr_t dst=word(out,24);
        float sample=load_float(src),accumulator=load_float(dst+8);
        store_float(dst+8,ordered_add(accumulator,sample));
        src=(uintptr_t)word(out,8)+i*24u+16;dst=word(out,24);
        sample=load_float(src);accumulator=load_float(dst+16);
        store_float(dst+16,ordered_add(accumulator,sample));++i;
    }
    uintptr_t summary=word(out,24);
    store_float(summary+8,load_float(summary+8)/(float)count);
    count=word(desc,0);summary=word(out,24);
    store_float(summary+16,load_float(summary+16)/(float)count);
    put(out,12,signed_quotient(word(out,12),period));
    put(out,16,signed_quotient(word(out,16),period));
    put(out,20,signed_quotient(word(out,20),period));
    return 0;
}

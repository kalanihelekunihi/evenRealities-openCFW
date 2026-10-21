/* Instruction-derived locked ADC control42ec0c..42ed60. Explicit scalar
 * FP operations retain original rounding, exception and lazy-cache ordering. */
#include "adc_control.h"
#define R(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
static float as_float(uint32_t bits) {union {uint32_t bits;float value;} x={.bits=bits};return x.value;}
static uint32_t as_bits(float value) {union {uint32_t bits;float value;} x={.value=value};return x.bits;}
static float single_add(float left,float right) {
    float result;__asm__ volatile("vadd.f32 %0, %1, %2" : "=t"(result) : "t"(left),"t"(right));return result;
}
static float single_multiply(float left,float right) {
    float result;__asm__ volatile("vmul.f32 %0, %1, %2" : "=t"(result) : "t"(left),"t"(right));return result;
}
static uint32_t single_equal(float left,float right) {
    uint32_t flags;__asm__ volatile("vcmp.f32 %1, %2\n\tvmrs APSR_nzcv, FPSCR\n\tmrs %0, APSR" : "=r"(flags) : "t"(left),"t"(right) : "cc");return (flags>>30)&1u;
}
__attribute__((noinline))
uint32_t opencfw_bl_adc_configure(uint32_t context,uint32_t request,void *arguments) {
    (void)R(context+4u); /* Original loads module before checking handle NULL. */
    if(!context || (R(context)&0x01ffffffu)!=0x01afafafu)return 2;
    uint32_t op=(uint8_t)request;uintptr_t args=(uintptr_t)arguments;
    if(op==0) {
        if(R(args+4)>=0x100000u || R(args+8)>=0x100000u)return 5;
        R(0x4003802cu)=R(args+4)&0xfffffu;
        R(0x40038030u)=R(args+8)&0xfffffu;
        R(0x40038034u)=B(args);return 0;
    }
    if(op>3)return 6;
    if(!arguments)return 6;
    uint32_t sentinel_offset=op==1?8u:12u;
    if(!single_equal(as_float(R(args+sentinel_offset)),as_float(OPENCFW_ADC_SENTINEL_BITS)))return 7;
    if(op==2) {
        R(args)=R(0x20026fc0u);R(args+4)=R(0x20026fc4u);R(args+8)=R(0x20026fc8u);
        R(args+12)=B(0x20026fccu);return 0;
    }
    if(op==3) {
        R(args)=R(0x20026fe0u);R(args+4)=R(0x20026fe4u);R(args+8)=0;R(args+12)=0;return 0;
    }
    float input=as_float(R(args));
    float ate=as_float(R(0x20026fc0u));
    float measured=as_float(R(0x20026fc4u));
    float offset=as_float(R(0x20026fc8u));
    float cache=as_float(R(0x20027028u));
    if(single_equal(cache,as_float(0))) {
        R(0x20027028u)=0xc3910000u;
        float sum=single_add(measured,offset);
        float product=single_multiply(sum,as_float(R(0x20027028u)));
        R(0x20027028u)=as_bits(product);
        float intercept=single_add(as_float(R(0x20027028u)),ate);
        R(0x20027028u)=as_bits(intercept);
    }
    float result=single_multiply(input,as_float(0x43910000u));
    result=single_add(result,as_float(R(0x20027028u)));
    result=single_add(result,as_float(0xc3889333u));
    R(args+4)=as_bits(result);return 0;
}

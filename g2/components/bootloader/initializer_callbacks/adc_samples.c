/* Instruction-derived locked ADC sample/lifecycle bodies; no physical FIFO model here. */
#include "adc_samples.h"
#include "../clock_manager/clock_manager.h"
#define R(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
static float as_float(uint32_t n) {union {uint32_t bits;float value;} x={.bits=n};return x.value;}
static uint32_t valid(uint32_t context) {(void)R(context+4u);return context&&(R(context)&0x01ffffffu)==0x01afafafu;}
static float unsigned_to_float(uint32_t n) {float f;__asm__ volatile("vmov %0, %1\n\tvcvt.f32.u32 %0, %0":"=t"(f):"r"(n));return f;}
static uint32_t float_to_unsigned(float f) {uint32_t n;__asm__ volatile("vcvt.u32.f32 %1, %1\n\tvmov %0, %1":"=r"(n),"+t"(f));return n;}
static float subtract(float x,float y) {float f;__asm__ volatile("vsub.f32 %0, %1, %2":"=t"(f):"t"(x),"t"(y));return f;}
static float divide(float x,float y) {float f;__asm__ volatile("vdiv.f32 %0, %1, %2":"=t"(f):"t"(x),"t"(y));return f;}
static float multiply(float x,float y) {float f;__asm__ volatile("vmul.f32 %0, %1, %2":"=t"(f):"t"(x),"t"(y));return f;}
static float accumulate(float x,float y,float z) {__asm__ volatile("vmla.f32 %0, %1, %2":"+t"(x):"t"(y),"t"(z));return x;}
__attribute__((noinline))
uint32_t opencfw_boot_adc_correct_sample(uint32_t word,uint32_t enabled) {
    if(!B(0x20027199u)||!(uint8_t)enabled)return word;
    uint32_t scaled=(((word>>6)&0x3fffu)*1190u)>>12;
    float sample=unsigned_to_float(scaled);
    sample=divide(sample,subtract(as_float(0x3f800000u),as_float(R(0x20026fe4u))));
    sample=accumulate(sample,as_float(R(0x20026fe0u)),as_float(0xc47a0000u));
    sample=multiply(sample,as_float(0x45800000u));
    sample=divide(sample,as_float(0x4494c000u));
    return (word&0xfff00000u)|((float_to_unsigned(sample)<<6)&0x3ffffu);
}
__attribute__((noinline))
uint32_t opencfw_bl_adc_enumerate(uint32_t context,uint32_t full_sample,const uint32_t *buffer,uint32_t *count,opencfw_boot_adc_sample *output) {
    uintptr_t n=(uintptr_t)count,p=(uintptr_t)buffer,out=(uintptr_t)output;
    uint32_t capacity=R(n); /* Original precedes context/output guards. */
    if(!valid(context))return 2;
    if(!output)return 6;
    R(n)=0;
    if(!buffer) {
        uint32_t word;
        do {
            word=R(0x4003803cu);
            uint32_t slot=(word>>28)&7u;
            uint32_t input=(R(0x4003800cu+slot*4u)>>8)&15u;
            word=opencfw_boot_adc_correct_sample(word,input!=8u);
            R(out+4)=(word>>28)&7u;
            R(out)=(uint8_t)full_sample?(word&0xfffffu):((word>>6)&0x3fffu);
            out+=8;R(n)=R(n)+1;
            if(((word>>20)&255u)==0)break;
        }while(R(n)<capacity);
    }else {
        uint32_t temperature_mask=0;
        for(uint32_t slot=0;slot<8;slot++)if(((R(0x4003800cu+slot*4u)>>8)&15u)==8u)temperature_mask|=1u<<slot;
        do {
            uint32_t slot=(R(p)>>28)&7u;
            uint32_t word=R(p)&0xfffffu;
            word=opencfw_boot_adc_correct_sample(word,((temperature_mask>>slot)&1u)^1u);
            R(out)=(word>>6)&0x3fffu;R(out+4)=slot;
            p+=4;out+=8;R(n)=R(n)+1;
        }while(R(n)<capacity);
    }
    return 0;
}
__attribute__((noinline))
uint32_t opencfw_bl_adc_activate(uint32_t context) {
    if(!valid(context))return 2;
    if((R(context)>>25)&1u)return 0;
    R(0x40038000u)=R(0x40038000u)|1u;
    R(context)=R(context)|0x2000000u;return 0;
}
__attribute__((noinline))
uint32_t opencfw_bl_adc_enable(uint32_t context) {
    if(!valid(context))return 2;
    if(!(R(0x40038000u)&1u))return 7;
    R(0x40038040u)=R(0x40038040u)|0x80000000u;return 0;
}
__attribute__((noinline))
uint32_t opencfw_bl_adc_disable(uint32_t context) {
    if(!valid(context))return 2;
    R(0x40038040u)=R(0x40038040u)&~0x80000000u;return 0;
}
__attribute__((noinline))
uint32_t opencfw_bl_adc_command(uint32_t context) {
    if(!valid(context))return 2;
    R(0x40038008u)=0x37u;return 0;
}
__attribute__((noinline))
uint32_t opencfw_bl_adc_normalize(uint32_t context) {
    if(!valid(context))return 2;
    R(0x40038000u)=R(0x40038000u)&~4u;
    R(0x40038000u)=R(0x40038000u)&~1u;
    if(((R(0x40038000u)>>24)&7u)==3u)R(0x40038000u)=R(0x40038000u)&~0x7000000u;
    (void)clock_release(4u,15u);
    R(context)=R(context)&~0x2000000u;return 0;
}

#include <stdint.h>
extern float r1_math_invalid32(void);
static __attribute__((noinline,noclone)) int32_t quantize(float value)
{
    union {float value;uint32_t bits;} input={.value=value};
    uint32_t magnitude=input.bits&0x7fffffffu;
    /* VCVT saturates infinities/overflow and returns zero for NaNs.  Keep the
       C cast inside its defined domain; invalid arithmetic supplies IOC. */
    if(magnitude>0x7f800000u) {r1_math_invalid32();return 0;}
    if((input.bits>>31) ? magnitude>0x4f000000u : magnitude>=0x4f000000u) {
        r1_math_invalid32();return input.bits>>31 ? INT32_MIN : INT32_MAX;
    }
    return (int32_t)value;
}
static __attribute__((noinline,noclone)) float convert(int32_t value){return (float)value;}
static __attribute__((noinline,noclone)) uint32_t less(float a,float b){return a<b;}
uint32_t r1_gomore_quantized_argmin_native(uint32_t values,uint32_t begin,uint32_t end)
{
    if(end<begin)return UINT32_MAX;
    uint32_t result=begin;
    int32_t minimum=quantize(*(volatile float *)(uintptr_t)(values+begin*4u));
    for(uint32_t index=begin;(int32_t)index<(int32_t)end;index++) {
        float threshold=convert(minimum);
        float value=*(volatile float *)(uintptr_t)(values+index*4u);
        if(less(value,threshold)) {result=index;minimum=quantize(value);}
    }
    return result;
}

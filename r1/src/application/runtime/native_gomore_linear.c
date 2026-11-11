/* Stock interpolation: signed counts, wrapped arithmetic, ordered non-fused FP. */
#include <stdint.h>
#include <stddef.h>
extern void *r1_native_memory_move(void *,const void *,size_t);
static __attribute__((noinline,noclone)) float mul(float a,float b){return a*b;}
static __attribute__((noinline,noclone)) float sub(float a,float b){return a-b;}
static __attribute__((noinline,noclone)) float add(float a,float b){return a+b;}
static __attribute__((noinline,noclone)) float fraction(float left,float ratio,float index){return ratio*index-left;}
static int32_t truncate_position(float value)
{
    union {float f;uint32_t u;} bits={.f=value};
    uint32_t magnitude=bits.u&0x7fffffffu;
    if (magnitude>0x7f800000u || (!(bits.u>>31) && magnitude>=0x4f000000u) || ((bits.u>>31) && magnitude>0x4f000000u)) {
        volatile float zero=0.0f;volatile float invalid=zero/zero;(void)invalid;
        return magnitude>0x7f800000u?0:(bits.u>>31)?INT32_MIN:INT32_MAX;
    }
    return (int32_t)value;
}
uint32_t r1_gomore_linear_native(uint32_t source,uint32_t input,uint32_t output,uint32_t total,uint32_t destination)
{
    if (input==output) return (uint32_t)(uintptr_t)r1_native_memory_move((void *)(uintptr_t)destination,(void *)(uintptr_t)source,total*4u);
    int32_t blocks=0;
    if (input) blocks=(total==0x80000000u && input==0xffffffffu)?INT32_MIN:(int32_t)total/(int32_t)input;
    uint32_t produced=output*(uint32_t)blocks;
    volatile float ratio=0.0f;
    if (output) ratio=(float)(int32_t)input/(float)(int32_t)output;
    for (uint32_t i=0;(int32_t)i<(int32_t)produced;i++) {
        float position=mul(ratio,(float)(int32_t)i);
        uint32_t left=(uint32_t)truncate_position(position),right=left+1u;
        if ((int32_t)right>=(int32_t)total) right=total-1u;
        float part=fraction((float)(int32_t)left,ratio,(float)(int32_t)i);
        float right_value=*(volatile float *)(uintptr_t)(source+right*4u);
        float left_value=*(volatile float *)(uintptr_t)(source+left*4u);
        float difference=sub(right_value,left_value);
        float weighted=mul(difference,part);
        *(volatile float *)(uintptr_t)(destination+i*4u)=add(left_value,weighted);
    }
    return produced;
}

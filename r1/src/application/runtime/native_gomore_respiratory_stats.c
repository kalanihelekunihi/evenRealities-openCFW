#include "native_gomore_respiratory_stats.h"
static __attribute__((noinline,noclone)) int greater(float value,float maximum){return value>maximum;}
static __attribute__((noinline,noclone)) int at_least(float value,float threshold){return value>=threshold;}
static __attribute__((noinline,noclone)) float add(float a,float b){return a+b;}
struct __attribute__((packed,may_alias)) stats_word {uint32_t value;};
uint32_t r1_gomore_encoded_count_native(volatile const void *values,uint32_t length)
{
    uintptr_t source=(uintptr_t)values;
    uint32_t count=0;
    for(uint32_t i=0;(int32_t)i<(int32_t)length;i++)
        if (((volatile struct stats_word *)(uintptr_t)(source+i*4u))->value+0xbf200000u<=0xe80000u) count++;
    return count;
}
uint32_t r1_gomore_argmax_native(volatile const float *values,uint32_t length)
{
    uintptr_t source=(uintptr_t)values;
    uint32_t selected=length-1u;float maximum=0.0f;
    for(uint32_t i=length-1u;(int32_t)i>=0;i--) {
        float value=*(volatile float *)(uintptr_t)(source+i*4u);
        if(greater(value,maximum)){selected=i;maximum=value;}
    }
    return selected;
}
uint32_t r1_gomore_threshold5_native(float threshold,volatile const float *values,volatile const float *comparisons,volatile float *output)
{
    uintptr_t source=(uintptr_t)values,weights=(uintptr_t)comparisons,destination=(uintptr_t)output;
    *(volatile float *)(uintptr_t)destination=0.0f;uint32_t count=0;
    for(uint32_t i=0;i<5;i++) {
        float weight=*(volatile float *)(uintptr_t)(weights+i*4u);
        if(at_least(weight,threshold)) {
            float accumulator=*(volatile float *)(uintptr_t)destination;
            float value=*(volatile float *)(uintptr_t)(source+i*4u);
            *(volatile float *)(uintptr_t)destination=add(accumulator,value);count++;
        }
    }
    float total=*(volatile float *)(uintptr_t)destination;
    *(volatile float *)(uintptr_t)destination=total/(float)(int32_t)count;
    return count;
}

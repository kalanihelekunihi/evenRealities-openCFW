#include <stdint.h>
typedef int32_t (*r1_comparator)(const void *,const void *);
extern void r1_native_qsort(uint8_t *,uint32_t,uint32_t,r1_comparator);
extern float r1_native_powf(float,float),r1_native_sqrtf(float);
static __attribute__((noinline,noclone)) float add(float a,float b){return a+b;}
static __attribute__((noinline,noclone)) float sub(float a,float b){return a-b;}
static __attribute__((noinline,noclone)) float mul(float a,float b){return a*b;}
static __attribute__((noinline,noclone)) float divide(float a,float b){return a/b;}
static __attribute__((noinline,noclone)) float convert(uint32_t value){return (float)(int32_t)value;}
static __attribute__((noinline,noclone)) uint32_t greater(float a,float b){return a>b;}
static __attribute__((noinline,noclone)) uint32_t less(float a,float b){return a<b;}
static float sample(uint32_t at){return *(volatile float *)(uintptr_t)at;}
__attribute__((noinline,noclone))
float r1_gomore_mean_native(uint32_t values,uint32_t count)
{
    float sum=0.0f;
    for(uint32_t i=0;(int32_t)i<(int32_t)count;i++) {float value=sample(values+i*4u);sum=add(value,sum);}
    return count?divide(sum,convert(count)):0.0f;
}
int32_t r1_gomore_float_compare_native(const void *left,const void *right)
{
    float a=*(volatile const float *)left;
    float b=*(volatile const float *)right;
    if(greater(a,b)) return 1;
    return less(a,b)?-1:0;
}
float r1_gomore_median_native(uint32_t values,uint32_t count)
{
    r1_native_qsort((uint8_t *)(uintptr_t)values,count,4,r1_gomore_float_compare_native);
    uint32_t middle=(uint32_t)((int32_t)count/2);
    uint32_t at=values+middle*4u;
    if((count&0x80000001u)==1u) return sample(at);
    float upper=sample(at),lower=sample(at-4u);
    return mul(add(lower,upper),0.5f);
}
float r1_gomore_deviation_native(uint32_t values,uint32_t count)
{
    float mean=r1_gomore_mean_native(values,count),sum=0.0f;
    volatile float variance=0.0f;
    for(uint32_t i=0;(int32_t)i<(int32_t)count;i++) {
        float value=sample(values+i*4u);
        float power=r1_native_powf(sub(value,mean),2.0f);
        sum=add(power,sum);
    }
    if(count!=1u) variance=divide(sum,convert(count-1u));
    return r1_native_sqrtf(variance);
}

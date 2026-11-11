/* Native correlation/scaling support for the sensor feature extractor.
 * Positive correlation/normalization lengths; output correlation span is
 * 2*max(lengths)-1 words, with padding untouched. See the probe receipt. */
#include "native_autocorrelation.h"
#include <stdint.h>
#include <stddef.h>
extern void *goodix_mem_malloc(int32_t);
extern void goodix_mem_free(void *);
extern void *memmove(void *,const void *,size_t);
extern void r1_goodix_native_maximum_index(const void *,uint32_t,void *,void *);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t x){*(volatile uint32_t *)(p+o)=x;}
static float F(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static uint32_t B(float x){union{uint32_t u;float f;}v={.f=x};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
static float dot(uintptr_t first,uintptr_t second,uint32_t count)
{
 float sum=0.0f;while(count--){float a=F(W(first,0)),b=F(W(second,0));first+=4u;second+=4u;sum=add(sum,mul(a,b));}return sum;
}
void r1_goodix_native_full_correlation(const void *first,uint32_t first_count,const void *second,uint32_t second_count,void *output)
{
 uintptr_t large,small,destination;uint32_t large_count,small_count,advance;
 if(first_count<second_count){large=(uintptr_t)second;small=(uintptr_t)first;large_count=second_count;small_count=first_count;destination=(uintptr_t)output+(first_count+second_count-2u)*4u;advance=0xfffffffcu;}
 else{large=(uintptr_t)first;small=(uintptr_t)second;large_count=first_count;small_count=second_count;destination=(uintptr_t)output+(first_count-second_count)*4u;advance=4u;}
 for(uint32_t remaining=small_count-1u,block=1;remaining;--remaining,++block){float v=dot(large,small+(small_count-block)*4u,block);S(destination,0,B(v));destination+=advance;}
 for(uint32_t j=0,remaining=large_count-small_count+1u;remaining;--remaining,++j){float v=dot(large+j*4u,small,small_count);S(destination,0,B(v));destination+=advance;}
 for(uint32_t j=large_count-small_count+1u,remaining=small_count-1u;remaining;--remaining,++j){float v=dot(large+j*4u,small,remaining);S(destination,0,B(v));destination+=advance;}
}
void r1_goodix_native_vector_scale(float factor,const void *input,void *output,uint32_t count)
{
 uintptr_t p=(uintptr_t)input,out=(uintptr_t)output;while(count--){float value=F(W(p,0));p+=4u;S(out,0,B(mul(value,factor)));out+=4u;}
}
void r1_goodix_native_vector_scale_veneer(float factor,const void *input,void *output,uint32_t count)
{
 r1_goodix_native_vector_scale(factor,input,output,count);
}
void r1_goodix_native_normalized_autocorrelation(const void *input,uint32_t count,void *output)
{
 void *temporary=goodix_mem_malloc((int32_t)(count*8u-4u));r1_goodix_native_full_correlation(input,count,input,count,temporary);memmove(output,temporary,count*4u);goodix_mem_free(temporary);
 uint32_t maximum=0,index=0;r1_goodix_native_maximum_index(output,count,&maximum,&index);
 if((int32_t)maximum>=(int32_t)0x358637bdu){float gain=divide(1.0f,F(maximum));r1_goodix_native_vector_scale_veneer(gain,output,output,count);}
}

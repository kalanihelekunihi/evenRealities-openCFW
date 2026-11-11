/* Native confidence statistics: nine entries,388 instruction bytes.
 * Preserve sample-first NaN priority, distinct count edge cases, strided
 * incremental arithmetic and live output/count aliases. No assembly/state.
 * See r1/docs/reference/goodix-spo2-statistics-c-review.md.
 */
#include "native_spo2_statistics.h"
#include <stdint.h>
#include "../runtime/native_f32_integer.h"
extern float r1_native_sqrtf(float);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint32_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t x){*(volatile uint32_t *)(p+o)=x;}
static float F(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static uint32_t B(float x){union{uint32_t u;float f;}v={.f=x};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float sub(float a,float b){volatile float v=a-b;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
__attribute__((noinline)) static float from_unsigned(uint32_t x){volatile float v=(float)x;return v;}
float r1_goodix_native_array_sum(const void *input,uint32_t count)
{
 uintptr_t p=(uintptr_t)input;float total=0.0f;
 for(uint32_t i=0;i<count;++i)total=add(F(W(p,i*4u)),total);
 return total;
}
float r1_goodix_native_array_mean(const void *input,uint32_t count)
{
 float total=r1_goodix_native_array_sum(input,count);float denominator=from_unsigned(count?count:1u);return divide(total,denominator);
}
float r1_goodix_native_array_mean_inline(const void *input,uint32_t count)
{
 return r1_goodix_native_array_mean(input,count);
}
float r1_goodix_native_array_variance(const void *input,uint32_t count)
{
 uintptr_t p=(uintptr_t)input;float mean=r1_goodix_native_array_mean_inline(input,count),total=0.0f;
 for(uint32_t i=0;i<count;++i){float delta=sub(F(W(p,i*4u)),mean);total=add(total,mul(delta,delta));}
 float denominator=from_unsigned(count==1?1u:count-1u);return divide(total,denominator);
}
float r1_goodix_native_array_standard_deviation(float count,const void *input)
{
 uint32_t n=r1_native_f32_integer_bits(B(count),1);return r1_native_sqrtf(r1_goodix_native_array_variance(input,n));
}
float r1_goodix_native_incremental_standard_deviation(const void *input,int32_t stride,uint32_t count)
{
 uintptr_t p=(uintptr_t)input;float mean=0.0f,variance=0.0f;
 for(uint32_t i=0;i<count;++i){uint32_t offset=(i*(uint32_t)stride)*4u;float delta=sub(F(W(p,offset)),mean);float n=from_unsigned(i+1u);mean=add(divide(delta,n),mean);}
 for(uint32_t i=0;i<count;++i){uint32_t offset=(i*(uint32_t)stride)*4u;float delta=sub(F(W(p,offset)),mean);float update=add(F(B(variance)^0x80000000u),mul(delta,delta));float n=from_unsigned(i+1u);variance=add(divide(update,n),variance);}
 float n=from_unsigned(count),denominator=from_unsigned(count-1u);return r1_native_sqrtf(mul(divide(n,denominator),variance));
}
void r1_goodix_native_window_standard_deviation(const void *record,void *output)
{
 uintptr_t p=(uintptr_t)record;if(H(p,4)){S((uintptr_t)output,0,0);uint32_t count=H(p,4);uintptr_t data=W(p,0);float value=r1_goodix_native_incremental_standard_deviation((void *)data,1,count);S((uintptr_t)output,0,B(value));}
}
float r1_goodix_native_window_last(const void *record)
{
 uintptr_t p=(uintptr_t)record;uint32_t count=H(p,4);if(!count)return 0.0f;return F(W(W(p,0),count*4u-4u));
}
uint32_t r1_goodix_native_window_count(const void *record)
{
 return H((uintptr_t)record,4);
}

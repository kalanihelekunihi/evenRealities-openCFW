/* Native peak-feature metrics0x37a84. Preserve sentinel mutation,
 * signaling FP status,raw-bit score cap and ordered input/output aliases.
 * See r1/docs/reference/goodix-peak-metrics-c-review.md.
 */
#include "native_spo2_peak_metrics.h"
#include <stdint.h>
extern float r1_native_sqrtf(float);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint32_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t x){*(volatile uint32_t *)(p+o)=x;}
static void SH(uintptr_t p,uint32_t o,uint32_t x){*(volatile uint16_t *)(p+o)=(uint16_t)x;}
static float F(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static uint32_t B(float x){union{uint32_t u;float f;}v={.f=x};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float sub(float a,float b){volatile float v=a-b;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
__attribute__((noinline)) static float from_unsigned(uint32_t x){volatile float v=(float)x;return v;}
__attribute__((noinline)) static uint32_t compare(uint32_t a,uint32_t b)
{
 uint32_t fp=__builtin_arm_get_fpscr(),flags;
 if(fp&(1u<<24)){
  if((a&0x7fffffffu)&&(a&0x7fffffffu)<0x800000u){a&=0x80000000u;fp|=128u;}
  if((b&0x7fffffffu)&&(b&0x7fffffffu)<0x800000u){b&=0x80000000u;fp|=128u;}
 }
 if((a&0x7fffffffu)>0x7f800000u||(b&0x7fffffffu)>0x7f800000u){flags=0x30000000u;fp|=1u;}
 else if(a==b||!((a|b)&0x7fffffffu))flags=0x60000000u;
 else{int less=(a>>31)!=(b>>31)?(a>>31)!=0:((a>>31)?a>b:a<b);flags=less?0x80000000u:0x20000000u;}
 __builtin_arm_set_fpscr((fp&0x0fffffffu)|flags);return flags;
}
void r1_goodix_native_peak_feature_metrics(void *values,void *indices,uint32_t count,uint32_t length,void *rms,void *quality)
{
 uintptr_t v=(uintptr_t)values,ix=(uintptr_t)indices;S(v,count*4u,0x3f800000u);SH(ix,count*2u,length-1u);
 float squares=0.0f,absolute=0.0f;uint32_t used=0;
 for(uint32_t i=0;i<count+1u;++i){
  uint32_t value=W(v,i*4u);if(compare(value,0)!=0x20000000u)continue;
  float point=from_unsigned(H(ix,i*2u)+1u);float n=from_unsigned(length);float fraction=divide(point,n);float difference=sub(F(value),fraction);
  squares=add(squares,mul(difference,difference));
  if(!(compare(B(difference),0)&0x20000000u))difference=sub(fraction,F(value));
  ++used;absolute=add(difference,absolute);
 }
 if(!used){S((uintptr_t)rms,0,0);S((uintptr_t)quality,0,0);return;}
 float n=from_unsigned(used);S((uintptr_t)rms,0,B(r1_native_sqrtf(divide(squares,n))));n=from_unsigned(used);float mean=divide(absolute,n);
 if((int32_t)B(mean)>(int32_t)0x3f000000u)mean=.5f;
 float scaled=mul(mean,2.0f);float result=add(100.0f,F(B(mul(scaled,100.0f))^0x80000000u));S((uintptr_t)quality,0,B(result));
}

/* Native SpO2 quality 0x88e80 and logistic 0x3efd8.
 * Preserve live record loads, signed raw clamps and binary32 score boundaries. */
#include <stdint.h>
#include "native_spo2_quality.h"
#include "../runtime/native_f32_integer.h"
extern float r1_native_expf(float);
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint16_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static uint8_t U(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static void SB(uintptr_t p,uint32_t o,uint8_t v){*(volatile uint8_t *)(p+o)=v;}
static float F(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float sub(float a,float b){volatile float v=a-b;return v;}
__attribute__((noinline)) static float nmul(float a,float b){volatile float v=-(a*b);return v;}
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
static int lt(uint32_t f){return ((f>>31)^((f>>28)&1u))!=0;}
static int gt(uint32_t f){return !(f&0x40000000u)&&!lt(f);}

float r1_goodix_native_quality_logistic(float value,float pivot,float below,float above)
{
 uint32_t flags=compare(B(value),B(pivot));float slope=(flags&0x20000000u)?above:below;
 float delta=sub(value,pivot);float exponential=r1_native_expf(nmul(slope,delta));
 return divide(100.0f,add(exponential,1.0f));
}
static uint32_t score(uint32_t previous,float value,float pivot,float below,float above,uint64_t weight)
{
 float transformed=r1_goodix_native_quality_logistic(value,pivot,below,above);
 uint64_t product=r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(B(transformed)),weight);
 return r1_log_double_to_float_bits(r1_format_double_add_bits(r1_binary32_to_binary64_bits(previous),product));
}
static float reciprocal(uint32_t value)
{
 if((int32_t)value<=(int32_t)0x358637bdu)value=0x358637bdu;
 return divide(1.0f,F(value));
}
uint32_t r1_goodix_spo2_quality(const void *descriptor,void *context,uint32_t iteration,void *summary)
{
 (void)context;(void)iteration;uintptr_t d=(uintptr_t)descriptor,s=(uintptr_t)summary;
 uint32_t common=U(s,3)>W(d,48)?1u:0u;
 if((uint32_t)(int32_t)(int16_t)H(s,4)>W(d,52))common|=2u;
 uintptr_t record=W(s,8);uint32_t flags=0;
 if((int32_t)W(record,20)>0||(int32_t)W(record,0)>0)flags|=4u;
 if(!U(record,37)||!U(record,17))flags|=8u;
 float threshold=divide((float)U(d,65),100.0f);uint32_t metric=W(record,32);
 if(gt(compare(metric,B(threshold)))||metric==0xbf800000u)flags|=16u;
 else{metric=W(record,12);if(gt(compare(metric,B(threshold)))||metric==0xbf800000u)flags|=16u;}
 if((int8_t)U(record,40)<(int)U(d,66))flags|=32u;
 SB(record,41,(uint8_t)((common|flags)&U(d,67)));
 float pivot=F(0x41855556u),below=F(0x3f0f5c27u),above=F(0x3bba9c69u);
 uint32_t result=score(0,reciprocal(W(record,32)),pivot,below,above,UINT64_C(0x3fd999999999999a));
 result=score(result,reciprocal(W(record,12)),pivot,below,above,UINT64_C(0x3fd999999999999a));
 result=score(result,(float)(int8_t)U(record,40),75.0f,F(0x3d98ead6u),F(0x3e656041u),UINT64_C(0x3fc999999999999a));
 if((int32_t)result>(int32_t)0x42c80000u)result=0x42c80000u;
 SB(record,42,(uint8_t)r1_native_f32_integer_bits(result,1));return 0;
}

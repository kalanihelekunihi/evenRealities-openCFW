/* Native Gaussian interval0x3e6c8. Retain single-precision steps,
 * signaling loop comparisons, unconditional normalization/division and actual
 * double exp plus software double arithmetic. No assembly or owned state.
 * See r1/docs/reference/goodix-gaussian-interval-c-review.md.
 */
#include "native_gaussian_interval.h"
#include <stdint.h>
#include "../runtime/native_float_bits.h"
extern float r1_native_sqrtf(float);
extern double r1_native_exp(double);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t),r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
static float F(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static uint32_t B(float x){union{uint32_t u;float f;}v={.f=x};return v.u;}
static double D(uint64_t x){union{uint64_t u;double d;}v={.u=x};return v.d;}
static uint64_t DB(double x){union{uint64_t u;double d;}v={.d=x};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float sub(float a,float b){volatile float v=a-b;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
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
float r1_goodix_native_gaussian_interval(float lower,float upper,float mean,float sigma,float step)
{
 float position=add(lower,step),first=position,total=0.0f;
 float denominator=mul(r1_native_sqrtf(F(0x40c90fdbu)),sigma);
 uint32_t flags=compare(B(sigma),0);float gain=divide(1.0f,denominator);
 if(flags&0x40000000u)return total;
 for(;;){
  flags=compare(B(first),B(position));if((flags&0x20000000u)&&!(flags&0x40000000u))break;
  flags=compare(B(position),B(upper));if((flags&0x20000000u)&&!(flags&0x40000000u))break;
  float left=sub(mean,position),right=sub(position,mean);
  float exponent=divide(mul(left,right),mul(mul(sigma,sigma),2.0f));
  uint64_t step64=r1_binary32_to_binary64_bits(B(step));
  uint64_t exponential=DB(r1_native_exp(D(r1_binary32_to_binary64_bits(B(exponent)))));
  uint64_t product=r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(B(gain)),exponential);
  product=r1_format_double_multiply_bits(product,step64);
  uint32_t sum=r1_log_double_to_float_bits(r1_format_double_add_bits(r1_binary32_to_binary64_bits(B(total)),product));
  position=add(position,step);total=F(sum);
 }
 return total;
}

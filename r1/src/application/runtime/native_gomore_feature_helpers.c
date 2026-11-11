#include <stdint.h>
#include "native_float_bits.h"
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t),r1_format_double_multiply_bits(uint64_t,uint64_t),r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
extern float r1_math_invalid32(void);
extern void r1_gomore_sort_float_subrange_native(uint32_t,uint32_t,uint32_t);
#define FP __attribute__((noinline,noclone))
static FP float mul(float a,float b){return a*b;}
static FP float sub(float a,float b){return a-b;}
static FP float divide(float a,float b){return a/b;}
static FP float madd(float acc,float a,float b){return acc+a*b;}
static FP float msub(float acc,float a,float b){return acc-a*b;}
static FP float convert(uint32_t x){return (float)(int32_t)x;}
static FP uint32_t equal(float a,float b){return a==b;}
static uint32_t bits(float x){union {float value;uint32_t bits;} u={.value=x};return u.bits;}
static float value(uint32_t x){union {float value;uint32_t bits;} u={.bits=x};return u.value;}
static uint64_t promote(float x){return r1_binary32_to_binary64_bits(bits(x));}
static float narrow(uint64_t x){return value(r1_log_double_to_float_bits(x));}
static float sample(uint32_t at){return *(volatile float *)(uintptr_t)at;}
static void store(uint32_t at,float x){*(volatile float *)(uintptr_t)at=x;}
static FP uint32_t quantize(float x)
{
 uint32_t raw=bits(x),magnitude=raw&0x7fffffffu;
 if(magnitude>0x7f800000u){r1_math_invalid32();return 0;}
 if(raw>>31 ? magnitude>0x4f000000u : magnitude>=0x4f000000u) {
  r1_math_invalid32();return raw>>31?0x80000000u:0x7fffffffu;
 }
 return (uint32_t)(int32_t)x;
}
uint32_t r1_gomore_sleep_iir2_filter_native(uint32_t samples,uint32_t count)
{
 float x0=0.0f,x1=0.0f,y0=0.0f,y1=0.0f;
 for(uint32_t i=0;(int32_t)i<(int32_t)count;i++) {
  float input=sample(samples+i*4u);
  uint64_t acc=promote(mul(value(0x3dbba7a8),input));
  acc=r1_format_double_add_bits(promote(mul(x0,0.0f)),acc);
  acc=r1_binary64_reverse_subtract_bits(promote(mul(y0,value(0xbfe71223))),acc);
  acc=r1_format_double_add_bits(promote(mul(x1,value(0xbdbba7a8))),acc);
  acc=r1_binary64_reverse_subtract_bits(promote(mul(y1,value(0x3f511616))),acc);
  x1=x0;y1=y0;x0=input;y0=narrow(acc);
  store(samples+i*4u,y0);
 }
 return count;
}
float r1_gomore_sorted_percentile_native(uint32_t samples,uint32_t count,uint32_t percentile)
{
 r1_gomore_sort_float_subrange_native(samples,0,count-1u);
 uint32_t last=count-1u;
 volatile float step=count==1u?0.0f:divide(100.0f,convert(last));
 if(percentile==0u)return sample(samples);
 if(percentile==100u)return sample(samples+last*4u);
 float position=equal(step,0.0f)?0.0f:divide(convert(percentile),step);
 uint32_t index=quantize(position);
 float remainder=msub(convert(percentile),convert(index),step);
 if((int32_t)bits(remainder)<(int32_t)0x3dcccccdu)return sample(samples+index*4u);
 float lower=sample(samples+index*4u),upper=sample(samples+(index+1u)*4u),slope=0.0f;
 if(!equal(step,0.0f))slope=divide(sub(upper,lower),step);
 return madd(lower,slope,remainder);
}
float r1_gomore_bounded_linear_complement_native(float primary,float secondary)
{
 if((int32_t)bits(primary)>(int32_t)0x40a00000u || (int32_t)bits(secondary)>(int32_t)0x3f333333u)return 0.0f;
 uint64_t secondary_part=r1_format_double_divide_bits(promote(secondary),UINT64_C(0x3fe6666666666666));
 uint64_t normalized=r1_format_double_add_bits(promote(divide(primary,5.0f)),secondary_part);
 uint64_t scaled=r1_format_double_multiply_bits(normalized,UINT64_C(0x3fe0000000000000));
 return narrow(r1_binary64_reverse_subtract_bits(scaled,UINT64_C(0x3ff0000000000000)));
}

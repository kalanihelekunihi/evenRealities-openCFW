/* Native model quantization, residual addition and dequantization callbacks. */
#include <stdint.h>
#include "native_model_quantization.h"
#include "../runtime/native_f32_integer.h"
extern float r1_native_fminf(float,float),r1_native_fmaxf(float,float),r1_native_floorf(float);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static uint32_t I(uintptr_t p,uint32_t o){return (uint32_t)(int32_t)*(const volatile int8_t *)(p+o);}
static void SB(uintptr_t p,uint32_t o,uint8_t v){*(volatile uint8_t *)(p+o)=v;}
static float F(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float sub(float a,float b){volatile float v=a-b;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
__attribute__((noinline)) static float nmul(float a,float b){volatile float v=-(a*b);return v;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
__attribute__((noinline)) static float from_signed(uint32_t a){volatile float v=(float)(int32_t)a;return v;}
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


uint32_t r1_goodix_native_quantize_round(float value)
{
 uint32_t flags=compare(B(value),0);float rounded=add(gt(flags)?.5f:-.5f,value);return r1_native_f32_integer_bits(B(rounded),0);
}
uint32_t r1_goodix_native_quantize_index(float value,float minimum,float maximum)
{
 float width=r1_native_fmaxf(F(0x38d1b717u),sub(maximum,minimum));float inverse=divide(255.0f,width);
 return r1_goodix_native_quantize_round(mul(sub(value,minimum),inverse));
}
void r1_goodix_native_quantization_parameters(float minimum,float maximum,void *low,void *high,void *step,void *inverse)
{
 float lower=r1_native_fminf(0.0f,minimum);float upper=r1_native_fmaxf(0.0f,maximum);
 float width=r1_native_fmaxf(F(0x38d1b717u),sub(upper,lower));float scale=divide(255.0f,width);
 if(!(compare(B(lower),0)&0x20000000u)){
  float point=nmul(lower,scale),rounded=r1_native_floorf(point),fraction=sub(point,rounded);
  if(B(fraction)+0xc77fffffu<0x06fffbffu){
   uint32_t flags=compare(B(rounded),0);int change_lower=(flags&0x40000000u)||lt(flags);
   if(!change_lower&&(int32_t)B(rounded)<=(int32_t)0x437d0000u){
    float a=sub(fraction,1.0f);float b=mul(fraction,upper);a=mul(a,lower);change_lower=lt(compare(B(a),B(b)));
   }
   if(change_lower){float a=add(rounded,1.0f);a=mul(a,upper);float b=sub(rounded,254.0f);lower=divide(a,b);width=sub(upper,lower);}
   else{width=divide(mul(lower,-255.0f),rounded);upper=add(lower,width);}
   scale=divide(255.0f,width);
  }
 }
 S((uintptr_t)low,0,B(lower));S((uintptr_t)high,0,B(upper));S((uintptr_t)step,0,B(divide(width,255.0f)));S((uintptr_t)inverse,0,B(scale));
}
static uint8_t clipped_zero_point(uint32_t value)
{
 if((int32_t)value<0)return 0x80u;if((int32_t)value>255)return 0x7fu;return (uint8_t)(value-128u);
}
uint32_t r1_goodix_native_graph_quantize(const void *operation,const void *inputs,const void *outputs)
{
 uintptr_t op=(uintptr_t)operation,ins=(uintptr_t)inputs,outs=(uintptr_t)outputs;
 uintptr_t input=W(W(ins,0),16),output=W(W(outs,0),16);uint32_t low=0,high=0,step=0,inverse=0;
 r1_goodix_native_quantization_parameters(F(W(op,0)),F(W(op,4)),&low,&high,&step,&inverse);
 uintptr_t descriptor=W(ins,0);uint32_t count=W(descriptor,4)*W(descriptor,8)*W(descriptor,12);
 for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){float scaled=mul(sub(F(W(input,i*4u)),F(low)),F(inverse));uint32_t value=r1_goodix_native_quantize_round(scaled);SB(output,i,clipped_zero_point(value));}
 uintptr_t range=W(W(outs,4),16);S(range,0,low);S(range,4,high);S(W(outs,0),0,1);return 0;
}
uint32_t r1_goodix_native_graph_quantized_add(const void *operation,const void *inputs,const void *outputs)
{
 uintptr_t op=(uintptr_t)operation,ins=(uintptr_t)inputs,outs=(uintptr_t)outputs,d=W(ins,0);
 uintptr_t first=W(d,16),second=W(W(ins,8),16),output=W(W(outs,0),16);uint32_t count=W(d,8)*W(d,12);
 uintptr_t a=W(W(ins,4),16);float low=F(W(a,0)),high=F(W(a,4));float first_step=divide(sub(high,low),255.0f);uint32_t first_zero=r1_goodix_native_quantize_index(0.0f,low,high)-128u;
 uintptr_t b=W(W(ins,12),16);low=F(W(b,0));high=F(W(b,4));float second_step=divide(sub(high,low),255.0f);uint32_t second_zero=r1_goodix_native_quantize_index(0.0f,low,high)-128u;
 float target_low=F(W(op,4)),target_high=F(W(op,8));float target_step=divide(sub(target_high,target_low),255.0f);uint32_t target_zero=r1_goodix_native_quantize_index(0.0f,target_low,target_high)-128u;
 for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){float first_value=from_signed(I(first,i)-first_zero);uint32_t second_value=I(second,i)-second_zero;float value=mul(first_value,first_step);float other=from_signed(second_value);value=add(value,mul(other,second_step));value=divide(value,target_step);uint32_t code=r1_goodix_native_quantize_round(value)+target_zero;int32_t saturated=__builtin_arm_ssat((int32_t)code,8);SB(output,i,(uint8_t)saturated);}
 uintptr_t range=W(W(outs,4),16);S(range,0,B(target_low));S(range,4,B(target_high));return 0;
}
uint32_t r1_goodix_native_graph_dequantize(const void *operation,const void *inputs,const void *outputs)
{
 (void)operation;uintptr_t ins=(uintptr_t)inputs,d=W(ins,0),input=W(d,16),out=W(W((uintptr_t)outputs,0),16);uint32_t count=W(d,8)*W(d,12);
 uintptr_t range=W(W(ins,4),16);float low=F(W(range,0)),high=F(W(range,4));float width=r1_native_fmaxf(F(0x38d1b717u),sub(high,low));float step=divide(width,255.0f);
 uint32_t zero=r1_goodix_native_quantize_round(divide(F(B(low)^0x80000000u),step));uint32_t offset=(uint32_t)(int32_t)(int8_t)clipped_zero_point(zero);
 for(uint32_t i=0;(int32_t)i<(int32_t)count;++i)S(out,i*4u,B(mul(from_signed(I(input,i)-offset),step)));
 return 0;
}
const uint32_t r1_goodix_graph_quantizer_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_graph_quantize;
const uint32_t r1_goodix_graph_pair_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_graph_quantized_add;
const uint32_t r1_goodix_graph_vector_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_graph_dequantize;

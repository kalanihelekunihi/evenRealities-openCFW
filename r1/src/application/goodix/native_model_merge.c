#include <stdint.h>
#include <stddef.h>
#include "native_model_quantization.h"
extern void *memmove(void *,const void *,size_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static float F(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float sub(float a,float b){volatile float v=a-b;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
__attribute__((noinline)) static float from_signed(int32_t a){volatile float v=(float)a;return v;}
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
static int close_bounds(uint32_t a,uint32_t b)
{
 float difference=sub(F(a),F(b));
 if(!(compare(B(difference),0)&0x20000000u))difference=sub(F(b),F(a));
 return (int32_t)B(difference)<(int32_t)0x358637bdu;
}
uint32_t r1_goodix_native_graph_merge(const void *operation,const void *inputs,const void *outputs,uint32_t operands)
{
 (void)operation;uintptr_t ins=(uintptr_t)inputs,outs=(uintptr_t)outputs,output=W(outs,0);
 uint32_t batches=W(output,4),columns=W(W(ins,0),12),lower=0,upper=0;
 for(uint32_t input=0;input<operands;++input){
  uintptr_t range=W(W(ins,input*8u+4u),16);
  if(input==0){lower=W(range,0);upper=W(range,4);}
  else{uint32_t low=W(range,0);if(!(compare(low,lower)&0x20000000u))lower=low;uint32_t high=W(range,4);if(gt(compare(high,upper)))upper=high;}
 }
 uintptr_t target=W(output,16);
 for(uint32_t batch=0;(int32_t)batch<(int32_t)batches;++batch){
  for(uint32_t input=0;input<operands;++input){
   uintptr_t range=W(W(ins,input*8u+4u),16);uint32_t low=W(range,0),high=W(range,4);uintptr_t descriptor=W(ins,input*8u);uint32_t count=W(descriptor,8)*columns;
   if(close_bounds(upper,high)&&close_bounds(lower,low)){
    uintptr_t data=W(descriptor,16);(void)memmove((void *)target,(const void *)(data+batch*count),count);target+=count;
   }else{
    float input_width=sub(F(high),F(low)),output_width=sub(F(upper),F(lower)),delta=sub(F(low),F(lower));
    float input_step=divide(input_width,255.0f);uintptr_t data=W(descriptor,16)+batch*count;
    float output_step=divide(output_width,255.0f),scale=divide(input_step,output_step),offset=divide(delta,output_step);offset=add(offset,mul(scale,128.0f));
    for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){float value=from_signed(*(const volatile int8_t *)(data+i));value=add(offset,mul(value,scale));uint32_t code=r1_goodix_native_quantize_round(value);uint8_t result=(int32_t)code<0?0x80u:(int32_t)code>255?0x7fu:(uint8_t)(code-128u);*(volatile uint8_t *)target=result;++target;}
   }
  }
 }
 uintptr_t range=W(W(outs,4),16);S(range,0,lower);S(range,4,upper);return 0;
}
const uint32_t r1_goodix_graph_merge_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_graph_merge;

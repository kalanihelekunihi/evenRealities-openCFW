#include <stdint.h>
#include <stddef.h>
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
extern float r1_native_expf(float);
uint32_t r1_goodix_native_model_dense(const void *operation,const void *inputs,const void *outputs)
{
 uintptr_t op=(uintptr_t)operation,ins=(uintptr_t)inputs,outs=(uintptr_t)outputs,input=W(ins,0);
 uint32_t span=W(input,8)*W(input,12);uintptr_t data=W(input,16),output=W(outs,0);
 uintptr_t weights=W(op,12),bias=W(op,16);uint32_t units=W(op,0);uintptr_t target=W(output,16);
 for(uint32_t unit=0;(int32_t)unit<(int32_t)units;++unit){
  float value=F(0);
  for(uint32_t i=0;(int32_t)i<(int32_t)span;++i)value=add(value,mul(F(W(data,i*4u)),F(W(weights,(unit*span+i)*4u))));
  value=add(F(W(bias,unit*4u)),value);S(target,unit*4u,B(value));
 }
 if(*(const volatile uint8_t *)(op+5)==1){
  float slope=F(W(op,8));
  for(uint32_t i=0;;++i){
   uintptr_t d=W(outs,0);uint32_t n=W(d,4)*W(d,8)*W(d,12);if((int32_t)n<=(int32_t)i)break;
   float value=F(W(target,i*4u));if(!(compare(B(value),0)&0x20000000u))value=mul(value,slope);S(target,i*4u,B(value));
  }
 }
 if(*(const volatile uint8_t *)(op+5)==2){
  for(uint32_t i=0;;++i){
   uintptr_t d=W(outs,0);uint32_t n=W(d,4)*W(d,8)*W(d,12);if((int32_t)n<=(int32_t)i)break;
   uint32_t negated=W(target,i*4u)^0x80000000u;if((int32_t)negated>=(int32_t)0x42b00000u)negated=0x42b00000u;
   float value=r1_native_expf(F(negated));value=add(value,1.0f);value=divide(1.0f,value);S(target,i*4u,B(value));
  }
 }
 return 0;
}
const uint32_t r1_goodix_model_dense_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_model_dense;

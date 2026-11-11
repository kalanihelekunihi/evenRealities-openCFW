#include <stdint.h>
extern float r1_native_expf(float);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static float F(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float sub(float a,float b){volatile float v=a-b;return v;}
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
static int lt(uint32_t f){return ((f>>31)^((f>>28)&1u))!=0;}
static int gt(uint32_t f){return !(f&0x40000000u)&&!lt(f);}
uint32_t r1_goodix_native_model_softmax(const void *operation,const void *inputs,const void *outputs)
{
 (void)operation;uintptr_t source=W(W((uintptr_t)inputs,0),16),out=W((uintptr_t)outputs,0),target=W(out,16);uint32_t count=W(out,8);
 float maximum=F(0xff7fffffu),sum=0.0f;
 for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){uint32_t value=W(source,i*4u);if(gt(compare(value,B(maximum))))maximum=F(value);}
 for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){float value=sub(F(W(source,i*4u)),maximum);if((int32_t)B(value)>=(int32_t)0x42b00000u)value=F(0x42b00000u);float exponential=r1_native_expf(value);sum=add(exponential,sum);S(target,i*4u,B(exponential));}
 for(uint32_t i=0;(int32_t)i<(int32_t)count;++i)S(target,i*4u,B(divide(F(W(target,i*4u)),sum)));
 return 0;
}
const uint32_t r1_goodix_model_softmax_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_model_softmax;

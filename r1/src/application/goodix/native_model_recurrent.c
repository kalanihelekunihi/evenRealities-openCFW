#include <stdint.h>
#include "native_model_recurrent_support.h"
extern float r1_native_expf(float),r1_native_tanhf(float);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static float F(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float sub(float a,float b){volatile float v=a-b;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
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
static int gt(uint32_t f){return !(f&0x40000000u)&&(((f>>31)^((f>>28)&1u))==0);}
uint32_t r1_goodix_native_model_recurrent(const void *operation,const void *inputs,const void *outputs)
{
 uintptr_t op=(uintptr_t)operation,desc=W((uintptr_t)inputs,0);uint32_t units=W(op,0),columns=W(desc,8);uintptr_t input=W(desc,16),recurrent_weights=W(op,12),parameters=W(op,16),input_weights=W(op,8),state=W(op,4),output=W(W((uintptr_t)outputs,0),16);
 uint32_t n3=units*3u,n2=units*2u;uintptr_t ranges=parameters+units*16u,coefficients=ranges+24u;
 float input_low=F(W(ranges,0)),input_high=F(W(ranges,4)),input_weight_step=divide(sub(input_high,input_low),255.0f);
 uint32_t input_zero=r1_goodix_native_recurrent_zero_point(0.0f,input_low,input_high);
 float recurrent_low=F(W(ranges,8)),recurrent_high=F(W(ranges,12)),recurrent_weight_step=divide(sub(recurrent_high,recurrent_low),255.0f);
 uint32_t recurrent_zero=r1_goodix_native_recurrent_zero_point(0.0f,recurrent_low,recurrent_high);
 if(input_zero!=128u||recurrent_zero!=128u)return 0xf000000eu;
 uint32_t state_zero=r1_goodix_native_recurrent_zero_point(0.0f,F(W(ranges,8)),F(W(ranges,12)));
 uintptr_t input_scales=input+columns*4u,recurrent_scales=input_scales+n3*4u,dots=recurrent_scales+n3*4u,gates=dots+units*8u,state_bytes=gates+units*8u,candidate=state_bytes+((units+3u)&~3u),input_bytes=candidate+units*4u;
 float recurrent_factor=mul(F(0x3c010204u),recurrent_weight_step);
 for(uint32_t i=0;(int32_t)i<(int32_t)n3;++i)S(recurrent_scales,i*4u,B(mul(recurrent_factor,F(W(coefficients,(n3+i)*4u)))));
 uint32_t low=0,high=0;
 for(uint32_t i=0;(int32_t)i<(int32_t)columns;++i){uint32_t value=W(input,i*4u);if(!(compare(value,low)&0x20000000u))low=value;if(gt(compare(value,high)))high=value;}
 r1_goodix_native_recurrent_range_adjust(&low,&high,3);
 float step=divide(sub(F(high),F(low)),255.0f);if((int32_t)B(step)<(int32_t)0x358637bdu)step=F(0x358637bdu);
 uint32_t zero=r1_goodix_native_recurrent_round(divide(F(low^0x80000000u),step));
 float input_factor=mul(step,input_weight_step);
 for(uint32_t i=0;(int32_t)i<(int32_t)n3;++i)S(input_scales,i*4u,B(mul(input_factor,F(W(coefficients,i*4u)))));
 for(uint32_t i=0;(int32_t)i<(int32_t)columns;++i){uint32_t q=r1_goodix_native_recurrent_round(divide(F(W(input,i*4u)),step))+zero;*(volatile uint8_t *)(input_bytes+i)=(uint8_t)__builtin_arm_usat((int32_t)q,8);}
 for(uint32_t i=0;(int32_t)i<(int32_t)units;++i){float v=add(from_signed(state_zero),mul(F(W(state,i*4u)),127.0f));uint32_t q=r1_goodix_native_recurrent_round(v);*(volatile uint8_t *)(state_bytes+i)=(uint8_t)__builtin_arm_usat((int32_t)q,8);}
 r1_goodix_native_recurrent_matrix((void *)input_bytes,(void *)input_weights,(void *)dots,1,columns,n2,zero,input_zero);
 for(uint32_t i=0;(int32_t)i<(int32_t)n2;++i){float v=add(F(W(parameters,i*4u)),mul(from_signed(W(dots,i*4u)),F(W(input_scales,i*4u))));S(gates,i*4u,B(v));}
 r1_goodix_native_recurrent_matrix((void *)state_bytes,(void *)recurrent_weights,(void *)dots,1,units,n2,state_zero,recurrent_zero);
 for(uint32_t i=0;(int32_t)i<(int32_t)n2;++i){float v=add(F(W(gates,i*4u)),mul(from_signed(W(dots,i*4u)),F(W(recurrent_scales,i*4u))));S(gates,i*4u,B(v));}
 for(uint32_t i=0;(int32_t)i<(int32_t)n2;++i){uint32_t bits=W(gates,i*4u)^0x80000000u;if((int32_t)bits>=(int32_t)0x42b00000u)bits=0x42b00000u;float v=divide(1.0f,add(r1_native_expf(F(bits)),1.0f));S(gates,i*4u,B(v));}
 r1_goodix_native_recurrent_matrix((void *)input_bytes,(void *)(input_weights+columns*units*2u),(void *)dots,1,columns,units,zero,input_zero);
 for(uint32_t i=0;(int32_t)i<(int32_t)units;++i){float v=add(F(W(parameters,(n2+i)*4u)),mul(from_signed(W(dots,i*4u)),F(W(input_scales,(n2+i)*4u))));S(candidate,i*4u,B(v));}
 r1_goodix_native_recurrent_matrix((void *)state_bytes,(void *)(recurrent_weights+units*units*2u),(void *)dots,1,units,units,state_zero,recurrent_zero);
 for(uint32_t i=0;(int32_t)i<(int32_t)units;++i){float v=add(F(W(parameters,(units*3u+i)*4u)),mul(from_signed(W(dots,i*4u)),F(W(recurrent_scales,(n2+i)*4u))));v=add(F(W(candidate,i*4u)),mul(v,F(W(gates,(units+i)*4u))));S(candidate,i*4u,B(v));}
 for(uint32_t i=0;(int32_t)i<(int32_t)units;++i)S(candidate,i*4u,B(r1_native_tanhf(F(W(candidate,i*4u)))));
 for(uint32_t i=0;(int32_t)i<(int32_t)units;++i){float z=F(W(gates,i*4u));float v=mul(z,F(W(state,i*4u)));v=add(v,mul(sub(1.0f,z),F(W(candidate,i*4u))));S(state,i*4u,B(v));S(output,i*4u,B(v));}
 return 0;
}
const uint32_t r1_goodix_model_recurrent_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_model_recurrent;

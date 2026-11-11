#include <stdint.h>
extern float r1_native_fmaxf(float,float);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint32_t U(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static float F(uint32_t u){union{uint32_t u;float f;}v={.u=u};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
__attribute__((noinline)) static float signed_float(uint32_t a){volatile float v=(float)(int32_t)a;return v;}
uint32_t r1_goodix_native_graph_float_pool(const void *operation,const void *inputs,const void *outputs)
{
 uintptr_t op=(uintptr_t)operation;uint32_t stride=U(op,2),kernel=U(op,1),padding=U(op,3);
 uintptr_t in=W((uintptr_t)inputs,0),out=W((uintptr_t)outputs,0);uint32_t input_columns=W(in,12),rows=W(out,8),columns=W(out,12);
 uintptr_t source=W(in,16),target=W(out,16);uint32_t mode=U(op,0);
 if(mode==0u||mode==1u){
  for(uint32_t column=0;(int32_t)column<(int32_t)columns;++column){
   uint32_t begin=column*stride-padding,end=begin+kernel;
   if((int32_t)end>(int32_t)input_columns)end=input_columns;
   for(uint32_t row=0;(int32_t)row<(int32_t)rows;++row){
    float value=mode==0u?F(0xff7fffffu):0.0f;uint32_t count=0;
    for(uint32_t at=begin;(int32_t)at<(int32_t)end;++at){
     float next=F(W(source,(row*input_columns+at)*4u));
     value=mode==0u?r1_native_fmaxf(value,next):add(value,next);++count;
    }
    if(mode==1u)value=divide(value,signed_float(count));
    S(target,(row*columns+column)*4u,B(value));
   }
  }
 }
 return 0;
}
const uint32_t r1_goodix_graph_alternate_pool_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_graph_float_pool;

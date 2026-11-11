#include <stdint.h>
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static float F(uint32_t u){union{uint32_t u;float f;}v={.u=u};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float product(float a,float b){volatile float v=a*b;return v;}
uint32_t r1_goodix_native_graph_scale(const void *operation,const void *inputs,const void *outputs)
{
 (void)operation;uintptr_t ins=(uintptr_t)inputs,first=W(ins,0),out=W((uintptr_t)outputs,0),second=W(ins,4);
 uintptr_t source=W(first,16);uint32_t rows=W(first,8),columns=W(first,12);uintptr_t target=W(out,16);uint32_t count=rows*columns;
 uint32_t other_rows=W(second,8),other_columns=W(second,12);uintptr_t weights=W(second,16);
 if(other_rows+other_columns==3u){
  float scalar=F(W(weights,0));
  for(uint32_t i=0;(int32_t)i<(int32_t)count;++i)S(target,i*4u,B(product(F(W(source,i*4u)),scalar)));
 }else if(other_rows==1u){
  for(uint32_t row=0;(int32_t)row<(int32_t)rows;++row){
   uintptr_t input=source+(row*other_columns)*4u,output=target+(row*other_columns)*4u;
   for(uint32_t column=0;(int32_t)column<(int32_t)W(W(ins,4),12);++column){
    float value=F(W(input,column*4u)),weight=F(W(weights,column*4u));S(output,column*4u,B(product(value,weight)));
   }
  }
 }
 return 0;
}
const uint32_t r1_goodix_graph_tail_vector_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_graph_scale;

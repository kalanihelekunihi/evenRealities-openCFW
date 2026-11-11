#include <stdint.h>
#include "native_model_i8_convolution.h"
#include <stddef.h>
#include "native_model_recurrent_support.h"
#include "../runtime/native_f32_integer.h"
extern void *memmove(void *,const void *,size_t);
extern void *memset(void *,int,size_t);
extern float r1_native_fmaxf(float,float);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static uint32_t byte(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static uint32_t I(uintptr_t p){return (uint32_t)(int32_t)*(const volatile int8_t *)p;}
static float F(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float sub(float a,float b){volatile float v=a-b;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
__attribute__((noinline)) static float from_signed(uint32_t a){volatile float v=(float)(int32_t)a;return v;}
uint32_t r1_goodix_native_i8_round(float value){return r1_goodix_native_recurrent_round(value);}
uint32_t r1_goodix_native_i8_range_adjust(void *minimum,void *maximum,uint32_t policy){return r1_goodix_native_recurrent_range_adjust(minimum,maximum,policy);}
uint32_t r1_goodix_native_i8_clip(uint32_t code)
{
 if((int32_t)code<0)return 0xffffff80u;
 if((int32_t)code>255)return 127;
 return code-128u;
}
static uint8_t scaled(uint32_t accumulator,uint32_t multiplier)
{
 int64_t product=(int64_t)(int32_t)accumulator*(int64_t)multiplier;
 uint32_t code=(uint32_t)((uint64_t)(product+INT64_C(0x40000000))>>31);
 return (uint8_t)r1_goodix_native_i8_clip(code);
}
uint32_t r1_goodix_native_graph_i8_convolution(const void *operation,const void *inputs,const void *outputs)
{
 uintptr_t op=(uintptr_t)operation,ins=(uintptr_t)inputs,outs=(uintptr_t)outputs,d=W(ins,0);
 uint32_t rows=W(d,8),columns=W(d,12),element=W(d,0);uintptr_t data=W(d,16);
 uint32_t padded=columns+byte(op,2)+byte(op,3),span=rows*columns,padded_span=rows*padded;
 uintptr_t in_range=W(W(ins,4),16);float input_low=F(W(in_range,0)),input_width=sub(F(W(in_range,4)),input_low);
 float inverse=divide(255.0f,r1_native_fmaxf(F(0x38d1b717u),input_width));uint32_t zero=r1_goodix_native_i8_round(mul(F(B(input_low)^0x80000000u),inverse))-128u;uintptr_t original=0;
 if(span!=padded_span){
  uintptr_t outd=W(outs,0),out=W(outd,16),live_data=W(W(ins,0),16);
  if(out>=live_data&&out<live_data+padded_span){original=out;S(outd,16,live_data+padded_span);}
  for(int32_t row=(int32_t)(rows-1u);row>=0;--row){uintptr_t p=W(W(ins,0),16),target=p+padded*(uint32_t)row+byte(op,2);memmove((void *)target,(void *)(p+columns*(uint32_t)row),columns*element);memset((void *)(target-byte(op,2)),(int)(int8_t)zero,byte(op,2));memset((void *)(target+columns),(int)(int8_t)zero,byte(op,3));}
 }
 float input_step=divide(input_width,255.0f);uint32_t groups=byte(op,6),ip=groups?byte(op,4)/groups:0,up=groups?byte(op,5)/groups:0,kernel=byte(op,0),outcols=W(W(outs,0),12),total=groups*up;
 uintptr_t weight_data=W(op,12),bias_data=W(op,16);uint32_t weight_words=(groups*ip*kernel*up+3u)>>2;
 float weight_low=F(W(weight_data,weight_words*4u)),weight_high=F(W(weight_data,weight_words*4u+4u));float product_step=mul(input_step,divide(sub(weight_high,weight_low),255.0f));
 uint32_t low=W(bias_data,total*4u+8u),high=W(bias_data,total*4u+12u);r1_goodix_native_i8_range_adjust(&low,&high,3);
 float output_step=divide(sub(F(high),F(low)),255.0f),factor=mul(F(0x4f000000u),divide(product_step,output_step));uintptr_t coefficients=W(op,12)+weight_words*4u+8u;
 uint32_t table[128];memset(table,0,sizeof(table));
 for(uint32_t u=0;(int32_t)u<(int32_t)total;++u){float value=mul(F(W(coefficients,u*4u)),factor);uint32_t scale=0;if((int32_t)B(value)>=(int32_t)0x3f000000u)scale=r1_native_f32_integer_bits(B(add(value,.5f)),1);if(scale>=0x7fffffffu)scale=0x7fffffffu;table[u]=scale;}
 bias_data=W(op,16);float bias_low=F(W(bias_data,total*4u)),bias_high=F(W(bias_data,total*4u+4u));float bias_step=divide(mul(sub(bias_high,bias_low),F(0x2f800000u)),product_step),point=divide(F(low),product_step);
 for(uint32_t u=0;(int32_t)u<(int32_t)total;++u){float v=mul(from_signed(W(bias_data,u*4u)),bias_step),coefficient=F(W(coefficients,u*4u));v=sub(divide(v,coefficient),divide(point,coefficient));table[total+u]=r1_goodix_native_i8_round(v);}
 weight_data=W(op,12);uintptr_t target=W(W(outs,0),16);
 if(kernel==5){
  if(zero){for(uint32_t u=0;u<up;++u){uint32_t sum=0;for(uint32_t i=0;i<ip*5u;++i)sum+=I(weight_data+u*ip*5u+i);table[total+u]-=zero*sum;}}
  if(ip==1||ip==4){for(uint32_t u=0;u<up;++u){uint32_t multiplier=table[u];for(uint32_t col=0;(int32_t)col<(int32_t)outcols;++col){uint32_t value=table[total+u];for(uint32_t i=0;i<ip;++i)for(uint32_t k=0;k<5;++k)value+=I(data+i*padded+col+k)*I(weight_data+(u*ip+i)*5u+k);*(volatile uint8_t *)(target+u*outcols+col)=scaled(value,multiplier);}}}
 }else if(kernel==3){
  if(groups==1){for(uint32_t u=0;u<up;++u){uint32_t multiplier=table[u];for(uint32_t col=0;(int32_t)col<(int32_t)outcols;++col){uint32_t value=table[total+u];for(uint32_t i=0;i<ip;++i)for(uint32_t k=0;k<3;++k)value+=(I(data+i*padded+col+k)-zero)*I(weight_data+(u*ip+i)*3u+k);*(volatile uint8_t *)(target+u*outcols+col)=scaled(value,multiplier);}}}
  else{for(uint32_t g=0;g<groups;++g)for(uint32_t u=0;u<up;++u)for(uint32_t k=0;k<3;++k)table[total+g*up+u]-=zero*I(weight_data+(g*up+u)*3u+k);for(uint32_t g=0;g<groups;++g){uint32_t multiplier=table[g];for(uint32_t col=0;(int32_t)col<(int32_t)outcols;++col){uint32_t value=table[total+g];for(uint32_t k=0;k<3;++k)value+=I(data+g*padded+col+k)*I(weight_data+g*3u+k);*(volatile uint8_t *)(target+g*outcols+col)=scaled(value,multiplier);}}}
 }else if(kernel==1){
  for(uint32_t u=0;u<up;++u)for(uint32_t i=0;i<ip;++i)table[total+u]-=zero*I(weight_data+u*ip+i);
  for(uint32_t u=0;u<up;++u){uint32_t multiplier=table[u];if(ip==1||ip==2){for(uint32_t col=0;(int32_t)col<(int32_t)outcols;col+=4u){uint32_t value[4]={table[total+u],table[total+u],table[total+u],table[total+u]};for(uint32_t i=0;i<ip;++i){uint32_t w=I(weight_data+u*ip+i);for(uint32_t k=0;k<4;++k)value[k]+=I(data+i*padded+col+k)*w;}for(uint32_t k=0;k<4;++k)*(volatile uint8_t *)(target+u*outcols+col+k)=scaled(value[k],multiplier);}}
   else{for(uint32_t col=0;(int32_t)col<(int32_t)outcols;++col){uint32_t value=table[total+u];for(uint32_t i=0;i<ip;++i)value+=I(data+i*padded+col)*I(weight_data+u*ip+i);*(volatile uint8_t *)(target+u*outcols+col)=scaled(value,multiplier);}}}
 }
 if(span!=padded_span){for(uint32_t row=0;(int32_t)row<(int32_t)rows;++row){uintptr_t p=W(W(ins,0),16);memmove((void *)(p+row*columns),(void *)(p+row*padded+byte(op,2)),columns*element);}if(original){uintptr_t p=W(outs,0);uint32_t count=W(p,0)*W(p,12)*W(p,8);memmove((void *)original,(void *)(uintptr_t)W(p,16),count);S(W(outs,0),16,original);}}
 uintptr_t out_range=W(W(outs,4),16);S(out_range,0,low);S(out_range,4,high);return 0;
}
const uint32_t r1_goodix_graph_aligned_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_graph_i8_convolution;

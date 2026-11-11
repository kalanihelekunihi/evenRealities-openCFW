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
extern void *memset(void *,int,size_t);
static uint32_t byte(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
uint32_t r1_goodix_native_graph_convolution(const void *operation,const void *inputs,const void *outputs)
{
 uintptr_t op=(uintptr_t)operation,ins=(uintptr_t)inputs,outs=(uintptr_t)outputs,d=W(ins,0);
 uint32_t rows=byte(d,8),columns=byte(d,12),element=byte(d,0);
 uint32_t padded=(columns+byte(op,2)+byte(op,3))&255u,span=rows*columns,padded_span=rows*padded;
 uintptr_t data=W(d,16),original=0;
 if(span!=padded_span){
  uintptr_t outd=W(outs,0),out=W(outd,16);
  if(out>data&&out<data+padded_span){original=out;S(outd,16,data+padded_span*4u);}
  data=W(W(ins,0),16);
  for(int32_t row=(int32_t)rows-1;row>=0;--row){
   uintptr_t p=W(W(ins,0),16),target=p+(uint32_t)row*padded*4u+byte(op,2)*4u;
   memmove((void *)target,(void *)(p+(uint32_t)row*columns*4u),columns*element);
   uint32_t left=byte(op,2);memset((void *)(target-left*4u),0,left*element);
   memset((void *)(target+columns*4u),0,byte(op,3)*element);
  }
 }
 uintptr_t outd=W(outs,0);uint32_t outspan=W(outd,8)*W(outd,12),groups=byte(op,6),in_per_group=groups?byte(op,4)/groups:0,out_per_group=groups?byte(op,5)/groups:0;
 uint32_t stride=byte(op,1),kernel=byte(op,0),outcols=byte(outd,12);uintptr_t weights=W(op,12),bias=W(op,16),target=W(outd,16);
 if(kernel==1||kernel==3|| (kernel==5&&groups==1)){
  uint32_t group_count=kernel==3?groups:1;
  for(uint32_t group=0;group<group_count;++group){
   uint32_t dynamic=(kernel==3||kernel==5)&&groups==1;
   for(uint32_t unit=0;;++unit){
    uint32_t units=dynamic?byte(op,5):out_per_group;if((int32_t)unit>=(int32_t)units)break;
    uint32_t channel=group*out_per_group+unit;float bias_value=F(W(bias,channel*4u));
    for(uint32_t col=0;(int32_t)col<(int32_t)outcols;++col){
     float value=F(0);
     for(uint32_t input=0;(int32_t)input<(int32_t)in_per_group;++input){
      for(uint32_t k=0;k<kernel;++k){
       uintptr_t a=data+((group*in_per_group+input)*padded+col*stride+k)*4u;
       uintptr_t w=weights+(group*out_per_group*kernel+(unit*in_per_group+input)*kernel+k)*4u;
       value=add(value,mul(F(W(a,0)),F(W(w,0))));
      }
     }
     S(target,(channel*outcols+col)*4u,B(add(value,bias_value)));
    }
   }
  }
 }
 if(byte(op,7)==1){
  float slope=F(W(op,8));uint32_t zero=compare(B(slope),0)&0x40000000u;
  for(uint32_t i=0;;++i){uint32_t count=W(W(outs,0),4)*outspan;if((int32_t)count<=(int32_t)i)break;float v=F(W(target,i*4u));if(!(compare(B(v),0)&0x20000000u))v=zero?F(0):mul(v,slope);S(target,i*4u,B(v));}
 }
 if(byte(op,7)==2){
  for(uint32_t i=0;;++i){uint32_t count=W(W(outs,0),4)*outspan;if((int32_t)count<=(int32_t)i)break;uint32_t negated=W(target,i*4u)^0x80000000u;if((int32_t)negated>=(int32_t)0x42b00000u)negated=0x42b00000u;float v=r1_native_expf(F(negated));v=add(v,1.0f);v=divide(1.0f,v);S(target,i*4u,B(v));}
 }
 if(span!=padded_span){
  for(uint32_t row=0;row<rows;++row){uintptr_t p=W(W(ins,0),16);memmove((void *)(p+row*columns*4u),(void *)(p+row*padded*4u+byte(op,2)*4u),columns*element);}
  if(original){uintptr_t p=W(outs,0);uint32_t count=W(p,8)*W(p,12)*W(p,0);memmove((void *)original,(void *)(uintptr_t)W(p,16),count);S(W(outs,0),16,original);}
 }
 return 0;
}
const uint32_t r1_goodix_graph_convolution_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_graph_convolution;

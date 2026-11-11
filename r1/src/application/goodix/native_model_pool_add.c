/* Native pooling0x41816 and float-add0x98edc model callbacks. */
#include <stdint.h>
#include "native_model_operators.h"
#include "../runtime/native_f32_integer.h"
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint8_t U(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static int32_t I(uintptr_t p,uint32_t o){return (int8_t)U(p,o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static void SB(uintptr_t p,uint32_t o,uint8_t v){*(volatile uint8_t *)(p+o)=v;}
static float F(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
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
static int lt(uint32_t f){return ((f>>31)^((f>>28)&1u))!=0;}
static int gt(uint32_t f){return !(f&0x40000000u)&&!lt(f);}


uint32_t r1_goodix_native_graph_pool(const void *operation,const void *inputs,const void *outputs)
{
 uintptr_t op=(uintptr_t)operation,input=W((uintptr_t)inputs,0);uint32_t kernel=U(op,1),stride=U(op,2),input_width=W(input,12);
 uintptr_t output=W((uintptr_t)outputs,0);uint32_t rows=W(output,8),columns=W(output,12);uintptr_t in=W(input,16),out=W(output,16);uint32_t kind=U(op,0);
 if(kind==0&&kernel==2){
  for(uint32_t row=0;(int32_t)row<(int32_t)rows;++row){uintptr_t base=in+row*input_width;
   for(uint32_t col=0;(int32_t)col<(int32_t)columns;col+=4u){uint32_t at=col*stride;
    int32_t a=I(base,at),b=I(base,at+1u),c=I(base,at+2u),d=I(base,at+3u),e=I(base,at+4u),f=I(base,at+6u),g=I(base,at+5u),h=I(base,at+7u);
    if(a>b)b=a;if(c<=d)c=d;if(g<e)g=e;if(h<f)h=f;
    SB(out,row*columns+col,(uint8_t)b);SB(out,row*columns+col+1u,(uint8_t)c);SB(out,row*columns+col+2u,(uint8_t)g);SB(out,row*columns+col+3u,(uint8_t)h);
   }
  }
 }else if(kind==0&&kernel==4){
  for(uint32_t row=0;(int32_t)row<(int32_t)rows;++row){uintptr_t base=in+row*input_width;
   for(uint32_t col=0;(int32_t)col<(int32_t)columns;++col){int32_t maximum=-128;for(uint32_t i=0;i<kernel;++i){int32_t sample=I(base,col*stride+i);if(sample>maximum)maximum=sample;}SB(out,row*columns+col,(uint8_t)maximum);}
  }
 }else if(kind==1&&kernel==3){
  for(uint32_t row=0;(int32_t)row<(int32_t)rows;++row){uintptr_t base=in+row*input_width;
   for(uint32_t col=0;(int32_t)col<(int32_t)columns;++col){uint32_t sum=0;for(uint32_t i=0;i<kernel;++i)sum+=(uint32_t)I(base,col*stride+i);
    float mean=divide(from_signed(sum),from_signed(kernel));uint32_t flags=compare(B(mean),0);float rounded=add(gt(flags)?.5f:-.5f,mean);SB(out,row*columns+col,(uint8_t)r1_native_f32_integer_bits(B(rounded),0));
   }
  }
 }
 return 0;
}
uint32_t r1_goodix_native_graph_float_add(const void *operation,const void *inputs,const void *outputs)
{
 uintptr_t op=(uintptr_t)operation,a=W((uintptr_t)inputs,0),b=W((uintptr_t)inputs,4);uintptr_t first=W(a,16),second=W(b,16),out=W(W((uintptr_t)outputs,0),16);uint32_t count=W(a,8)*W(a,12);
 for(uint32_t i=0;(int32_t)i<(int32_t)count;++i)S(out,i*4u,B(add(F(W(first,i*4u)),F(W(second,i*4u)))));
 if(U(op,0)==1){
  if(compare(W(op,4),0)&0x40000000u){for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){uint32_t value=W(out,i*4u);if(!(compare(value,0)&0x20000000u))value=0;S(out,i*4u,value);}}
  else{for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){uint32_t value=W(out,i*4u);if(!(compare(value,0)&0x20000000u))value=B(mul(F(value),F(W(op,4))));S(out,i*4u,value);}}
 }
 return 0;
}
const uint32_t r1_goodix_graph_pool_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_graph_pool;
const uint32_t r1_goodix_graph_operator_executor_address=(uint32_t)(uintptr_t)&r1_goodix_native_graph_float_add;

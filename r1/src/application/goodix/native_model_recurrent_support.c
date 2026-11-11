#include "native_model_recurrent_support.h"
#include "native_model_quantization.h"
uint32_t r1_goodix_native_recurrent_round(float value)
{
 return r1_goodix_native_quantize_round(value);
}
uint32_t r1_goodix_native_recurrent_zero_point(float value,float minimum,float maximum)
{
 return r1_goodix_native_quantize_index(value,minimum,maximum);
}
uint32_t r1_goodix_native_recurrent_matrix(const void *inputs,const void *weights,void *outputs,uint32_t ignored,uint32_t columns,uint32_t rows,uint32_t input_zero,uint32_t weight_zero)
{
 (void)ignored;uintptr_t in=(uintptr_t)inputs,w=(uintptr_t)weights,out=(uintptr_t)outputs;
 for(uint32_t row=0;(int32_t)row<(int32_t)rows;++row){
  uint32_t total=0;
  for(uint32_t column=0;(int32_t)column<(int32_t)columns;++column){
   uint32_t a=*(const volatile uint8_t *)(in+column),b=*(const volatile uint8_t *)(w+row*columns+column);
   total+=(a-input_zero)*(b-weight_zero);
  }
  *(volatile uint32_t *)(out+row*4u)=total;
 }
 return (uint32_t)in;
}

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
extern float r1_native_floorf(float);
static int lt(uint32_t f){return ((f>>31)^((f>>28)&1u))!=0;}
static int gt(uint32_t f){return !(f&0x40000000u)&&!lt(f);}
uint32_t r1_goodix_native_recurrent_range_adjust(void *minimum,void *maximum,uint32_t policy)
{
 float low=F(*(const volatile uint32_t *)minimum),high=F(*(const volatile uint32_t *)maximum),width=sub(high,low);
 uint32_t flags=compare(B(width),0);if(!(flags&0x20000000u)||(flags&0x40000000u))return 0xffffffffu;
 if(compare(B(low),0)&0x40000000u)return 0;
 float point=divide(mul(low,F(0xc37f0000u)),width),floor=r1_native_floorf(point),fraction=sub(point,floor);
 if((int32_t)B(fraction)<=(int32_t)0x38800000u||(int32_t)B(fraction)>=(int32_t)0x3f7ffc00u)return 0;
 float a=mul(sub(fraction,1.0f),low),b=mul(fraction,high),selected=(int32_t)B(fraction)>=(int32_t)0x3f000000u?add(floor,1.0f):floor;
 int upper=0;float divisor=floor;
 switch(policy&3u){
 case 1:
  if((int32_t)B(floor)>=(int32_t)0x3f800000u){
   if((int32_t)B(point)>=(int32_t)0x43404000u)upper=1;
   else if(gt(compare(B(mul(a,8.0f)),B(b))))upper=1;
  }
  break;
 case 2:
  if((int32_t)B(point)<(int32_t)0x427f0000u)selected=add(floor,1.0f);
  else if((int32_t)B(floor)>=(int32_t)0x437e0000u){upper=1;divisor=selected;}
  else if(!(compare(B(mul(b,8.0f)),B(a))&0x20000000u)){upper=1;divisor=selected;}
  else selected=add(floor,1.0f);
  break;
 case 3:
  if((int32_t)B(point)<=(int32_t)0x427f0000u)break;
  if((int32_t)B(point)>=(int32_t)0x43404000u){upper=1;divisor=selected;break;}
  {
   float delta=mul(mul(sub(point,selected),width),F(0x3b808081u));
   *(volatile uint32_t *)minimum=B(add(low,delta));*(volatile uint32_t *)maximum=B(add(high,delta));return 3;
  }
 default:
  if((int32_t)B(floor)<(int32_t)0x3f800000u)selected=add(floor,1.0f);
  else if((int32_t)B(floor)>=(int32_t)0x437e0000u)upper=1;
  else if(!lt(compare(B(a),B(b))))upper=1;
  else selected=add(floor,1.0f);
  break;
 }
 if(upper){*(volatile uint32_t *)maximum=B(sub(low,divide(mul(low,255.0f),divisor)));return 2;}
 *(volatile uint32_t *)minimum=B(divide(mul(high,selected),sub(selected,255.0f)));return 1;
}

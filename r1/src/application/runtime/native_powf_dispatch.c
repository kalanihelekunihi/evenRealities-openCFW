#include <stdint.h>
extern float r1_powf_reduced(uint32_t,int32_t,float,float,float);
extern void r1_native_errno_set(uint32_t);
extern float r1_math_invalid32(void);
extern float r1_math_add32(float,float);
extern float r1_math_divzero32(void);
__attribute__((section(".r1.math.powf_dispatch_data"),used))
const uint32_t r1_powf_dispatch_data[4]={0x003fffff,0xff800000,0x7f800000,0x80000000};
typedef union{uint32_t bits;float value;} encoded_float;
static uint32_t bits(float value){encoded_float x={.value=value};return x.bits;}
static float value(uint32_t bits){encoded_float x={.bits=bits};return x.value;}
static float absolute(float x){__asm__ volatile("vabs.f32 %0,%0":"+t"(x));return x;}
static float negate(float x){__asm__ volatile("vneg.f32 %0,%0":"+t"(x));return x;}
static float multiply(float a,float b){float r;__asm__ volatile("vmul.f32 %0,%1,%2":"=t"(r):"t"(a),"t"(b));return r;}
static uint32_t zero_flags(float x){uint32_t status;__asm__ volatile("vcmpe.f32 %1,#0.0\n\tvmrs %0,fpscr":"=r"(status):"t"(x));return status;}
/* Native integer words and live FP slots are deliberately separate. */
float r1_native_powf(float base,float exponent)
{
 uint32_t x=bits(base),y=bits(exponent),wrapped=0x02000000u+(y<<1);int32_t adjustment=0;float sign=1.0f;
 if((x-0x00800000u)<0x7f000000u && wrapped>=0x40000000u)goto reduced;
 if(wrapped<0x40000000u){
  uint32_t t=0x02000000u+(y<<1);
  if(t>=0x02000000u){
   if(zero_flags(exponent)&0x40000000u){
    if((x<<1)!=0 && 0xff000000u>(x<<1))return 1.0f;
   }else{y=(y&0x80000000u)|0x1f800000u;exponent=value(y);}
  }else{
   if(t>=0x01000000u)goto special;
   exponent=value(bits(exponent)-0x00800000u);
  }
 }
 if((x+0x7f800000u)<0x7f000000u){
negative_base:
  base=absolute(base);x=bits(base);
  uint32_t e=(y>>23)&255;
  if(e>=151)goto reduced;
  if(e>=127){uint32_t unit=1u<<(150-e);if(!(y&(unit-1))){if(y&unit)sign=-1.0f;goto reduced;}}
  r1_native_errno_set(1);return r1_math_invalid32();
 }
 if((x<<1)!=0 && (x<<1)<0x01000000u){
  adjustment=-27;base=multiply(base,value(0x4d000000u));x=bits(base);
  if(x>>31)goto negative_base;
  goto reduced;
 }
 if((x-0x00800000u)<0x7f000000u)goto reduced;
 goto special;
reduced:
 return r1_powf_reduced(x,adjustment,base,exponent,sign);
special:;
 uint32_t ax=x&0x7fffffffu,ay=y&0x7fffffffu;
 if((ax+0x807fffffu)<r1_powf_dispatch_data[0] || (ay+0x807fffffu)<r1_powf_dispatch_data[0])return r1_math_add32(base,exponent);
 if(x==0x3f800000u || (y<<1)==0)return 1.0f;
 if(ax>0x7f800000u || ay>0x7f800000u)return r1_math_add32(base,exponent);
 if(x==0x7f800000u)return y>>31 ? 0.0f : value(r1_powf_dispatch_data[2]);
 uint32_t parity=0,e=(y>>23)&255;
 if(e>=151)parity=2;
 else if(e>=127){uint32_t unit=1u<<(150-e);if(!(y&(unit-1)))parity=y&unit ? 1 : 2;}
 if(x==0xff800000u){
  if(y>>31)return parity==1 ? value(r1_powf_dispatch_data[3]) : 0.0f;
  return value(r1_powf_dispatch_data[parity==1 ? 1 : 2]);
 }
 if(x==0){if(y>>31)goto pole;return 0.0f;}
 if(x==0x80000000u){
  if(y==0x7f800000u)return 0.0f;
  if(y==0xff800000u)goto pole;
  if(y>>31){if(parity==1){r1_native_errno_set(2);return negate(r1_math_divzero32());}goto pole;}
  return parity==1 ? value(r1_powf_dispatch_data[3]) : 0.0f;
 }
 if(x==0xbf800000u)return 1.0f;
 return ((0x7f000000u<=(x<<1)) ? 1u : 0u)==(1u-(y>>31)) ? value(r1_powf_dispatch_data[2]) : 0.0f;
pole:
 r1_native_errno_set(2);return r1_math_divzero32();
}

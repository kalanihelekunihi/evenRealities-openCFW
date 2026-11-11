/* Native profile conversion0x71e34: preserve raw ranges,error precedence,
 * RTZ/FPSCR,persisted fallback-slot asymmetry and late resting-rate copy. */
#include "native_gomore_engine_profile.h"
#include <stdint.h>
#include "../runtime/native_f32_integer.h"
#include "../runtime/native_float_bits.h"
extern volatile uint32_t r1_gomore_native_context;
extern void r1_gomore_log_native(uint32_t,uint32_t,const char *,...);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static void Y(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint8_t *)(p+o)=(uint8_t)v;}
static float F(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static uint32_t B(float x){union{uint32_t u;float f;}v={.f=x};return v.u;}
static double D(uint64_t x){union{uint64_t u;double f;}v={.u=x};return v.f;}
__attribute__((noinline)) static float from_unsigned(uint32_t x){volatile float v=(float)x;return v;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
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

uint32_t r1_gomore_native_engine_profile_convert(const void *input,void *output)
{
 uintptr_t in=(uintptr_t)input,out=(uintptr_t)output;uint32_t result=0;
 for(uint32_t i=0;i<7;++i)r1_gomore_log_native(1,1,"[Into][%d]=%f\r\n",i,D(r1_binary32_to_binary64_bits(W(in,i*4u))));
 uint32_t bits=W(in,0),age,sex,height,weight,maximum,rest;
 if(bits+0xbee00000u<=0x1a60000u)age=r1_native_f32_integer_bits(bits,1)&255u;else{age=30;result=(uint32_t)-101;}
 bits=W(in,4);if(compare(bits,0)==0x60000000u||bits==0x3f800000u)sex=r1_native_f32_integer_bits(bits,1)&255u;else{sex=1;result=(uint32_t)-102;}
 bits=W(in,8);if(bits+0xbd380000u<=0x940000u)height=bits;else{height=0x432a0000u;result=(uint32_t)-103;}
 bits=W(in,12);if(bits+0xbee00000u<=0x1f60000u)weight=bits;else{weight=0x42700000u;result=(uint32_t)-104;}
 bits=W(in,16);if(bits+0xbcf60000u<=0x520000u)maximum=bits;else{float years=from_unsigned(age);maximum=B(add(208.0f,F(B(mul(years,F(0x3f333333u)))^0x80000000u)));if(bits!=0xbf800000u)result=(uint32_t)-105;}
 bits=W(in,20);if(bits+0xbde00000u<=0xa80000u)rest=bits;else{rest=0x42700000u;if(bits!=0xbf800000u)result=(uint32_t)-106;}
 uint32_t local[2];bits=W(in,24);uint32_t flags=compare(bits,0);if((flags&0x60000000u)==0x20000000u)local[0]=bits;else{local[0]=0x420c0000u;if(bits!=0xbf800000u)result=(uint32_t)-107;}local[1]=0x420c0000u;
 uintptr_t context=r1_gomore_native_context;
 for(uint32_t i=0;i<2;++i){uintptr_t previous=W(context,0x39dc);uint32_t value=W(previous,0x2d8+i*4u);flags=compare(value,0);if(flags==0x20000000u)local[i]=value;else S(previous,0x2d8,local[i]);}
 Y(out,0x7c,age);Y(out,0x7d,sex);S(out,0x74,height);S(out,0x78,weight);S(out,0x80,maximum);S(out,0x84,W(in,20));S(out,0x28,maximum);S(out,0x110,rest);S(out,0x20,local[0]);S(out,0x24,local[1]);return result;
}

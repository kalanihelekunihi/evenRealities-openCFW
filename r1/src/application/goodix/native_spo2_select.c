/* Native SpO2 selection0x36f88: mode transitions, native soft-double
 * rounding, signed/unsigned RTZ conversions and cached-value ordering.
 * See r1/docs/reference/goodix-spo2-select-c-review.md.
 */
#include "native_spo2_select.h"
#include <stdint.h>
#include "../runtime/native_float_bits.h"
#include "../runtime/native_f32_integer.h"
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint32_t U8(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static uint32_t U16(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t x){*(volatile uint32_t *)(p+o)=x;}
static void SB(uintptr_t p,uint32_t o,uint32_t x){*(volatile uint8_t *)(p+o)=(uint8_t)x;}
static float F(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static uint32_t B(float x){union{uint32_t u;float f;}v={.f=x};return v.u;}
__attribute__((noinline)) static float multiply(float a,float b){volatile float v=a*b;return v;}
static int32_t rounded(uint32_t x){return (int32_t)r1_binary64_to_signed32_bits(r1_format_double_add_bits(r1_binary32_to_binary64_bits(x),UINT64_C(0x3fe0000000000000)));}
static uint32_t clamp(int32_t x){return x<66?65u:x>100?100u:(uint32_t)x;}
static void fallback(uintptr_t out,uintptr_t valid,int32_t value){S(out,0,B((float)(int32_t)clamp(value)));SB(valid,0,5);}
static void selected(uintptr_t out,uintptr_t valid,uint32_t value){S(out,0,B((float)value));SB(valid,0,2);}
void r1_goodix_spo2_select(const void *configuration,void *owner,uint32_t iteration,void *output,void *valid_output)
{
 uintptr_t cfg=(uintptr_t)configuration,state=W((uintptr_t)owner,0),out=(uintptr_t)output,valid=(uintptr_t)valid_output;
 uintptr_t data=W(state,4);uint32_t count=U16(state,8);int32_t value=rounded(W(data,count*4u-4u));
 uint32_t auxiliary=r1_native_f32_integer_bits(W(state,24),0);
 int32_t parity=rounded(B(multiply(F(W(state,64)),10000.0f)));uint32_t adjusted=U8(state,23);
 if(!((uint32_t)parity&1u)){
  uint32_t rem=(uint8_t)(value%6);
  if(rem==1)adjusted=clamp((int32_t)adjusted+2);
  if(rem-2u<2u)adjusted=clamp((int32_t)adjusted-1);
  if(rem-4u<2u)adjusted=clamp((int32_t)adjusted+1);
 }
 uint32_t mode=U8(state,22),flags=U8(state,20);
 switch(mode){
 case 0:
  if(U8(cfg,69)<=iteration&&!flags){fallback(out,valid,value);SB(state,22,(int32_t)U8(cfg,68)<=value?1:2);}break;
 case 1:
  if((int32_t)U8(cfg,68)<=value)fallback(out,valid,value);
  else if((U8(cfg,75)&1u)&&flags){selected(out,valid,adjusted);SB(state,22,12);}
  else{fallback(out,valid,value);SB(state,22,2);}break;
 case 2:
  if((int32_t)U8(cfg,68)>value)fallback(out,valid,value);
  else if((U8(cfg,75)&2u)&&flags){selected(out,valid,adjusted);SB(state,22,21);}
  else{fallback(out,valid,value);SB(state,22,1);}break;
 case 12:
  if((int32_t)U8(cfg,68)<=value){fallback(out,valid,value);SB(state,22,1);}
  else if(flags)selected(out,valid,adjusted);
  else{fallback(out,valid,value);SB(state,22,2);}break;
 case 21:
  if((int32_t)U8(cfg,68)>value){fallback(out,valid,value);SB(state,22,2);}
  else if(flags)selected(out,valid,adjusted);
  else{fallback(out,valid,value);SB(state,22,1);}break;
 default:break;
 }
 if(U8(valid,0)==5)SB(state,23,r1_native_f32_integer_bits(W(out,0),1));
 if(!U8(state,22)&&(U8(cfg,75)&4u)&&U8(cfg,70)<=iteration&&(U8(state,21)>=6||auxiliary)&&((int32_t)U8(cfg,68)<=value||value%3==0||auxiliary)){
  S(out,0,B((float)(int32_t)clamp(value%4+97)));SB(valid,0,1);
 }
}

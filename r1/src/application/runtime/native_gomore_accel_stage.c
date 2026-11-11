#include <stdint.h>
#include <stddef.h>
#include "native_gomore_stages.h"
#include "native_gomore_accel_history.h"
#include "native_gomore_accel_collect.h"
#include "native_gomore_accel_features.h"
#include "native_float_to_signed.h"
extern void __aeabi_memclr(void *,uint32_t);
extern float r1_native_sqrtf(float);
static uint32_t byte(uint32_t at){return *(volatile uint8_t *)(uintptr_t)at;}
static uint32_t word(uint32_t at){return *(volatile uint32_t *)(uintptr_t)at;}
static uint32_t half(uint32_t at){return *(volatile uint16_t *)(uintptr_t)at;}
static void put_half(uint32_t at,uint32_t value){*(volatile uint16_t *)(uintptr_t)at=(uint16_t)value;}
static void put_byte(uint32_t at,uint32_t value){*(volatile uint8_t *)(uintptr_t)at=(uint8_t)value;}
static float sample(uint32_t at){return *(volatile float *)(uintptr_t)at;}
static __attribute__((noinline,noclone)) void shift(uint32_t state)
{
 for(uint32_t i=25;i<200;i++)put_half(state+84u+(i-25u)*2u,half(state+84u+i*2u));
}
static __attribute__((noinline,noclone)) void mirror(uint32_t state)
{
 for(uint32_t i=0;i<25;i++)put_half(state+84u+(175u+i)*2u,half(state+84u+(174u-i)*2u));
}
typedef struct {int16_t z[26],y[26],x[26],magnitude[26];} accel_frame;
_Static_assert(offsetof(accel_frame,y)==52 && offsetof(accel_frame,x)==104,"native axis positions");
_Static_assert(sizeof(accel_frame)==208,"native channel scratch span");
_Static_assert(offsetof(accel_frame,magnitude)==156,"native magnitude position");
#define ADDRESS(field) ((uint32_t)(uintptr_t)&frame.field)
uint32_t r1_gomore_stage_5ed14_native(uint32_t state,uint32_t elapsed,uint32_t input,uint32_t output)
{
 volatile accel_frame frame;
 if(elapsed<=1u && byte(input+12u)!=1u) {
  int32_t warm=(int8_t)byte(state);
  if(warm>0)put_byte(state,(uint32_t)warm-1u);
 } else {
  if(elapsed>8u){r1_gomore_missing_window_reset_native(output);r1_gomore_accel_state_reset_native(state);return 1;}
  if(byte(input+12u)==1u)elapsed++;
  for(int32_t i=0;i<(int32_t)(elapsed-1u);i++) {
   r1_gomore_accel_slot_advance_native(state);shift(state);mirror(state);
  }
 }
 if(byte(input+12u)==1u){r1_gomore_missing_window_reset_native(output);return 1;}
 __aeabi_memclr((void *)(uintptr_t)ADDRESS(magnitude),52);
 __aeabi_memclr((void *)(uintptr_t)ADDRESS(x),52);
 __aeabi_memclr((void *)(uintptr_t)ADDRESS(y),52);
 __aeabi_memclr((void *)(uintptr_t)ADDRESS(z),52);
 for(uint32_t i=0;i<25;i++) {
  frame.x[i]=(int16_t)r1_native_float_to_signed32(sample(word(input)+i*4u));
  frame.y[i]=(int16_t)r1_native_float_to_signed32(sample(word(input+4u)+i*4u));
  frame.z[i]=(int16_t)r1_native_float_to_signed32(sample(word(input+8u)+i*4u));
 }
 for(uint32_t i=0;i<25;i++) {
  int32_t x=frame.x[i],y=frame.y[i],z=frame.z[i];
  uint32_t square=(uint32_t)(x*x);square+=(uint32_t)(y*y);square+=(uint32_t)(z*z);
  frame.magnitude[i]=(int16_t)r1_native_float_to_signed32(r1_native_sqrtf((float)(int32_t)square));
 }
 shift(state);
 for(uint32_t i=0;i<25;i++)put_half(state+84u+(175u+i)*2u,(uint16_t)frame.magnitude[i]);
 r1_gomore_accel_collect_native(state,ADDRESS(x),ADDRESS(y),ADDRESS(z),ADDRESS(magnitude),25);
 if((int8_t)byte(state)>=8) {
  for(uint32_t window=0;window<7;window++)for(uint32_t i=0;i<25;i++)
   put_half(state+84u+(window*25u+i)*2u,(uint16_t)frame.magnitude[i]);
 }
 put_byte(state,0);
 for(uint32_t i=0;i<8;i++)if(half(state+50u+i*2u)==0)put_byte(state,byte(state)+1u);
 if((int8_t)byte(state)<=4)r1_gomore_accel_features_native(state,output);
 else r1_gomore_missing_window_reset_native(output);
 return 0;
}

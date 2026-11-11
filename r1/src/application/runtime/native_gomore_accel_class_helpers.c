#include "native_gomore_accel_class_helpers.h"
#define FP __attribute__((noinline,noclone))
static FP float convert(uint32_t x){return (float)(int32_t)x;}
static FP float divide(float a,float b){return a/b;}
static FP float multiply(float a,float b){return a*b;}
static FP float madd(float acc,float a,float b){return acc+a*b;}
static FP float add(float a,float b){return a+b;}
static FP uint32_t less(float a,float b){volatile uint32_t result=a<b;return result;}
static float value(uint32_t bits){union {uint32_t bits;float value;} u={.bits=bits};return u.value;}
static int32_t signed_half(uint32_t at){return *(volatile int16_t *)(uintptr_t)at;}
static uint32_t half(uint32_t at){return *(volatile uint16_t *)(uintptr_t)at;}
float r1_gomore_accel_nonzero_mean8_native(uint32_t input)
{
 int32_t sum=0,count=0;
 for(uint32_t i=0;i<8;i++) {
  int32_t x=signed_half(input+i*2u);
  if(x){sum+=x;count++;}
 }
 if(count>0)return divide(convert((uint32_t)sum),convert((uint32_t)count));
 return 0.0f;
}
uint32_t r1_gomore_accel_hysteresis_count_native(uint32_t input,uint32_t count)
{
 uint32_t armed=1,crossings=0;
 for(int32_t i=0;i<(int32_t)count;i++) {
  if(armed) {
   if(half(input+(uint32_t)i*2u)>1200u){armed=0;crossings=(crossings+1u)&255u;}
  } else if(half(input+(uint32_t)i*2u)<1000u)armed=1;
 }
 return crossings;
}
uint32_t r1_gomore_accel_linear_classify_native(float first,float second,float third,uint32_t extra)
{
 /* Stock coefficient words at 0xbd26c and bias word at 0x5697c. */
 float score=multiply(value(0xbe445123),convert(extra));
 score=madd(score,first,value(0x3f697fe1));
 score=madd(score,second,value(0xbc00b405));
 score=madd(score,third,value(0x3f7237e0));
 score=add(score,value(0xbf4485ee));
 /* Native BCS includes unordered after the signaling comparison. */
 return less(score,0.0f)?1u:UINT32_MAX;
}

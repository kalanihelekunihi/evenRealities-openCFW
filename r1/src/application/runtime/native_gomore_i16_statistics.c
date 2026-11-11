#include "native_gomore_i16_statistics.h"
extern float r1_native_sqrtf(float);
static int32_t sample(uint32_t at){return *(volatile int16_t *)(uintptr_t)at;}
static uint32_t quotient(uint32_t numerator,uint32_t denominator)
{
 /* SDIV's sole signed-overflow case wraps; avoid C's undefined division. */
 if(numerator==0x80000000u && denominator==0xffffffffu)return numerator;
 return (uint32_t)((int32_t)numerator/(int32_t)denominator);
}
static uint32_t narrow(uint32_t value){return (uint32_t)(int32_t)(int16_t)value;}
uint32_t r1_gomore_i16_mean_native(uint32_t input,uint32_t count)
{
 uint32_t sum=0;
 for(int32_t i=0;i<(int32_t)count;i++)sum+=(uint32_t)sample(input+(uint32_t)i*2u);
 return count?narrow(quotient(sum,count)):0;
}
uint32_t r1_gomore_i16_variance_bits(uint32_t input,uint32_t count,uint32_t center)
{
 uint32_t sum=0;
 for(int32_t i=0;i<(int32_t)count;i++) {
  uint32_t delta=(uint32_t)sample(input+(uint32_t)i*2u)-center;
  sum+=delta*delta;
 }
 return count==1u?0:quotient(sum,count-1u);
}
float r1_gomore_i16_deviation_native(uint32_t input,uint32_t count,uint32_t center)
{
 uint32_t variance=r1_gomore_i16_variance_bits(input,count,center);
 return r1_native_sqrtf((float)(int32_t)variance);
}
uint32_t r1_gomore_i16_range_native(uint32_t input,uint32_t count)
{
 /* Stock loads element zero even for a zero or negative signed count. */
 int32_t minimum=sample(input),maximum=minimum;
 for(int32_t i=0;i<(int32_t)count;i++) {
  int32_t value=sample(input+(uint32_t)i*2u);
  if(value<minimum)minimum=value;
  if(value>maximum)maximum=value;
 }
 int32_t range=maximum-minimum;
 return range>32000?32000u:narrow((uint32_t)range);
}
uint32_t r1_gomore_i16_mean_difference_native(uint32_t input,uint32_t count)
{
 uint32_t sum=0,bound=count-1u;
 for(int32_t i=0;i<(int32_t)bound;i++) {
  int32_t current=sample(input+(uint32_t)i*2u),next=sample(input+((uint32_t)i+1u)*2u);
  int32_t delta=next-current;
  sum+=(uint32_t)(delta<0?-delta:delta);
 }
 return count==1u?0:narrow(quotient(sum,bound));
}

#include <stdint.h>
#include "native_float_bits.h"
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t),r1_format_double_multiply_bits(uint64_t,uint64_t),r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
extern double r1_native_pow(double,double),r1_native_sqrt(double);
extern float r1_gomore_mean_native(uint32_t,uint32_t),r1_gomore_deviation_native(uint32_t,uint32_t);
extern uint32_t r1_gomore_sleep_iir2_filter_native(uint32_t,uint32_t);
extern void r1_gomore_sort_float_subrange_native(uint32_t,uint32_t,uint32_t);
extern float r1_gomore_sorted_percentile_native(uint32_t,uint32_t,uint32_t),r1_gomore_bounded_linear_complement_native(float,float);
extern uint32_t r1_gomore_extrema_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
#define FP __attribute__((noinline,noclone))
static FP float add(float a,float b){return a+b;}
static FP float sub(float a,float b){return a-b;}
static FP float mul(float a,float b){return a*b;}
static FP float divide(float a,float b){return a/b;}
static FP float madd(float acc,float a,float b){return acc+a*b;}
static FP float msub(float acc,float a,float b){return acc-a*b;}
static FP float convert(uint32_t value){return (float)(int32_t)value;}
static FP uint32_t equal(float a,float b){return a==b;}
static FP uint32_t less(float a,float b){return a<b;}
static FP uint32_t greater(float a,float b){return a>b;}
static uint32_t bits(float value){union {float value;uint32_t bits;} x={.value=value};return x.bits;}
static float value(uint32_t word){union {float value;uint32_t bits;} x={.bits=word};return x.value;}
static uint32_t byte(uint32_t at){return *(volatile uint8_t *)(uintptr_t)at;}
static float sample(uint32_t at){return *(volatile float *)(uintptr_t)at;}
static void store(uint32_t at,float x){*(volatile float *)(uintptr_t)at=x;}
static uint64_t promote(float x){return r1_binary32_to_binary64_bits(bits(x));}
static float narrow(uint64_t x){return value(r1_log_double_to_float_bits(x));}
static uint32_t carry(uint64_t a,uint64_t b)
{
 uint64_t ka=a>>63?a:UINT64_C(0x8000000000000000)-a;
 uint64_t kb=b>>63?b:UINT64_C(0x8000000000000000)-b;
 return kb>=ka;
}
static FP float rate(uint64_t delta)
{return narrow(r1_format_double_multiply_bits(r1_format_double_divide_bits(UINT64_C(0x4029000000000000),delta),UINT64_C(0x404e000000000000)));}
static FP uint32_t periods(uint32_t signal,uint32_t first,uint32_t second,uint32_t first_count,uint32_t second_count,float first_threshold,float second_threshold,uint32_t output,uint32_t n,uint32_t reverse)
{
 uint32_t j=0,previous=UINT32_MAX,crossings=0;
 for(uint32_t i=0;i<byte(first_count) && j<byte(second_count);i=(i+1u)&255u) {
  uint32_t current=byte(first+i);float height=sample(signal+current*4u);
  if(reverse ? !less(height,first_threshold) : !greater(height,first_threshold))continue;
  if((int32_t)previous<0) {
   previous=current;
   while(byte(second+j)<current) {uint32_t next=j+1u;if(next>=byte(second_count))break;j=next&255u;}
   continue;
  }
  while(byte(second+j)<current) {
   float opposite=sample(signal+byte(second+j)*4u);
   if(reverse ? greater(opposite,second_threshold) : less(opposite,second_threshold))crossings++;
   uint32_t next=j+1u;if(next>=byte(second_count))break;j=next&255u;
  }
  if(crossings==1u) {store(output+n*4u,rate(promote(convert(current-previous))));n=(n+1u)&255u;}
  previous=byte(first+i);crossings=0;
 }
 return n;
}
static FP uint32_t fallback(uint32_t minima,uint32_t max_count,uint32_t min_count,uint32_t controls)
{
 uint32_t n=0;
  for(uint32_t pass=0;pass<2;pass++) {
   uint32_t count_pointer=pass?max_count:min_count;
   for(uint32_t i=0;(int32_t)i<(int32_t)(byte(count_pointer)-1u);i++) {
    uint32_t earlier=byte(minima+i),later=byte(minima+i+1u),delta=later-earlier;
    if((int32_t)delta>50 && !carry(r1_signed32_to_binary64_bits(delta),UINT64_C(0x405cbfffffffffff))) {
     later=byte(minima+i+1u);earlier=byte(minima+i);
     store(controls+n*4u,rate(r1_signed32_to_binary64_bits(later-earlier)));n=(n+1u)&255u;
    }
   }
  }
 return n;
}
static FP void summarize(uint32_t controls,uint32_t n,uint32_t primary,uint32_t secondary_argument)
{
 store(primary,-1.0f);store(*(volatile uint32_t *)(uintptr_t)secondary_argument,0.0f);
 if(n<2u)return;
 float mean=r1_gomore_mean_native(controls,n),deviation=r1_gomore_deviation_native(controls,n);
 float upper=madd(mean,deviation,2.0f),lower=msub(mean,deviation,2.0f),sum=0.0f;
 uint32_t included=0;
 for(uint32_t i=0;i<n;i++) {
  float x=sample(controls+i*4u);
  if(less(x,upper) && greater(x,lower)) {sum=add(x,sum);included++;}
 }
 if(included<=2u)return;
 float included_mean=divide(sum,convert(included)),squared_sum=0.0f;
 for(uint32_t i=0;i<n;i++) {
  float x=sample(controls+i*4u);
  if(less(x,upper) && greater(x,lower)) {
   union {double value;uint64_t bits;} power={.bits=promote(sub(included_mean,x))};
   power.value=r1_native_pow(power.value,2.0);
   squared_sum=narrow(r1_format_double_add_bits(promote(squared_sum),power.bits));
  }
 }
 union {double value;uint64_t bits;} dispersion={.bits=promote(divide(squared_sum,convert(included)))};
 dispersion.value=r1_native_sqrt(dispersion.value);
 float spread=narrow(dispersion.bits);
 store(primary,included_mean);
 float denominator=mul(mul(included_mean,value(0x3eaaaaab)),2.0f);
 float complement=sub(1.0f,divide(convert(included),denominator));
 float result=r1_gomore_bounded_linear_complement_native(spread,complement);
 store(*(volatile uint32_t *)(uintptr_t)secondary_argument,result);
}
uint32_t r1_gomore_locomotion_feature_reduce_native(uint32_t expanded,uint32_t maxima,uint32_t minima,uint32_t controls,volatile uint32_t incoming_primary,volatile uint32_t secondary)
{
 uint32_t primary=incoming_primary;
 float mean=r1_gomore_mean_native(expanded,250);
 float deviation=r1_gomore_deviation_native(expanded,250);
 for(uint32_t i=0;i<250;i++) {
  float normalized=0.0f;
  if(!equal(deviation,0.0f))normalized=divide(sub(sample(expanded+i*4u),mean),deviation);
  store(expanded+i*4u,normalized);
 }
 r1_gomore_sleep_iir2_filter_native(expanded,250);
 /* Keep native extrema counter offsets and provider depth in the C frame. */
 volatile struct {uint32_t prefix,minimum,maximum,reserved[7];} counts;
 counts.maximum=0;counts.minimum=0;
 uint32_t max_count=(uint32_t)(uintptr_t)&counts.maximum,min_count=(uint32_t)(uintptr_t)&counts.minimum;
 r1_gomore_extrema_native(expanded,250,38,12,maxima,minima,max_count,min_count);
 for(uint32_t i=0;i<byte(max_count);i++)store(controls+i*4u,sample(expanded+byte(maxima+i)*4u));
 r1_gomore_sort_float_subrange_native(controls,0,byte(max_count)-1u);
 float first_threshold=narrow(r1_format_double_multiply_bits(promote(r1_gomore_sorted_percentile_native(controls,byte(max_count),75)),UINT64_C(0x3fc999999999999a)));
 for(uint32_t i=0;i<byte(min_count);i++)store(controls+i*4u,sample(expanded+byte(minima+i)*4u));
 r1_gomore_sort_float_subrange_native(controls,0,byte(min_count)-1u);
 float second_threshold=narrow(r1_format_double_multiply_bits(promote(r1_gomore_sorted_percentile_native(controls,byte(min_count),25)),UINT64_C(0x3fc999999999999a)));
 uint32_t n=periods(expanded,maxima,minima,max_count,min_count,first_threshold,second_threshold,controls,0,0);
 n=periods(expanded,minima,maxima,min_count,max_count,second_threshold,first_threshold,controls,n,1);
 if(byte(max_count)<6u && n<2u) {
  n=0;
  n=fallback(minima,max_count,min_count,controls);
 }
 summarize(controls,n,primary,(uint32_t)(uintptr_t)&secondary);return 0;
}

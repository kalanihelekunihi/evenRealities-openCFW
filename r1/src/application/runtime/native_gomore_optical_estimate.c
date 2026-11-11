#include <stdint.h>
#include <stddef.h>
#include "native_float_bits.h"
extern uint32_t r1_gomore_optical_reset_native(uint32_t),r1_gomore_optical_compact_native(uint32_t),r1_gomore_optical_append_native(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_extrema_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_peak_candidate_match_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_optical_interval_merge_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_locomotion_control_extract_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_locomotion_feature_reduce_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t),r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
extern double r1_native_fabs(double);
#define FP __attribute__((noinline,noclone))
static FP float add(float a,float b){return a+b;}
static FP float sub(float a,float b){return a-b;}
static FP float mul(float a,float b){return a*b;}
static FP float divide(float a,float b){return a/b;}
static FP float madd(float acc,float a,float b){return acc+a*b;}
static FP uint32_t less(float a,float b){volatile uint32_t r=a<b;return r;}
static FP uint32_t greater(float a,float b){volatile uint32_t r=a>b;return r;}
static FP uint32_t equal(float a,float b){volatile uint32_t r=a==b;return r;}
static float value(uint32_t x){union {float value;uint32_t bits;} u={.bits=x};return u.value;}
static uint32_t bits(float x){union {float value;uint32_t bits;} u={.value=x};return u.bits;}
static uint32_t word(uint32_t at){return *(volatile uint32_t *)(uintptr_t)at;}
static uint32_t byte(uint32_t at){return *(volatile uint8_t *)(uintptr_t)at;}
static void put(uint32_t at,uint32_t x){*(volatile uint32_t *)(uintptr_t)at=x;}
static void put_byte(uint32_t at,uint32_t x){*(volatile uint8_t *)(uintptr_t)at=(uint8_t)x;}
static float sample(uint32_t at){return *(volatile float *)(uintptr_t)at;}
static uint64_t promote(float x){return r1_binary32_to_binary64_bits(bits(x));}
static uint32_t narrow(uint64_t x){return r1_log_double_to_float_bits(x);}
static uint32_t carry(uint64_t a,uint64_t b)
{
 uint64_t ka=a>>63?a:UINT64_C(0x8000000000000000)-a;
 uint64_t kb=b>>63?b:UINT64_C(0x8000000000000000)-b;
 return kb>=ka;
}
typedef struct {
 uint32_t fallback_confidence,fallback_rate,mode1_rate,mode2_rate;
 uint32_t mode1_confidence,mode2_confidence,mean_amplitude,median_spacing;
 uint32_t expanded[250],controls[40];
 uint32_t minimum_count,maximum_count;
 uint8_t minima[20],maxima[20];
 uint32_t cached_primary,cached_secondary,cached_input,reserved[5];
} optical_frame;
_Static_assert(offsetof(optical_frame,expanded)==32,"native expansion layout");
_Static_assert(offsetof(optical_frame,controls)==1032,"native control layout");
_Static_assert(offsetof(optical_frame,minimum_count)==1192,"native count layout");
_Static_assert(offsetof(optical_frame,maxima)==1220,"native extrema layout");
_Static_assert(sizeof(optical_frame)==1272,"optical frame reservation");
static FP void advance(uint32_t state)
{uint32_t total=word(state+84u);if(total<0xfffffffeu)put(state+84u,total+1u);}
static FP uint32_t update(uint32_t old_address,uint32_t current_address)
{
 uint32_t old=word(old_address);
 if(less(value(old),0.0f)) {
  float current=sample(current_address);
  if(greater(current,0.0f))return narrow(promote(current));
 }
 uint64_t previous=r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(old),UINT64_C(0x3fe8000000000000));
 uint64_t current=r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(word(current_address)),UINT64_C(0x3fd0000000000000));
 return narrow(r1_format_double_add_bits(current,previous));
}
static FP uint32_t fallback_needed(uint32_t state)
{
 uint64_t required=r1_format_double_multiply_bits(promote(divide(500.0f,sample(state+1728u))),UINT64_C(0x3feb333333333333));
 return !carry(r1_unsigned32_to_binary64_bits(byte(state+81u)),required);
}
static FP void smooth(uint32_t state,volatile optical_frame *frame)
{
 float accumulated=0.0f,weight=value(0x3c888889);
 for(uint32_t i=0;i<60;i++)accumulated=madd(accumulated,sample(state+728u+i*4u),weight);
 float complement=sub(1.0f,weight);
 for(uint32_t i=0;i<125;i++) {
  float even=sample(state+728u+i*8u),odd=sample(state+728u+(i*2u+1u)*4u);
  float contribution=mul(mul(add(even,odd),weight),0.5f);
  accumulated=madd(contribution,complement,accumulated);
  frame->expanded[249u-i]=bits(accumulated);frame->expanded[i]=bits(accumulated);
 }
}
static FP uint64_t boosted(volatile optical_frame *frame)
{
 float second=value(frame->mode2_confidence),first=value(frame->mode1_confidence);
 return r1_format_double_multiply_bits(promote(mul(add(second,first),0.5f)),UINT64_C(0x3ff3333333333333));
}
static FP void select_outputs(volatile optical_frame *frame,uint32_t primary,uint32_t secondary)
{
 float second=value(frame->mode2_confidence);
 if(equal(second,0.0f) && equal(value(frame->mode1_confidence),0.0f)) {
  float fallback=value(frame->fallback_confidence);
  if(greater(fallback,0.0f) && (int32_t)frame->fallback_rate<=(int32_t)0x41c80000u && (int32_t)bits(fallback)>(int32_t)0x3f000000u) {
   put(primary,frame->fallback_rate);put(secondary,frame->fallback_confidence);
  } else {put(primary,0xbf800000u);put(secondary,0);}
  return;
 }
 if(greater(second,0.0f) && greater(value(frame->mode1_confidence),0.0f)) {
  float first_rate=value(frame->mode1_rate),second_rate=value(frame->mode2_rate);
  union {double value;uint64_t bits;} difference={.bits=promote(sub(first_rate,second_rate))};
  difference.value=r1_native_fabs(difference.value);
  if(!carry(difference.bits,UINT64_C(0x3ff0000000000000))) {
   second_rate=value(frame->mode2_rate);first_rate=value(frame->mode1_rate);
   put(primary,bits(mul(add(second_rate,first_rate),0.5f)));
   uint64_t confidence=UINT64_C(0x3ff0000000000000);
   if(!carry(boosted(frame),confidence))confidence=boosted(frame);
   put(secondary,narrow(confidence));return;
  }
 }
 second=value(frame->mode2_confidence);float first=value(frame->mode1_confidence);
 uint32_t rate=greater(second,first)?frame->mode2_rate:frame->mode1_rate;
 put(primary,rate);
 second=value(frame->mode2_confidence);first=value(frame->mode1_confidence);
 uint32_t confidence=bits(greater(second,first)?second:first);
 put(secondary,confidence);
 if((int32_t)frame->fallback_confidence>(int32_t)0x3f000000u && (int32_t)confidence<(int32_t)0x3e99999au && (int32_t)frame->fallback_rate<=(int32_t)0x41c80000u) {
  put(primary,frame->fallback_rate);put(secondary,frame->fallback_confidence);
 }
}
#define ADDRESS(field) ((uint32_t)(uintptr_t)&frame.field)
uint32_t r1_gomore_optical_estimate_native(uint32_t state,uint32_t elapsed,uint32_t input,uint32_t flags,volatile float *volatile incoming_primary,volatile float *volatile incoming_secondary)
{
 volatile optical_frame frame;
 uint32_t primary=(uint32_t)(uintptr_t)incoming_primary,secondary=(uint32_t)(uintptr_t)incoming_secondary;
 put(primary,0xbf800000u);put(secondary,0);
 frame.cached_primary=primary;frame.cached_secondary=secondary;frame.cached_input=input;
 frame.reserved[4]=0; /* Allocate the full provider frame on every entry path. */
 if(elapsed>1u || (flags&64u)) {
  if(elapsed>20u){r1_gomore_optical_reset_native(state);return 1;}
  put_byte(state+80u,9);
  for(uint32_t i=0;i<elapsed;i++) {
   r1_gomore_optical_compact_native(state);
   r1_gomore_optical_append_native(state,frame.cached_input,(i==elapsed-1u && !flags)?0u:1u);
   advance(state);
  }
  return 1;
 }
 uint32_t warmup=byte(state+80u);
 if(warmup) {
  put_byte(state+80u,warmup-1u);
  r1_gomore_optical_append_native(state,frame.cached_input,0);
  r1_gomore_optical_compact_native(state);advance(state);return 1;
 }
 advance(state);frame.maximum_count=0;frame.minimum_count=0;
 r1_gomore_optical_append_native(state,frame.cached_input,0);
 if(word(state+84u)<10u)return 1;
 r1_gomore_extrema_native(state+728u,250,25,6,ADDRESS(maxima),ADDRESS(minima),ADDRESS(maximum_count),ADDRESS(minimum_count));
 r1_gomore_peak_candidate_match_native(state+728u,ADDRESS(maxima),ADDRESS(minima),ADDRESS(maximum_count),ADDRESS(minimum_count),ADDRESS(median_spacing),ADDRESS(controls));
 r1_gomore_optical_interval_merge_native(state,ADDRESS(maxima),ADDRESS(minima),ADDRESS(maximum_count),ADDRESS(mean_amplitude));
 put(state+1728u,update(state+1728u,ADDRESS(median_spacing)));
 put(state+1732u,update(state+1732u,ADDRESS(mean_amplitude)));
 if(byte(state+81u)<3u)return 1;
 frame.mode2_confidence=0;frame.mode1_confidence=0;frame.mode2_rate=0xbf800000u;frame.mode1_rate=0xbf800000u;
 r1_gomore_locomotion_control_extract_native(state,ADDRESS(expanded),ADDRESS(maxima),ADDRESS(minima),ADDRESS(controls),ADDRESS(mode1_rate),ADDRESS(mode1_confidence),1);
 r1_gomore_locomotion_control_extract_native(state,ADDRESS(expanded),ADDRESS(maxima),ADDRESS(minima),ADDRESS(controls),ADDRESS(mode2_rate),ADDRESS(mode2_confidence),2);
 frame.fallback_rate=0xbf800000u;frame.fallback_confidence=0;
 if(fallback_needed(state)) {
  smooth(state,&frame);
  r1_gomore_locomotion_feature_reduce_native(ADDRESS(expanded),ADDRESS(maxima),ADDRESS(minima),ADDRESS(controls),ADDRESS(fallback_rate),ADDRESS(fallback_confidence));
 }
 select_outputs(&frame,frame.cached_primary,frame.cached_secondary);return 0;
}

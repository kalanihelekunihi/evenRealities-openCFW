#include <stdint.h>
#include "native_float_bits.h"
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint32_t r1_gomore_optical_compact_native(uint32_t);
#define FP __attribute__((noinline,noclone))
static FP float sub(float a,float b){return a-b;}
static FP float add(float a,float b){return a+b;}
static FP float divide(float a,float b){return a/b;}
static FP float convert(uint32_t x){return (float)x;}
/* Keep repeated comparisons observable across the later period comparison. */
static FP uint32_t less(float a,float b){volatile uint32_t r=a<b;return r;}
static FP uint32_t greater(float a,float b){volatile uint32_t r=a>b;return r;}
static uint32_t bits(float x){union {float value;uint32_t bits;} u={.value=x};return u.bits;}
static float value(uint32_t x){union {float value;uint32_t bits;} u={.bits=x};return u.value;}
static uint32_t byte(uint32_t at){return *(volatile uint8_t *)(uintptr_t)at;}
static uint32_t half(uint32_t at){return *(volatile uint16_t *)(uintptr_t)at;}
static uint32_t word(uint32_t at){return *(volatile uint32_t *)(uintptr_t)at;}
static float sample(uint32_t at){return *(volatile float *)(uintptr_t)at;}
static void put(uint32_t at,uint32_t x){*(volatile uint8_t *)(uintptr_t)at=(uint8_t)x;}
static void put_word(uint32_t at,uint32_t x){*(volatile uint32_t *)(uintptr_t)at=x;}
static uint64_t scale(uint32_t raw,uint64_t factor){return r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(raw),factor);}
static uint32_t carry(uint64_t a,uint64_t b)
{
 uint64_t ka=a>>63?a:UINT64_C(0x8000000000000000)-a;
 uint64_t kb=b>>63?b:UINT64_C(0x8000000000000000)-b;
 return kb>=ka;
}
uint32_t r1_gomore_max_difference_index_native(uint32_t signal,uint32_t begin,uint32_t end)
{
 float next=sample(signal+(begin+1u)*4u),current=sample(signal+begin*4u);
 volatile float initial=sub(next,current);
 float best=initial;uint32_t result=begin;
 for(uint32_t i=begin;(int32_t)i<(int32_t)end;i++) {
  next=sample(signal+(i+1u)*4u);current=sample(signal+i*4u);
  float difference=sub(next,current);
  if(greater(difference,best)){best=difference;result=i&65535u;}
 }
 return result;
}
typedef struct {uint32_t a,b,c,d;} record;
static record read_record(uint32_t at)
{
 uint32_t b=word(at+4u),c=word(at+8u),a=word(at),d=word(at+12u);
 return (record){a,b,c,d};
}
static void publish(uint32_t at,record r)
{put_word(at,r.a);put_word(at+4u,r.b);put_word(at+8u,r.c);put_word(at+12u,r.d);}
static void shift_record(uint32_t at,record r)
{put_word(at+4u,r.b);put_word(at+8u,r.c);put_word(at,r.a);put_word(at+12u,r.d);}
static FP uint32_t merge(uint32_t state,uint32_t maxima,uint32_t minima,uint32_t candidate_count,uint32_t output_argument,uint32_t inherited_padding)
{
 uint32_t total=word(state+84u),offset=(total<20u?(total-10u)*25u:250u)&65535u;
 r1_gomore_optical_compact_native(state);
 uint32_t cached=byte(state+81u),cursor=0;
 for(uint32_t i=0;(int32_t)i<(int32_t)byte(candidate_count);i++) {
  uint32_t end_index=byte(maxima+i),end=(offset+end_index)&65535u;
  uint32_t start_index=byte(minima+i),start=(offset+start_index)&65535u;
  float end_value=sample(state+728u+end_index*4u),start_value=sample(state+728u+start_index*4u);
  uint32_t middle=(r1_gomore_max_difference_index_native(state+728u,start_index,end_index)+offset)&65535u;
  record candidate={end|(start<<16),middle|(inherited_padding<<16),bits(end_value),bits(start_value)};
  if(cached && (int32_t)cursor<(int32_t)(cached-1u)) {
   uint32_t at=state+88u+cursor*16u;
   while(half(at)<end && half(at+2u)<start) {
    uint32_t next=cursor+1u;if(next>=cached)break;cursor=next&255u;at=state+88u+cursor*16u;
   }
   record old=read_record(at);uint32_t old_end=old.a&65535u,old_start=old.a>>16;
   if((int32_t)cursor>=(int32_t)(cached-1u) && old_end<end){i--;continue;}
   if(old_start==start && old_end==end)continue;
   if(old_start>start && old_end>end) {
    uint32_t count=byte(state+81u);if(count>=40u)return 1;
    for(uint32_t n=count;(int32_t)n>(int32_t)cursor;n--)shift_record(state+88u+n*16u,read_record(state+88u+(n-1u)*16u));
    put(state+81u,byte(state+81u)+1u);publish(at,candidate);cached=(cached+1u)&255u;continue;
   }
   uint64_t tolerance=scale(word(state+1728u),UINT64_C(0x3fe0000000000000));
   uint32_t selected=!carry(r1_signed32_to_binary64_bits(old_end-end),tolerance);
   if(!selected) {
    tolerance=scale(word(state+1728u),UINT64_C(0x3fe0000000000000));
    selected=!carry(r1_signed32_to_binary64_bits(old_start-start),tolerance);
   }
   if(!selected)continue;
   float old_amplitude=sub(value(old.c),value(old.d)),new_amplitude=sub(end_value,start_value);
   float smaller=less(old_amplitude,new_amplitude)?old_amplitude:new_amplitude;
   uint64_t threshold=scale(word(state+1732u),UINT64_C(0x3fe6666666666666));
   uint32_t replace=0;
   if(!carry(r1_binary32_to_binary64_bits(bits(smaller)),threshold))replace=less(old_amplitude,new_amplitude);
   else {
    float period=sample(state+1728u);
    if(greater(period,0.0f)) {
     uint32_t target=r1_binary64_to_unsigned32_bits(scale(bits(period),UINT64_C(0x3fd3333333333333)))&255u;
     int32_t old_delta=(int32_t)target-(int32_t)((old_end-old_start)&255u),new_delta=(int32_t)target-(int32_t)((end-start)&255u);
     uint32_t old_distance=old_delta<0?(uint32_t)-old_delta:(uint32_t)old_delta;
     uint32_t new_distance=new_delta<0?(uint32_t)-new_delta:(uint32_t)new_delta;
     uint32_t largest=(old_distance>new_distance?old_distance:new_distance)&255u;
     if(largest<=(target>>1))replace=less(old_amplitude,new_amplitude);
     else replace=old_distance>new_distance;
    }
   }
   if(replace) {
    uint32_t next=state+88u+(cursor+1u)*16u;
    if(half(next)<end && half(next+2u)<start)old=candidate;
   }
   (void)old; /* The native replacement changes only this discarded private copy. */
   continue;
  }
  uint32_t count=byte(state+81u),last=UINT32_MAX;
  if(count) {
   uint32_t at=state+88u+(count-1u)*16u;
   if(half(at)>=end || half(at+2u)>=start)last=count-1u;
  }
  if((int32_t)last>=0)publish(state+88u+last*16u,candidate);
  else {
   if(count>=40u)return 1;
   publish(state+88u+count*16u,candidate);put(state+81u,byte(state+81u)+1u);
  }
 }
 uint32_t count=byte(state+81u);
 for(uint32_t i=0;(int32_t)i<(int32_t)(count-1u);i++) {
  uint32_t at=state+88u+i*16u,next=at+16u;
  uint32_t next_end=half(next),end=half(at);
  if(next_end<=end){put(state+81u,0);return 1;}
  uint32_t next_start=half(next+2u),start=half(at+2u);
  if(next_start<=start){put(state+81u,0);return 1;}
 }
 if(count) {
  float sum=0.0f;
  for(uint32_t i=0;i<count;i++) {
   float end=sample(state+96u+i*16u),start=sample(state+100u+i*16u);
   sum=add(sub(end,start),sum);
  }
  *(volatile float *)(uintptr_t)word(output_argument)=divide(sum,convert(count));
 }
 return 0;
}
uint32_t r1_gomore_optical_interval_merge_native(uint32_t state,uint32_t maxima,uint32_t minima,uint32_t candidate_count,volatile uint32_t output)
{
 *(volatile float *)(uintptr_t)output=0.0f;
 /* Native publishes the untouched halfword at entry SP-114 as record padding.
    Capture the mapped stack bytes before our worker uses that stack region. */
 uint32_t entry=(uint32_t)(uintptr_t)__builtin_dwarf_cfa();
 uint32_t padding=half(entry-114u);
 uint32_t result=merge(state,maxima,minima,candidate_count,(uint32_t)(uintptr_t)&output,padding);
 *(volatile uint16_t *)(uintptr_t)(entry-114u)=(uint16_t)padding;
 return result;
}

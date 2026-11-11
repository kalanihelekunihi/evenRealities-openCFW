/* Native optical accumulation0x2f660, decimated signed16 window0x665a0
 * and accumulation dispatch0x357ce. Shared rolling features execute in C.
 * Motion processing remains an explicit provider. The native comparisons use
 * float bit patterns; encoded conversions avoid out-of-range C casts.
 */
#include <stdint.h>
#include <stddef.h>
extern void *memmove(void *,const void *,size_t);
extern void r1_goodix_native_rolling_pair(const volatile float *,uint32_t,const void *,void *);
extern void r1_goodix_native_float_window_push(float,void *);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint16_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static uint8_t B(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static void SH(uintptr_t p,uint32_t o,uint16_t v){*(volatile uint16_t *)(p+o)=v;}
static void SB(uintptr_t p,uint32_t o,uint8_t v){*(volatile uint8_t *)(p+o)=v;}
static float F(uintptr_t p,uint32_t o){return *(const volatile float *)(p+o);}
static uint32_t bits(float v){union{float f;uint32_t u;}x={.f=v};return x.u;}
static float value(uint32_t v){union{float f;uint32_t u;}x={.u=v};return x.f;}
static uint32_t rem(uint32_t a,uint32_t b){return b?a%b:a;}
void r1_goodix_native_decimated_s16_push(void *record,uint32_t sample)
{
 uintptr_t p=(uintptr_t)record;
 if(!rem(B(p,10),B(p,11))){
  uint32_t count=H(p,4),capacity=H(p,6);uintptr_t values=W(p,0);
  if(count<capacity){SH(values,count*2u,(uint16_t)sample);SH(p,4,(uint16_t)(H(p,4)+1u));}
  else{memmove((void *)values,(const void *)(values+2u),capacity*2u-2u);SH(W(p,0),H(p,6)*2u-2u,(uint16_t)sample);}
  uint16_t cursor=(uint16_t)(H(p,8)+1u);SH(p,8,cursor);if(cursor>=H(p,6))cursor=0;SH(p,8,cursor);
 }
 uint8_t phase=(uint8_t)(B(p,10)+1u);SB(p,10,phase);if(phase>=B(p,11))phase=0;SB(p,10,phase);
}
static uint32_t unsigned_truncate(uint32_t v)
{
 uint32_t fp=__builtin_arm_get_fpscr(),m=v&0x7fffffffu,e=m>>23,f=m&0x7fffffu,sign=v>>31,r=0,flags=0;
 if(e==255){flags=1;if(!f&&!sign)r=0xffffffffu;}
 else if(!e){if(f)flags=(fp&(1u<<24))?128u:16u;}
 else if(e<127)flags=16;
 else if(sign||e>158){flags=1;if(!sign)r=0xffffffffu;}
 else{uint32_t sig=f|0x800000u;if(e<150){uint32_t shift=150-e;r=sig>>shift;if(sig&((1u<<shift)-1u))flags=16;}else r=sig<<(e-150);}
 __builtin_arm_set_fpscr(fp|flags);return r;
}
static uint32_t native_abs_bits(uint32_t v)
{
 uint32_t fp=__builtin_arm_get_fpscr(),m=v&0x7fffffffu;
 if((fp&(1u<<24))&&m&&m<0x800000u){m=0;fp|=128;}
 uint32_t flags;
 if(m>0x7f800000u){flags=0x30000000u;fp|=1;}
 else if(!m)flags=0x60000000u;
 else if(v>>31){flags=0x80000000u;v^=0x80000000u;}
 else flags=0x20000000u;
 __builtin_arm_set_fpscr((fp&0x0fffffffu)|flags);return v;
}
/* Keep the division conditional: speculation would alter active FPSCR. */
__attribute__((noinline)) static float conditional_divide(float numerator,float denominator){return numerator/denominator;}
static float ratio(uintptr_t record)
{
 float numerator=F(W(record,48),(uint32_t)H(record,52)*4u-4u);
 uint32_t count=H(record,20),index=count>13u?count-13u:0;
 float denominator=F(W(record,16),index*4u);
 if((int32_t)bits(denominator)<=0x358637bd)denominator=value(0x358637bd);
 return numerator/denominator;
}
void r1_goodix_spo2_optical_accumulate(const volatile float *input,uint32_t sequence,const void *descriptor,void *record)
{
 uintptr_t p=(uintptr_t)record,d=(uintptr_t)descriptor;
 r1_goodix_native_rolling_pair(input+2,sequence,descriptor,(void *)p);
 r1_goodix_native_rolling_pair(input+4,sequence,descriptor,(void *)(p+100));
 uint32_t period=W(d,88);
 if(rem(sequence,period)==period-1u){
  float first=ratio(p);r1_goodix_native_float_window_push(first,(void *)(p+216));
  float second=ratio(p+100);r1_goodix_native_float_window_push(second,(void *)(p+232));
  uint32_t magnitude=native_abs_bits(bits(first));float combined=0;
  if((int32_t)magnitude>=0x33d6bf95)combined=conditional_divide(second,first);
  if(bits(combined)+0xc1b33333u>=0x01b33334u)combined=0;
  r1_goodix_native_float_window_push(combined,(void *)(p+200));
 }
 float pulse=input[2]*0.5f;
 r1_goodix_native_decimated_s16_push((void *)(p+248),unsigned_truncate(bits(pulse))&0xffffu);
}
extern void r1_goodix_spo2_motion_accumulate(const volatile uint32_t *,uint32_t,const void *,volatile uint32_t *);
uint32_t r1_goodix_spo2_accumulate(void *input,const void *descriptor,void *result)
{
 const volatile uint32_t *raw=input;volatile uint32_t *output=result;
 /* Match stock load order and reload the sequence after each stage. */
 uint32_t optical_output=output[0],sequence=raw[0],optical_input=raw[6];
 r1_goodix_spo2_optical_accumulate((const volatile float *)(uintptr_t)optical_input,sequence,descriptor,(void *)(uintptr_t)optical_output);
 r1_goodix_spo2_motion_accumulate(raw+3,raw[0],descriptor,output+1);
 sequence=raw[0];return sequence%25u==24u && sequence+1u>=125u?0u:4u;
}

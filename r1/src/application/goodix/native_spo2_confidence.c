/* Native confidence0x95828: actual C features,timing statistics,
 * software-double blend,live counters,rolling rate history and Gaussian. */
#include "native_spo2_confidence.h"
#include <stdint.h>
#include "native_dual_window_features.h"
#include "native_spo2_statistics.h"
#include "native_spo2_summary.h"
#include "native_gaussian_interval.h"
#include "../runtime/native_f32_integer.h"
#include "../runtime/native_float_bits.h"
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t),r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
extern void *goodix_mem_malloc(int32_t);
extern void goodix_mem_free(void *);
extern void r1_goodix_native_float_window_push(float,void *);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint32_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static uint32_t Y(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static void SY(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint8_t *)(p+o)=(uint8_t)v;}
static float F(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static uint32_t B(float x){union{uint32_t u;float f;}v={.f=x};return v.u;}
__attribute__((noinline)) static float from_signed(int32_t x){volatile float v=(float)x;return v;}
static int32_t distance(uint32_t a,uint32_t b){uint32_t d=a-b;if(d&0x80000000u)d=b-a;return (int32_t)d;}
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

void r1_goodix_spo2_confidence(void *record_pointer,const void *configuration,void *state_pointer)
{
 uintptr_t record=W((uintptr_t)record_pointer,0),state=W((uintptr_t)state_pointer,0),config=(uintptr_t)configuration;
 uint32_t rms0=0,rms1=0,correlation=0,rate0=0,rate1=0,quality0=0,quality1=0;
 r1_goodix_native_dual_window_features((void *)record,&rms0,&rms1,&correlation,&rate0,&rate1,&quality0,&quality1);
 int32_t rate=(int32_t)rate0;uint32_t quality=quality0;
 if(distance(rate0,rate1)<10){uint64_t b=r1_format_double_multiply_bits(r1_signed32_to_binary64_bits(rate1),UINT64_C(0x3fc999999999999a));uint64_t a=r1_format_double_multiply_bits(r1_signed32_to_binary64_bits(rate0),UINT64_C(0x3fe999999999999a));rate=(int32_t)r1_binary64_to_signed32_bits(r1_format_double_add_bits(a,b));if(!(compare(quality0,quality1)&0x20000000u))quality=quality1;}
 else if(!rate0&&(int32_t)rate1>0){rate=(int32_t)rate1;quality=quality1;}
 if(!W(config,28))return;
 uintptr_t timing=(uintptr_t)goodix_mem_malloc(496);
 for(int32_t i=0;i<(int32_t)H(record,252)-1;++i){uintptr_t p=W(record,248);int32_t delta=(int32_t)(H(p,(uint32_t)(i+1)*2u)-H(p,(uint32_t)i*2u));S(timing,(uint32_t)i*4u,B(from_signed(delta)));}
 (void)r1_goodix_native_array_mean((void *)timing,124);uint32_t deviation=B(r1_goodix_native_array_standard_deviation(124.0f,(void *)timing));goodix_mem_free((void *)timing);
 if((int32_t)quality>(int32_t)0x42a00000u&&(int32_t)deviation>(int32_t)0x42c80000u)S(state,0,W(state,0)+1u);else S(state,0,0);
 if((int32_t)quality>(int32_t)0x42a00000u&&(int32_t)deviation<(int32_t)0x42480000u)S(state,4,W(state,4)+1u);else S(state,4,0);
 if((int32_t)W(state,0)>4)SY(state,36,1);else if((int32_t)W(state,4)>4)SY(state,36,0);
 if(rate<=0){SY(state,8,Y(state,8)+1u);return;}
 uintptr_t window=state+20;int32_t old=(int32_t)r1_native_f32_integer_bits(B(r1_goodix_native_window_last((void *)window)),0);int32_t diff=distance((uint32_t)old,(uint32_t)rate);int32_t mode=(int8_t)Y(state,36);int32_t limit=mode==0?200:(mode==1||mode==2?2000:0);
 int accept=0;
 if(diff<10){if(old){if((int32_t)quality>(int32_t)0x42480000u)accept=1;}else if(rate>50&&rate<90&&(int32_t)quality>(int32_t)0x42200000u)accept=1;}
 else if(!old&&rate>50&&rate<90&&(int32_t)quality>(int32_t)0x42200000u)accept=1;
 if(!accept){if(diff<5&&old)accept=1;else if(!old&&(int32_t)quality>(int32_t)0x428c0000u)accept=1;
  if(!accept&&Y(state,8)>=10u&&((int32_t)quality>(int32_t)0x428c0000u||(rate>50&&rate<90&&(int32_t)quality>(int32_t)0x42200000u)))accept=1;}
 if(accept){uint32_t flags=compare(deviation,B(from_signed(limit)));if(flags==0x20000000u&&old)rate=old;r1_goodix_native_float_window_push(from_signed(rate),(void *)window);SY(state,8,0);}else SY(state,8,Y(state,8)+1u);
 r1_goodix_native_float_window_mean((void *)window,(void *)(state+12));if(r1_goodix_native_window_count((void *)window)<=1u){S(state,16,0);return;}
 uint32_t radius=r1_log_double_to_float_bits(r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(W(state,12)),UINT64_C(0x3fa999999999999a)));uint32_t sigma=0;r1_goodix_native_window_standard_deviation((void *)window,&sigma);float probability=r1_goodix_native_gaussian_interval(F(radius^0x80000000u),F(radius),0.0f,F(sigma),F(0x3dcccccdu));S(state,16,B(probability));
}

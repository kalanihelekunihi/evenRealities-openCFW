/* Native rate extraction0x42bd0: preserve raw selection,integer-mean
 * filtering,actual heap,gap tolerance and mixed-precision rounding. */
#include "native_peak_rate.h"
#include <stdint.h>
#include "../runtime/native_f32_integer.h"
#include "../runtime/native_float_bits.h"
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern void *goodix_mem_malloc(int32_t);
extern void goodix_mem_free(void *);
extern float r1_goodix_native_array_mean(const void *,uint32_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint32_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static float F(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static uint32_t B(float x){union{uint32_t u;float f;}v={.f=x};return v.u;}
__attribute__((noinline)) static float from_signed(int32_t x){volatile float v=(float)x;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
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

void r1_goodix_native_peak_rate(const void *values,const void *indices,uint32_t count,void *output)
{
 uintptr_t v=(uintptr_t)values,ix=(uintptr_t)indices,out=(uintptr_t)output;
 uintptr_t selected=(uintptr_t)goodix_mem_malloc((int32_t)(count*4u));int32_t used=0;
 int32_t mean=(int32_t)r1_native_f32_integer_bits(B(r1_goodix_native_array_mean(values,count)),0);
 for(uint32_t i=0;i<count;++i)if((int32_t)W(v,i*4u)>=(int32_t)0x3dcccccdu){S(selected,(uint32_t)used*4u,H(ix,i*2u));++used;}
 if(used>=7){int32_t kept=0;for(int32_t i=0;i<used;++i){float threshold=from_signed(mean);uint32_t flags=compare(W(v,(uint32_t)i*4u),B(threshold));if(flags==0x60000000u||flags==0x20000000u){S(selected,(uint32_t)kept*4u,W(selected,(uint32_t)i*4u));++kept;}}used=kept;}
 if((uint32_t)(used-3)>=11u){S(out,0,0);goodix_mem_free((void *)selected);return;}
 uintptr_t gaps=(uintptr_t)goodix_mem_malloc(used*4-4);
 for(int32_t i=0;i<used-1;++i)S(gaps,(uint32_t)i*4u,W(selected,(uint32_t)(i+1)*4u)-W(selected,(uint32_t)i*4u));
 int valid=1;for(int32_t i=0;i<used-2;++i){int32_t first=(int32_t)W(gaps,(uint32_t)i*4u),second=(int32_t)W(gaps,(uint32_t)(i+1)*4u);int32_t delta=second-first;if(delta<0)delta=first-second;if(delta>3){valid=0;break;}}
 int32_t span=(int32_t)(W(selected,(uint32_t)(used-1)*4u)-W(selected,0));if(span<=0)valid=0;
 if(!valid)S(out,0,0);
 else{float n=from_signed(used-1),scaled=mul(n,1500.0f),denominator=from_signed(span);float rate=divide(scaled,denominator);int32_t result=(int32_t)r1_binary64_to_signed32_bits(r1_format_double_add_bits(r1_binary32_to_binary64_bits(B(rate)),UINT64_C(0x3fe0000000000000)));S(out,0,(uint32_t)result);if(result>200)S(out,0,200);else if(result<40)S(out,0,40);}
 goodix_mem_free((void *)selected);goodix_mem_free((void *)gaps);
}

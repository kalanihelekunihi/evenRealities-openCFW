/* Native SpO2 output-quality stage0x44a78. Uses the reconstructed C
 * rolling window/extrema and software double helpers. Preserve saturation,
 * whole-byte versus low-three-bit flag policies and signaling FP status.
 * See r1/docs/reference/goodix-spo2-output-quality-c-review.md.
 */
#include "native_spo2_output_quality.h"
#include <stdint.h>
#include "../runtime/native_float_bits.h"
extern void r1_goodix_native_float_window_push(float,void *);
extern void r1_goodix_native_maximum_index(const void *,uint32_t,void *,void *);
extern void r1_goodix_native_float_min_index(const void *,uint32_t,void *,void *);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint32_t U8(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static uint32_t U16(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static void SB(uintptr_t p,uint32_t o,uint32_t x){*(volatile uint8_t *)(p+o)=(uint8_t)x;}
static float F(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static uint32_t B(float x){union{uint32_t u;float f;}v={.f=x};return v.u;}
__attribute__((noinline)) static float sub(float a,float b){volatile float x=a-b;return x;}
__attribute__((noinline)) static float add(float a,float b){volatile float x=a+b;return x;}
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
void r1_goodix_spo2_output_quality(const void *configuration,void *summary,void *adjusted,void *owner)
{
 uintptr_t config=(uintptr_t)configuration,record=W((uintptr_t)summary,8),state=W((uintptr_t)owner,0);
 if(U8(record,41))SB(state,0,0);else if(U8(state,0)<255)SB(state,0,U8(state,0)+1);
 uintptr_t window=state+4;r1_goodix_native_float_window_push(F(W((uintptr_t)adjusted,0)),(void *)window);
 float threshold=(float)U8(config,74);uint32_t count=U16(window,4);uintptr_t data=W(window,0);int32_t span=(int8_t)U8(config,72);
 uint32_t rounded=r1_binary64_to_signed32_bits(r1_format_double_add_bits(r1_binary32_to_binary64_bits(W(data,(count-1u)*4u)),UINT64_C(0x3fe0000000000000)));
 if((int32_t)U8(config,68)<=(int32_t)rounded){span=(int8_t)U8(config,71);threshold=(float)U8(config,73);}
 uint32_t maximum,minimum,max_index,min_index;
 if((int32_t)(count-(uint32_t)span)>=0){
  r1_goodix_native_maximum_index((void *)(data+(count-(uint32_t)span)*4u),(uint32_t)span,&maximum,&max_index);
  r1_goodix_native_float_min_index((void *)(uintptr_t)(W(window,0)+(U16(window,4)-(uint32_t)span)*4u),(uint32_t)span,&minimum,&min_index);
 }else{maximum=B(add(threshold,1.0f));minimum=0;max_index=0;min_index=0;}
 uint32_t insufficient=(int32_t)U8(state,0)<span;
 float difference=sub(F(maximum),F(minimum));if(!(compare(B(difference),0)&0x20000000u))difference=sub(F(minimum),F(maximum));
 uint32_t greater=compare(B(difference),B(threshold))==0x20000000u;SB(state,20,(insufficient<<2)|(greater<<7));
 if(U8(record,41)&7u)SB(state,21,0);else if(U8(state,21)<255)SB(state,21,U8(state,21)+1);
}

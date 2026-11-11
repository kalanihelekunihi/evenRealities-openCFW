/* Native SpO2 snapshot/packet stage0x36974. Preserve live field reads,
 * signed status, single-precision scaling before software double rounding,
 * confidence gates and ordered writes. No assembly or owned global state.
 * See r1/docs/reference/goodix-spo2-output-c-review.md.
 */
#include "native_spo2_output.h"
#include <stdint.h>
#include "../runtime/native_float_bits.h"
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint32_t U8(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t x){*(volatile uint32_t *)(p+o)=x;}
static void SB(uintptr_t p,uint32_t o,uint32_t x){*(volatile uint8_t *)(p+o)=(uint8_t)x;}
static float F(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static uint32_t B(float x){union{uint32_t u;float f;}v={.f=x};return v.u;}
__attribute__((noinline)) static float multiply(float a,float b){volatile float v=a*b;return v;}
static uint32_t rounded(uint32_t x){return r1_binary64_to_signed32_bits(r1_format_double_add_bits(r1_binary32_to_binary64_bits(x),UINT64_C(0x3fe0000000000000)));}
static uint32_t scaled(uint32_t x,float factor){return rounded(B(multiply(F(x),factor)));}
void r1_goodix_spo2_output(const void *configuration,void *inference,void *selected,void *valid,void *summary,void *confidence_owner,void *state_owner,void *packet)
{
 uintptr_t cfg=(uintptr_t)configuration,in=(uintptr_t)inference,out=(uintptr_t)selected,status=(uintptr_t)valid,summary_record=(uintptr_t)summary,confidence=(uintptr_t)confidence_owner,destination=(uintptr_t)packet;
 uintptr_t state=W((uintptr_t)state_owner,0);
 S(state,24,W(out,0));SB(state,28,U8(status,0));SB(state,29,U8(summary_record,42));S(state,32,0);
 if(W(cfg,28)==1){S(state,36,W(W(confidence,0),12));S(state,40,W(W(confidence,0),16));}else{S(state,36,0);S(state,40,0);}
 SB(state,44,U8(summary_record,41));S(state,48,W(summary_record,28));S(state,52,W(summary_record,8));S(state,56,W(summary_record,32));S(state,60,W(summary_record,12));S(state,64,W(in,0));
 S(destination,0,scaled(W(out,0),10000.0f));S(destination,4,(uint32_t)(int32_t)(int8_t)U8(status,0));S(destination,8,U8(summary_record,42));S(destination,12,0);
 if(W(cfg,28)==1){S(destination,16,rounded(W(W(confidence,0),12)));S(destination,20,scaled(W(W(confidence,0),16),100.0f));}else{S(destination,16,0);S(destination,20,0);}
 S(destination,24,U8(summary_record,41));S(destination,28,scaled(W(summary_record,28),100000.0f));S(destination,32,scaled(W(summary_record,8),100000.0f));S(destination,36,0);S(destination,40,0);
 S(destination,44,scaled(W(in,0),10000.0f));S(destination,48,1);S(destination,52,0);S(destination,56,0);S(destination,60,0);
}

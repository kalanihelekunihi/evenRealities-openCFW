/* SPDX-License-Identifier: MIT
 * Fixed-ABI reconstruction of locked428068..428240 (472bytes).
 * Pinned Apollo510 PCM2.2 transition_sequence_1 corroborates the sequence;
 * locked instructions govern delay values and the R0/R1 return.
 */
#include <stdint.h>
#define W(p) (*(volatile uint32_t *)(uintptr_t)(p))
extern void event_a_power_ton_adjust(uint32_t,uint32_t);
extern uint32_t opencfw_pcm22_timer_service(void);
extern void opencfw_hal_delay_us(uint32_t);
extern void opencfw_pcm22_icache_disable(void);
extern void opencfw_boot_icache_enable(void);
static uint32_t boost(uint32_t target,uint32_t current) {
 int32_t delta=(int32_t)(target-current);
 uint32_t value=current+(delta>0?(uint32_t)delta*2u:0u);
 return value<128u?value:127u;
}
uint64_t opencfw_spot_pcm22_transition1(uint32_t target,uint32_t current,uint32_t ton,uint32_t current_ton) {
 (void)current_ton;
 uintptr_t p=0x20026ba4u+target*4u;
 uint32_t n=W(p),o=W(0x20026ba4u+current*4u);
 /* Original rereads the volatile low-voltage word for each packed byte. */
 uint32_t packed=(W(0x20026c04u)&127u)|(((W(0x20026c04u)>>7)&127u)<<8)|(((W(0x20026c04u)>>14)&127u)<<16)|(((W(0x20026c04u)>>21)&127u)<<24);
 uint32_t nf=n&127u,of=o&127u,nc=(n>>21)&127u,oc=(o>>21)&127u;
 if(W(0x400083e0u)&1u) {
  for(uint32_t i=0;i<60u;i++){if(W(0x40008064u)&0x40000000u)break;opencfw_hal_delay_us(1);}
  (void)opencfw_pcm22_timer_service();
 }
 W(0x200270c0u)=ton;W(0x200270c4u)=target;
 W(0x200270b8u)=(W(p)>>7)&1023u;W(0x200270bcu)=(W(p)>>17)&15u;
 W(0x200270b0u)=nc;W(0x200270b4u)=nf;
 event_a_power_ton_adjust(ton,target);
 W(0x4002004cu)=(W(0x4002004cu)&~127u)|boost(nf,of);
 W(0x40020044u)=(W(0x40020044u)&~127u)|boost(nc,oc);
 opencfw_hal_delay_us(50);
 W(0x40020044u)=(W(0x40020044u)&~127u)|nc;
 W(0x40020080u)=(W(0x40020080u)&~0x3c00u)|(((W(p)>>17)&15u)<<10);
 W(0x40020080u)=(W(0x40020080u)&~1023u)|((W(p)>>7)&1023u);
 opencfw_hal_delay_us(5);
 W(0x4002004cu)=(W(0x4002004cu)&~127u)|nf;
 uint32_t enabled=W(0xe000ed14u)&0x20000u;
 if(enabled)opencfw_pcm22_icache_disable();
 W(0x4002037cu)|=0x10000u;W(0x4002037cu)|=8u;W(0x4002037cu)|=0x40u;
 opencfw_hal_delay_us(20);
 if(enabled)opencfw_boot_icache_enable();
 return ((uint64_t)packed<<32)|(uint32_t)p;
}

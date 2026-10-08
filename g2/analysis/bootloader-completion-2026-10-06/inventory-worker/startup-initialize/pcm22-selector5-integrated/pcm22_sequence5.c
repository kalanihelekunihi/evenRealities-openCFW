/* Reconstruction of locked 42863e..428840; private raw-R0 ABI, not status. */
#include <stdint.h>
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern void opencfw_hal_delay_us(uint32_t);
extern uint32_t opencfw_pcm22_timer_service(void);
extern void opencfw_pcm22_spot_timer_stop(void);
extern void event_a_power_ton_adjust(uint32_t,uint32_t);
extern uint32_t opencfw_boot_control_delay_status_change(uint32_t,volatile uint32_t *,uint32_t,uint32_t);
__attribute__((section(".text.pcm22_sequence5")))
uint32_t opencfw_spot_pcm22_transition5(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton){
 (void)old_ton;
 uintptr_t profile=0x20026ba0,word=profile+4+target*4;
 uint32_t p0=B(profile+0x64)&127,p1=(W(profile+0x64)>>7)&127,p2=(W(profile+0x64)>>14)&127,p3=(W(profile+0x64)>>21)&127;
 uint32_t packed=p0|(p1<<8)|(p2<<16)|(p3<<24);
 (void)B(profile+4+current*4);(void)W(profile+4+current*4);
 uint32_t ldo=(W(word)>>21)&127,vddf=B(word)&127;
 if(W(0x400083e0)&1){
  if(target==W(0x20000154)){
   (void)event_a_power_ton_adjust(ton,target);
   W(0x40020044)=(W(0x40020044)&~127u)|ldo;
   (void)opencfw_pcm22_spot_timer_stop();B(0x2000055a)=26;return packed;
  }
  /* Hardware control is deliberately reread after the last-state comparison. */
  if(W(0x400083e0)&1){
   uint32_t n=0;while(n<60 && !(W(0x40008064)&0x40000000)){opencfw_hal_delay_us(1);n++;}
   (void)opencfw_pcm22_timer_service();
  }
 }
 W(0x200270c0)=ton;W(0x200270c4)=target;
 W(0x200270b8)=(W(word)>>7)&1023;W(0x200270bc)=(W(word)>>17)&15;
 W(0x200270b0)=ldo;W(0x200270b4)=vddf;
 (void)event_a_power_ton_adjust(ton,target);
 W(0x40021000)=(W(0x40021000)&~3u)|1u;
 uint32_t n=0;while(n<20 && !(W(0x40021000)&4)){opencfw_hal_delay_us(1);n++;}
 W(0x4002037c)=W(0x4002037c)&~8u;
 W(0x4002037c)=W(0x4002037c)&~64u;
 W(0x4002037c)=W(0x4002037c)|0x02000000u;
 uint32_t temporary=0;
 if(!(W(0x40004044)&32)){
  W(0x40004044)=W(0x40004044)|32u;opencfw_hal_delay_us(1);
  (void)opencfw_boot_control_delay_status_change(15,(volatile uint32_t *)0x40004030,0x01000000,0x01000000);
  temporary=1;
 }
 if(W(0x40004030)&0x01000000){
  W(0x40021000)=(W(0x40021000)&~3u)|2u;
  n=0;while(n<20 && !(W(0x40021000)&4)){opencfw_hal_delay_us(1);n++;}
 }
 if(temporary)W(0x40004044)=W(0x40004044)&~32u;
 /* Profile core/tempco are reread; LDO is the pre-timer snapshot. */
 uint32_t temp=(W(word)>>17)&15;
 W(0x40020080)=(W(0x40020080)&~0x3c00u)|(temp<<10);
 uint32_t core=(W(word)>>7)&1023;
 W(0x40020080)=(W(0x40020080)&~1023u)|core;
 W(0x40020044)=(W(0x40020044)&~127u)|ldo;
 return packed;
}

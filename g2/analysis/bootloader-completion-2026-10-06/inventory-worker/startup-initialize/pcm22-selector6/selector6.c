/* Fixed-address reconstruction of locked selector6,428840..42891e. */
#include <stdint.h>
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern void opencfw_hal_delay_us(uint32_t);
extern uint32_t opencfw_pcm22_timer_service(void);
extern void event_a_power_ton_adjust(uint32_t,uint32_t);
uint32_t opencfw_spot_pcm22_transition6(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton){
 (void)old_ton;
 uintptr_t profile=0x20026ba0,word=profile+4+target*4;
 uint32_t p0=B(profile+0x64)&127,p1=(W(profile+0x64)>>7)&127,p2=(W(profile+0x64)>>14)&127,p3=(W(profile+0x64)>>21)&127;
 uint32_t packed=p0|(p1<<8)|(p2<<16)|(p3<<24);
 /* Stock reads current profile word/packed LV bytes before timer handling. */
 (void)B(profile+4+current*4);(void)W(profile+4+current*4);
 uint32_t target_ldo=(W(word)>>21)&127,target_vddf=B(word)&127;
 if(W(0x400083e0)&1){
  uint32_t elapsed=0;
  while(elapsed<60 && !(W(0x40008064)&0x40000000)){opencfw_hal_delay_us(1);elapsed++;}
  (void)opencfw_pcm22_timer_service();
 }
 W(0x200270c0)=ton;W(0x200270c4)=target;
 W(0x200270b8)=(W(word)>>7)&1023;W(0x200270bc)=(W(word)>>17)&15;
 W(0x200270b0)=target_ldo;W(0x200270b4)=target_vddf;
 W(0x4002004c)=(W(0x4002004c)&~127u)|target_vddf;
 event_a_power_ton_adjust(ton,target);return packed;
}

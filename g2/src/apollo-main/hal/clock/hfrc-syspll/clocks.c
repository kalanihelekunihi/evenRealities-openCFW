#include "clocks.h"
#include "../clock/clock-manager-ownership/ownership.h"
#include "../xtal-request/request.h"
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20004530[] __asm__("g2_stock_ram_20004530");
extern unsigned char g2ref_g2_stock_ram_20073f30[] __asm__("g2_stock_ram_20073f30");
extern unsigned char g2ref_g2_stock_ram_20074228[] __asm__("g2_stock_ram_20074228");
extern unsigned char g2ref_g2_stock_ram_20074f30[] __asm__("g2_stock_ram_20074f30");
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
extern uint32_t stock_save_irq(void),stock_hfrc_force(uint32_t),stock_hfrc_apply(uint32_t),stock_hfrc2_force(uint32_t),stock_hfrc2_apply(const void *),stock_hfrc2_disable(void);
extern uint32_t stock_ext_request(uint32_t),stock_ext_release(uint32_t);
extern uint32_t stock_pll_init(uint32_t,void *),stock_pll_config(uint32_t,const void *),stock_pll_enable(uint32_t),stock_pll_deinit(uint32_t),stock_pll_disable(uint32_t),stock_pll_wait(uint32_t);
static void restore(uint32_t m){__asm volatile("msr primask, %0"::"r"(m):"memory");}
void audio_hfrc_wait(volatile uint32_t *c){if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x27u))){audio_clock_counter_wait((volatile uint8_t*)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x27u),c);uint32_t m=stock_save_irq();B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x29u))=1;B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x27u))=0;W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x3cu))=0;restore(m);}}
void audio_hfrc2_wait(volatile uint32_t *c){if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x28u))){audio_clock_counter_wait((volatile uint8_t*)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x28u),c);uint32_t m=stock_save_irq();B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x28u))=0;W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x40u))=0;restore(m);}}
uint32_t audio_hfrc_request(uint32_t u){
 u=(uint8_t)u;uint32_t s=0;volatile uint32_t c=1000;
 if(audio_clock_user(4,u)){uint32_t m=stock_save_irq();if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x27u)))c=*(volatile uint32_t*)W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x3cu));W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x3cu))=(uint32_t)&c;restore(m);audio_hfrc_wait(&c);return 0;}
 uint32_t m=stock_save_irq();if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x27u)))c=*(volatile uint32_t*)W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x3cu));
 if(!B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20004530+0x6u)))s=1;
 if(!s){
  if(!audio_clock_count(4)){stock_hfrc_force(1);if(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x28u))){s=stock_hfrc_apply(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30)));if(!s){if(!B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x27u))&&!B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x29u)))B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x27u))=1;}else stock_hfrc_force(0);}}
  if(!s)audio_clock_set(4,u,1);
  if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x27u)))W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x3cu))=(uint32_t)&c;
 }
 restore(m);audio_hfrc_wait(&c);return s;
}
uint32_t audio_hfrc_release(uint32_t u){u=(uint8_t)u;if(!audio_clock_user(4,u))return 0;uint32_t m=stock_save_irq();audio_clock_set(4,u,0);if(!audio_clock_any(4))stock_hfrc_force(0);restore(m);return 0;}
uint32_t audio_hfrc2_request(uint32_t u){
 u=(uint8_t)u;uint32_t s=0;volatile uint32_t c=50;
 if(audio_clock_user(5,u)){uint32_t m=stock_save_irq();if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x28u)))c=*(volatile uint32_t*)W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x40u));W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x40u))=(uint32_t)&c;restore(m);audio_hfrc2_wait(&c);return 0;}
 uint32_t m=stock_save_irq();if(!audio_clock_count(5))B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x2au))=1;audio_clock_set(5,u,1);restore(m);
 if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20004530+0x7u))&&W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x2cu))){s=B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0xcu))==0?audio_xtal_request(54):stock_ext_request(54);if(s){m=stock_save_irq();audio_clock_set(5,u,0);restore(m);}}
 if(!s){
  m=stock_save_irq();if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x28u)))c=*(volatile uint32_t*)W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x40u));
  if(!B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20004530+0x7u)))s=1;
  if(!s&&B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x2au))){B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x2au))=0;stock_hfrc2_force(1);if(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x2cu))){s=stock_hfrc2_apply((void*)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0xcu));if(!s){if(!B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x28u)))B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x28u))=1;}else stock_hfrc2_force(0);}}
  if(s)audio_clock_set(5,u,0);
  if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x28u)))W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x40u))=(uint32_t)&c;
  restore(m);
 }
 if(s&&B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20004530+0x7u))&&W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x2cu)))s=B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0xcu))==0?audio_xtal_release(54):stock_ext_release(54);
 audio_hfrc2_wait(&c);return s;
}
uint32_t audio_hfrc2_release(uint32_t u){
 u=(uint8_t)u;if(!audio_clock_user(5,u))return 0;uint32_t m=stock_save_irq();audio_clock_set(5,u,0);
 if(!audio_clock_any(5)){if(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x2cu))){B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x2au))=0;stock_hfrc2_disable();audio_xtal_release(54);stock_ext_release(54);B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x28u))=0;W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x40u))=0;}stock_hfrc2_force(0);}
 restore(m);return 0;
}
uint32_t audio_syspll_request(uint32_t u){
 u=(uint8_t)u;uint32_t s=0,wait=0;if(audio_clock_user(6,u))return 0;
 uint32_t m=stock_save_irq();if(!audio_clock_count(6))B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x2bu))=1;audio_clock_set(6,u,1);restore(m);
 if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x25u))){if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0x18u))==0){s=audio_xtal_request(53);stock_ext_request(53);}else{s=stock_ext_request(53);audio_xtal_request(53);}}
 m=stock_save_irq();
 if(!s){
  if(!B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x25u)))s=1;
  if(!s&&B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x2bu))){
   B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x2bu))=0;if(!W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x34u)))s=stock_pll_init(0,(void*)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x34u));
   if(!s)s=stock_pll_config(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x34u)),(void*)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0x18u));
   if(!s)s=stock_pll_enable(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x34u)));
   if(!s)wait=1;else if(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x34u))){stock_pll_deinit(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x34u)));W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x34u))=0;}
  }
  if(s)audio_clock_set(6,u,0);
 }else audio_clock_set(6,u,0);
 restore(m);
 if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x25u))){if(!s){if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0x18u))==0)stock_ext_release(53);else audio_xtal_release(53);}else{audio_xtal_release(53);stock_ext_release(53);}}
 if(wait)s=stock_pll_wait(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x34u)));return s;
}
uint32_t audio_syspll_release(uint32_t u){
 u=(uint8_t)u;if(!audio_clock_user(6,u))return 0;uint32_t m=stock_save_irq();audio_clock_set(6,u,0);
 if(!audio_clock_any(6)){B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x2bu))=0;stock_pll_disable(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x34u)));stock_pll_deinit(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x34u)));W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x34u))=0;if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0x18u))==0)audio_xtal_release(53);else stock_ext_release(53);}
 restore(m);return 0;
}

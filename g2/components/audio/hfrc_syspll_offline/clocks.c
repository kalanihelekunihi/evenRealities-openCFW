#include "clocks.h"
#include "../clock_manager_ownership_offline/ownership.h"
#include "../xtal_request_offline/request.h"
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
extern uint32_t stock_save_irq(void),stock_hfrc_force(uint32_t),stock_hfrc_apply(uint32_t),stock_hfrc2_force(uint32_t),stock_hfrc2_apply(const void *),stock_hfrc2_disable(void);
extern uint32_t stock_ext_request(uint32_t),stock_ext_release(uint32_t);
extern uint32_t stock_pll_init(uint32_t,void *),stock_pll_config(uint32_t,const void *),stock_pll_enable(uint32_t),stock_pll_deinit(uint32_t),stock_pll_disable(uint32_t),stock_pll_wait(uint32_t);
static void restore(uint32_t m){__asm volatile("msr primask, %0"::"r"(m):"memory");}
void audio_hfrc_wait(volatile uint32_t *c){if(B(0x20074f57)){audio_clock_counter_wait((volatile uint8_t*)0x20074f57,c);uint32_t m=stock_save_irq();B(0x20074f59)=1;B(0x20074f57)=0;W(0x20074264)=0;restore(m);}}
void audio_hfrc2_wait(volatile uint32_t *c){if(B(0x20074f58)){audio_clock_counter_wait((volatile uint8_t*)0x20074f58,c);uint32_t m=stock_save_irq();B(0x20074f58)=0;W(0x20074268)=0;restore(m);}}
uint32_t audio_hfrc_request(uint32_t u){
 u=(uint8_t)u;uint32_t s=0;volatile uint32_t c=1000;
 if(audio_clock_user(4,u)){uint32_t m=stock_save_irq();if(B(0x20074f57))c=*(volatile uint32_t*)W(0x20074264);W(0x20074264)=(uint32_t)&c;restore(m);audio_hfrc_wait(&c);return 0;}
 uint32_t m=stock_save_irq();if(B(0x20074f57))c=*(volatile uint32_t*)W(0x20074264);
 if(!B(0x20004536))s=1;
 if(!s){
  if(!audio_clock_count(4)){stock_hfrc_force(1);if(W(0x20074250)){s=stock_hfrc_apply(W(0x20073f30));if(!s){if(!B(0x20074f57)&&!B(0x20074f59))B(0x20074f57)=1;}else stock_hfrc_force(0);}}
  if(!s)audio_clock_set(4,u,1);
  if(B(0x20074f57))W(0x20074264)=(uint32_t)&c;
 }
 restore(m);audio_hfrc_wait(&c);return s;
}
uint32_t audio_hfrc_release(uint32_t u){u=(uint8_t)u;if(!audio_clock_user(4,u))return 0;uint32_t m=stock_save_irq();audio_clock_set(4,u,0);if(!audio_clock_any(4))stock_hfrc_force(0);restore(m);return 0;}
uint32_t audio_hfrc2_request(uint32_t u){
 u=(uint8_t)u;uint32_t s=0;volatile uint32_t c=50;
 if(audio_clock_user(5,u)){uint32_t m=stock_save_irq();if(B(0x20074f58))c=*(volatile uint32_t*)W(0x20074268);W(0x20074268)=(uint32_t)&c;restore(m);audio_hfrc2_wait(&c);return 0;}
 uint32_t m=stock_save_irq();if(!audio_clock_count(5))B(0x20074f5a)=1;audio_clock_set(5,u,1);restore(m);
 if(B(0x20004537)&&W(0x20074254)){s=B(0x20073f3c)==0?audio_xtal_request(54):stock_ext_request(54);if(s){m=stock_save_irq();audio_clock_set(5,u,0);restore(m);}}
 if(!s){
  m=stock_save_irq();if(B(0x20074f58))c=*(volatile uint32_t*)W(0x20074268);
  if(!B(0x20004537))s=1;
  if(!s&&B(0x20074f5a)){B(0x20074f5a)=0;stock_hfrc2_force(1);if(W(0x20074254)){s=stock_hfrc2_apply((void*)0x20073f3c);if(!s){if(!B(0x20074f58))B(0x20074f58)=1;}else stock_hfrc2_force(0);}}
  if(s)audio_clock_set(5,u,0);
  if(B(0x20074f58))W(0x20074268)=(uint32_t)&c;
  restore(m);
 }
 if(s&&B(0x20004537)&&W(0x20074254))s=B(0x20073f3c)==0?audio_xtal_release(54):stock_ext_release(54);
 audio_hfrc2_wait(&c);return s;
}
uint32_t audio_hfrc2_release(uint32_t u){
 u=(uint8_t)u;if(!audio_clock_user(5,u))return 0;uint32_t m=stock_save_irq();audio_clock_set(5,u,0);
 if(!audio_clock_any(5)){if(W(0x20074254)){B(0x20074f5a)=0;stock_hfrc2_disable();audio_xtal_release(54);stock_ext_release(54);B(0x20074f58)=0;W(0x20074268)=0;}stock_hfrc2_force(0);}
 restore(m);return 0;
}
uint32_t audio_syspll_request(uint32_t u){
 u=(uint8_t)u;uint32_t s=0,wait=0;if(audio_clock_user(6,u))return 0;
 uint32_t m=stock_save_irq();if(!audio_clock_count(6))B(0x20074f5b)=1;audio_clock_set(6,u,1);restore(m);
 if(B(0x20074f55)){if(B(0x20073f48)==0){s=audio_xtal_request(53);stock_ext_request(53);}else{s=stock_ext_request(53);audio_xtal_request(53);}}
 m=stock_save_irq();
 if(!s){
  if(!B(0x20074f55))s=1;
  if(!s&&B(0x20074f5b)){
   B(0x20074f5b)=0;if(!W(0x2007425c))s=stock_pll_init(0,(void*)0x2007425c);
   if(!s)s=stock_pll_config(W(0x2007425c),(void*)0x20073f48);
   if(!s)s=stock_pll_enable(W(0x2007425c));
   if(!s)wait=1;else if(W(0x2007425c)){stock_pll_deinit(W(0x2007425c));W(0x2007425c)=0;}
  }
  if(s)audio_clock_set(6,u,0);
 }else audio_clock_set(6,u,0);
 restore(m);
 if(B(0x20074f55)){if(!s){if(B(0x20073f48)==0)stock_ext_release(53);else audio_xtal_release(53);}else{audio_xtal_release(53);stock_ext_release(53);}}
 if(wait)s=stock_pll_wait(W(0x2007425c));return s;
}
uint32_t audio_syspll_release(uint32_t u){
 u=(uint8_t)u;if(!audio_clock_user(6,u))return 0;uint32_t m=stock_save_irq();audio_clock_set(6,u,0);
 if(!audio_clock_any(6)){B(0x20074f5b)=0;stock_pll_disable(W(0x2007425c));stock_pll_deinit(W(0x2007425c));W(0x2007425c)=0;if(B(0x20073f48)==0)audio_xtal_release(53);else stock_ext_release(53);}
 restore(m);return 0;
}

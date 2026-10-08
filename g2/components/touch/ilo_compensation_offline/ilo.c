/* Independent9d90/9ddc/9e18/5dd8; offline only, no physical oscillator model. */
#include "ilo.h"
#include "../clock_selection_offline/clock.h"
#define REG(a) (*(volatile uint32_t *)(a))
#define FLAG(a) (*(volatile uint8_t *)(a))
#define CORE REG(0x20000878u)
void touch_ilo_start(void){
 if(!FLAG(0x20000f1du)){FLAG(0x20000f1eu)=1;REG(0x40030034u)=(REG(0x40030034u)&0xfffff0ffu)|0x100u;REG(0x40030018u)=(REG(0x40030018u)&0xfffff0f0u)|0x908u;}
}
void touch_ilo_stop(void){
 if(!FLAG(0x20000f1du)){FLAG(0x20000f1eu)=0;REG(0x40030034u)&=0xfffff0ffu;REG(0x40030018u)&=0xf0fu;}
}
uint32_t touch_ilo_measure(uint32_t delay,uint32_t *out){
 if(delay<100u || delay>2000000u || !out)return TOUCH_ILO_BAD_PARAM;
 uint32_t control=REG(0x40030018u),selection=REG(0x40030034u)&0xf0fu;
 if(control!=0x908u || selection!=0x100u)return TOUCH_ILO_INVALID_STATE;
 if(!FLAG(0x20000f1cu)){REG(0x4003001cu)=CORE>>10;FLAG(0x20000f1cu)=1;return TOUCH_ILO_STARTED;}
 if(!(REG(0x4003001cu)&0x80000000u))return TOUCH_ILO_STARTED;
 if(!REG(0x40030020u))return TOUCH_ILO_INVALID_STATE;
 uint32_t rounded=delay*100u+1250u,counts=rounded/2500u,value;
 if(REG(0x40030020u)*counts>=0x400000u){
  uint32_t ratio=(REG(0x40030020u)*CORE)/(CORE>>10);
  value=(ratio/40u)*(rounded/2500000u);
 }else{
  uint32_t ratio=(REG(0x40030020u)*CORE)/(CORE>>10);
  value=(ratio*counts)/40000u;
 }
 *out=value;FLAG(0x20000f1cu)=0;return TOUCH_ILO_SUCCESS;
}
uint32_t touch_ilo_compensate(uint8_t *c){
 if(!c)return 1;uint32_t dummy=500;touch_ilo_start();while(touch_ilo_measure(dummy,&dummy)!=0){}
 uint32_t count=REG(0x40030020u);touch_ilo_stop();uint8_t *i=*(uint8_t **)(c+8);
 *(uint32_t *)(i+44)=(count<<24)/1000000u;
 *(uint32_t *)(i+32)=touch_timer_cycles(*(uint32_t *)(i+28),c);
 *(uint32_t *)(i+40)=touch_timer_cycles(*(uint32_t *)(i+36),c);
 uint32_t cycles=*(uint32_t *)(i+32);if(*(uint32_t *)(*(uint8_t **)(c+4)+8)&0x20u)cycles=*(uint32_t *)(i+40);
 const uint8_t *ch=*(const uint8_t **)(*(const uint8_t **)c+8);volatile uint32_t *hw=*(volatile uint32_t **)ch;hw[0x70/4]&=0xffff0000u;
 ch=*(const uint8_t **)(*(const uint8_t **)c+8);hw=*(volatile uint32_t **)ch;hw[0x70/4]|=cycles;return 0;
}

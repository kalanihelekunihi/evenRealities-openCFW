/* Independent6608/685c/6a80. Delay instruction timing is not physical proof. */
#include "mode.h"
extern void touch_bootstrap_cycles(uint32_t);
static volatile uint32_t *hardware(const uint8_t *c){const uint8_t *common=*(const uint8_t **)c;return **(volatile uint32_t *const *const *)(common+8);}
uint32_t touch_wait_mrss(uint32_t timeout,uint32_t target,uint8_t *c){
 uint32_t mask=1,desired=target;if(target==2 || target==3){mask=0x1000000u;desired=(target<<24)&mask;}
 while((hardware(c)[0x180/4]&mask)==desired){if(!timeout)return 4;touch_bootstrap_cycles(*(volatile uint8_t *)0x20000870u);timeout--;}
 return 0;
}
void touch_cpu_operating(uint8_t *c){
 volatile uint32_t *hw=hardware(c);hw[0]&=0x7fffffffu;hw[0x80/4]=0;
 if(!(hardware(c)[0x180/4]&1)){hw[0x144/4]=1;(void)touch_wait_mrss(315,0,c);}
 hw[0]|=0x80000000u;hw[0x74/4]=0;hw[0x128/4]=0;(void)hw[0x128/4];hw[0x120/4]=0x01110011u;(void)hw[0x120/4];hw[0x100/4]=0xc1011111u;(void)hw[0x100/4];(*(uint8_t **)(c+8))[113]=0;hw[0]&=0xfffcffffu;hw[2]|=0x10000000u;
}
void touch_saturation_mode(uint8_t *c){
 volatile uint32_t *hw=hardware(c);touch_cpu_operating(c);hw[0x400/4]=0;
 for(uint32_t i=0;i<3;i++){hw[(0x608+i*64)/4]=0x03000000u;hw[(0x60c+i*64)/4]=0x00101000u;}
}

/* Independent5d90; public SDK identifies caller interval units as microseconds.
 * Multiply/wrap/clamp behavior is delegated to tested stock5d70 reconstruction. */
#include "timer.h"
#include "../clock_selection_offline/clock.h"
uint32_t touch_set_active_interval(uint32_t us,uint8_t *c){
 if(!c)return 1;uint8_t *i=*(uint8_t **)(c+8);*(uint32_t *)(i+28)=us;
 *(uint32_t *)(i+32)=touch_timer_cycles(us,c);
 if(*(uint32_t *)(*(uint8_t **)(c+4)+8)&0x10u){
  const uint8_t *ch=*(const uint8_t **)(*(const uint8_t **)c+8);volatile uint32_t *hw=*(volatile uint32_t **)ch;
  hw[0x70/4]&=0xffff0000u;
  ch=*(const uint8_t **)(*(const uint8_t **)c+8);hw=*(volatile uint32_t **)ch;
  hw[0x70/4]|=*(uint32_t *)(*(uint8_t **)(c+8)+32);
 }
 return 0;
}

void touch_active_budget_step(uint8_t *state,uint32_t *budget,uint8_t *c){
 *budget-=1u;if(!*budget){*state=2;*budget=160;(void)touch_set_active_interval(31211,c);}
}

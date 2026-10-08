/* Independent all-LP wrapper7050 and application3e28..3e6e/3e8c.
 * PM dependency remains explicit; stock launch return is deliberately ignored. */
#include "application.h"
#include "../lp_scan_offline/scan.h"
uint32_t touch_start_all_lp(uint8_t *c){return c?touch_start_lp_slots(0,4,c):1;}
void touch_app_lp_phase(uint8_t *c,uint8_t *state,uint32_t *budget,const touch_lp_pm_dependencies *pm){
 (void)touch_start_all_lp(c);uint32_t token=pm->enter();
 while(*(volatile uint32_t *)(*(uint8_t **)(c+4)+8)&0x80u){
  (void)pm->sleep();pm->restore(token);token=pm->enter();
 }
 pm->restore(token);
 if(*(uint32_t *)(*(uint8_t **)(c+4)+8)&0x400u){*state=1;*budget=640;}
 else{*state=2;*budget=160;}
}

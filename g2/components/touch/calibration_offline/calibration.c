/* Independent calibration/report source; original gesture4070 is an explicit
 * borrowed-code dependency pending its own reconstruction, not an entry stub. */
#include "calibration.h"
#include "bootstrap.h"
#include "cy_scb_i2c.h"
#define CFG ((uint8_t *)0x200004ecu)
#define RECORD ((touch_saved_record *)0x200009d0u)
extern uint32_t touch_bootstrap_log(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t touch_saved_baseline(void){return RECORD->magic==0x45564e55u?RECORD->baseline:0;}
uint32_t touch_sensor_active(uint32_t w,uint32_t sensor,const uint8_t *c){
 if(w>2)return 0;
 uint8_t *widget=(uint8_t *)(*(const uint32_t *)(c+12)+w*144u);
 if(widget[123]!=6 || *(uint16_t *)(widget+56)<=sensor)return 0;
 return ((uint8_t *)(*(uint32_t *)(widget+4)+sensor*10u))[6];
}
uint32_t touch_widget_active(uint32_t w,const uint8_t *c){
 if(w>2)return 0;
 uint8_t *widget=(uint8_t *)(*(const uint32_t *)(c+12)+w*144u);
 if(widget[123]==7)return 0;
 return ((uint8_t *)(*(const uint32_t *)(c+16)+w*60u))[35]&1u;
}
uint32_t touch_proximity_change(void){
 uint8_t *sensor=(uint8_t *)(*(uint32_t *)(*(uint32_t *)(CFG+12)+2*144u+4));
 uint32_t desired=touch_sensor_active(2,0,CFG)?2:1,b=touch_saved_baseline();
 uint32_t measured=*(uint16_t *)(sensor+2),raw=*(uint16_t *)sensor;
 if(b){if(measured>b+500u)desired=2;else if(measured<b && raw<=b+49u)desired=1;}
 uint8_t *prior=(uint8_t *)0x200009d8u;
 if(*prior==desired)return 0;*prior=(uint8_t)desired;return desired;
}
uint32_t touch_config_save(void){
 RECORD->magic=0x45564e55u;
 uint32_t s=touch_application_write(0,(const uint8_t *)RECORD,8);
 if(s)touch_bootstrap_log(0xabe4,s,0xaa5c,0);else touch_bootstrap_log(0xac0c,RECORD->baseline,RECORD->parameter,0xaa5c);
 return s;
}
void touch_gesture_initialize(uint8_t *state,const uint16_t *parameter){
 if(!state || !parameter)return;
 for(unsigned i=0;i<80;i++)state[i]=0;
 *(uint16_t *)state=*parameter;if(!*(uint16_t *)state)*(uint16_t *)state=1000;
}
void touch_calibration_report(void){
 uint32_t active=touch_widget_active(1,CFG);
 uint8_t *widget=(uint8_t *)(*(uint32_t *)(CFG+12)+144u);
 /* Stock7d6c permits only widget types2..5; valid centroid pointer is precondition. */
 uint16_t position=**(uint16_t **)(*(uint32_t *)widget+36u);
 uint32_t stamp=*(uint32_t *)0x200008e8u,change=touch_proximity_change();
 uint8_t *gesture=((uint8_t *(*)(uint8_t *,uint32_t,uint32_t,uint32_t))0x4071u)((uint8_t *)0x20000940u,active,(uint8_t)position,stamp);
 if(!change && (!gesture || !gesture[0]))return;
 uint8_t *report=(uint8_t *)0x20000990u;report[0]=(uint8_t)change;
 report[1]=gesture?gesture[0]:0;report[2]=gesture?gesture[1]:0;report[3]=gesture?gesture[2]:0;
 uint8_t *sensor=(uint8_t *)(*(uint32_t *)(*(uint32_t *)(CFG+12)+288u+4));
 uint16_t baseline=*(uint16_t *)(sensor+2),raw=*(uint16_t *)sensor,diff=*(uint16_t *)(sensor+4),saved=(uint16_t)touch_saved_baseline();
 if(*(uint8_t *)0x200009cfu){
  uint16_t old=RECORD->baseline,delta=baseline>old?baseline-old:old-baseline;
  if(delta>49){RECORD->baseline=baseline;(void)touch_config_save();}
  *(uint8_t *)0x200009cfu=0;
 }
 *(uint16_t *)(report+4)=baseline;*(uint16_t *)(report+6)=raw;*(uint16_t *)(report+8)=diff;*(uint16_t *)(report+10)=saved;
 for(unsigned i=0;i<16;i++)((uint8_t *)0x200009b0u)[i]=report[i];
 Cy_SCB_I2C_SlaveConfigReadBuf(SCB1,(uint8_t *)0x200009b0u,16,(void *)0x200008ecu);
 *(volatile uint32_t *)0x40040444u=1;*(uint8_t *)0x200009ccu=1;*(uint32_t *)0x200009c8u=640;
}

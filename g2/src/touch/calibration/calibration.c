/* Calibration/report source composed with the source-owned gesture machine. */
#include "calibration.h"
#include "bootstrap.h"
#include "cy_scb_i2c.h"
#include "../gesture-machine/gesture.h"
#include "../application/ram_state.h"
#include "../reset-layout/reset_capsense_context.h"
#define CFG ((uint8_t *)&touch_reset_capsense_context)
#define RECORD (&touch_saved_record_ram)
extern uint32_t touch_bootstrap_log(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t Cy_CapSense_IsWidgetActive(uint32_t,const uint8_t *);
/* Stock 0x00003A1C (saved_proximity_baseline_read) */
uint32_t touch_saved_baseline(void){return RECORD->magic==0x45564e55u?RECORD->baseline:0;}
/* Stock 0x00007D36 (capsense_sensor_raw_count_read) */
uint32_t touch_sensor_active(uint32_t w,uint32_t sensor,const uint8_t *c){
 if(w>2)return 0;
 uint8_t *widget=(uint8_t *)(*(const uint32_t *)(c+12)+w*144u);
 if(widget[123]!=6 || *(uint16_t *)(widget+56)<=sensor)return 0;
 return ((uint8_t *)(*(uint32_t *)(widget+4)+sensor*10u))[6];
}
/* Stock 0x0000441C (proximity_baseline_update_adapter) */
uint32_t touch_proximity_change(void){
 uint8_t *sensor=(uint8_t *)(*(uint32_t *)(*(uint32_t *)(CFG+12)+2*144u+4));
 uint32_t desired=touch_sensor_active(2,0,CFG)?2:1,b=touch_saved_baseline();
 uint32_t measured=*(uint16_t *)(sensor+2),raw=*(uint16_t *)sensor;
 if(b){if(measured>b+500u)desired=2;else if(measured<b && raw<=b+49u)desired=1;}
 uint8_t *prior=touch_proximity_prior_ram;
 if(*prior==desired)return 0;*prior=(uint8_t)desired;return desired;
}
/* Stock 0x00003A38 (touch_config_load_from_eeprom) */
uint32_t touch_config_save(void){
 RECORD->magic=0x45564e55u;
 uint32_t s=touch_application_write(0,(const uint8_t *)RECORD,8);
 if(s)touch_bootstrap_log(TOUCH_LOG_ADDR(touch_log_save_failed),s,TOUCH_LOG_ADDR(touch_log_color_reset),0);
 else touch_bootstrap_log(TOUCH_LOG_ADDR(touch_log_saved),RECORD->baseline,RECORD->parameter,TOUCH_LOG_ADDR(touch_log_color_reset));
 return s;
}
/* Stock 0x0000404C (touch_startup_0d4c_initialize) */
void touch_gesture_initialize(uint8_t *state,const uint16_t *parameter){
 if(!state || !parameter)return;
 for(unsigned i=0;i<80;i++)state[i]=0;
 *(uint16_t *)state=*parameter;if(!*(uint16_t *)state)*(uint16_t *)state=1000;
}
/* Stock 0x00003B24 (report_builder) */
void touch_calibration_report(void){
 uint32_t active=Cy_CapSense_IsWidgetActive(1,CFG);
 uint8_t *widget=(uint8_t *)(*(uint32_t *)(CFG+12)+144u);
 /* Stock7d6c permits only widget types2..5; valid centroid pointer is precondition. */
 uint16_t position=**(uint16_t **)(*(uint32_t *)widget+36u);
 uint32_t stamp=touch_gesture_ticks_ram,change=touch_proximity_change();
 uint8_t *gesture=touch_gesture_step(touch_gesture_state_ram,active,(uint8_t)position,stamp);
 if(!change && (!gesture || !gesture[0]))return;
 uint8_t *report=touch_report_ram;report[0]=(uint8_t)change;
 report[1]=gesture?gesture[0]:0;report[2]=gesture?gesture[1]:0;report[3]=gesture?gesture[2]:0;
 uint8_t *sensor=(uint8_t *)(*(uint32_t *)(*(uint32_t *)(CFG+12)+288u+4));
 uint16_t baseline=*(uint16_t *)(sensor+2),raw=*(uint16_t *)sensor,diff=*(uint16_t *)(sensor+4),saved=(uint16_t)touch_saved_baseline();
 if(touch_save_pending_ram){
  uint16_t old=RECORD->baseline,delta=baseline>old?baseline-old:old-baseline;
  if(delta>49){RECORD->baseline=baseline;(void)touch_config_save();}
  touch_save_pending_ram=0;
 }
 *(uint16_t *)(report+4)=baseline;*(uint16_t *)(report+6)=raw;*(uint16_t *)(report+8)=diff;*(uint16_t *)(report+10)=saved;
 for(unsigned i=0;i<16;i++)touch_i2c_tx_ram[i]=report[i];
 Cy_SCB_I2C_SlaveConfigReadBuf(SCB1,touch_i2c_tx_ram,16,touch_i2c_context_ram);
 *(volatile uint32_t *)0x40040444u=1;touch_app_state_ram=1;touch_active_budget_ram=640;
}

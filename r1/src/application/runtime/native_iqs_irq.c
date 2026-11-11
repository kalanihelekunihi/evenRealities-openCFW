/* Stock IQS IRQ worker 0x30e6c, channel/event helpers and register adapters. */
#include <stdint.h>
#include <stddef.h>
extern void *memset(void *,int,size_t);
#include "cmsis_os2.h"
#include "../board/native_iqs_state.h"
#include "../board/native_touch_transport.h"
#include "../board/native_battery_memory.h"
extern uint32_t r1_advertising_configuration_byte_get(void),r1_hardware_variant_bsn_detect(void);
extern void r1_iqs7211e_reset_reconfigure(void),r1_iqs7211e_ati_recovery_policy(void);
extern uint32_t r1_glasses_connection_handle_get(void);
extern int32_t r1_ble_tx_queue_dispatch_type2(uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
#define FIELD(type,name,section_name,value) volatile type name __attribute__((section(section_name)))=value
FIELD(uint8_t,r1_iqs_control0,".r1.iqs.control0",0);
FIELD(uint8_t,r1_iqs_control1,".r1.iqs.control1",0);
FIELD(uint8_t,r1_iqs_recovery_consecutive,".r1.iqs.recovery_consecutive",0);
FIELD(uint8_t,r1_iqs_recovery_used,".r1.iqs.recovery_used",0);
FIELD(int8_t,r1_iqs_raw_report_selection,".r1.iqs.raw_selection",-1);
FIELD(uint16_t,r1_iqs_last_position,".r1.iqs.last_position",0);
volatile uint16_t r1_iqs_status_live[3] __attribute__((section(".r1.iqs.status_live"),aligned(2)))={0};
volatile uint16_t r1_iqs_status_snapshot[3] __attribute__((section(".r1.iqs.status_snapshot"),aligned(2)))={0};
#define TEXT(name,value) const char r1_iqs_irq_##name[]=value
TEXT(suspend_ring,"[RING]IQS7211E: Entering Suspend Mode.");TEXT(suspend_sdk,"IQS7211E: Entering Suspend Mode.");
TEXT(reati_ring,"[RING]!!!!!!!!!!!!!!!IS_RE_ATI_OCCURRED!!!!!!!!!!!!!!!");TEXT(reati_sdk,"!!!!!!!!!!!!!!!IS_RE_ATI_OCCURRED!!!!!!!!!!!!!!!");
TEXT(clear_ring,"[RING]ATI_ERR_RECOVERY|cleared (consec=%u, used=%u)");TEXT(clear_sdk,"ATI_ERR_RECOVERY|cleared (consec=%u, used=%u)");
TEXT(fingers_ring,"[RING]IS_TOO_MANY_FINGERS: %04X");TEXT(fingers_sdk,"IS_TOO_MANY_FINGERS: %04X");
static int ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void log_plain(const char *ring,const char *sdk)
{
 if(ring_enabled())(void)r1_structured_log_format(0x0c000000,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,sdk);
}
uint32_t r1_iqs7211e_irq_config_refresh(void)
{
 uint8_t byte=0x6c;return r1_iqs7211e_register_write_port(0x56,0x34,&byte,1,1);
}
uint32_t r1_iqs7211e_communication_end(void)
{
 uint8_t unused=0;return r1_iqs7211e_register_write_port(0x56,255,&unused,0,1);
}
uint32_t r1_iqs7211e_read_word_adapter(uint32_t reg)
{
 uint8_t word[2]={0};(void)r1_iqs7211e_register_read_port(0x56,reg,word,2,1);
 return read16(word);
}
uint32_t r1_iqs7211e_reg56_write(uint32_t reg,uint32_t value)
{
 uint8_t word[2]={(uint8_t)value,(uint8_t)(value>>8)};
 return r1_iqs7211e_register_write_port(0x56,reg,word,2,1);
}
void r1_iqs7211e_suspend(void)
{
 uint32_t word=r1_iqs7211e_read_word_adapter(0x33);
 (void)r1_iqs7211e_reg56_write(0x33,word|0x800u);
 log_plain(r1_iqs_irq_suspend_ring,r1_iqs_irq_suspend_sdk);
}
uint32_t r1_model_b210a_check(void) { return r1_hardware_variant_bsn_detect()==1; }
uint32_t r1_model_dependent_limit_get(void) { return r1_model_b210a_check()?24:21; }
float r1_touch_channel_average(const void *data)
{
 const uint8_t *bytes=data;uint16_t samples[24];
 uint32_t count=r1_model_dependent_limit_get();
 for(uint32_t i=0;i<count;i++)samples[i]=(uint16_t)read16(bytes+2*i);
 float sum=0.0f;
 for(uint32_t i=0;i<count;i++)sum+=(float)samples[i];
 return sum/(float)count;
}
void r1_touch_irq_event_dispatch(float average)
{
 if(!r1_touch_slider_callback_word)return;
 uint32_t flags=((volatile uint8_t *)r1_iqs_status_snapshot)[0]&7u;
 uint32_t position=r1_iqs_status_snapshot[2];
 _Static_assert(sizeof(float)==sizeof(uint32_t),"native binary32 bit view");
 union { float value;uint32_t bits; } representation={.value=average};
 uint32_t valid,ticks;
 if(position==UINT16_MAX && (int32_t)representation.bits<(int32_t)UINT32_C(0x43af0000)) {
  ticks=osKernelGetTickCount();position=r1_iqs_last_position;valid=0;
 }else{
  r1_iqs_last_position=(uint16_t)position;
  ticks=osKernelGetTickCount();position=r1_iqs_status_snapshot[2];valid=1;
 }
 r1_iqs_slider_callback callback=(r1_iqs_slider_callback)(uintptr_t)r1_touch_slider_callback_word;
 callback(valid,position,ticks,flags,average);
}
void r1_iqs7211e_irq_worker(void)
{
 if(r1_iqs_control0) {
  (void)r1_iqs7211e_irq_config_refresh();r1_iqs7211e_suspend();r1_iqs_control0=0;
  (void)r1_iqs7211e_communication_end();return;
 }
 (void)r1_iqs7211e_irq_config_refresh();
 (void)r1_iqs7211e_register_read_port(0x56,0x0f,(void *)r1_iqs_status_live,6,1);
 uint32_t status=r1_iqs_status_live[0];r1_iqs_status_snapshot[0]=(uint16_t)status;
 r1_iqs_status_snapshot[1]=r1_iqs_status_live[1];r1_iqs_status_snapshot[2]=r1_iqs_status_live[2];
 if(status&0x80u){r1_iqs7211e_reset_reconfigure();(void)r1_iqs7211e_communication_end();return;}
 if(status&0x10u)log_plain(r1_iqs_irq_reati_ring,r1_iqs_irq_reati_sdk);
 if(r1_advertising_configuration_byte_get()!=0x55) {
  status=r1_iqs_status_snapshot[0];
  if(status&8u) {
   if(!r1_iqs_control1){r1_iqs7211e_ati_recovery_policy();(void)r1_iqs7211e_communication_end();return;}
  }else if(!r1_iqs_control1) {
   if((uint32_t)r1_iqs_recovery_consecutive|r1_iqs_recovery_used) {
    if(ring_enabled()) {
     uint32_t used=r1_iqs_recovery_used,consecutive=r1_iqs_recovery_consecutive;
     (void)r1_structured_log_format(0x0c800000,r1_iqs_irq_clear_ring,r1_iqs_irq_clear_ring,consecutive,used);
    }
    if(r1_structured_log_mode_get()&2u) {
     uint32_t used=r1_iqs_recovery_used,consecutive=r1_iqs_recovery_consecutive;
     nrf_log_frontend_std_2(0x001c0003,r1_iqs_irq_clear_sdk,consecutive,used);
    }
    r1_iqs_recovery_consecutive=0;r1_iqs_recovery_used=0;
   }
  }
 }
 if(r1_iqs_status_snapshot[0]&0x1000u) {
  uint8_t byte=8;(void)r1_iqs7211e_register_write_port(0x56,0x33,&byte,1,1);
  if(ring_enabled())(void)r1_structured_log_format(0x0c400000,r1_iqs_irq_fingers_ring,r1_iqs_irq_fingers_ring,(uint32_t)r1_iqs_status_snapshot[0]);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,r1_iqs_irq_fingers_sdk,r1_iqs_status_snapshot[0]);
  return;
 }
 uint32_t length=r1_model_b210a_check()?48:42;
 uint8_t buffer[48]={0};
 (void)r1_iqs7211e_register_read_port(0x56,0xe0,buffer,length,1);
 float average=r1_touch_channel_average(buffer);r1_touch_irq_event_dispatch(average);
 int32_t selected=r1_iqs_raw_report_selection;
 if((uint32_t)(selected-1)<=2u) {
  memset(buffer,0,length);
  (void)r1_iqs7211e_register_read_port(0x56,0xe0u+(uint32_t)selected,buffer,length,1);
 }
 (void)r1_iqs7211e_communication_end();
 selected=r1_iqs_raw_report_selection;
 if((uint32_t)selected<=3u) {
  r1_iqs_raw_report_selection=-1;
  uint32_t handle=r1_glasses_connection_handle_get();
  (void)r1_ble_tx_queue_dispatch_type2(handle,buffer,length);
 }
}

/* Stock dock policy 0x77430, field-seen adapters 0x96a48/54 and
 * recurring field-control callback 0x32174. */
#include <stdint.h>
#include <string.h>
#include "st25dvxxkc.h"
extern ST25DVxxKC_Object_t r1_st25_device;
extern uint32_t r1_battery_task_flags_set(uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern void r1_battery_periodic_callback(uint32_t);
extern int32_t r1_native_snprintf(char *,uint32_t,const char *,...);
extern void r1_st25dvxxkc_dock_advertisement_send(volatile uint8_t *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
volatile uint8_t r1_dock_temperature_limit __attribute__((section(".r1.dock.limit")))=40;
volatile uint8_t r1_dock_phase __attribute__((section(".r1.dock.phase")))=0xaa;
volatile uint8_t r1_dock_type __attribute__((section(".r1.dock.type")))=0;
volatile uint8_t r1_dock_heartbeat_count __attribute__((section(".r1.dock.heartbeat")))=0;
volatile uint8_t r1_dock_last_voltage __attribute__((section(".r1.dock.voltage")))=0;
char r1_dock_version[11] __attribute__((section(".r1.dock.version")))="NULL";

/* Stock 0x77250/0x77268: dock hardware code accessors. */
void r1_st25dvxxkc_dock_hardware_clear(void)
{r1_dock_type=0u;}
uint32_t r1_st25dvxxkc_dock_hardware_get(void)
{return r1_dock_type;}
/* Stock 0x77290/0x7729c: low-byte dock controls. */
void r1_st25dvxxkc_dock_temperature_limit_set(uint32_t value)
{r1_dock_temperature_limit=(uint8_t)value;}
void r1_st25dvxxkc_dock_advertisement_set(uint32_t value)
{r1_dock_phase=(uint8_t)value;}

/* Stock 0x7725c/0x77274: eleven-byte dock version accessors. */
void r1_st25dvxxkc_dock_version_clear(void)
{(void)memset(r1_dock_version,0,sizeof r1_dock_version);}
const char *r1_st25dvxxkc_dock_version_get(uint8_t *length)
{
 if(length==0)return 0;
 *length=(uint8_t)strlen(r1_dock_version);
 return r1_dock_version;
}

volatile uint8_t r1_st25_field_seen __attribute__((section(".r1.st25.field_seen")))=0;
const char r1_dock_heartbeat_ring[]="[RING]heatbeat_cnt > 60, stop nfc field get right adc";
const char r1_dock_heartbeat_sdk[]="heatbeat_cnt > 60, stop nfc field get right adc";
const char r1_dock_empty_ring[]="[RING]mailbox free or empty, stop nfc field  %d s";
const char r1_dock_empty_sdk[]="mailbox free or empty, stop nfc field  %d s";
const char r1_dock_adv_ring[]="[RING]RING_CTRL_ADV_SUBCMD";
const char r1_dock_adv_sdk[]="RING_CTRL_ADV_SUBCMD";
const char r1_dock_charge_ring[]="[RING]RING_CTRL_CHAREG_FIELD_SUBCMD";
const char r1_dock_charge_sdk[]="RING_CTRL_CHAREG_FIELD_SUBCMD";
static void log0(const char *ring,const char *sdk)
{
 if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x0c000000,ring,ring);
 if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0003,sdk);
}
uint32_t r1_st25dvxxkc_field_seen_get(void) {return r1_st25_field_seen;}
void r1_st25dvxxkc_field_seen_set(uint32_t value) {r1_st25_field_seen=(uint8_t)value;}
void r1_dock_field_control_callback(uint32_t argument)
{
 (void)argument;
 (void)r1_battery_task_flags_set(0x40);
 (void)r1_native_delayed_cancel(r1_battery_periodic_callback,0);
 r1_native_delayed_schedule(r1_battery_periodic_callback,0,0x2800);
}
void r1_st25dvxxkc_dock_frame_policy(uint8_t *data,uint32_t length,
                                    volatile uint8_t *output)
{
 (void)length;
 const volatile uint8_t *frame=data;
 if (frame[0]==0x55) {
  if (frame[1]==3) log0(r1_dock_adv_ring,r1_dock_adv_sdk);
  else if (frame[1]==4) {
   log0(r1_dock_charge_ring,r1_dock_charge_sdk);
   r1_native_delayed_schedule(r1_dock_field_control_callback,0,0x800);
  }
  return;
 }
 if (frame[0]!=1||frame[1]!=2||frame[2]!=3||frame[3]!=4) return;
 r1_dock_heartbeat_count=(uint8_t)(r1_dock_heartbeat_count+1u);
 uint32_t version=((uint32_t)frame[4]<<8)|frame[5];
 uint32_t build=((uint32_t)frame[6]<<8)|frame[7];
 (void)r1_native_snprintf(r1_dock_version,11,"%d.%d.%d.%04d",
                         (version/100u)%10u,(version/10u)%10u,version%10u,build);
 r1_dock_type=frame[8];
 r1_st25dvxxkc_field_seen_set(1);
 uint8_t control=0;
 if (ST25DVxxKC_GetMB_CTRL_DYN_ALL(&r1_st25_device.Ctx,&control)!=0) return;
 if (control!=0x81) return;
 uint32_t phase=r1_dock_phase;
 if (phase!=0xaa) {
  r1_st25dvxxkc_dock_advertisement_send(output,phase);
  r1_dock_phase=0xaa;
  return;
 }
 if (r1_dock_heartbeat_count>60) {
  r1_dock_heartbeat_count=0;
  log0(r1_dock_heartbeat_ring,r1_dock_heartbeat_sdk);
  uint32_t temperature=output[4]>>2;
  output[1]=0x55;output[2]=4;output[3]=0;
  output[4]=temperature>r1_dock_temperature_limit ? 60 : 4;
  if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   r1_structured_log_format(0x0c400000,r1_dock_empty_ring,r1_dock_empty_ring,(uint32_t)output[4]);
  if (r1_structured_log_mode_get()&2u)
   nrf_log_frontend_std_1(0x001c0003,r1_dock_empty_sdk,output[4]);
 } else {
  uint8_t voltage=output[6];
  if (voltage<44) r1_dock_last_voltage=voltage;
  else output[6]=r1_dock_last_voltage;
 }
 (void)ST25DVxxKC_WriteMailboxData(&r1_st25_device,(const uint8_t *)(uintptr_t)output,23);
}

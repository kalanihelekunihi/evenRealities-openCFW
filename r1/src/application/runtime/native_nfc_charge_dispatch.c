/* Stock NFC/charging dispatcher 0x461cc and native status/event adapters. */
#include <stdint.h>
#include "cmsis_os2.h"
#include "../board/native_battery_context.h"
extern osMessageQueueId_t volatile r1_nfc_charge_task_queue;
extern uint32_t volatile r1_nfc_charge_task_watchdog;
extern void r1_pmic_charged_notification_plan(uint32_t),r1_pmic_charge_event_plan(uint32_t);
extern uint32_t r1_service_touch_open(uint32_t),r1_service_touch_close(uint32_t);
extern void r1_i2c5_nfc_resource_acquire(void),r1_pmic_retry_callback_plan(uint32_t);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_protocol_service_thread_flags_set(uint32_t);
extern uint32_t r1_charge_state_byte_get(void),r1_proto_report_battery_status(uint32_t,uint32_t);
extern uint32_t r1_glasses_tag_frame_send(uint32_t,uint32_t);
extern uint32_t r1_native_charger_tracking_clear(void),r1_native_charger_state_get(void);
extern uint32_t r1_battery_runtime_service(void);
extern void r1_gxt310_id_pair_read(volatile uint8_t *);
extern uint32_t r1_yhm_register_read_native(uint32_t,uint32_t,uint8_t *);
extern uint32_t r1_yhm_register_write_native(uint32_t,uint32_t,const uint8_t *);
extern _Noreturn void r1_native_worker_park(uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
const char r1_nfc_irq_ring[]="[RING]NFC_CHARGE_EVENT_STDCMD_IRQ_HANDLER";
const char r1_nfc_irq_sdk[]="NFC_CHARGE_EVENT_STDCMD_IRQ_HANDLER";
const char r1_nfc_not_charging_ring[]="[RING]NFC_CHARGE_EVENT_NOT_CHARGING";
const char r1_nfc_not_charging_sdk[]="NFC_CHARGE_EVENT_NOT_CHARGING";
const char r1_nfc_id_success_ring[]="[RING]retry %d success";
const char r1_nfc_id_success_sdk[]="retry %d success";
const char r1_nfc_id_failed_ring[]="[RING]charge end: temp id invalid (retry=%d, T1=0x%02x T2=0x%02x)";
const char r1_nfc_id_failed_sdk[]="charge end: temp id invalid (retry=%d, T1=0x%02x T2=0x%02x)";
const char r1_nfc_id_reset_ring[]="[RING]charge end: temp id invalid 3 times, enable wdg and reset";
const char r1_nfc_id_reset_sdk[]="charge end: temp id invalid 3 times, enable wdg and reset";
const char r1_nfc_update_ring[]="[RING]NFC_CHARGE_EVENT_CHARGING_BATTERY_UPDATA = %d";
const char r1_nfc_update_sdk[]="NFC_CHARGE_EVENT_CHARGING_BATTERY_UPDATA = %d";
static int ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void log0(const char *ring,const char *sdk)
{
 if (ring_enabled()) r1_structured_log_format(0x0c000000,ring,ring);
 if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0003,sdk);
}
/* Stock 0x31fac clears these two accessed bytes in this order. */
void r1_battery_charge_status_reset(void)
{r1_battery_device_context[46]=0;r1_battery_device_context[45]=0;}
/* Stock 0x350e0 and veneer 0x50614; keep initialized fallback and ignored read status. */
uint32_t r1_yhm_charging_event_set_native(void)
{
 uint8_t value=0;
 (void)r1_yhm_register_read_native(3,1,&value);
 value|=8u;
 return r1_yhm_register_write_native(3,1,&value);
}
void r1_nfc_charge_task_plan_build(uint32_t flags)
{
 volatile uint8_t ids[3]={0,0,0};
 if (flags&0x400000u) {
  uint32_t message[11]={0};
  while (osMessageQueueGet(r1_nfc_charge_task_queue,message,NULL,0)==osOK) {}
 }
 if (flags&1u) {
  r1_pmic_charged_notification_plan(1);
  (void)r1_service_touch_open(1);
 }
 if (flags&2u) {
  r1_i2c5_nfc_resource_acquire();
  uint8_t active=1;
  (void)r1_event_publish(0x100b,&active,1);
  log0(r1_nfc_irq_ring,r1_nfc_irq_sdk);
  r1_pmic_retry_callback_plan(0);
  (void)r1_protocol_service_thread_flags_set(0x800);
  (void)r1_proto_report_battery_status(r1_charge_state_byte_get(),1);
  (void)r1_glasses_tag_frame_send(r1_charge_state_byte_get(),1);
  (void)r1_service_touch_open(1);
 }
 if (flags&0x10u) {
  (void)r1_native_charger_tracking_clear();
  r1_battery_charge_status_reset();
  uint8_t active=0;
  (void)r1_event_publish(0x100b,&active,1);
  log0(r1_nfc_not_charging_ring,r1_nfc_not_charging_sdk);
  (void)r1_protocol_service_thread_flags_set(0x1000);
  (void)r1_proto_report_battery_status(r1_charge_state_byte_get(),0);
  (void)r1_glasses_tag_frame_send(r1_charge_state_byte_get(),0);
  (void)r1_service_touch_close(1);
  uint32_t retry;
  for (retry=0;retry<3;++retry) {
   r1_gxt310_id_pair_read(ids);
   if (ids[1]==0x50 && ids[2]==0x50) {
    if (ring_enabled()) r1_structured_log_format(0x0c400000,r1_nfc_id_success_ring,r1_nfc_id_success_ring,retry);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_1(0x001c0003,r1_nfc_id_success_sdk,retry);
    break;
   }
   if (ring_enabled()) r1_structured_log_format(0x0cc00000,r1_nfc_id_failed_ring,r1_nfc_id_failed_ring,retry,(uint32_t)ids[1],(uint32_t)ids[2]);
   if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_3(0x001c0003,r1_nfc_id_failed_sdk,retry,ids[1],ids[2]);
   (void)osDelay(100);
  }
  if (retry==3) {
   log0(r1_nfc_id_reset_ring,r1_nfc_id_reset_sdk);
   (void)r1_yhm_charging_event_set_native();
  }
 }
 if (flags&4u) r1_pmic_charged_notification_plan(0);
 if (flags&8u) r1_pmic_charge_event_plan(0x5a);
 if (flags&0x40u) {
  if (ring_enabled()) r1_structured_log_format(0x0c400000,r1_nfc_update_ring,r1_nfc_update_ring,r1_native_charger_state_get());
  if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_1(0x001c0003,r1_nfc_update_sdk,r1_native_charger_state_get());
  if (!r1_native_charger_state_get())
   for (unsigned i=0;i<8;++i) {(void)r1_battery_runtime_service();(void)osDelay(10);}
 }
 if (flags&0x20u) (void)r1_battery_runtime_service();
 if (flags&0x800000u) r1_native_worker_park(1,r1_nfc_charge_task_watchdog);
}

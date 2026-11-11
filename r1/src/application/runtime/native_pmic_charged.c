/* Stock charged notification 0x96cc8 and NFC continuation 0x47f10. */
#include <stdint.h>
#include "st25dvxxkc.h"
extern ST25DVxxKC_Object_t r1_st25_device;
extern volatile uint8_t r1_nfc_charge_late_flag;
extern uint32_t r1_native_charger_state_get(void),r1_battery_voltage_read(void);
extern uint32_t r1_battery_voltage_get(void),r1_ship_mode_pin_pulse(void);
extern uint32_t r1_battery_task_flags_set(uint32_t);
extern void r1_pmic_retry_callback_plan(uint32_t),r1_pmic_charge_event_plan(uint32_t);
extern void r1_pmic_post_timer_callback_plan(uint32_t);
extern uint32_t r1_pmic_post_device_callback_plan(uint32_t);
extern uint32_t r1_pmic_event_op_dispatch(uint32_t),r1_service_touch_close(uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
const char r1_pmic_process_not_ring[]="[RING]process PMIC_CHARGED_NOT";
const char r1_pmic_process_not_sdk[]="process PMIC_CHARGED_NOT";
const char r1_pmic_low_isns_ring[]="[RING]!!!!!!!!!!!!!!!!isns_voltage:%d mv < 50 mv (cnt:%d), !!!!!!!!!!!!!!";
const char r1_pmic_low_isns_sdk[]="!!!!!!!!!!!!!!!!isns_voltage:%d mv < 50 mv (cnt:%d), !!!!!!!!!!!!!!";
static void mailbox_enable_read(uint8_t *enabled)
{
 uint8_t raw=0;
 if (ST25DVxxKC_GetMB_CTRL_DYN_ALL(&r1_st25_device.Ctx,&raw)==0)
  *enabled=raw&1u;
}
void r1_pmic_nfc_charge_continue(uint32_t argument)
{
 (void)argument;
 uint8_t interrupt=0,enabled=0;
 uint32_t status=(uint32_t)ST25DVxxKC_ReadITSTStatus_Dyn(&r1_st25_device,&interrupt);
 if (!status) {
  if (!interrupt && !r1_native_charger_state_get()) {
   (void)r1_native_delayed_cancel(r1_pmic_retry_callback_plan,0);
   r1_pmic_charge_event_plan(enabled);
   return;
  }
  if (interrupt&8u) (void)r1_service_touch_close(1);
 }
 (void)r1_native_delayed_cancel(r1_pmic_retry_callback_plan,0);
 mailbox_enable_read(&enabled);
 if (!enabled) {
  (void)ST25DVxxKC_SetMBEN_Dyn(&r1_st25_device);
  mailbox_enable_read(&enabled);
 }
 r1_pmic_charge_event_plan(enabled);
 r1_native_delayed_schedule(r1_pmic_post_timer_callback_plan,0,0x1400);
 (void)r1_pmic_event_op_dispatch((uint32_t)(uintptr_t)r1_pmic_post_device_callback_plan);
}
void r1_pmic_charged_notification_plan(uint32_t argument)
{
 if (r1_nfc_charge_late_flag==0xa5) {
  r1_nfc_charge_late_flag=0;
  if (!r1_native_charger_state_get()) {
   if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
    r1_structured_log_format(0x0c000000,r1_pmic_process_not_ring,r1_pmic_process_not_ring);
   if (r1_structured_log_mode_get()&2u)
    nrf_log_frontend_std_0(0x001c0003,r1_pmic_process_not_sdk);
   (void)r1_native_delayed_cancel(r1_pmic_retry_callback_plan,0);
   (void)r1_battery_task_flags_set(0x10);
   return;
  }
 }
 uint32_t isns=r1_battery_voltage_read();
 uint32_t voltage=r1_battery_voltage_get();
 if (isns<50 && voltage<4200) {
  uint32_t previous=r1_nfc_charge_late_flag;
  r1_nfc_charge_late_flag=(uint8_t)(previous+1u);
  if (previous<=12) {
   uint32_t state=r1_native_charger_state_get();
   if (!state) {r1_pmic_nfc_charge_continue(argument);return;}
   if (state!=2) {
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
     r1_structured_log_format(0x08800000,r1_pmic_low_isns_ring,r1_pmic_low_isns_ring,
                              isns,(uint32_t)r1_nfc_charge_late_flag);
    if (r1_structured_log_mode_get()&2u)
     nrf_log_frontend_std_2(0x001c0002,r1_pmic_low_isns_sdk,isns,r1_nfc_charge_late_flag);
    (void)r1_ship_mode_pin_pulse();
    r1_native_delayed_schedule(r1_pmic_retry_callback_plan,0,0x199);
    return;
   }
  }
 }
 r1_nfc_charge_late_flag=0;
 r1_pmic_nfc_charge_continue(argument);
}

/* Stock 0x91f54 BLE worker and timer callbacks 0x4e008/0x4d2e8. */
#include <stdint.h>
#include "cmsis_os2.h"
extern void *volatile r1_ble_message_queue;
extern volatile uint16_t r1_connection_field8,r1_connection_field10;
extern void r1_native_sync_wait(uint32_t),r1_native_sync_signal(uint32_t);
extern uint32_t r1_native_watchdog_register(const char *,uint32_t);
extern void r1_native_watchdog_arm(uint32_t),r1_native_watchdog_disarm(uint32_t);
extern void r1_native_watchdog_feed(uint32_t);
extern _Noreturn void r1_native_worker_park(uint32_t,uint32_t);
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern uint32_t r1_protocol_service_thread_flags_set(uint32_t);
extern void nrf_sdh_evts_poll(void);
/* These native hardware policies remain real, unresolved dependencies. */
extern void r1_peer_record_commit(void);
extern uint32_t r1_nordic_ble_bootstrap_configuration(void);
extern void r1_ble_connection_control_event_consumer(void),r1_advertising_stop_guard(void);
extern void r1_advertising_restart(uint32_t),r1_peripheral_watchdog_plan_step(uint32_t);
extern void r1_tx_power_plan(uint32_t);
extern uint32_t r1_dfu_bootloader_prepare_boundary(void);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
volatile uint32_t r1_ble_io_watchdog
 __attribute__((section(".r1.ble.io.watchdog"),aligned(4)))=0;
const char r1_ble_dfu_start_ring[]="[RING]THREAD_BLE_EVT_DFU_START";
const char r1_ble_dfu_start_sdk[]="THREAD_BLE_EVT_DFU_START";
const char r1_ble_role_sync_ring[]="[RING]app_ble_start_fast_advertising called, phone_handle=%d, glasses_handle=%d";
const char r1_ble_role_sync_sdk[]="app_ble_start_fast_advertising called, phone_handle=%d, glasses_handle=%d";
static int ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
void r1_connection_control_role_sync_thread_flags(uint32_t argument)
{
 (void)argument;
 if (ring_enabled()) {
  uint32_t glasses=r1_connection_field10,phone=r1_connection_field8;
  r1_structured_log_format(0x0c800000,r1_ble_role_sync_ring,r1_ble_role_sync_ring,phone,glasses);
 }
 if (r1_structured_log_mode_get()&2u) {
  uint32_t glasses=r1_connection_field10,phone=r1_connection_field8;
  nrf_log_frontend_std_2(0x001c0003,r1_ble_role_sync_sdk,phone,glasses);
 }
 (void)r1_protocol_service_thread_flags_set(0x100);
}
void r1_ble_flag_2000_callback(uint32_t argument)
{
 (void)argument;
 (void)r1_protocol_service_thread_flags_set(0x2000);
}
_Noreturn void r1_ble_io_worker(void *argument)
{
 (void)argument;
 r1_native_sync_wait(4);
 osMessageQueueId_t queue=osMessageQueueNew(8,4,NULL);
 r1_ble_message_queue=queue;
 if (!queue) r1_bae8_rx_allocation_fault();
 r1_peer_record_commit();
 r1_nordic_ble_bootstrap_configuration();
 r1_native_sync_signal(4);
 r1_native_delayed_schedule(r1_connection_control_role_sync_thread_flags,0,0xc00);
 r1_native_delayed_schedule(r1_ble_flag_2000_callback,0,0x2800);
 r1_ble_io_watchdog=r1_native_watchdog_register("ble",10000);
 for (;;) {
  r1_native_watchdog_arm(r1_ble_io_watchdog);
  uint32_t flags=osThreadFlagsWait(0xffffff,0,UINT32_MAX);
  r1_native_watchdog_disarm(r1_ble_io_watchdog);
  if (flags-1u<UINT32_C(0x7fffffff)) {
   nrf_sdh_evts_poll();
   if (flags&0x400000u) r1_ble_connection_control_event_consumer();
   if (flags&0x80u) r1_advertising_stop_guard();
   else if (flags&0x100u) {
    (void)r1_native_delayed_cancel(r1_connection_control_role_sync_thread_flags,0);
    r1_advertising_restart(3);
   } else if (flags&0x400u) r1_advertising_restart(4);
   if (flags&0x2000u) r1_peripheral_watchdog_plan_step(0);
   if (flags&4u) {
    if (ring_enabled()) r1_structured_log_format(0x0c000000,r1_ble_dfu_start_ring,r1_ble_dfu_start_ring);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0003,r1_ble_dfu_start_sdk);
    (void)r1_dfu_bootloader_prepare_boundary();
   }
   if (flags&0x800u) r1_tx_power_plan(0);
   if (flags&0x1000u) r1_tx_power_plan(1);
   nrf_sdh_evts_poll();
   if (flags&0x800000u) r1_native_worker_park(4,r1_ble_io_watchdog);
  }
  r1_native_watchdog_feed(r1_ble_io_watchdog);
 }
}

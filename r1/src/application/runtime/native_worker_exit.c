/* Stock 0x46bac/0x46d10: synchronized worker exit and persistence. */
#include "native_task_suspend.h"
#include "../board/native_task_contexts.h"
extern void *volatile r1_battery_thread_handle,*volatile r1_bae8_rx_thread;
extern void *volatile r1_factory_rx_thread,*volatile r1_touch_task_thread_handle;
extern void *volatile r1_protocol_service_thread;
extern uint32_t r1_advertising_configuration_byte_get(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern uint32_t r1_nv_modules_idle_check(void);
extern void r1_ep_export_force_flush(void);
extern void *r1_crash_record_marker_set(volatile uint16_t *);
extern void r1_previous_state_append_native(const void *,uint32_t);
static void signal_worker(osThreadId_t thread)
{(void)osThreadFlagsSet(thread,0x800000u);}
uint32_t r1_task_suspend_broadcast_plan_build(void)
{
 uint32_t mask;
 if(r1_advertising_configuration_byte_get()==0x55u){
  mask=0x40u;signal_worker(r1_factory_rx_thread);
 }else{
  mask=0x20u;signal_worker(((volatile struct r1_event_context *)&r1_event_system)->thread);
 }
 signal_worker(((volatile struct r1_event_context *)&r1_event_storage)->thread);
 signal_worker(((volatile struct r1_event_context *)&r1_event_sensor)->thread);
 signal_worker(r1_battery_thread_handle);
 signal_worker(r1_touch_task_thread_handle);
 signal_worker(r1_bae8_rx_thread);
 signal_worker(((volatile struct r1_tx_context *)&r1_tx_channel1)->thread);
 signal_worker(((volatile struct r1_tx_context *)&r1_tx_shared)->thread);
 signal_worker(r1_protocol_service_thread);
 return mask|0x69fu;
}
/* Stock 0x6ad64: getter length is a halfword; the native append ABI is not
 * the seven-argument standalone GoMore primitive's ABI. */
void r1_manager_persist_exit_state_6ad64(void)
{
 volatile uint16_t length=0;
 void *state=r1_crash_record_marker_set(&length);
 if(state)r1_previous_state_append_native(state,length);
}
static uint32_t ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void log0(const char *ring,const char *sdk)
{
 if(ring_enabled())(void)r1_structured_log_format(0x0c000000u,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003u,sdk);
}
void r1_manager_workers_exit_46bac(void)
{
 log0("[thread_manager]thread exit start:","thread exit start:");
 uint32_t expected=r1_task_suspend_broadcast_plan_build();
 uint32_t result=osEventFlagsWait(r1_native_sync_event_flags,expected,osFlagsWaitAll,0x1400);
 if(result!=expected){
  if(ring_enabled())(void)r1_structured_log_format(0x04800000u,"[thread_manager]thread sync exit failed:0x%x != 0x%x\r\n","[thread_manager]thread sync exit failed:0x%x != 0x%x\r\n",result,expected);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0001u,"thread sync exit failed:0x%x != 0x%x\r\n",result,expected);
 }
 (void)r1_nv_modules_idle_check();
 r1_manager_persist_exit_state_6ad64();
 r1_ep_export_force_flush();
 log0("[thread_manager]thread exit end.","thread exit end.");
}

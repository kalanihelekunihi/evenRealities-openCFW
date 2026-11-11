/* Stock 0x46004: ordered manager reset/suspend event policy. */
#include <stdint.h>
extern void r1_status_record_ring_publish(uint32_t,uint32_t,uint32_t,uint32_t);
extern void r1_manager_workers_exit_46bac(void);
extern uint32_t r1_reset_trace_persist_tag_write(uint32_t);
extern uint32_t r1_reset_trace_current_site_capture(void);
extern _Noreturn void r1_manager_system_reset(void);
extern uint32_t pm_peers_delete(void);
extern void r1_adc_error(uint32_t);
extern void r1_health_clear_all_caches(void);
extern uint32_t r1_kv_dev_info_bit2_set(uint32_t);
extern uint32_t r1_peer_address_record_write(const void *,const void *);
extern int32_t osDelay(uint32_t);
extern void nrf_delay_ms(uint32_t);
extern uint32_t r1_structured_log_typed(uint32_t,const char *,...);
extern uint32_t r1_retained_log_printf_sink(const char *,...);
extern void r1_sysctl_op_sequence_thunk(void);
void r1_peers_delete_checked(void)
{
 uint32_t status=pm_peers_delete();
 if(status)r1_adc_error(status);
}
static void state(uint32_t value)
{r1_status_record_ring_publish(2,value,0,0);}
static void capture(uint32_t tag)
{
 (void)r1_reset_trace_persist_tag_write(tag);
 (void)r1_reset_trace_current_site_capture();
}
void r1_manager_event_dispatch_46004(uint32_t events)
{
 if(events&1u){
  state(1);r1_manager_workers_exit_46bac();
  (void)r1_sysctl_op_sequence_thunk();nrf_delay_ms(5000);r1_manager_system_reset();
 }
 if(events&2u){
  state(2);r1_manager_workers_exit_46bac();capture(2);r1_manager_system_reset();
 }
 if(events&0x100u){
  r1_peers_delete_checked();r1_health_clear_all_caches();
  (void)r1_kv_dev_info_bit2_set(0);
  uint32_t erased[2]={0xffffffffu,0x0000ffffu};
  (void)r1_peer_address_record_write(erased,erased);
  (void)osDelay(200);state(2);r1_manager_workers_exit_46bac();
  capture(8);nrf_delay_ms(2000);r1_manager_system_reset();
 }
 if(events&0x200u){
  (void)r1_structured_log_typed(0x0c000000u,"[thread_manager][sys] algo mem error -> graceful reset");
  r1_manager_workers_exit_46bac();capture(9);nrf_delay_ms(200);
  (void)r1_retained_log_printf_sink("ASSERTION FAILED!");
  (void)r1_retained_log_printf_sink("File: %s","..\\..\\..\\platform\\threads\\thread_manager.c");
  (void)r1_retained_log_printf_sink("Line: %d",401);
  (void)r1_retained_log_printf_sink("Function: %s","_thread_notify_event_handler");
  (void)r1_retained_log_printf_sink("Expression: %s","0");
  __builtin_trap();
 }
 if(events&4u){
  state(3);r1_manager_workers_exit_46bac();
  (void)r1_sysctl_op_sequence_thunk();nrf_delay_ms(5000);r1_manager_system_reset();
 }
 if(events&8u){state(4);r1_manager_workers_exit_46bac();}
 if(events&16u)r1_manager_workers_exit_46bac();
}

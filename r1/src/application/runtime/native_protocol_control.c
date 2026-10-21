#include <stdint.h>
#include "../board/native_battery_memory.h"
extern uintptr_t r1_packet_field12_get(const volatile uint8_t *);
extern uint32_t r1_protocol_send_flag_set_c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_protocol_send_checked(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_ble_thread_message_encode(uint32_t,uint32_t,uint32_t,const void *);
extern uint32_t r1_phone_connection_role_assign(uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern int32_t osDelay(uint32_t);
extern uint32_t osThreadFlagsSet(void *,uint32_t);
volatile uint8_t r1_health_report_enabled __attribute__((section(".r1.control.report.enabled")))=0;
void *volatile r1_protocol_service_thread __attribute__((section(".r1.control.service.thread"),aligned(4)))=0;
const char r1_control_report_ring[] __attribute__((section(".r1.control.report_ring")))="[RING]service_health_proto_set_report_enable: %d";
const char r1_control_report_sdk[] __attribute__((section(".r1.control.report_sdk")))="service_health_proto_set_report_enable: %d";
const char r1_control_pair_ring[] __attribute__((section(".r1.control.pair_ring")))="[RING]CMD_SYSTEM_PAIR_AUTH type = %d PHONE";
const char r1_control_pair_sdk[] __attribute__((section(".r1.control.pair_sdk")))="CMD_SYSTEM_PAIR_AUTH type = %d PHONE";
uint32_t r1_service_health_report_set(uint32_t value)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,r1_control_report_ring,r1_control_report_ring,(int32_t)value);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_1(0x001c0003,r1_control_report_sdk,value);
 r1_health_report_enabled=(uint8_t)value;return (uintptr_t)&r1_health_report_enabled;
}
uint32_t r1_connection_control_adv_start_handler_plan_decode(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{
 (void)scratch;(void)seed;const volatile uint8_t *bytes=packet;
 const void *payload=(const void *)r1_packet_field12_get(bytes);
 if(!payload||(uint16_t)(read16(bytes+8)-12u)<12u)
  return r1_protocol_send_flag_set_c(handle,10,1,read16(bytes+3),1);
 (void)r1_protocol_send_flag_set_c(handle,10,1,read16(bytes+3),0);
 uint32_t phone=r1_phone_connection_handle_get();
 return r1_ble_thread_message_encode(phone,0x200,12,payload);
}
uint32_t r1_pair_role_handler(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{
 (void)scratch;(void)seed;const volatile uint8_t *bytes=packet;
 const volatile uint8_t *payload=(const volatile uint8_t *)r1_packet_field12_get(bytes);
 if(!payload)return 0;
 if(payload[0]==1){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x0c400000,r1_control_pair_ring,r1_control_pair_ring,(int32_t)payload[0]);
  if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_1(0x001c0003,r1_control_pair_sdk,payload[0]);
  (void)r1_phone_connection_role_assign(handle);
  (void)r1_ble_thread_message_encode(handle,2,1,(const void *)(uintptr_t)payload);
 }
 uint32_t response=0;
 return r1_protocol_send_checked(handle,8,0,read16(bytes+3),&response,1);
}
/* Supplemental callable bodies: preserve worker signaling, without assigning
 * a reset/reboot meaning to flag4 beyond the authenticated call path. */
__attribute__((noinline)) uint32_t r1_protocol_service_thread_flags_set(uint32_t flags)
{void *thread=r1_protocol_service_thread;return thread?osThreadFlagsSet(thread,flags):0;}
uint32_t r1_protocol_command_00083e2c(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{
 (void)scratch;(void)seed;
 (void)r1_protocol_send_flag_set_c(handle,9,1,read16((const volatile uint8_t *)packet+3),0);
 (void)osDelay(2000);
 return r1_protocol_service_thread_flags_set(4);
}

#include <stdint.h>
#include "../board/native_battery_memory.h"
extern uintptr_t r1_packet_field12_get(const volatile uint8_t *);
extern uint32_t r1_protocol_send_flag_set_c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_reset_trace_reboot_caller_write(uint32_t);
extern uint32_t r1_battery_voltage_get(void),r1_time_backend_timestamp(void);
extern void r1_kv_dev_info_fields_set(volatile void *);
extern void *volatile r1_low_battery_thread_handle;
extern uint32_t osThreadFlagsSet(void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_0(uint32_t,const char *);
const char r1_power_command_ring[] __attribute__((section(".r1.power.command.ring")))="[RING]CMD_SYSTEM_POWER_CONTROL: recovery, post EVENT_SYSTEM_RESUME_SETTING";
const char r1_power_command_sdk[] __attribute__((section(".r1.power.command.sdk")))="CMD_SYSTEM_POWER_CONTROL: recovery, post EVENT_SYSTEM_RESUME_SETTING";
/* Protocol arguments have ordinary C semantics. The stored event record
 * contains only timestamp, kind three and a fourteen-bit voltage. */
uint32_t r1_protocol_command_000843c8(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{
 (void)scratch;(void)seed;
 const volatile uint8_t *p=packet;
 const volatile uint8_t *payload=(const void *)r1_packet_field12_get(p);
 if(!payload)return 0;
 uint32_t command=payload[0];
 if(command==0 || command>3)
  return r1_protocol_send_flag_set_c(handle,18,1,read16(p+3),1);
 (void)r1_protocol_send_flag_set_c(handle,18,1,read16(p+3),0);
 (void)osDelay(100);
 command=payload[0];
 if(command==1){
  (void)r1_reset_trace_reboot_caller_write(1);
  return osThreadFlagsSet(r1_low_battery_thread_handle,2);
 }
 if(command==2){
  volatile uint32_t record[2]={0,3};
  uint32_t voltage=r1_battery_voltage_get();
  record[1]=((voltage&0x3fffu)<<2)|3u;
  record[0]=r1_time_backend_timestamp();
  r1_kv_dev_info_fields_set(record);
  return osThreadFlagsSet(r1_low_battery_thread_handle,1);
 }
 if(command!=3)return command;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c000000,r1_power_command_ring,r1_power_command_ring);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_0(0x001c0003,r1_power_command_sdk);
 return osThreadFlagsSet(r1_low_battery_thread_handle,256);
}

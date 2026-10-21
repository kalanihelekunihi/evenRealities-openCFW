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
/* Frame is the native push{r2,r3,r4,r5,r6,lr} view. The separate tail words are
 * implementation scratch; they never replace the externally saved frame. */
__attribute__((used,noinline)) static uint32_t power_command_kernel(uint32_t handle,const volatile uint8_t *packet,volatile uint32_t *frame,volatile uint32_t *tail)
{
 tail[1]=0;
 const volatile uint8_t *payload=(const void *)r1_packet_field12_get(packet);
 if(!payload)return 0;
 uint32_t command=payload[0];
 if(command==0 || command>3){frame[0]=1;return r1_protocol_send_flag_set_c(handle,18,1,read16(packet+3),1);}
 frame[0]=0;
 (void)r1_protocol_send_flag_set_c(handle,18,1,read16(packet+3),0);
 (void)osDelay(100);
 command=payload[0];
 if(command==1){
  (void)r1_reset_trace_reboot_caller_write(1);
  tail[0]=(uintptr_t)r1_low_battery_thread_handle;tail[1]=2;return 0;
 }
 if(command==2){
  frame[1]=frame[1]|3u;
  uint32_t voltage=r1_battery_voltage_get();
  frame[1]=(frame[1]&0xffff0003u)|((voltage&0x3fffu)<<2);
  frame[0]=r1_time_backend_timestamp();
  r1_kv_dev_info_fields_set((volatile void *)frame);
  return osThreadFlagsSet(r1_low_battery_thread_handle,1);
 }
 if(command!=3)return command;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c000000,r1_power_command_ring,r1_power_command_ring);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_0(0x001c0003,r1_power_command_sdk);
 tail[0]=(uintptr_t)r1_low_battery_thread_handle;tail[1]=256;return 0;
}
/* Native command1/3 restore their frame before tail-calling flags; command2
 * calls flags first and restores the event words into r2/r3 afterwards. */
__attribute__((naked,noinline)) uint32_t r1_protocol_command_000843c8(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)),uintptr_t scratch __attribute__((unused)),uint32_t seed __attribute__((unused)))
{
 __asm__ volatile("push {r2,r3,r4,r5,r6,lr}\nsub sp,sp,#8\nadd r2,sp,#8\nmov r3,sp\nbl power_command_kernel\nldr r1,[sp,#4]\ncbz r1,1f\nldr r0,[sp]\nadd sp,sp,#8\npop {r2,r3,r4,r5,r6,lr}\nb osThreadFlagsSet\n1: add sp,sp,#8\npop {r2,r3,r4,r5,r6,pc}");
}

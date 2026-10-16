#include <stdint.h>
#include "../board/native_battery_memory.h"
extern uintptr_t r1_packet_field12_get(const volatile uint8_t *);
extern uint32_t r1_protocol_send_flag_set_c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_protocol_response_send_0x100(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
volatile uint8_t r1_health_mode_byte __attribute__((section(".r1.system.command.health_mode")))=0;
const char r1_wear_status_ring[] __attribute__((section(".r1.system.command.wear_ring")))="[RING]proto system recv wear status, wear status: %d";
const char r1_wear_status_sdk[] __attribute__((section(".r1.system.command.wear_sdk")))="proto system recv wear status, wear status: %d";
__attribute__((noinline)) uint32_t r1_health_mode_get(void) {return r1_health_mode_byte;}
/* Same explicit saved-word ABI as the admitted operation1 wrapper; operation3
 * sends one byte, restoring payload/length into the saved r2/r3 words. */
__attribute__((noinline)) uint32_t r1_phone_cmd_send_op3(const void *payload,uint32_t first,uint32_t second)
{
 uint32_t incoming3;__asm__ volatile("mov %0, r3":"=r"(incoming3));
 volatile uint32_t saved2=second,saved3=incoming3;uint32_t result=0;
 if(payload){uint32_t handle=r1_phone_connection_handle_get();saved2=(uintptr_t)payload;saved3=1;result=r1_protocol_response_send_0x100(handle,3,first,second,payload,1);}
 uint32_t restored2=saved2,restored3=saved3;__asm__ volatile("mov r2, %0\nmov r3, %1"::"r"(restored2),"r"(restored3):"r2","r3");return result;
}
uint32_t r1_protocol_command_000844ec(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{
 (void)scratch;(void)seed;const volatile uint8_t *p=packet;
 const volatile uint8_t *payload=(const void *)r1_packet_field12_get(p);
 if(!payload)return 0;
 (void)r1_protocol_send_flag_set_c(handle,12,1,read16(p+3),0);
 return r1_event_publish(0x2004,(const void *)(uintptr_t)payload,(uint32_t)payload[0]+1u);
}
uint32_t r1_protocol_command_00084860(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{
 (void)scratch;(void)seed;return r1_protocol_send_flag_set_c(handle,131,1,read16((const volatile uint8_t *)packet+3),0);
}
uint32_t r1_protocol_command_00084b24(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{
 (void)handle;(void)scratch;(void)seed;uint32_t value=0;
 if(!r1_health_mode_get())value=1;else if(r1_health_mode_get()==1)value=2;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,r1_wear_status_ring,r1_wear_status_ring,value);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_1(0x001c0003,r1_wear_status_sdk,value);
 return r1_phone_cmd_send_op3(&value,0,read16((const volatile uint8_t *)packet+3));
}

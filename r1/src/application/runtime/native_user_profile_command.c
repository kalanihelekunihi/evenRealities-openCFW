#include <stdint.h>
#include "../board/native_battery_memory.h"
extern uintptr_t r1_packet_field12_get(const volatile uint8_t *);
extern uint32_t r1_protocol_send_flag_set_c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
const char r1_profile_command_ring[] __attribute__((section(".r1.profile.command.ring")))="[RING]proto user info,%d,%d,%d,%d";
const char r1_profile_command_sdk[] __attribute__((section(".r1.profile.command.sdk")))="proto user info,%d,%d,%d,%d";
__attribute__((used,noinline)) static uint32_t profile_command_kernel(uint32_t handle,const volatile uint8_t *packet,volatile uint8_t *frame)
{
 const volatile uint8_t *payload=(const void *)r1_packet_field12_get(packet);
 if(!payload)return r1_protocol_send_flag_set_c(handle,4,1,read16(packet+3),1);
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  uint32_t second=payload[1],fourth=read16(payload+4),third=read16(payload+2),first=payload[0];
  (void)r1_structured_log_format(0x0d000000,r1_profile_command_ring,r1_profile_command_ring,first,second,third,fourth);
 }
 if(r1_structured_log_mode_get()&2u){
  uint32_t fourth=read16(payload+4),third=read16(payload+2),second=payload[1],first=payload[0];
  (void)nrf_log_frontend_std_4(0x001c0003,r1_profile_command_sdk,first,second,third,fourth);
 }
 (void)r1_protocol_send_flag_set_c(handle,4,1,read16(packet+3),0);
 frame[12]=payload[1];frame[13]=payload[0]?2:1;frame[14]=payload[2];frame[15]=payload[4];
 write16(frame+16,0xffff);write16(frame+18,0xffff);write16(frame+20,0xffff);
 /* Native publishes12 bytes but only initializes10. Retain the external
  * frame's last two bytes; this is not a default profile or admission policy. */
 return r1_event_publish(0x100a,(const void *)(uintptr_t)(frame+12),12);
}
__attribute__((naked,noinline)) uint32_t r1_native_user_profile_handler(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)))
{__asm__ volatile("push {r4,r5,r6,lr}\nsub sp,sp,#24\nmov r2,sp\nbl profile_command_kernel\nadd sp,sp,#24\npop {r4,r5,r6,pc}");}

#include <stdint.h>
#include "../board/native_battery_memory.h"
extern uintptr_t r1_packet_field12_get(const volatile uint8_t *);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
/* Build-only native boundary. The bounded recovery planner is a separate API;
 * persistent/identity-bearing native dispatch is deliberately unresolved. */
extern uint32_t r1_native_nv_recovery_command_dispatch(uint32_t,uint32_t,uint32_t,const void *);
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_protocol_send_flag_inv(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
const char r1_nv_recover_null_ring[] __attribute__((section(".r1.nv.envelope.null_ring")))="[RING]CMD_SYSTEM_NV_RECOVER nv_recover is NULL";
const char r1_nv_recover_null_sdk[] __attribute__((section(".r1.nv.envelope.null_sdk")))="CMD_SYSTEM_NV_RECOVER nv_recover is NULL";
const char r1_nv_recover_fields_ring[] __attribute__((section(".r1.nv.envelope.fields_ring")))="[RING]CMD_SYSTEM_NV_RECOVER cmd: %d, len: %d, crc: %d";
const char r1_nv_recover_fields_sdk[] __attribute__((section(".r1.nv.envelope.fields_sdk")))="CMD_SYSTEM_NV_RECOVER cmd: %d, len: %d, crc: %d";
uint32_t r1_native_nv_recovery_envelope_handler(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{
 (void)handle;(void)scratch;(void)seed;
 const volatile uint8_t *payload=(const void *)r1_packet_field12_get(packet);
 if(!payload){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x04000000,r1_nv_recover_null_ring,r1_nv_recover_null_ring);
  uint32_t mode=r1_structured_log_mode_get();
  if(mode&2u)return nrf_log_frontend_std_0(0x001c0001,r1_nv_recover_null_sdk);
  return mode<<30;
 }
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  uint32_t crc=read16(payload+3),length=read16(payload+1),command=payload[0];
  (void)r1_structured_log_format(0x0cc00000,r1_nv_recover_fields_ring,r1_nv_recover_fields_ring,command,length,crc);
 }
 if(r1_structured_log_mode_get()&2u){
  uint32_t crc=read16(payload+3),length=read16(payload+1),command=payload[0];
  (void)nrf_log_frontend_std_3(0x001c0003,r1_nv_recover_fields_sdk,command,length,crc);
 }
 uint32_t crc=read16(payload+3),length=read16(payload+1),command=payload[0];
 return r1_native_nv_recovery_command_dispatch(command,length,crc,(const void *)(uintptr_t)(payload+5));
}
__attribute__((used,noinline)) static uint32_t link_ready_body(volatile uint32_t *frame)
{
 uint32_t handle=r1_phone_connection_handle_get();frame[0]=0;frame[1]=0;frame[2]=0;
 return r1_protocol_send_flag_inv(handle,17,1,1,0,0,0)!=0;
}
__attribute__((naked,noinline)) uint32_t r1_phone_link_ready_query(void)
{__asm__ volatile("push {r1,r2,r3,lr}\nmov r0,sp\nbl link_ready_body\npop {r1,r2,r3,pc}");}

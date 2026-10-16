#include <stdint.h>
#include "../board/native_battery_memory.h"
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
/* Native 84c82 callback is deliberately unresolved; no numeric function pointer
 * substitutes for its missing source body or final-image placement. */
extern void r1_protocol_time_timeout_callback(uint32_t);
extern uintptr_t r1_packet_field12_get(const volatile uint8_t *);
extern int32_t r1_time_utc_offset_get(void);
extern uint32_t r1_time_backend_timestamp(void);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_protocol_send_flag_set_c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_protocol_ack_header_send(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
/* 7bb20 ignores its cached-read status and can consume private-frame history.
 * Keep that provider gate explicit rather than inventing a default record. */
extern uint32_t r1_nv_recovery_needed_query_boundary(void);
extern uint32_t r1_phone_link_ready_query(void);
extern uint32_t r1_native_nv_recovery_report_boundary(void);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_0(uint32_t,const char *);
const char r1_time_sync_lost_ring[] __attribute__((section(".r1.time.sync.lost_ring")))="[RING]nv data lose, request nv recover";
const char r1_time_sync_lost_sdk[] __attribute__((section(".r1.time.sync.lost_sdk")))="nv data lose, request nv recover";
const char r1_time_sync_valid_ring[] __attribute__((section(".r1.time.sync.valid_ring")))="[RING]nv data valid, report nv recover";
const char r1_time_sync_valid_sdk[] __attribute__((section(".r1.time.sync.valid_sdk")))="nv data valid, report nv recover";
/* Build-only native control flow. Event bytes are all explicitly initialized.
 * Lower private-frame/scratch ABI and recovery admission remain separate gates. */
uint32_t r1_protocol_command_000846dc(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{
 (void)scratch;(void)seed;
 (void)r1_native_delayed_cancel(r1_protocol_time_timeout_callback,0);
 const volatile uint8_t *p=packet;
 const volatile uint8_t *payload=(const void *)r1_packet_field12_get(p);
 if(!payload)return 0;
 volatile uint8_t event[12];
 write16(event,(uint32_t)r1_time_utc_offset_get());
 write32(event+4,r1_time_backend_timestamp());
 write16(event+2,read16(payload));
 write32(event+8,read32(payload+2));
 (void)r1_event_publish(3,(const void *)(uintptr_t)event,12);
 (void)r1_protocol_send_flag_set_c(handle,5,1,read16(p+3),0);
 (void)r1_protocol_ack_header_send(handle,4,1,1,0,0,0);
 const char *ring,*sdk;
 if(r1_nv_recovery_needed_query_boundary()){
  (void)r1_phone_link_ready_query();ring=r1_time_sync_lost_ring;sdk=r1_time_sync_lost_sdk;
 }else{
  (void)r1_native_nv_recovery_report_boundary();ring=r1_time_sync_valid_ring;sdk=r1_time_sync_valid_sdk;
 }
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c000000,ring,ring);
 uint32_t mode=r1_structured_log_mode_get();
 if(mode&2u)return nrf_log_frontend_std_0(0x001c0003,sdk);
 return mode<<30;
}

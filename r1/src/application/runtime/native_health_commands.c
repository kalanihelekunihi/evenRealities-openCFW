#include <stdint.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_protocol_send_response(uint32_t,const void *,const void *,uint32_t);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_service_health_report_set(uint32_t);
#define FLAG_HELPER(suffix) \
__attribute__((noinline)) uint32_t r1_protocol_send_flag_set_##suffix(uint32_t handle,uint32_t command,uint32_t version,uint32_t sequence,uint32_t flags) { \
 uint32_t header[2]={(uint8_t)((flags<<2)|3u)|((uint32_t)(uint8_t)version<<8)|((command&0xff00u)<<8)|((command&255u)<<24),(uint16_t)sequence}; \
 return r1_protocol_send_response(handle,header,0,0); }
FLAG_HELPER(a) FLAG_HELPER(b) FLAG_HELPER(c)
/* Four arguments expose the native incoming r3 seed, already passed by the
 * module's four-word callback ABI. It is event data, not zero padding. */
#define DAILY(name,command,kind) \
uint32_t name(uint32_t handle,const void *packet_arg,uintptr_t scratch,uint32_t seed) { \
 (void)scratch;const volatile uint8_t *packet=packet_arg;uint32_t flags=packet[5];if(flags&3u)return handle; \
 uint32_t record[2]={0,seed}; \
 (void)r1_protocol_send_flag_set_b(handle,command,2,read16(packet+3),0); \
 record[0]=(kind)|0x100u|((uint32_t)read16(packet+3)<<16); \
 return r1_event_publish(14,record,8); }
DAILY(r1_activity_daily_handler,0x501,4)
DAILY(r1_heart_rate_daily_handler,0x101,0)
DAILY(r1_hrv_daily_handler,0x401,5)
DAILY(r1_sleep_daily_handler,0x601,6)
DAILY(r1_spo2_daily_handler,0x201,1)
#define POINT(name,kind) \
uint32_t name(uint32_t handle,const void *packet_arg,uintptr_t scratch,uint32_t seed) { \
 (void)handle;(void)scratch;const volatile uint8_t *packet=packet_arg;uint32_t flags=packet[5];if(flags&2u)return flags;if(flags&1u)return 0; \
 uint32_t record[2]={(kind)|((uint32_t)read16(packet+3)<<16),seed};return r1_event_publish(14,record,8); }
POINT(r1_heart_rate_point_handler,0)
POINT(r1_hrv_point_handler,5)
POINT(r1_spo2_point_handler,1)
#define MEASURE(name,command,event) \
uint32_t name(uint32_t handle,const void *packet_arg,uintptr_t scratch,uint32_t seed) { \
 (void)scratch;(void)seed;const volatile uint8_t *packet=packet_arg;uint32_t flags=packet[5];if(!(flags&2u)||(flags&1u))return handle; \
 (void)r1_protocol_send_flag_set_b(handle,command,2,read16(packet+3),0);uint8_t value=1;return r1_event_publish(event,&value,1); }
MEASURE(r1_heart_rate_measurement_plan,0x103,0x1002)
MEASURE(r1_spo2_measurement_plan,0x203,0x1004)
uint32_t r1_sleep_detail_plan(uint32_t handle,const void *packet_arg,uintptr_t scratch,uint32_t seed)
{(void)handle;(void)scratch;(void)seed;const volatile uint8_t *packet=packet_arg;uint32_t flags=packet[5];if(!(flags&2u))return flags;if(flags&1u)return 0;return r1_event_publish(0x100e,0,0);}
uint32_t r1_health_history_noop_handler(uint32_t handle,const void *packet,uintptr_t scratch,uint32_t seed)
{(void)packet;(void)scratch;(void)seed;return handle;}
uint32_t r1_health_report_setting_plan(uint32_t handle,const void *packet_arg,uintptr_t scratch,uint32_t seed)
{
 (void)handle;(void)scratch;(void)seed;const volatile uint8_t *packet=packet_arg;
 uint16_t length=(uint16_t)(read16(packet+8)-12u);
 /* Native length==12 selects address0 and still reads its first byte. */
 const volatile uint8_t *payload=length?packet+12:(const volatile uint8_t *)0;
 return r1_service_health_report_set(*payload!=0);
}

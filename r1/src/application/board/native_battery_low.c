#include <stdint.h>
#include "native_battery_context.h"
#include "native_battery_memory.h"
extern void *volatile r1_low_battery_thread_handle;
extern uint32_t r1_structured_log_mode_get(void),r1_battery_voltage_get(void),time_backend_timestamp_thunk(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void r1_kv_dev_info_fields_set(volatile void *);
extern uint32_t osThreadFlagsSet(void *,uint32_t),r1_event_publish(uint32_t,const void *,uint32_t);
const char r1_battery_low_ring[] __attribute__((section(".r1.battery_low.ring")))="[RING]battery voltage low %d(3350mv), low_power_cnt=%d";
const char r1_battery_low_sdk[] __attribute__((section(".r1.battery_low.sdk")))="battery voltage low %d(3350mv), low_power_cnt=%d";
/* Counter and live-provider sequencing follow stock 0x3d88c. Private caller
 * scratch words are replaced by an initialized timestamp/voltage record. */
void r1_battery_low_escalation(void)
{
 volatile uint8_t *d=r1_battery_device_context;
 if(read16(d+42)>=3350u){d[47]=0;return;}
 d[47]=(uint8_t)(d[47]+1u);
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  uint32_t count=d[47],voltage=read16(d+42);
  (void)r1_structured_log_format(0x08800000,r1_battery_low_ring,r1_battery_low_ring,voltage,count);
 }
 if(r1_structured_log_mode_get()&2u){
  uint32_t count=d[47],voltage=read16(d+42);
  nrf_log_frontend_std_2(0x001c0002,r1_battery_low_sdk,voltage,count);
 }
 uint32_t count=d[47];
 if(count==9){(void)r1_event_publish(0x100c,0,0);return;}
 if(count<10)return;
 volatile uint32_t record[2]={0,0};
 uint32_t voltage=r1_battery_voltage_get();
 record[1]=(voltage&0x3fffu)<<2;
 record[0]=time_backend_timestamp_thunk();
 r1_kv_dev_info_fields_set(record);
 (void)osThreadFlagsSet(r1_low_battery_thread_handle,1);
}

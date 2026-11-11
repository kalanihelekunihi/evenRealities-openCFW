#include <stdint.h>
#include "../board/native_battery_memory.h"
extern volatile uint8_t r1_cache_activity[];
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t),nrf_log_frontend_std_6(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t r1_activity_ten_minute_bucket(uint32_t);
extern const char r1_activity_multi_ring[],r1_activity_multi_sdk[];
/* Stock 0x5aa14: update only the start bucket, retaining separate packed writes. */
void r1_activity_event_storage(const volatile uint8_t *sample)
{
 if(!sample)return;
 uint32_t duration=read16(sample+6),timestamp=read32(sample+8);
 uint32_t start=r1_activity_ten_minute_bucket(timestamp-duration);
 timestamp=read32(sample+8);
 uint32_t end=r1_activity_ten_minute_bucket(timestamp);
 if(start>=144u || end>=144u){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
   duration=read16(sample+6);timestamp=read32(sample+8);
   (void)r1_structured_log_format(0x05000000,"[RING]activity in fai:%d,%d,st:%d,et:%d","[RING]activity in fai:%d,%d,st:%d,et:%d",timestamp,duration,start,end);
  }
  if(r1_structured_log_mode_get()&2u){
   duration=read16(sample+6);timestamp=read32(sample+8);
   nrf_log_frontend_std_4(0x001c0001,"activity in fai:%d,%d,st:%d,et:%d",timestamp,duration,start,end);
  }
  return;
 }
 if(start!=end){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
   uint32_t activity=read16(sample+2),steps=read16(sample+4);
   duration=read16(sample+6);timestamp=read32(sample+8);
   (void)r1_structured_log_format(0x0d800000,r1_activity_multi_ring,r1_activity_multi_ring,timestamp,duration,start,end,steps,activity);
  }
  if(r1_structured_log_mode_get()&2u){
   uint32_t activity=read16(sample+2),steps=read16(sample+4);
   duration=read16(sample+6);timestamp=read32(sample+8);
   nrf_log_frontend_std_6(0x001c0003,r1_activity_multi_sdk,timestamp,duration,start,end,steps,activity);
  }
 }
 volatile uint8_t *entry=r1_cache_activity+start*4u;
 uint32_t add=read16(sample+4),value=read32(entry);
 value=(value&~0xfffu)|((value+add)&0xfffu);write32(entry,value);
 add=read16(sample+2);value=(value&~(0x3ffu<<12))|((((value>>12)+add)&0x3ffu)<<12);write32(entry,value);
 add=read16(sample);value=(value&~(0x3ffu<<22))|((((value>>22)+add)&0x3ffu)<<22);write32(entry,value);
}
#include "../../vendor/time_calendar/time_calendar.h"
extern int32_t r1_time_utc_offset_get(void);
/* Stock 0x5ac74. Only the bucket result is public; calendar scratch is local. */
__attribute__((noinline,section(".text.r1_activity_ten_minute_bucket")))
uint32_t r1_activity_ten_minute_bucket(uint32_t timestamp)
{
 volatile time_calendar_datetime calendar={0};
 _Static_assert(sizeof(calendar)==8 && offsetof(time_calendar_datetime,hour)==4 && offsetof(time_calendar_datetime,minute)==5,"native calendar layout");
 int32_t offset=r1_time_utc_offset_get();
 (void)time_calendar_utc_to_calendar((int32_t)timestamp,offset,(time_calendar_datetime *)(uintptr_t)&calendar);
 uint32_t ten_minutes=calendar.minute/10u;
 return (uint8_t)(calendar.hour*6u+ten_minutes);
}
const char r1_activity_multi_ring[] __attribute__((aligned(1),section(".r1.activity.multi_ring")))="[RING]activity span multi 10min bucket, ts:%d,dur:%d,st:%d,et:%d,steps:%d,act:%d";
const char r1_activity_multi_sdk[] __attribute__((aligned(1),section(".r1.activity.multi_sdk")))="activity span multi 10min bucket, ts:%d,dur:%d,st:%d,et:%d,steps:%d,act:%d";

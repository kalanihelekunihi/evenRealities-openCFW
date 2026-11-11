/* Stock R1 0x5a2b8: retained record metadata, snapshot, then checksum. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "../board/native_battery_memory.h"
#include "../../include/r1_stock_checksums.h"
#include "../../vendor/time_calendar/time_calendar.h"
extern volatile uint32_t r1_reset_trace_context[6];
extern time_calendar_state r1_time_state;
extern int32_t r1_time_utc_offset_get(void);
extern uint32_t r1_time_backend_timestamp(void);
extern void *r1_crash_record_marker_set(volatile uint16_t *);
extern uint32_t r1_health_crash_snapshot_builder(void *,uint32_t,uint32_t);
uint32_t r1_time_status_get(void)
{
 _Static_assert(offsetof(time_calendar_state,time_update_pending)==11,"native status byte");
 return ((const volatile time_calendar_state *)&r1_time_state)->time_update_pending;
}
uint32_t r1_health_crash_record_initializer(void)
{
 uint32_t base=r1_reset_trace_context[2];
 volatile uint8_t *record=(volatile uint8_t *)(uintptr_t)base;
 write32(record,UINT32_C(0x5a5a5a5a));
 write16(record+6,(uint16_t)r1_time_utc_offset_get());
 write32(record+8,r1_time_backend_timestamp());
 uint32_t valid=r1_time_status_get();
 write16(record+4,(read16(record+4)&0xfffeu)|(valid&1u));
 volatile uint16_t length=0;
 void *blob=r1_crash_record_marker_set(&length);
 /* The actual getter advertises736 bytes; stock admits only896 here.
  * Preserve the distinct contracts and do not fabricate a producer payload. */
 if(blob && length==896){
  (void)memcpy((void *)(uintptr_t)(base+12),blob,896);
  write32(record+908,UINT32_C(0x5a5a5a5a));
 }
 (void)r1_health_crash_snapshot_builder((void *)(uintptr_t)(base+912),read32(record+8),read16(record+6));
 uint32_t crc=r1_stock_crc16_modbus((const uint8_t *)(uintptr_t)record,964);
 write16(record+964,crc);
 return crc;
}

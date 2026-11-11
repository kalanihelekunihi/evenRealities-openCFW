#ifndef R1_NATIVE_HEALTH_OFFLINE_QUEUE_H
#define R1_NATIVE_HEALTH_OFFLINE_QUEUE_H
#include <stdint.h>
struct r1_offline_cursor {uint8_t read,write,count;};
extern volatile struct r1_offline_cursor r1_offline_hr_cursor,r1_offline_spo2_cursor,r1_offline_hrv_cursor,r1_offline_activity_cursor;
extern volatile uint8_t r1_offline_hr_records[384],r1_offline_spo2_records[384],r1_offline_hrv_records[480],r1_offline_activity_records[2304];
#define R1_OFFLINE_API(name) void name(uint32_t,uint32_t,uint32_t,volatile uint8_t *,uint32_t)
R1_OFFLINE_API(r1_hr_cache_future_record_guard);
R1_OFFLINE_API(r1_spo2_cache_future_record_guard);
R1_OFFLINE_API(r1_hrv_cache_future_record_guard);
R1_OFFLINE_API(r1_activity_flash_record_enqueue_plan);
R1_OFFLINE_API(r1_heart_rate_offline_queue_enqueue);
R1_OFFLINE_API(r1_spo2_offline_queue_enqueue);
R1_OFFLINE_API(r1_hrv_offline_queue_enqueue);
R1_OFFLINE_API(r1_activity_offline_queue_enqueue);
#undef R1_OFFLINE_API
#endif

/* Reconstructed stock R1 2.2.6.0009 future-record guards and bounded offline
 * enqueue paths. Cursor zeroes come from authenticated scatter decompression;
 * record arrays lie in its zero region. No allocation/lock is added. */
#include "native_health_offline_queue.h"
#include "../board/native_battery_memory.h"
#include <stddef.h>
#define RECORDS(name,size) volatile uint8_t r1_offline_##name##_records[size] __attribute__((section(".bss.r1.offline." #name ".records"),aligned(4)))={0}
#define CURSOR(name) volatile struct r1_offline_cursor r1_offline_##name##_cursor __attribute__((section(".r1.offline." #name ".cursor"),aligned(1)))={0,0,0}
RECORDS(hr,384);RECORDS(spo2,384);RECORDS(hrv,480);RECORDS(activity,2304);
CURSOR(hr);CURSOR(spo2);CURSOR(hrv);CURSOR(activity);
_Static_assert(sizeof(struct r1_offline_cursor)==3 && offsetof(struct r1_offline_cursor,count)==2,"native cursor ABI");
extern uint32_t r1_time_backend_timestamp(void),r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t),nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
enum queue_kind {HR,SPO2,HRV,ACTIVITY};
struct queue_view {volatile uint8_t *records;volatile struct r1_offline_cursor *cursor;uint32_t stride,capacity;};
static const struct queue_view queues[4]={
 {r1_offline_hr_records,&r1_offline_hr_cursor,16,24},
 {r1_offline_spo2_records,&r1_offline_spo2_cursor,16,24},
 {r1_offline_hrv_records,&r1_offline_hrv_cursor,20,24},
 {r1_offline_activity_records,&r1_offline_activity_cursor,16,144}
};
struct guard_messages {const char *record_ring,*record_sdk,*day_ring,*day_sdk;};
#define GUARD_TEXT(name) {"[RING]" name " cache ignore future record:%u now:%u",name " cache ignore future record:%u now:%u","[RING]" name " cache ignore future day_zero:%u now:%u",name " cache ignore future day_zero:%u now:%u"}
static const struct guard_messages guard_messages[4]={GUARD_TEXT("hr"),GUARD_TEXT("spo2"),GUARD_TEXT("hrv"),GUARD_TEXT("activity")};
#undef GUARD_TEXT
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void log_two(uint32_t level,uint32_t metadata,const char *ring,const char *sdk,uint32_t value,uint32_t now)
{
    if(ring_enabled())(void)r1_structured_log_format(level,ring,ring,value,now);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(metadata,sdk,value,now);
}
static const char *const queue_ring[3]={"[RING]hr unsynced cache drop future record day:%u ts:%u now:%u","[RING]spo2 unsynced cache drop future record day:%u ts:%u now:%u","[RING]hrv unsynced cache drop future record day:%u ts:%u now:%u"};
static const char *const queue_sdk[3]={"hr unsynced cache drop future record day:%u ts:%u now:%u","spo2 unsynced cache drop future record day:%u ts:%u now:%u","hrv unsynced cache drop future record day:%u ts:%u now:%u"};
static void enqueue(enum queue_kind kind,uint32_t day,uint32_t offset,uint32_t slot,volatile uint8_t *data,uint32_t timestamp)
{
    if(!data)return;
    if(kind==HRV){if(slot>=24 || !read16(data))return;}
    else if(kind==ACTIVITY){if(!read32(data))return;}
    else if(!data[0] || slot>=24)return;
    uint32_t now=r1_time_backend_timestamp();
    if(timestamp>now || day>now){
        if(kind==ACTIVITY){
            if(timestamp>now)log_two(0x0c800000,0x001c0003,"[RING]activity unsynced cache drop future record:%u now:%u","activity unsynced cache drop future record:%u now:%u",timestamp,now);
            else log_two(0x0c800000,0x001c0003,"[RING]activity unsynced cache drop future day_zero:%u now:%u","activity unsynced cache drop future day_zero:%u now:%u",day,now);
        }else{
            if(ring_enabled())(void)r1_structured_log_format(0x0cc00000,queue_ring[kind],queue_ring[kind],day,timestamp,now);
            if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_3(0x001c0003,queue_sdk[kind],day,timestamp,now);
        }
        return;
    }
    const struct queue_view *queue=&queues[kind];
    uint32_t index=queue->cursor->write;
    volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)queue->records+index*queue->stride);
    uint32_t day_at=4,offset_at=12,slot_at=14,timestamp_at=8;
    if(kind==HRV){write32(entry,read32(data));write16(entry+4,read16(data+4));day_at=8;offset_at=16;slot_at=18;timestamp_at=12;}
    else if(kind==ACTIVITY)write32(entry,read32(data));
    else{write16(entry,read16(data));entry[2]=data[2];}
    write32(entry+day_at,day);write16(entry+offset_at,offset);entry[slot_at]=(uint8_t)slot;write32(entry+timestamp_at,timestamp);
    queue->cursor->write=(uint8_t)((index+1u)%queue->capacity);
    uint32_t count=queue->cursor->count;
    if(count<queue->capacity)queue->cursor->count=(uint8_t)(count+1u);
    else queue->cursor->read=(uint8_t)(((uint32_t)queue->cursor->read+1u)%queue->capacity);
}
#define ENQUEUE(name,kind) void name(uint32_t day,uint32_t offset,uint32_t slot,volatile uint8_t *data,uint32_t timestamp){enqueue(kind,day,offset,slot,data,timestamp);}
ENQUEUE(r1_heart_rate_offline_queue_enqueue,HR)
ENQUEUE(r1_spo2_offline_queue_enqueue,SPO2)
ENQUEUE(r1_hrv_offline_queue_enqueue,HRV)
ENQUEUE(r1_activity_offline_queue_enqueue,ACTIVITY)
#undef ENQUEUE
static void guard(enum queue_kind kind,uint32_t day,uint32_t offset,uint32_t hour,volatile uint8_t *data,uint32_t timestamp)
{
    if(!data)return;
    if((kind==HRV || kind==ACTIVITY) && hour>=24)return;
    if(timestamp>UINT32_C(0x38640900))return;
    uint32_t now=r1_time_backend_timestamp();
    const struct guard_messages *messages=&guard_messages[kind];
    if(timestamp>now){log_two(0x08800000,0x001c0002,messages->record_ring,messages->record_sdk,timestamp,now);return;}
    if(day>now){log_two(0x08800000,0x001c0002,messages->day_ring,messages->day_sdk,day,now);return;}
    if(kind==ACTIVITY){
        for(uint32_t i=0;i<6;++i)r1_activity_offline_queue_enqueue(day,offset,(uint8_t)(hour*6u+i),(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)data+i*4u),timestamp);
    }else enqueue(kind,day,offset,hour,data,timestamp);
}
#define GUARD(name,kind) void name(uint32_t day,uint32_t offset,uint32_t hour,volatile uint8_t *data,uint32_t timestamp){guard(kind,day,offset,hour,data,timestamp);}
GUARD(r1_hr_cache_future_record_guard,HR)
GUARD(r1_spo2_cache_future_record_guard,SPO2)
GUARD(r1_hrv_cache_future_record_guard,HRV)
GUARD(r1_activity_flash_record_enqueue_plan,ACTIVITY)
#undef GUARD

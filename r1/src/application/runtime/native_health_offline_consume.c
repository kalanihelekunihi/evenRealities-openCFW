/* Reconstructed from locked R1 2.2.6.0009: four offline consumers/empty
 * checks and four builder resets. No second queue storage is introduced. */
#include "native_health_offline_consume.h"
#include "native_health_offline_queue.h"
#include "../board/native_battery_memory.h"
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
struct consumer_view {volatile uint8_t *records;volatile struct r1_offline_cursor *cursor;uint32_t stride,capacity,timestamp_at;const char *ring,*sdk;};
#define CONSUMER(name,stride,capacity,stamp,label) {r1_offline_##name##_records,&r1_offline_##name##_cursor,stride,capacity,stamp,"[RING]" label " offline consumed:%u remain:%u",label " offline consumed:%u remain:%u"}
static const struct consumer_view consumers[4]={CONSUMER(hr,16,24,8,"hr"),CONSUMER(spo2,16,24,8,"spo2"),CONSUMER(hrv,20,24,12,"hrv"),CONSUMER(activity,16,144,8,"activity")};
#undef CONSUMER
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void consume(uint32_t kind,uint32_t cutoff)
{
    const struct consumer_view *queue=&consumers[kind];
    uint8_t consumed=0;
    for(;;){
        uint32_t count=queue->cursor->count;
        if(!count)break;
        uint32_t head=queue->cursor->read;
        volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)
            ((uint32_t)(uintptr_t)queue->records+head*queue->stride);
        if(read32(entry+queue->timestamp_at)>cutoff)break;
        if(kind==2){
            /* Native HRV clears twenty bytes, then reloads cursor state. */
            for(uint32_t i=0;i<20;++i)entry[i]=0;
            head=queue->cursor->read;
            queue->cursor->read=(uint8_t)((head+1u)%queue->capacity);
            count=queue->cursor->count;
        }else{
            write32(entry,0);write32(entry+4,0);write32(entry+8,0);write32(entry+12,0);
            queue->cursor->read=(uint8_t)((head+1u)%queue->capacity);
        }
        consumed=(uint8_t)(consumed+1u);
        queue->cursor->count=(uint8_t)(count-1u);
    }
    if(!consumed)return;
    if(ring_enabled())(void)r1_structured_log_format(0x0c800000,queue->ring,queue->ring,(uint32_t)consumed,(uint32_t)queue->cursor->count);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003,queue->sdk,consumed,queue->cursor->count);
}
#define CONSUME(name,kind) void name(uint32_t cutoff){consume(kind,cutoff);}
CONSUME(r1_heart_rate_offline_queue_consume,0)
CONSUME(r1_spo2_offline_queue_consume,1)
CONSUME(r1_hrv_offline_queue_consume,2)
CONSUME(r1_activity_offline_queue_consume,3)
#undef CONSUME
uint32_t r1_heart_rate_offline_queue_empty(void){return r1_offline_hr_cursor.count==0;}
uint32_t r1_spo2_offline_queue_empty(void){return r1_offline_spo2_cursor.count==0;}
uint32_t r1_hrv_offline_queue_empty(void){return r1_offline_hrv_cursor.count==0;}
uint32_t r1_activity_offline_queue_empty(void){return r1_offline_activity_cursor.count==0;}
static void builder_reset(volatile uint8_t *buffer,uint32_t size,uint32_t header)
{
    if(!buffer)return;
    volatile uint8_t *metadata=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)buffer+header);
    uint32_t offset=read16(metadata);uint8_t flag=metadata[8];uint32_t timestamp=read32(metadata+4);
    for(uint32_t i=0;i<size;++i)buffer[i]=0;
    write16(metadata,offset);write32(metadata+4,timestamp);metadata[8]=flag;
}
void r1_hr_sync_builder_reset(volatile uint8_t *buffer){builder_reset(buffer,148,136);}
void r1_spo2_sync_builder_reset(volatile uint8_t *buffer){builder_reset(buffer,148,136);}
void r1_hrv_sync_builder_reset(volatile uint8_t *buffer){builder_reset(buffer,220,208);}
void r1_activity_day_builder_reset(volatile uint8_t *buffer){builder_reset(buffer,1180,1168);}

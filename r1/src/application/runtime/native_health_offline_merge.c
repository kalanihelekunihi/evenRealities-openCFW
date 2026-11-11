/* Reconstructed locked R1 2.2.6.0009 offline merge roots. Existing queues,
 * builder resets and packet flush providers retain their single owners. */
#include "native_health_offline_merge.h"
#include "native_health_offline_queue.h"
#include "native_health_offline_consume.h"
#include "../board/native_battery_memory.h"
extern uint32_t r1_time_backend_timestamp(void),r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
#include "native_health_packet_flush.h"

struct merge_view {
    volatile uint8_t *records;volatile struct r1_offline_cursor *cursor;
    uint32_t stride,capacity,day_at,timestamp_at,offset_at,slot_at;
    uint32_t count_at,builder_day,builder_offset,builder_timestamp;
    uint32_t (*empty)(void);void (*reset)(volatile uint8_t *),(*flush)(volatile uint8_t *);
    const char *ring,*sdk;
};
#define MERGE_TEXT(name) "[RING]" name "_sync offline skip future entry day:%u ts:%u now:%u",name "_sync offline skip future entry day:%u ts:%u now:%u"
static const struct merge_view views[4]={
 {r1_offline_hr_records,&r1_offline_hr_cursor,16,24,4,8,12,14,120,124,128,132,r1_heart_rate_offline_queue_empty,r1_hr_sync_builder_reset,r1_hr_sync_flush,MERGE_TEXT("hr")},
 {r1_offline_spo2_records,&r1_offline_spo2_cursor,16,24,4,8,12,14,120,124,128,132,r1_spo2_offline_queue_empty,r1_spo2_sync_builder_reset,r1_spo2_sync_flush,MERGE_TEXT("spo2")},
 {r1_offline_hrv_records,&r1_offline_hrv_cursor,20,24,8,12,16,18,192,196,200,204,r1_hrv_offline_queue_empty,r1_hrv_sync_builder_reset,r1_hrv_sync_flush,MERGE_TEXT("hrv")},
 {r1_offline_activity_records,&r1_offline_activity_cursor,16,144,4,8,12,14,1152,1156,1160,1164,r1_activity_offline_queue_empty,r1_activity_day_builder_reset,r1_activity_day_packet_flush,MERGE_TEXT("activity")}
};
#undef MERGE_TEXT
static volatile uint8_t *at(volatile uint8_t *p,uint32_t n){return (volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)p+n);}
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void future_log(const struct merge_view *view,volatile uint8_t *entry,uint32_t now)
{
    if(ring_enabled())(void)r1_structured_log_format(0x0cc00000,view->ring,view->ring,read32(entry+view->day_at),read32(entry+view->timestamp_at),now);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_3(0x001c0003,view->sdk,read32(entry+view->day_at),read32(entry+view->timestamp_at),now);
}
static void short_row(volatile uint8_t *buffer,volatile uint8_t *entry,const struct merge_view *view)
{
    if(!buffer[entry[view->slot_at]]){
        buffer[entry[view->slot_at]]=1;
        at(buffer,24u+(uint32_t)entry[view->slot_at]*4u)[0]=entry[view->slot_at];
        at(buffer,25u+(uint32_t)entry[view->slot_at]*4u)[0]=entry[0];
        at(buffer,26u+(uint32_t)entry[view->slot_at]*4u)[0]=entry[1];
        at(buffer,27u+(uint32_t)entry[view->slot_at]*4u)[0]=entry[2];
        buffer[view->count_at]=(uint8_t)(buffer[view->count_at]+1u);
    }else{
        at(buffer,25u+(uint32_t)entry[view->slot_at]*4u)[0]=entry[0];
        at(buffer,26u+(uint32_t)entry[view->slot_at]*4u)[0]=entry[1];
        at(buffer,27u+(uint32_t)entry[view->slot_at]*4u)[0]=entry[2];
    }
}
static void hrv_row(volatile uint8_t *buffer,volatile uint8_t *entry,const struct merge_view *view)
{
    if(!buffer[entry[18]]){buffer[entry[18]]=1;buffer[192]=(uint8_t)(buffer[192]+1u);}
    at(buffer,24u+(uint32_t)entry[18]*7u)[0]=entry[18];
    write16(at(buffer,25u+(uint32_t)entry[18]*7u),read16(entry));
    write16(at(buffer,27u+(uint32_t)entry[18]*7u),read16(entry+2));
    write16(at(buffer,29u+(uint32_t)entry[18]*7u),read16(entry+4));
    (void)view;
}
static void activity_row(volatile uint8_t *buffer,volatile uint8_t *entry)
{
    uint32_t fresh=!buffer[entry[14]];
    buffer[entry[14]]=1;
    at(buffer,144u+(uint32_t)entry[14]*7u)[0]=entry[14];
    write16(at(buffer,145u+(uint32_t)entry[14]*7u),read16(entry)&0xfffu);
    write16(at(buffer,147u+(uint32_t)entry[14]*7u),(read32(entry)>>12)&0x3ffu);
    write16(at(buffer,149u+(uint32_t)entry[14]*7u),read32(entry)>>22);
    if(fresh)buffer[1152]=(uint8_t)(buffer[1152]+1u);
}
static void merge(uint32_t kind,volatile uint8_t *buffer)
{
    const struct merge_view *view=&views[kind];
    if(!buffer || view->empty())return;
    uint32_t now=r1_time_backend_timestamp(),index=view->cursor->read;
    uint8_t processed=0;
    while(processed<view->cursor->count){
        volatile uint8_t *entry=at(view->records,index*view->stride);
        uint32_t present=kind==2?read16(entry):kind==3?read32(entry):entry[0];
        if(present){
            if(read32(entry+view->timestamp_at)>now || read32(entry+view->day_at)>now)future_log(view,entry,now);
            else{
                uint32_t reset=!buffer[view->count_at];
                if(!reset && (read32(at(buffer,view->builder_day))!=read32(entry+view->day_at) || read16(at(buffer,view->builder_offset))!=read16(entry+view->offset_at))){view->flush(buffer);reset=1;}
                if(reset){
                    view->reset(buffer);
                    write32(at(buffer,view->builder_day),read32(entry+view->day_at));
                    write16(at(buffer,view->builder_offset),read16(entry+view->offset_at));
                }
                if(kind<2)short_row(buffer,entry,view);
                else if(kind==2)hrv_row(buffer,entry,view);
                else activity_row(buffer,entry);
                uint32_t timestamp=read32(entry+view->timestamp_at);
                if(timestamp>read32(at(buffer,view->builder_timestamp)))write32(at(buffer,view->builder_timestamp),timestamp);
            }
        }
        index=(index+1u)%view->capacity;
        processed=(uint8_t)(processed+1u);
    }
}
void r1_heart_rate_offline_queue_merge(volatile uint8_t *buffer){merge(0,buffer);}
void r1_spo2_offline_queue_merge(volatile uint8_t *buffer){merge(1,buffer);}
void r1_hrv_offline_queue_merge(volatile uint8_t *buffer){merge(2,buffer);}
void r1_activity_offline_queue_merge(volatile uint8_t *buffer){merge(3,buffer);}

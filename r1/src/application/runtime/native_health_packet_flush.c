/* Reconstructed locked R1 2.2.6.0009 packet flushes. Event-post and sync-field
 * providers use the shared C interfaces below. */
#include "native_health_packet_flush.h"
#include "native_health_event_post.h"
#include "native_health_offline_consume.h"
#include "../board/native_battery_memory.h"
#include <stddef.h>
extern uint32_t r1_time_backend_timestamp(void),r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern volatile uint8_t *r1_hr_daily_cache_accessor(void),*r1_spo2_daily_cache_accessor(void),*r1_hrv_daily_cache_accessor(void);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t),nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
typedef uint32_t (*post_fn)(const volatile uint8_t *,uint32_t,uint32_t,uint32_t,uint32_t,volatile uint8_t *);

struct flush_view {
    uint32_t slots,row_base,row_size,count_at,day_at,offset_at,max_at,header_at,packet_header,latest_at,latest_timestamp,latest_width;
    volatile uint8_t *(*cache)(void);void (*reset)(volatile uint8_t *);post_fn post;
    const char *future_ring,*future_sdk,*alloc_ring,*alloc_sdk,*ack_ring,*ack_sdk,*failed_ring,*failed_sdk,*sent_ring,*sent_sdk;
};
#define TEXTS(name) "[RING]" name "_sync flush drop future packet day:%u max_ts:%u now:%u",name "_sync flush drop future packet day:%u max_ts:%u now:%u","[RING]" name "_sync flush: alloc pkt failed",name "_sync flush: alloc pkt failed","[RING]" name "_sync flush: alloc ack ctx failed",name "_sync flush: alloc ack ctx failed","[RING]" name "_sync send failed: day:%u count:%u",name "_sync send failed: day:%u count:%u","[RING]" name "_sync sent: day:%u count:%u max_ts:%u",name "_sync sent: day:%u count:%u max_ts:%u"
static const struct flush_view views[4]={
 {24,24,4,120,124,128,132,136,12,75,76,1,r1_hr_daily_cache_accessor,r1_hr_sync_builder_reset,r1_event_post_module1,TEXTS("hr")},
 {24,24,4,120,124,128,132,136,12,75,76,1,r1_spo2_daily_cache_accessor,r1_spo2_sync_builder_reset,r1_event_post_module2,TEXTS("spo2")},
 {24,24,7,192,196,200,204,208,13,147,149,2,r1_hrv_daily_cache_accessor,r1_hrv_sync_builder_reset,r1_event_post_module4,TEXTS("hrv")},
 {144,144,7,1152,1156,1160,1164,1168,7,0,0,0,0,r1_activity_day_builder_reset,r1_event_post_module5,TEXTS("activity")}
};
#undef TEXTS
static volatile uint8_t *at(volatile uint8_t *p,uint32_t n){return (volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)p+n);}
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void allocation_log(const char *ring,const char *sdk)
{
    if(ring_enabled())(void)r1_structured_log_format(0x04000000,ring,ring);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001,sdk);
}
static void flush(uint32_t kind,volatile uint8_t *builder)
{
    const struct flush_view *view=&views[kind];
    /* Stock HR/SpO2 check null; HRV/activity require a mapped builder. */
    if(kind<2 && !builder)return;
    if(!builder[view->count_at])return;
    uint32_t now=r1_time_backend_timestamp();
    if(read32(at(builder,view->max_at))>now || (kind!=3 && read32(at(builder,view->day_at))>now)){
        if(ring_enabled())(void)r1_structured_log_format(0x08c00000,view->future_ring,view->future_ring,read32(at(builder,view->day_at)),read32(at(builder,view->max_at)),now);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_3(0x001c0002,view->future_sdk,read32(at(builder,view->day_at)),read32(at(builder,view->max_at)),now);
        view->reset(builder);return;
    }
    uint32_t length=view->packet_header+(uint32_t)builder[view->count_at]*view->row_size;
    volatile uint8_t *packet=pvPortMalloc(length);
    if(!packet){allocation_log(view->alloc_ring,view->alloc_sdk);return;}
    packet[0]=builder[view->count_at];write16(packet+1,read16(at(builder,view->offset_at)));write32(packet+3,read32(at(builder,view->day_at)));
    if(view->cache){
        volatile uint8_t *cache=view->cache();uint32_t stamp=0;
        if(view->latest_width==1){packet[11]=cache?cache[view->latest_at]:0;}
        else write16(packet+11,cache?read16(cache+view->latest_at):0);
        if(cache)stamp=read32(cache+view->latest_timestamp);
        write32(packet+7,stamp);
    }
    uint32_t out=0;
    for(uint32_t slot=0;slot<view->slots;++slot){
        if(!builder[slot])continue;
        volatile uint8_t *source=at(builder,view->row_base+slot*view->row_size);
        volatile uint8_t *destination=at(packet,view->packet_header+out*view->row_size);
        write32(destination,read32(source));
        if(view->row_size==7){write16(destination+4,read16(source+4));destination[6]=source[6];}
        out=(uint8_t)(out+1u);
    }
    volatile uint8_t *ack=0;
    if(read32(at(builder,view->header_at+4u))){
        ack=pvPortMalloc(8);
        if(ack){ack[0]=builder[view->header_at+8u];write32(ack+4,read32(at(builder,view->max_at)));}
        else allocation_log(view->ack_ring,view->ack_sdk);
    }
    uint32_t block=r1_sync_block_field_get();
    uint32_t posted=view->post(packet,length,block,read16(at(builder,view->header_at)),read32(at(builder,view->header_at+4u)),ack);
    if(!posted){
        if(ring_enabled())(void)r1_structured_log_format(0x04800000,view->failed_ring,view->failed_ring,read32(at(builder,view->day_at)),(uint32_t)builder[view->count_at]);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0001,view->failed_sdk,read32(at(builder,view->day_at)),builder[view->count_at]);
    }else{
        if(ring_enabled())(void)r1_structured_log_format(0x0cc00000,view->sent_ring,view->sent_ring,read32(at(builder,view->day_at)),(uint32_t)builder[view->count_at],read32(at(builder,view->max_at)));
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_3(0x001c0003,view->sent_sdk,read32(at(builder,view->day_at)),builder[view->count_at],read32(at(builder,view->max_at)));
    }
    vPortFree((void *)(uintptr_t)packet);
    /* The optional acknowledgement context is passed onward, not freed here. */
    view->reset(builder);
}
void r1_hr_sync_flush(volatile uint8_t *builder){flush(0,builder);}
void r1_spo2_sync_flush(volatile uint8_t *builder){flush(1,builder);}
void r1_hrv_sync_flush(volatile uint8_t *builder){flush(2,builder);}
void r1_activity_day_packet_flush(volatile uint8_t *builder){flush(3,builder);}

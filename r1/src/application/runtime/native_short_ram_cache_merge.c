/* Stock 0x3fef4/0x440c4/0x40de0 RAM cache merges and their timestamp clamps. */
#include <stdint.h>
#include "../board/native_battery_memory.h"
#include "native_health_offline_consume.h"
#include "native_health_packet_flush.h"
extern uint32_t r1_time_backend_timestamp(void),r1_time_utc_offset_get(void);
extern volatile uint8_t *r1_hr_daily_cache_accessor(void),*r1_spo2_daily_cache_accessor(void),*r1_hrv_daily_cache_accessor(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
struct merge_profile {
    volatile uint8_t *(*cache)(void);
    void (*reset)(volatile uint8_t *),(*flush)(volatile uint8_t *);
    uint16_t cache_offset_at,cache_day_at,count_at,day_at,offset_at,timestamp_at,flag_at;
    uint8_t cache_stride,row_stride,wide;
    const char *window_ring,*window_sdk,*stale_ring,*stale_sdk,*future_ring,*future_sdk;
};
static const struct merge_profile hr={
    r1_hr_daily_cache_accessor,r1_hr_sync_builder_reset,r1_hr_sync_flush,
    72,80,120,124,128,132,144,3,4,0,
    "[RING]hr_sync ram skip window start:%u >= now:%u",
    "hr_sync ram skip window start:%u >= now:%u",
    "[RING]hr_sync ram skip stale day:%u zero:%u",
    "hr_sync ram skip stale day:%u zero:%u",
    "[RING]hr_sync: clamp future ts %u -> %u",
    "hr_sync: clamp future ts %u -> %u"
};
static const struct merge_profile spo2={
    r1_spo2_daily_cache_accessor,r1_spo2_sync_builder_reset,r1_spo2_sync_flush,
    72,80,120,124,128,132,144,3,4,0,
    "[RING]spo2_sync ram skip window start:%u >= now:%u",
    "spo2_sync ram skip window start:%u >= now:%u",
    "[RING]spo2_sync ram skip stale day:%u zero:%u",
    "spo2_sync ram skip stale day:%u zero:%u",
    "[RING]spo2_sync: clamp future ts %u -> %u",
    "spo2_sync: clamp future ts %u -> %u"
};
static const struct merge_profile hrv={
    r1_hrv_daily_cache_accessor,r1_hrv_sync_builder_reset,r1_hrv_sync_flush,
    144,156,192,196,200,204,216,6,7,1,
    "[RING]hrv_sync ram skip window start:%u >= now:%u",
    "hrv_sync ram skip window start:%u >= now:%u",
    "[RING]hrv_sync ram skip stale day:%u zero:%u",
    "hrv_sync ram skip stale day:%u zero:%u",
    "[RING]hrv_sync: clamp future ts %u -> %u",
    "hrv_sync: clamp future ts %u -> %u"
};
static uint32_t ring_enabled(void)
{
    if (r1_structured_log_mode_get() & 1u) return 1u;
    return (r1_structured_log_mode_get() & 4u) != 0u;
}
static void note(const char *ring,const char *sdk,uint32_t first,uint32_t second)
{
    if (ring_enabled())
        (void)r1_structured_log_format(0x0c800000u,ring,ring,first,second);
    if (r1_structured_log_mode_get() & 2u)
        nrf_log_frontend_std_2(0x001c0003u,sdk,first,second);
}
static uint32_t clamp(const struct merge_profile *profile,uint32_t selected,uint32_t now)
{
    if (selected && selected<=now) return selected;
    if (selected>now) note(profile->future_ring,profile->future_sdk,selected,now);
    return now;
}
uint32_t r1_hr_sync_clamp_future_ts(uint32_t selected,uint32_t now)
{return clamp(&hr,selected,now);}
uint32_t r1_spo2_sync_clamp_future_ts(uint32_t selected,uint32_t now)
{return clamp(&spo2,selected,now);}
uint32_t r1_hrv_sync_clamp_future_ts(uint32_t selected,uint32_t now)
{return clamp(&hrv,selected,now);}
static void merge(const struct merge_profile *profile,volatile uint8_t *builder,
                  uint32_t start,uint32_t end)
{
    if (!builder || !start) return;
    uint32_t now=r1_time_backend_timestamp();
    if (end>=now) {
        note(profile->window_ring,profile->window_sdk,end,now);
        return;
    }
    volatile uint8_t *cache=profile->cache();
    if (!cache) return;
    write32(cache+profile->cache_day_at,start);
    write16(cache+profile->cache_offset_at,r1_time_utc_offset_get());
    if (read32(cache+profile->cache_day_at)<start) {
        if (ring_enabled())
            (void)r1_structured_log_format(0x0c800000u,profile->stale_ring,
                                           profile->stale_ring,read32(cache+profile->cache_day_at),start);
        if (r1_structured_log_mode_get() & 2u)
            nrf_log_frontend_std_2(0x001c0003u,profile->stale_sdk,
                                   read32(cache+profile->cache_day_at),start);
        return;
    }
    uint8_t old_flag=builder[profile->flag_at];
    builder[profile->flag_at]=2;
    profile->reset(builder);
    uint32_t day=read32(cache+profile->cache_day_at);
    write32(builder+profile->day_at,day);
    write16(builder+profile->offset_at,read16(cache+profile->cache_offset_at));
    uint8_t last_slot=(uint8_t)((now-day)/3600u);
    if (last_slot>=24) last_slot=23;
    uint32_t latest=0;
    for (uint32_t slot=0;slot<24;slot++) {
        volatile uint8_t *entry=cache+slot*profile->cache_stride;
        if (!(profile->wide?read16(entry):entry[0])) continue;
        uint32_t timestamp=day+slot*3600u;
        if (slot!=last_slot && (timestamp<end || timestamp>now)) continue;
        builder[slot]=1;
        volatile uint8_t *output=builder+24u+slot*profile->row_stride;
        output[0]=(uint8_t)slot;
        if (profile->wide) {
            write16(output+1,read16(entry));
            write16(output+3,read16(entry+2));
            write16(output+5,read16(entry+4));
        } else {
            output[1]=entry[0];output[2]=entry[1];output[3]=entry[2];
        }
        builder[profile->count_at]=(uint8_t)(builder[profile->count_at]+1u);
        if (timestamp>latest) latest=timestamp;
    }
    if (builder[profile->count_at]) {
        write32(builder+profile->timestamp_at,clamp(profile,latest,now));
        profile->flush(builder);
    }
    builder[profile->flag_at]=old_flag;
}
void r1_health_sync_provider_0003fef4(volatile uint8_t *builder,uint32_t start,uint32_t end)
{merge(&hr,builder,start,end);}
void r1_health_sync_provider_000440c4(volatile uint8_t *builder,uint32_t start,uint32_t end)
{merge(&spo2,builder,start,end);}
void r1_health_sync_provider_00040de0(volatile uint8_t *builder,uint32_t start,uint32_t end)
{merge(&hrv,builder,start,end);}

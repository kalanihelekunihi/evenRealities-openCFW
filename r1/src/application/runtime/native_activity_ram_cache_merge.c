/* Activity RAM cache merge and its local helpers, reconstructed from R1 stock. */
#include <stdint.h>
#include "../board/native_battery_memory.h"
#include "native_activity_accumulator.h"
#include "native_health_offline_consume.h"
#include "native_health_packet_flush.h"
extern uint32_t r1_time_backend_timestamp(void),r1_time_utc_offset_get(void);
extern uint32_t r1_activity_mode_byte_get(void),r1_health_mode_is_2(void);
extern volatile uint8_t *r1_activity_daily_cache_accessor(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static const char window_ring[]="[RING]activity_sync ram skip window start:%u >= now:%u";
static const char window_sdk[]="activity_sync ram skip window start:%u >= now:%u";
static const char stale_ring[]="[RING]activity_sync ram skip stale day:%u zero:%u";
static const char stale_sdk[]="activity_sync ram skip stale day:%u zero:%u";
static const char future_ring[]="[RING]activity_sync: clamp future ts %u -> %u";
static const char future_sdk[]="activity_sync: clamp future ts %u -> %u";
static uint32_t ring_enabled(void)
{
    if (r1_structured_log_mode_get() & 1u) return 1;
    return (r1_structured_log_mode_get() & 4u)!=0u;
}
static void note(const char *ring,const char *sdk,uint32_t a,uint32_t b)
{
    if (ring_enabled())(void)r1_structured_log_format(0x0c800000u,ring,ring,a,b);
    if (r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003u,sdk,a,b);
}
uint32_t r1_activity_acknowledgement_timestamp_clamp(uint32_t selected,uint32_t now)
{
    if (selected && selected<=now)return selected;
    if (selected>now)note(future_ring,future_sdk,selected,now);
    return now;
}
void r1_activity_pending_delta_accessor(volatile uint8_t *output)
{
    if (!output)return;
    write32(output,0);write32(output+4,0);write32(output+8,0);
    if (r1_activity_mode_byte_get()==1u || !r1_health_mode_is_2())return;
    volatile uint8_t *state=r1_activity_accumulator_state;
    uint32_t current=read32(state+16),baseline=read32(state+8);
    uint16_t current1=read16(state+22),baseline1=read16(state+14);
    uint16_t current2=read16(state+20),baseline2=read16(state+12);
    if (current<baseline || current1<baseline1 || current2<baseline2)return;
    write16(output+4,current-baseline);
    write16(output+2,current1-baseline1);
    write16(output,current2-baseline2);
}
void r1_health_sync_provider_0003c304(volatile uint8_t *builder,uint32_t start,uint32_t end)
{
    if (!builder || !start)return;
    uint32_t now=r1_time_backend_timestamp();
    if (end>=now) {note(window_ring,window_sdk,end,now);return;}
    volatile uint8_t *cache=r1_activity_daily_cache_accessor();
    if (!cache)return;
    write32(cache+580,start);
    write16(cache+576,r1_time_utc_offset_get());
    if (read32(cache+580)<start) {
        if (ring_enabled())(void)r1_structured_log_format(0x0c800000u,stale_ring,stale_ring,read32(cache+580),start);
        if (r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003u,stale_sdk,read32(cache+580),start);
        return;
    }
    uint8_t old_flag=builder[1176];builder[1176]=2;
    r1_activity_day_builder_reset(builder);
    uint32_t day=read32(cache+580);
    write32(builder+1156,day);write16(builder+1160,read16(cache+576));
    uint16_t last_slot=(uint16_t)((now-day)/600u);if (last_slot>=144)last_slot=143;
    uint8_t pending[12]={0};r1_activity_pending_delta_accessor(pending);
    uint32_t latest=0;
    for (uint16_t slot=0;slot<144;slot++) {
        uint32_t packed=read32(cache+4u*slot);
        uint32_t a=packed&0xfffu,b=(packed>>12)&0x3ffu,c=packed>>22;
        if (slot==last_slot) {
            a+=read16(pending+4);b+=read16(pending+2);c+=read16(pending);
        }
        if (!(a|b|c))continue;
        uint32_t timestamp=day+(uint32_t)slot*600u;
        if (slot!=last_slot && (timestamp<end || timestamp>now))continue;
        builder[slot]=1;
        volatile uint8_t *row=builder+144u+(uint32_t)slot*7u;
        row[0]=(uint8_t)slot;
        write16(row+1,a);write16(row+3,b);write16(row+5,c);
        builder[1152]=(uint8_t)(builder[1152]+1u);
        if (timestamp>latest)latest=timestamp;
    }
    if (builder[1152]) {
        write32(builder+1164,r1_activity_acknowledgement_timestamp_clamp(latest,now));
        r1_activity_day_packet_flush(builder);
    }
    builder[1176]=old_flag;
}

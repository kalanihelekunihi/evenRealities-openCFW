/* Diagnostic daily-cache fixture at stock 0x8b378. It injects one triple for
 * each admitted hour, then reports the selected cache through the normal
 * notification path. The hour indices retain the stock byte truncation. */
#include <stdint.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_time_backend_timestamp(void),r1_time_local_day_start(void);
extern uint32_t r1_native_rand(void);
extern volatile uint8_t *r1_hr_daily_cache_accessor(void);
extern volatile uint8_t *r1_spo2_daily_cache_accessor(void);
extern void r1_health_fixture_notify_hr(void),r1_health_fixture_notify_spo2(void);
extern void r1_health_fixture_notify_temperature(void);
extern uint8_t r1_health_storage_temperature_prefix[80];
extern volatile uint32_t r1_daily_hr_timestamp,r1_daily_spo2_timestamp;
extern volatile uint32_t r1_daily_temperature_timestamp;
volatile uint8_t *r1_temperature_daily_cache_accessor(void)
{ return r1_health_storage_temperature_prefix; }

static int ring_enabled(void)
{
    return (r1_structured_log_mode_get()&1u) ||
           (r1_structured_log_mode_get()&4u);
}
static int sdk_enabled(void)
{ return (r1_structured_log_mode_get()&2u)!=0; }
static volatile uint8_t *cache_for_kind(uint32_t kind)
{
    if(kind==0u)return r1_hr_daily_cache_accessor();
    if(kind==1u)return r1_spo2_daily_cache_accessor();
    return r1_temperature_daily_cache_accessor();
}
static uint8_t random_byte(uint32_t divisor,uint32_t offset)
{
    int32_t value=(int32_t)r1_native_rand();
    return (uint8_t)(value%(int32_t)divisor+(int32_t)offset);
}
static void cache_missing(uint32_t kind)
{
    const char *ring=kind==0u?"[RING]hr_daily is NULL":
                     kind==1u?"[RING]spo2_daily is NULL":
                              "[RING]temp_daily is NULL";
    const char *sdk=kind==0u?"hr_daily is NULL":
                    kind==1u?"spo2_daily is NULL":
                             "temp_daily is NULL";
    if(ring_enabled())(void)r1_structured_log_format(0x0c000000u,ring,ring);
    if(sdk_enabled())nrf_log_frontend_std_0(0x001c0003u,sdk);
}
void r1_event_service_0008b378(const void *payload)
{
    const volatile uint8_t *request=payload;
    if(!request) {
        const char *ring="[RING]health_daily_test is NULL";
        if(ring_enabled())(void)r1_structured_log_format(0x0c000000u,ring,ring);
        if(sdk_enabled())nrf_log_frontend_std_0(0x001c0003u,
            "health_daily_test is NULL");
        return;
    }
    uint32_t kind=request[0];
    if(kind>2u) {
        const char *ring="[RING]health_daily_test->type = %d";
        if(ring_enabled())(void)r1_structured_log_format(0x0c400000u,ring,ring,kind);
        if(sdk_enabled())nrf_log_frontend_std_1(0x001c0003u,
            "health_daily_test->type = %d",kind);
        return;
    }
    uint32_t start=read32(request+1),end=read32(request+5);
    uint32_t now=r1_time_backend_timestamp();
    uint32_t day=r1_time_local_day_start();
    const char *ring="[RING]now_ts = %d, now_ts_zero = %d, start_ts = %d, end_ts = %d";
    if(ring_enabled())(void)r1_structured_log_format(0x0d000000u,ring,ring,
        now,day,start,end);
    if(sdk_enabled())nrf_log_frontend_std_4(0x001c0003u,
        "now_ts = %d, now_ts_zero = %d, start_ts = %d, end_ts = %d",
        now,day,start,end);
    if(end<now-30u || start<day)return;
    uint32_t start_hour=start-start%3600u;
    uint32_t end_hour=end-end%3600u;
    uint32_t count=(uint8_t)((end_hour-start_hour)/3600u);
    uint32_t first=(uint8_t)((start_hour-day)/3600u);
    if(count>23u)count=23u;
    if(first>23u)first=23u;
    uint32_t limit=first+count+1u;
    for(uint32_t i=first;i<limit;i=(uint8_t)(i+1u)) {
        volatile uint8_t *cache=cache_for_kind(kind);
        if(!cache){cache_missing(kind);return;}
        uint32_t position=3u*i;
        if(kind==0u) {
            cache[position]=random_byte(40u,60u);
            cache[position+1u]=random_byte(40u,100u);
            cache[position+2u]=random_byte(15u,45u);
        } else if(kind==1u) {
            cache[position]=random_byte(3u,97u);
            cache[position+1u]=random_byte(7u,90u);
            cache[position+2u]=random_byte(5u,85u);
        } else {
            cache[position]=random_byte(30u,100u);
            cache[position+1u]=random_byte(40u,130u);
            cache[position+2u]=random_byte(50u,50u);
        }
        if(i==first) {
            cache[75]=(uint8_t)(kind==0u?85u:kind==1u?98u:110u);
            write32(cache+76,now);
            /* The 80-byte cache prefix is followed by its source-owned
             * timestamp cell in the contiguous health-cache section. */
            if(kind==0u)r1_daily_hr_timestamp=day;
            else if(kind==1u)r1_daily_spo2_timestamp=day;
            else r1_daily_temperature_timestamp=day;
        }
    }
    if(kind==0u)r1_health_fixture_notify_hr();
    else if(kind==1u)r1_health_fixture_notify_spo2();
    else r1_health_fixture_notify_temperature();
}

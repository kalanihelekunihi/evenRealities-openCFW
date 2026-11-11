/* Daily cache notification fixtures reconstructed from the three native log
 * loops. The cache layout is byte-addressed because its sample triples and
 * metadata are consumed at distinct widths by the protocol logging API. */
#include <stdint.h>
#include "../board/native_battery_memory.h"

extern const volatile uint8_t *r1_hr_daily_cache_accessor(void);
extern const volatile uint8_t *r1_spo2_daily_cache_accessor(void);
extern const volatile uint8_t *r1_temperature_daily_cache_accessor(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);

static void notify_cache(const volatile uint8_t *cache, uint32_t offset,
                         const char *ring_header,const char *sdk_header)
{
    if (!cache) return;
    if ((r1_structured_log_mode_get()&1u) ||
        (r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c800000u,ring_header,ring_header,
            (uint32_t)cache[75]+offset,read32(cache+76));
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x001c0003u,sdk_header,
            (uint32_t)cache[75]+offset,read32(cache+76));
    for(uint32_t i=0;i<24u;i++) {
        const volatile uint8_t *sample=cache+3u*i;
        if ((r1_structured_log_mode_get()&1u) ||
            (r1_structured_log_mode_get()&4u)) {
            uint32_t first=(uint32_t)sample[0]+offset;
            uint32_t second=(uint32_t)sample[1]+offset;
            uint32_t third=(uint32_t)sample[2]+offset;
            (void)r1_structured_log_format(0x0d000000u,
                "[RING][%d],%d, %d-%d","[RING][%d],%d, %d-%d",
                i,first,third,second);
        }
        if (r1_structured_log_mode_get()&2u) {
            uint32_t first=(uint32_t)sample[0]+offset;
            uint32_t second=(uint32_t)sample[1]+offset;
            uint32_t third=(uint32_t)sample[2]+offset;
            nrf_log_frontend_std_4(0x001c0003u,"[%d],%d, %d-%d",
                i,first,third,second);
        }
    }
}

void r1_health_fixture_notify_hr(void)
{
    notify_cache(r1_hr_daily_cache_accessor(),0u,
        "[RING]last_hr: %d, timestamp: %d",
        "last_hr: %d, timestamp: %d");
}
void r1_health_fixture_notify_spo2(void)
{
    notify_cache(r1_spo2_daily_cache_accessor(),0u,
        "[RING]last_spo2: %d, timestamp: %d",
        "last_spo2: %d, timestamp: %d");
}
void r1_health_fixture_notify_temperature(void)
{
    notify_cache(r1_temperature_daily_cache_accessor(),250u,
        "[RING]last_temp: %d, timestamp: %d",
        "last_temp: %d, timestamp: %d");
}

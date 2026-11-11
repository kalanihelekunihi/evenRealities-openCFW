/* Native sleep-report notification at 0x8dd90. Logging reads the live record
 * separately for each sink; the event payload length includes the stage bytes. */
#include <stdint.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern void r1_event_service_0008dc94(const volatile uint8_t *);
const char r1_sleep_report_components_text[]
    __attribute__((section(".r1.sleep.report.components"),aligned(1)))=
    "[RING]wake_ratio:%d, rem_ratio:%d, light_ratio:%d, deep_ratio:%d";

static int ring_enabled(void)
{
    return (r1_structured_log_mode_get()&1u) ||
           (r1_structured_log_mode_get()&4u);
}
static int sdk_enabled(void)
{ return (r1_structured_log_mode_get()&2u)!=0; }

void r1_event_service_0008dd90(const volatile uint8_t *record)
{
    if (ring_enabled())
        (void)r1_structured_log_format(0x0d000000u,
            "[RING]sleep %d-%d, type:%d, numStages:%d",
            "[RING]sleep %d-%d, type:%d, numStages:%d",
            read32(record+12),read32(record+16),record[0],read16(record+30));
    if (sdk_enabled())
        nrf_log_frontend_std_4(0x001c0003u,
            "sleep %d-%d, type:%d, numStages:%d",
            read32(record+12),read32(record+16),record[0],read16(record+30));
    if (ring_enabled())
        (void)r1_structured_log_format(0x0d000000u,
            "[RING]efficiency:%d, score:%d, total_time:%d, body_temp:%d",
            "[RING]efficiency:%d, score:%d, total_time:%d, body_temp:%d",
            record[1],record[2],read16(record+20),read16(record+8));
    if (sdk_enabled())
        nrf_log_frontend_std_4(0x001c0003u,
            "efficiency:%d, score:%d, total_time:%d, body_temp:%d",
            record[1],record[2],read16(record+20),read16(record+8));
    if (ring_enabled())
        (void)r1_structured_log_format(0x0d000000u,
            r1_sleep_report_components_text,r1_sleep_report_components_text,
            record[4],record[5],record[6],record[7]);
    if (sdk_enabled())
        nrf_log_frontend_std_4(0x001c0003u,
            "wake_ratio:%d, rem_ratio:%d, light_ratio:%d, deep_ratio:%d",
            record[4],record[5],record[6],record[7]);
    if (ring_enabled())
        (void)r1_structured_log_format(0x0d000000u,
            "[RING]wake_time:%d, rem_time:%d, light_time:%d, deep_time:%d",
            "[RING]wake_time:%d, rem_time:%d, light_time:%d, deep_time:%d",
            read16(record+22),read16(record+24),read16(record+26),read16(record+28));
    if (sdk_enabled())
        nrf_log_frontend_std_4(0x001c0003u,
            "wake_time:%d, rem_time:%d, light_time:%d, deep_time:%d",
            read16(record+22),read16(record+24),read16(record+26),read16(record+28));
    uint32_t duration=read32(record+16)-read32(record+12);
    if(duration<3600u) {
        if (ring_enabled())
            (void)r1_structured_log_format(0x0c000000u,
                "[RING]sleep time is small than 1 hours",
                "[RING]sleep time is small than 1 hours");
        if (sdk_enabled())
            nrf_log_frontend_std_0(0x001c0003u,
                "sleep time is small than 1 hours");
        return;
    }
    uint32_t length=(uint16_t)(read16(record+30)+32u);
    if(r1_event_publish(8192,(const void *)record,length)) return;
    if (ring_enabled())
        (void)r1_structured_log_format(0x04000000u,
            "[RING]sleep storage msg send fail",
            "[RING]sleep storage msg send fail");
    if (sdk_enabled())
        nrf_log_frontend_std_0(0x001c0001u,
            "sleep storage msg send fail");
    r1_event_service_0008dc94(record);
}

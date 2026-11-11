/* Stock R1 0x5b39c: walk the eight sleep-record headers in each FAL sector. */
#include <stddef.h>
#include <stdint.h>
#include "../board/native_battery_memory.h"
#include "../../include/r1_stock_checksums.h"

struct r1_sleep_sync_report;
struct r1_sleep_sync_request;
typedef uint32_t (*r1_sleep_report_callback)(const uint8_t *,
        const struct r1_sleep_sync_report *, uint32_t,
        const struct r1_sleep_sync_request *);

extern uint32_t r1_sleep_sync_context_prefix[3];
extern uint32_t r1_sleep_sector_count(void);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);

static uint32_t ring_enabled(void)
{ return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u); }

static void error_no_address(const char *ring,const char *sdk)
{
    if (ring_enabled()) (void)r1_structured_log_format(0x04000000u,ring,ring);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0001u,sdk);
}

static void error_at_address(const char *ring,const char *sdk,uint32_t address)
{
    if (ring_enabled())
        (void)r1_structured_log_format(0x04400000u,ring,ring,address);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0001u,sdk,address);
}

static void sleep_read(uint32_t address,void *destination,uint32_t length)
{
    const volatile uint8_t *device=(const volatile uint8_t *)(uintptr_t)
        ((volatile uint32_t *)r1_sleep_sync_context_prefix)[2];
    int (*read)(long,void *,size_t)=(void *)(uintptr_t)read32(device+40);
    (void)read((long)address,destination,length);
}

__attribute__((section(".text.r1_health_sync_provider_0005b39c")))
uint32_t r1_health_sync_provider_0005b39c(uint32_t skip_synced,
        r1_sleep_report_callback callback,
        const struct r1_sleep_sync_request *request)
{
    if (!callback) {
        error_no_address("[RING]sleep storage iter callback is null",
                         "sleep storage iter callback is null");
        return 0;
    }

    const uint32_t sector_count=r1_sleep_sector_count();
    uint32_t header[6]={0};
    uint8_t *data=pvPortMalloc(232);
    if (!data) {
        error_no_address("[RING]sleep storage iter malloc fail",
                         "sleep storage iter malloc fail");
        return 0;
    }

    uint32_t status=1;
    uint32_t last_data_address=0;
    for (uint8_t sector=0;sector<sector_count;sector=(uint8_t)(sector+1u)) {
        const volatile uint8_t *partition=(const volatile uint8_t *)(uintptr_t)
            ((volatile uint32_t *)r1_sleep_sync_context_prefix)[1];
        const uint32_t sector_base=read32(partition+52)+((uint32_t)sector<<12);
        const uint32_t header_base=sector_base+16u;
        for (uint8_t slot=0;slot<8;slot++) {
            const uint32_t header_address=header_base+(uint32_t)slot*24u;
            sleep_read(header_address,header,sizeof(header));
            if (header[2]==UINT32_MAX || header[3]==UINT32_MAX) break;
            if (skip_synced && header[5]==UINT32_C(0x11223344)) continue;

            const uint32_t length=read16((const volatile uint8_t *)header);
            if (length>232u) {
                error_at_address(
                    "[RING]sleep storage iter data size too large, offset: %08X",
                    "sleep storage iter data size too large, offset: %08X",
                    last_data_address);
                continue;
            }

            last_data_address=sector_base+
                read16((const volatile uint8_t *)header+2);
            sleep_read(last_data_address,data,length);
            if (r1_stock_crc16_modbus(data,length)!=
                read16((const volatile uint8_t *)header+18)) {
                error_at_address("[RING]sleep storage iter crc error, offset: %08X",
                                 "sleep storage iter crc error, offset: %08X",
                                 last_data_address);
                (void)r1_event_publish(0x2002u,NULL,0);
                status=0;
                goto done;
            }

            uint32_t source[2]={header[5]==UINT32_C(0x11223344),header_address};
            if (!callback((const uint8_t *)source,
                          (const struct r1_sleep_sync_report *)data,
                          length,request)) goto done;
        }
    }
done:
    vPortFree(data);
    return status;
}

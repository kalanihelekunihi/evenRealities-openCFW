/* Stock 0x592bc: read the EP/log/cache/crash virtual export file. */
#include "native_export_snapshot.h"
#include "native_log_bin.h"
#include "native_ep_storage.h"
#include "native_crash_recovery.h"
#include <stddef.h>
#include <stdint.h>
#include <string.h>

volatile int8_t r1_log_export_start_sector
    __attribute__((section(".r1.log.export.start.sector")))=-1;
volatile uint16_t r1_log_export_cache_length
    __attribute__((section(".r1.log.export.cache.length"),aligned(2)))=0;

extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern uint32_t r1_structured_log_cache_read(void *,uint16_t *,uint32_t);
extern const char *r1_retained_log_text_get(void);
extern uint32_t r1_retained_log_text_length(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);

static uint32_t minimum(uint32_t first,uint32_t second)
{ return first<second ? first:second; }

static void error0(const char *ring,const char *plain)
{
    if (r1_structured_log_mode_get()&5u)
        (void)r1_structured_log_format(0x04000000u,ring,ring);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0001u,plain);
}

uint32_t r1_log_export_snapshot_read(uint32_t offset,void *destination,
                                      uint32_t bytes)
{
    if (!destination || !bytes) {
        error0("[RING]log data is null","log data is null");
        return 0;
    }
    uint32_t ep_length=r1_ep_export_length();
    uint32_t cache_length=r1_log_export_cache_length;
    uint32_t log_length=r1_log_export_file.length-cache_length-ep_length;
    uint32_t crash_length=0;
    if (r1_health_crash_record_magic_probe())
        crash_length=r1_retained_log_text_length();
    log_length-=crash_length;
    uint8_t *out=destination;
    while (bytes) {
        if (offset<ep_length) {
            uint32_t chunk=minimum(bytes,ep_length-offset);
            if (!r1_ep_export_read(offset,out,chunk)) {
                if (r1_structured_log_mode_get()&5u)
                    (void)r1_structured_log_format(0x04800000u,
                        "[RING]ep export read fail, off:%08X len:%d",
                        "[RING]ep export read fail, off:%08X len:%d",offset,chunk);
                if (r1_structured_log_mode_get()&2u)
                    nrf_log_frontend_std_2(0x001c0001u,
                        "ep export read fail, off:%08X len:%d",offset,chunk);
                return 0;
            }
            out+=chunk;offset+=chunk;bytes-=chunk;
        } else {
            uint32_t position=offset-ep_length;
            if (position<log_length) {
                int32_t first=r1_log_export_start_sector;
                if (first==-1) {
                    error0("[RING]log sector start not init",
                           "log sector start not init");
                    return 0;
                }
                uint32_t count=r1_log_bin_sector_count();
                int32_t serial=(int32_t)(position>>12)+first;
                uint32_t sector=(uint8_t)(count ? serial%(int32_t)count:serial);
                uint32_t address=r1_log_bin_partition->base+
                    ((sector<<12)|(position&4095u));
                uint32_t chunk=minimum(bytes,log_length-position);
                (void)r1_log_bin_flash->read(address,out,chunk);
                out+=chunk;offset+=chunk;bytes-=chunk;
                continue;
            }
            position-=log_length;
            if (position<cache_length) {
                uint32_t chunk=minimum(bytes,cache_length-position);
                uint8_t *scratch=pvPortMalloc(cache_length);
                if (!scratch) {
                    error0("[RING]malloc temp cache buffer failed",
                           "malloc temp cache buffer failed");
                    return 0;
                }
                uint16_t count=(uint16_t)cache_length;
                (void)r1_structured_log_cache_read(scratch,&count,0);
                memcpy(out,scratch+position,chunk);
                vPortFree(scratch);
                out+=chunk;offset+=chunk;bytes-=chunk;
                continue;
            }
            position-=cache_length;
            if (crash_length && position<crash_length) {
                uint32_t chunk=minimum(bytes,crash_length-position);
                memcpy(out,r1_retained_log_text_get()+position,chunk);
                out+=chunk;offset+=chunk;bytes-=chunk;
                continue;
            }
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_1(0x001c0001u,
                    "log read offset out of range: %08X",offset);
            return 0;
        }
    }
    return 1;
}

/* Stock 0x58de4: freeze the virtual log file's length, CRC and sector order. */
#include "native_export_snapshot.h"
#include "native_log_bin.h"
#include "native_ep_storage.h"
#include "native_crash_recovery.h"
#include "../../include/r1_stock_checksums.h"
#include <stddef.h>
#include <stdint.h>

extern void r1_log_bin_initialize(void);
extern void r1_manager_logging_start_91504(void);
extern uint32_t r1_ep_export_pause_begin(void);
extern uint32_t r1_log_export_snapshot_start(void);
extern uint32_t r1_log_export_snapshot_finish(void);
extern volatile uint8_t r1_structured_log_export_state;
extern uint32_t r1_structured_log_cache_count(void);
extern uint32_t r1_structured_log_cache_read(void *,uint16_t *,uint32_t);
extern const char *r1_retained_log_text_get(void);
extern uint32_t r1_retained_log_text_length(void);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);

/* The stock RW initializer has eight 32-bit words at 0x20006918. */
struct r1_export_file_descriptor r1_log_export_file={
    1,0,0,r1_log_export_snapshot_prepare,r1_log_export_snapshot_read,
    r1_log_export_snapshot_start,r1_log_export_snapshot_finish,
    (const uint8_t *)&r1_log_export_start_sector
};
#if UINTPTR_MAX==UINT32_MAX
_Static_assert(sizeof(struct r1_export_file_descriptor)==32,
               "stock export descriptor size");
#endif

static uint32_t marker_at(uint32_t sector)
{
    uint32_t marker=0;
    uint32_t address=r1_log_bin_partition->base+4u+(sector<<12);
    (void)r1_log_bin_flash->read(address,&marker,4);
    return marker;
}

static uint32_t fail(void)
{
    (void)r1_log_export_snapshot_finish();
    return 0;
}

uint32_t r1_log_export_snapshot_prepare(uint32_t *information)
{
    if (!information) return 0;
    if (!r1_log_bin_initialized) r1_log_bin_initialize();
    r1_manager_logging_start_91504();
    r1_structured_log_export_state=1;
    (void)r1_ep_export_pause_begin();
    uint32_t sectors=r1_log_bin_sector_count();
    uint32_t populated=0;
    for (uint32_t sector=0;sector<sectors;sector=(uint8_t)(sector+1)) {
        if (marker_at(sector)!=UINT32_MAX) populated=(uint8_t)(populated+1);
    }
    if (!populated) {
        if (!r1_ep_export_has_records()) return fail();
        nrf_log_frontend_std_0(0x001c0003u,
            "[ep] no valid log sector, export ep-only (+cache/crash if any)");
    }
    information[0]=r1_ep_export_length()+(populated<<12);
    uint8_t *scratch=pvPortMalloc(4096);
    if (!scratch) return fail();
    uint32_t crc=0;
    r1_ep_export_crc(&crc);

    /* The sector after the first erased sector is the oldest retained log.
     * Stock probes markers again after the initial count; retain that order. */
    uint32_t first=0;
    for (uint32_t sector=0;sector<sectors;sector=(uint8_t)(sector+1)) {
        if (marker_at(sector)==UINT32_MAX) {
            first=sectors ? (sector+1u)%sectors:sector+1u;
            break;
        }
    }
    for (uint32_t cursor=first;cursor<first+sectors;cursor=(uint8_t)(cursor+1)) {
        uint32_t sector=sectors ? cursor%sectors:cursor;
        if (marker_at(sector)==UINT32_MAX) continue;
        if (r1_log_export_start_sector==-1)
            r1_log_export_start_sector=(int8_t)sector;
        uint32_t address=r1_log_bin_partition->base+(sector<<12);
        (void)r1_log_bin_flash->read(address,scratch,4096);
        r1_stock_crc32_update(scratch,4096,&crc);
    }
    vPortFree(scratch);

    uint16_t cache_length=(uint16_t)r1_structured_log_cache_count();
    r1_log_export_cache_length=cache_length;
    if (cache_length) {
        scratch=pvPortMalloc(cache_length);
        if (scratch) {
            uint16_t requested=cache_length;
            (void)r1_structured_log_cache_read(scratch,&requested,0);
            r1_stock_crc32_update(scratch,cache_length,&crc);
            vPortFree(scratch);
        } else {
            cache_length=0;
            r1_log_export_cache_length=0;
        }
    }
    information[0]+=cache_length;
    information[1]=crc;
    if (r1_health_crash_record_magic_probe()) {
        uint32_t crash_length=r1_retained_log_text_length();
        r1_stock_crc32_update((const uint8_t *)r1_retained_log_text_get(),
                              crash_length,&crc);
        information[0]+=crash_length;
        information[1]=crc;
    }
    r1_log_export_file.length=information[0];
    r1_log_export_file.crc=information[1];
    nrf_log_frontend_std_3(0x001c0003u,
        "log flash get file info: %d, %08X, %d",
        information[0],information[1],cache_length);
    return 1;
}

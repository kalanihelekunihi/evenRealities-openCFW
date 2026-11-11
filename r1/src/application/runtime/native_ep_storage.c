#include "native_ep_storage.h"
#include "../../include/r1_stock_checksums.h"
#include <stddef.h>
volatile uint8_t r1_ep_storage_initialized __attribute__((section(".r1.ep.storage.initialized")))=0;
struct r1_log_partition *volatile r1_ep_storage_partition __attribute__((section(".r1.ep.storage.partition"),aligned(4)))=0;
struct r1_log_flash *volatile r1_ep_storage_flash __attribute__((section(".r1.ep.storage.flash"),aligned(4)))=0;
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern uint32_t r1_ep_storage_initialize(void);
static void range_error(uint32_t offset,uint32_t bytes,const char *ring,const char *plain)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04800000,ring,ring,offset,bytes);
    if (r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0001,plain,offset,bytes);
}
uint32_t r1_ep_record_read(uint32_t offset,void *data,uint32_t bytes)
{
    /* Preserve stock's bitwise pointer admission for noncanonical flag bytes. */
    if (!((0u-r1_ep_storage_initialized)&(uint32_t)(uintptr_t)data) || !bytes) return 0;
    if (offset+bytes>8192u) {
        range_error(offset,bytes,"[RING][ep] read out of range: off=%d len=%d","[ep] read out of range: off=%d len=%d");return 0;
    }
    uint32_t address=r1_ep_storage_partition->base+offset;
    (void)r1_ep_storage_flash->read(address,data,bytes);
    return 1;
}
uint32_t r1_ep_record_write(uint32_t offset,const void *data,uint32_t bytes)
{
    if (!((0u-r1_ep_storage_initialized)&(uint32_t)(uintptr_t)data) || !bytes) return 0;
    if (offset+bytes>8192u) {
        range_error(offset,bytes,"[RING][ep] write out of range: off=%d len=%d","[ep] write out of range: off=%d len=%d");return 0;
    }
    uint32_t address=r1_ep_storage_partition->base+offset;
    (void)r1_ep_storage_flash->write(address,data,bytes);
    return 1;
}
uint32_t r1_ep_sector_erase(uint32_t sector)
{
    if (!r1_ep_storage_initialized || sector>=2) return 0;
    uint32_t address=r1_ep_storage_partition->base+(sector<<12);
    (void)r1_ep_storage_flash->erase(address,4096);
    return 1;
}

/* Stock 0x5e060: the virtual-file reader ensures EP storage is ready
 * before forwarding the requested byte range to the bounded read owner. */
uint32_t r1_ep_export_read(uint32_t offset,void *destination,uint32_t bytes)
{
    if (!r1_ep_storage_initialized && !r1_ep_storage_initialize()) return 0;
    return r1_ep_record_read(offset,destination,bytes);
}

/* Stock 0x5dff8 admits an EP-only export when any persisted eight-byte
 * record in either sector has low tag nibble 10. */
uint32_t r1_ep_export_has_records(void)
{
    if (!r1_ep_storage_initialized && !r1_ep_storage_initialize()) return 0;
    uint8_t *scratch=pvPortMalloc(4096);
    if (!scratch) return 0;
    uint32_t found=0;
    for (uint32_t sector=0;sector<2 && !found;sector++) {
        if (!r1_ep_record_read(sector<<12,scratch,4096)) continue;
        for (uint32_t record=0;record<512;record++) {
            if ((scratch[record<<3]&15u)==10u) {found=1;break;}
        }
    }
    vPortFree(scratch);
    return found;
}

/* Stock 0x5e086: fold every readable EP sector into the caller's CRC state.
 * Read failures are skipped; the 4 KiB scratch allocation is always freed. */
void r1_ep_export_crc(uint32_t *state)
{
    if (!state) return;
    if (!r1_ep_storage_initialized && !r1_ep_storage_initialize()) return;
    uint8_t *scratch=pvPortMalloc(4096);
    if (!scratch) return;
    for (uint32_t sector=0;sector<2;sector++) {
        if (r1_ep_record_read(sector<<12,scratch,4096))
            r1_stock_crc32_update(scratch,4096,state);
    }
    vPortFree(scratch);
}

/* Stock 0x5e0d8 is the virtual-file length advertised by the EP reader. */
uint32_t r1_ep_export_length(void) { return 8192; }

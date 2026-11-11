#include "native_status_ring.h"
#include "native_ep_storage.h"
volatile uint16_t r1_ep_flash_cursor __attribute__((section(".r1.ep.flash.cursor"),aligned(2)))=0;
extern void vPortEnterCritical(void),vPortExitCritical(void);
void r1_ep_sector_erase_if_dirty(uint32_t sector)
{
    uint8_t marker=255;
    if (r1_ep_record_read(sector<<12,&marker,1) && marker!=255)
        (void)r1_ep_sector_erase(sector);
}
void r1_ep_export_ring_flush(void)
{
    for (;;) {
        vPortEnterCritical();
        if (r1_status_read_index==r1_status_write_index) {vPortExitCritical();return;}
        const volatile struct r1_status_record *record=(const volatile struct r1_status_record *)(uintptr_t)
            ((uint32_t)(uintptr_t)r1_status_records+((uint32_t)r1_status_read_index<<3));
        struct r1_status_record copy={record->packed,record->timestamp};
        r1_status_read_index=(uint8_t)((r1_status_read_index+1u)&15u);
        vPortExitCritical();
        uint32_t cursor=r1_ep_flash_cursor,sector=cursor>>9,position=cursor&511u;
        uint32_t address=(sector<<12)+(position<<3);
        if (!position)r1_ep_sector_erase_if_dirty(sector);
        if (r1_ep_record_write(address,&copy,8)) {
            r1_ep_flash_cursor=(uint16_t)((cursor+1u)&1023u);
            if (position==511)r1_ep_sector_erase_if_dirty(1u&~sector);
        }
    }
}

/* Native completion status 0x55bd70. Vendor polling 0x480826 is upstream
 * am_hal_delay_us_status_check (audio_ble_vendor_wait_480826 defsym).
 * ROM 0x55c548/54c/550: MMIO 0x40050000, errors 0x08000001/2. */
#include <stdint.h>

uint32_t audio_ble_vendor_finish_55bd70(uint32_t channel,uint32_t extra) {
    volatile uint32_t *const status=(volatile uint32_t *)(uintptr_t)
        (0x40050000u+channel*0x1000u+0x204u);
    uint32_t flags=extra|*status;
    if((flags&0x6cu)!=0u)return 0x08000000u;
    if((flags&0x0200u)!=0u)return 0x08000001u;
    if((flags&0x10u)!=0u)return 0x08000002u;
    return (flags&0x4800u)!=0u?1u:0u;
}

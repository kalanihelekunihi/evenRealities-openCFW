/* Native vendor polling 0x480826 and completion status 0x55bd70.
 * ROM 0x55c548/54c/550: MMIO 0x40050000, errors 0x08000001/2. */
#include <stdint.h>

extern void audio_ble_vendor_yield_4807a0(uint32_t);

uint32_t audio_ble_vendor_wait_480826(uint32_t timeout,volatile uint32_t *reg,
                                      uint32_t mask,uint32_t expected,uint32_t equal) {
    for(;;) {
        uint32_t current=*reg&mask;
        if(equal==0u) {
            if(current!=expected)return 0u;
        } else if(current==expected)return 0u;
        if(timeout==0u)return 4u;
        audio_ble_vendor_yield_4807a0(1u);
        --timeout;
    }
}

uint32_t audio_ble_vendor_finish_55bd70(uint32_t channel,uint32_t extra) {
    volatile uint32_t *const status=(volatile uint32_t *)(uintptr_t)
        (0x40050000u+channel*0x1000u+0x204u);
    uint32_t flags=extra|*status;
    if((flags&0x6cu)!=0u)return 0x08000000u;
    if((flags&0x0200u)!=0u)return 0x08000001u;
    if((flags&0x10u)!=0u)return 0x08000002u;
    return (flags&0x4800u)!=0u?1u:0u;
}

/* Apollo S200 MSPI enable/disable core at 0x4c0e1e and 0x4c0ea8. */
#include <stdint.h>

extern uint32_t display_driver_uled_mspi_wait_4bfd62(uint32_t *);
extern void display_driver_uled_mspi_shutdown_4bfc86(uint32_t *);
extern void display_driver_uled_delay_4807a0(uint32_t);
extern void display_driver_uled_mspi_setup_4bfc5a(uint32_t,uint32_t,uint32_t);

static uint32_t valid(uint32_t *handle) {
    return handle!=0 && ((handle[0]&0x01ffffffu)==0x01bebebeu);
}
static volatile uint32_t *module_register(uint32_t *handle,uint32_t offset) {
    return (volatile uint32_t *)(uintptr_t)(0x40060000u+handle[1]*0x1000u+offset);
}

uint32_t display_driver_uled_mspi_disable_4c0ea8(uint32_t *handle) {
    if (!valid(handle)) return 2u;
    if ((handle[0]&0x02000000u)==0u) return 0u;
    if (handle[0x210]!=0u || handle[8]!=0u) return 3u;
    if (handle[6]!=0u) {
        uint32_t result=display_driver_uled_mspi_wait_4bfd62(handle);
        if (result!=0u) return result;
        display_driver_uled_mspi_shutdown_4bfc86(handle);
    }
    handle[0]&=~0x02000000u;
    if ((*module_register(handle,0x90u)&1u)!=0u)
        display_driver_uled_delay_4807a0(handle[0x233]);
    return 0u;
}

uint32_t display_driver_uled_mspi_enable_4c0e1e(uint32_t *handle) {
    if (!valid(handle)) return 2u;
    if (((const uint8_t *)handle)[8]==0u) return 7u;
    if (handle[6]!=0u) {
        handle[7]=0u;handle[8]=0u;
        display_driver_uled_mspi_setup_4bfc5a(handle[1],handle[5],handle[6]);
        *module_register(handle,0x2b4u)=0x400080u;
        handle[0x215]=0u;
        ((uint8_t *)handle)[0x83c]=0u;
        handle[0x211]=0u;handle[0x20e]=0u;handle[0x210]=0u;
        ((uint8_t *)handle)[0x82c]=0u;
        handle[0x20c]=0u;
        ((uint8_t *)handle)[0x82d]=1u;
        handle[0x217]=0u;
    }
    handle[0]|=0x02000000u;
    return 0u;
}

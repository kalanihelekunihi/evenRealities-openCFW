/* Apollo S200 MSPI interrupt enable/clear at 0x4c2328 and 0x4c23de. */
#include <stdint.h>

static uint32_t valid(const uint32_t *handle) {
    return handle!=0 && (handle[0]&0x01ffffffu)==0x01bebebeu;
}
static volatile uint32_t *reg(const uint32_t *handle,uint32_t offset) {
    return (volatile uint32_t *)(uintptr_t)
        (0x40060000u+handle[1]*0x1000u+offset);
}

uint32_t display_driver_uled_interrupt_enable_4c2328(const uint32_t *handle,
                                                       uint32_t mask) {
    if (!valid(handle)) return 2u;
    volatile uint32_t *enable=reg(handle,0x200u);
    *enable|=mask;
    return 0u;
}

uint32_t display_driver_uled_interrupt_clear_4c23de(const uint32_t *handle,
                                                      uint32_t mask) {
    if (!valid(handle)) return 2u;
    *reg(handle,0x208u)=mask;
    (void)*reg(handle,0x204u);
    return 0u;
}

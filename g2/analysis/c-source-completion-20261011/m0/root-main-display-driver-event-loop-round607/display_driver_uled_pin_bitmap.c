/* Apollo pin bitmap providers 0x4c3750, 0x4c377a, 0x4c37a8,
 * 0x4c37ca and 0x4c37fe. Candidate; SRAM table placement remains fixed.
 */
#include <stdint.h>

#define ULED_PIN_BITMAP_BASE 0x20073324u
static volatile uint32_t *pin_bitmap(void) {
    return (volatile uint32_t *)(uintptr_t)ULED_PIN_BITMAP_BASE;
}

uint32_t display_driver_uled_popcount_4c3750(uint32_t value) {
    value -= (value >> 1u) & 0x55555555u;
    value = (value & 0x33333333u) + ((value >> 2u) & 0x33333333u);
    value = (value + (value >> 4u)) & 0x0f0f0f0fu;
    return (value * 0x01010101u) >> 24u;
}

uint32_t display_driver_uled_pin_group_query_4c377a(uint32_t kind) {
    volatile uint32_t *bitmap=pin_bitmap();
    uint32_t base=((uint8_t)kind)*2u;
    return (bitmap[base] != 0u || bitmap[base+1u] != 0u) ? 1u : 0u;
}

uint32_t display_driver_uled_pin_query_4c37a8(uint32_t kind,uint32_t pin) {
    volatile uint32_t *bitmap=pin_bitmap();
    uint32_t bank=((uint8_t)pin) >> 5u;
    return (bitmap[((uint8_t)kind)*2u+bank] >> (pin & 31u)) & 1u;
}

uint32_t display_driver_uled_pin_group_check_4c37ca(uint32_t kind) {
    volatile uint32_t *bitmap=pin_bitmap();
    uint32_t base=((uint8_t)kind)*2u;
    uint32_t count=display_driver_uled_popcount_4c3750(bitmap[base]);
    count+=display_driver_uled_popcount_4c3750(bitmap[base+1u]);
    return (uint8_t)count;
}

uint32_t display_driver_uled_pin_apply_4c37fe(uint32_t kind,
                                                uint32_t pin,
                                                uint32_t enabled) {
    uint32_t type=(uint8_t)kind;
    uint32_t index=(uint8_t)pin;
    if(type >= 7u || index >= 0x39u)return 6u;
    volatile uint32_t *slot=pin_bitmap()+type*2u+(index >> 5u);
    uint32_t mask=1u << (pin & 31u);
    if((uint8_t)enabled != 0u)*slot |= mask;
    else *slot &= ~mask;
    return 0u;
}

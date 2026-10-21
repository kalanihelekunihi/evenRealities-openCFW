/* Native DMA release/resume 0x538e3c/0x538e8c.
 * ROM 0x53924c/c50: 0x01cdcdcd identifier, 0x20080000 barrier threshold. */
#include <stdint.h>
static uint32_t get(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}
static volatile uint32_t *control(const uint8_t *row) {
    uint32_t descriptor=get(row+36u);
    uint32_t address=get((const uint8_t *)(uintptr_t)descriptor);
    return (volatile uint32_t *)(uintptr_t)address;
}

uint32_t audio_ble_vendor_dma_release_538e3c(uint32_t pointer) {
    uint8_t *row=(uint8_t *)(uintptr_t)pointer;
    if(row==0||(get(row)&0x01ffffffu)!=0x01cdcdcdu)return 2u;
    uint32_t flags=get(row);
    if((flags&0x02000000u)==0u) {
        if(get(row+8u)>=0x20080000u)__asm volatile("dmb sy" ::: "memory");
        volatile uint32_t *reg=control(row);
        *reg|=1u;
        put(row,flags|0x02000000u);
    }
    return 0u;
}
uint32_t audio_ble_vendor_dma_resume_538e8c(uint32_t pointer) {
    uint8_t *row=(uint8_t *)(uintptr_t)pointer;
    if(row==0||(get(row)&0x01ffffffu)!=0x01cdcdcdu)return 2u;
    uint32_t flags=get(row);
    if((flags&0x02000000u)!=0u) {
        volatile uint32_t *reg=control(row);
        *reg&=~1u;
        put(row,flags&~0x02000000u);
    }
    return 0u;
}

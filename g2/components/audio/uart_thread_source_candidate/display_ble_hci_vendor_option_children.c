/* Native vendor option callbacks 0x55c13a/0x55c168.
 * ROM 0x55c548 authenticates 0x40050000 vendor MMIO base. */
#include <stdint.h>
extern void audio_ble_vendor_dma_release_538e3c(uint32_t);
extern void audio_ble_vendor_dma_resume_538e8c(uint32_t);
static uint32_t get(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}

void audio_ble_vendor_option_before_store_55c13a(void *record) {
    uint8_t *row=(uint8_t *)record;
    uint32_t index=get(row+4u);
    if(get(row+0x24u)==0u) {
        volatile uint32_t *link=(volatile uint32_t *)(uintptr_t)
            (0x40050000u+index*0x1000u+0x22cu);
        uint8_t *node=(uint8_t *)(uintptr_t)*link;
        put(node,(uint32_t)(uintptr_t)link);
        put(node+4u,(uint32_t)(uintptr_t)node);
    }
    audio_ble_vendor_dma_release_538e3c(get(row+0x828u));
}

void audio_ble_vendor_option_after_load_55c168(void *record) {
    audio_ble_vendor_dma_resume_538e8c(get((const uint8_t *)record+0x828u));
}

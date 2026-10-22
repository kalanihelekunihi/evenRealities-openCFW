/* Native 0x55c11a. */
#include <stdint.h>
#include <stdbool.h>


static uint32_t load32(const uint8_t *p) {
    uint32_t value;
    __builtin_memcpy(&value,p,4u);
    return value;
}
static void store32(uint8_t *p,uint32_t value) {
    __builtin_memcpy(p,&value,4u);
}

/* am_hal_cmdq term 0x53909a and its static update_indices 0x538d18 (formerly
 * audio_ble_vendor_dma_close_53909a / _refresh_538d18 here) now come from
 * AmbiqSuite 5.1.0 hal/mcu/am_hal_cmdq.c; the old name is a payload defsym. */
extern uint32_t audio_ble_vendor_dma_close_53909a(uint8_t *row,uint32_t require_idle); /* am_hal_cmdq_term */

uint32_t audio_ble_vendor_stack_stop_hal_55c11a(uint8_t *row) {
    uint32_t channel=load32(row+0x828u);
    if(channel!=0u) {
        (void)audio_ble_vendor_dma_close_53909a((uint8_t *)(uintptr_t)channel,1u);
        store32(row+0x828u,0u);
    }
    return 0u;
}

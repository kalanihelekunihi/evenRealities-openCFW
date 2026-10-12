/* Native 0x55c11a and 0x53909a. The 0x53909a result's high word
 * preserves incoming R3; the selected callers use its low status only. */
#include <stdint.h>
#include <stdbool.h>

extern uint32_t g2_gpio_critical_save(void); /* native 0x473940 */
extern bool g2_log_is_privileged(void);       /* native CONTROL/IPSR test */

static uint32_t load32(const uint8_t *p) {
    uint32_t value;
    __builtin_memcpy(&value,p,4u);
    return value;
}
static void store32(uint8_t *p,uint32_t value) {
    __builtin_memcpy(p,&value,4u);
}

/* Native 0x538d18 samples the live DMA count while interrupts are disabled. */
__attribute__((noinline)) uint32_t audio_ble_vendor_dma_refresh_538d18(uint8_t *row) {
    uint32_t prior=g2_gpio_critical_save();
    uint8_t *descriptor=(uint8_t *)(uintptr_t)load32(row+36u);
    uint32_t counter=load32((const uint8_t *)(uintptr_t)load32(descriptor+8u));
    uint32_t producer=(load32(row+32u)&0xffffff00u)|(counter&0xffu);
    if((int32_t)(load32(row+32u)-producer)<0)producer-=0x100u;
    store32(row+28u,producer);
    store32(row+12u,load32((const uint8_t *)(uintptr_t)load32(descriptor+4u)));
    if(g2_log_is_privileged())
        __asm volatile("msr primask, %0" : : "r"(prior&1u) : "memory");
    return prior;
}

uint32_t audio_ble_vendor_dma_close_53909a(uint8_t *row,uint32_t require_idle) {
    if(row==0 || (load32(row)&0x01ffffffu)!=0x01cdcdcdu)return 2u;
    audio_ble_vendor_dma_refresh_538d18(row);
    if(require_idle==0u && load32(row+28u)!=load32(row+32u))return 3u;
    store32(row,load32(row)&~0x01000000u);
    uint8_t *descriptor=(uint8_t *)(uintptr_t)load32(row+36u);
    volatile uint32_t *enable=(volatile uint32_t *)(uintptr_t)load32(descriptor);
    *enable&=~1u;
    volatile uint32_t *status=(volatile uint32_t *)(uintptr_t)load32(descriptor+16u);
    *status&=~load32(descriptor+20u);
    return 0u;
}

uint32_t audio_ble_vendor_stack_stop_hal_55c11a(uint8_t *row) {
    uint32_t channel=load32(row+0x828u);
    if(channel!=0u) {
        (void)audio_ble_vendor_dma_close_53909a((uint8_t *)(uintptr_t)channel,1u);
        store32(row+0x828u,0u);
    }
    return 0u;
}

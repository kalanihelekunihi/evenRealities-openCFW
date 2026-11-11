/* Apollo LVGL image cache lookup at 0x489460..0x489499. */
#include <stdint.h>

extern uint32_t lv_cache_acquire(uint32_t,const void *,uint32_t);
extern uint32_t lv_cache_entry_get_data(uint32_t);

uint32_t audio_uart_lv_decoder_cache_489460(void *decoder_result) {
    uint8_t *out=(uint8_t *)decoder_result;
    uint32_t key[3]={0u,0u,0u};
    key[1]=*(uint32_t *)(void *)(out+12u);
    ((uint8_t *)key)[8]=out[16u];
    const uint32_t entry=lv_cache_acquire(
        *(uint32_t *)(void *)(out+64u),key,0u);
    if (entry==0u) return 0u;
    const uint32_t data=lv_cache_entry_get_data(entry);
    *(uint32_t *)(void *)(out+44u)=*(uint32_t *)(uintptr_t)(data+12u);
    *(uint32_t *)(void *)out=*(uint32_t *)(uintptr_t)(data+16u);
    *(uint32_t *)(void *)(out+68u)=entry;
    return 1u;
}

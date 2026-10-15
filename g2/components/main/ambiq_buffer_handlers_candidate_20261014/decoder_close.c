/* Apollo LVGL image decoder close at 0x48908c..0x4890c7. */
#include <stdint.h>

extern uint32_t audio_uart_lv_image_cache_enabled_4d4b24(void);
extern void audio_uart_lv_decoder_release_4d4e72(uint32_t,uint32_t,uint32_t);

void audio_uart_lv_image_decoder_close_48908c(void *decoder_result) {
    const uint32_t decoder=*(const uint32_t *)decoder_result;
    if (decoder==0u) return;
    const uint32_t close_callback=*(const uint32_t *)(uintptr_t)(decoder+12u);
    if (close_callback!=0u) {
        ((void (*)(uint32_t,void *))(uintptr_t)close_callback)(
            decoder,decoder_result);
    }
    if (audio_uart_lv_image_cache_enabled_4d4b24()!=0u) {
        const uint8_t *result=(const uint8_t *)decoder_result;
        const uint32_t owner=*(const uint32_t *)(const void *)(result+0x40u);
        const uint32_t resource=*(const uint32_t *)(const void *)(result+0x44u);
        if (owner!=0u && resource!=0u)
            audio_uart_lv_decoder_release_4d4e72(owner,resource,0u);
    }
}

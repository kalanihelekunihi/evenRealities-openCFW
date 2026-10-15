/* Apollo LVGL image source classifier and default decode options. */
#include <stdint.h>

uint32_t audio_uart_lv_image_source_type_488cb8(const void *source) {
    if (source==0) return 3u;
    const uint32_t first=*(const uint8_t *)source;
    if (first-32u<96u) return 1u;
    if (first<128u) return 0u;
    return 2u;
}

void audio_uart_lv_decoder_default_options_4d4ccc(void *options,uint32_t size) {
    uint8_t *bytes=(uint8_t *)options;
    for (uint32_t i=0;i<size;i++) bytes[i]=0u;
}

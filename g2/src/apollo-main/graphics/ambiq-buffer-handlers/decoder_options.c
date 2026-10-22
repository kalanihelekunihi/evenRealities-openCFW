/* Apollo LVGL image source classifier, stock 0x488cb8 (LVGL 9.3
 * lv_image_src_get_type: NULL -> UNKNOWN 3, printable first byte -> FILE 1,
 * byte >= 0x80 -> SYMBOL 2, otherwise VARIABLE 0).
 * The default-options zero fill 0x4d4ccc that used to live here duplicated
 * audio_app_zero_tail_4d4ccc (audio/audio-app); its old name
 * audio_uart_lv_decoder_default_options_4d4ccc is now a defsym to it. */
#include <stdint.h>

uint32_t audio_uart_lv_image_source_type_488cb8(const void *source) {
    if (source==0) return 3u;
    const uint32_t first=*(const uint8_t *)source;
    if (first-32u<96u) return 1u;
    if (first<128u) return 0u;
    return 2u;
}

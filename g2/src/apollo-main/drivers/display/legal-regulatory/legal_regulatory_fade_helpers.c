/* Native fade-in callback 0x58c12c. The second callback here, stock 0x45065a,
 * is upstream lv_anim_path_ease_in (lvgl/src/misc/lv_anim.c); its callers use that
 * name (build/dedup2/B/anim.py, 104,209 cases, 0 mismatches). */
#include <stdint.h>

extern void audio_uart_display_audio_reset_441488(uint32_t object,
                                                    uint32_t alpha,
                                                    uint32_t selector);

void audio_legal_regulatory_fade_callback_58c12c(uint32_t object,
                                                   uint32_t alpha) {
    audio_uart_display_audio_reset_441488(object, (uint8_t)alpha, 0u);
}

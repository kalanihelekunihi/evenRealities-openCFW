/* Two native fade-in callbacks, 0x58c12c and 0x45065a. */
#include <stdint.h>

extern void audio_uart_display_audio_reset_441488(uint32_t object,
                                                    uint32_t alpha,
                                                    uint32_t selector);
extern int32_t audio_uart_lv_anim_bezier_450a04(void *descriptor,
                                                 int32_t c1, int32_t c2,
                                                 int32_t c3, int32_t c4);

void audio_legal_regulatory_fade_callback_58c12c(uint32_t object,
                                                   uint32_t alpha) {
    audio_uart_display_audio_reset_441488(object, (uint8_t)alpha, 0u);
}

int32_t audio_uart_lv_anim_path_45065a(void *descriptor) {
    return audio_uart_lv_anim_bezier_450a04(descriptor, 0x1ae, 0, 0x400, 0x400);
}

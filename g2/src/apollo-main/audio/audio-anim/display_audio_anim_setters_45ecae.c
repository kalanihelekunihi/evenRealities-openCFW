/* Apollo audio animation value callbacks, stock 0x45ecae..0x45ecc8. */
#include <stdint.h>

extern void audio_uart_page_43f0e0(uint32_t object, uint32_t x);
extern void audio_uart_page_43f142(uint32_t object, uint32_t y);
extern void audio_uart_display_audio_reset_441488(uint32_t object,
                                                   uint32_t value,
                                                   uint32_t unused);

/* Stock 0x0045ECAE (lv_obj_set_x anim exec callback) */
void audio_uart_display_anim_x_a_45ecaf(uint32_t object, uint32_t value) {
    audio_uart_page_43f0e0(object, value);
}

/* Stock 0x0045ECB6 (lv_obj_set_y anim exec callback) */
void audio_uart_display_anim_y_a_45ecb7(uint32_t object, uint32_t value) {
    audio_uart_page_43f142(object, value);
}

/* Stock 0x0045ECBE (opa anim exec callback) */
void audio_uart_display_anim_alpha_45ecbf(uint32_t object, uint32_t value) {
    audio_uart_display_audio_reset_441488(object, (uint8_t)value, 0u);
}

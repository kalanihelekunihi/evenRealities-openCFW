/* Stock Terminal reset children 0x5eae2c and 0x5e4c84. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_terminal_mode_set_5eae1e(uint32_t mode, uint32_t mask);
extern void audio_lv_object_call_43ded4(uint32_t object, uint32_t value);
extern void audio_lv_obj_invalidate_43dfa4(uint32_t object, uint32_t value);
extern void audio_terminal_processing_prepare_5ea30c(void);

void audio_terminal_reset_mode_5eae2c(uint32_t mode) {
    audio_terminal_mode_set_5eae1e((uint8_t)mode, 0xffffu);
}

void audio_terminal_reset_display_5e4c84(uint32_t enabled) {
    uint32_t object = *(const uint32_t *)(const void *)
        (audio_terminal_ui_state_base + 4u);
    if (object == 0u)
        return;
    if ((uint8_t)enabled != 0u) {
        audio_lv_object_call_43ded4(object, 1u);
    } else if (audio_terminal_ui_state_base[0x27eu] == 0u) {
        audio_lv_obj_invalidate_43dfa4(object, 1u);
        audio_terminal_processing_prepare_5ea30c();
    }
}

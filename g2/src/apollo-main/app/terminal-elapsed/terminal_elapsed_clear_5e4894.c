/* Stock Terminal elapsed-label fallback 0x5e4894. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_lv_anim_start_49942e(uint32_t object, const uint32_t *value);
extern void audio_lv_object_call_43ded4(uint32_t object, uint32_t value);

static const uint32_t empty_animation_value = 0u; /* stock 0x5e4b64 */

void audio_terminal_elapsed_clear_5e4894(void) {
    uint32_t object = *(const uint32_t *)(const void *)
        (audio_terminal_ui_state_base + 0x1d8u);
    if (object == 0u)
        return;
    audio_lv_anim_start_49942e(object, &empty_animation_value);
    audio_lv_object_call_43ded4(object, 1u);
}

/* Stock Terminal output-content transition 0x5e49b0. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint8_t audio_terminal_output_style_20003f80[];
extern uint32_t audio_terminal_output_payload_20074a94;
extern uint8_t audio_terminal_output_mode_2007502d;
extern uint8_t audio_terminal_output_active_2007502c;
extern void audio_lv_obj_invalidate_43dfa4(uint32_t, uint32_t);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern uint32_t audio_terminal_set_label_style_5e482a(uint32_t, const void *,
                                                       uint32_t, uint32_t);
extern uint32_t audio_terminal_select_output_mode_5ea2a8(uint32_t);
extern void audio_lv_anim_start_49942e(uint32_t, const char *);
extern void audio_terminal_elapsed_refresh_5e4902(void);

static const char thinking_text[] = "Thinking...";
static const char hold_text[] = "[Tap & hold to stop response]";

static uint32_t state_word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

void audio_terminal_set_output_5e49b0(uint32_t output,
                                        uint32_t update,
                                        uint32_t payload) {
    if (state_word(0x1ccu) == 0u || state_word(0x1d0u) == 0u ||
        state_word(0x1d4u) == 0u || state_word(0x1dcu) == 0u)
        return;
    audio_lv_obj_invalidate_43dfa4(state_word(0x1ccu), 1u);
    audio_terminal_processing_prepare_5ea30c();
    (void)audio_terminal_set_label_style_5e482a(state_word(0x1d0u),
                                                  audio_terminal_output_style_20003f80,
                                                  6u, 100u);
    if ((uint8_t)output != 0u) {
        uint8_t mode = (uint8_t)audio_terminal_select_output_mode_5ea2a8(payload);
        audio_terminal_output_payload_20074a94 = payload;
        audio_terminal_output_mode_2007502d = mode;
        audio_terminal_output_active_2007502c = 1u;
    } else if ((uint8_t)update != 0u) {
        if (audio_terminal_output_active_2007502c != 0u)
            (void)audio_terminal_select_output_mode_5ea2a8(
                audio_terminal_output_mode_2007502d);
        else
            audio_lv_anim_start_49942e(state_word(0x1d4u), thinking_text);
    }
    audio_lv_anim_start_49942e(state_word(0x1dcu), hold_text);
    audio_terminal_elapsed_refresh_5e4902();
}

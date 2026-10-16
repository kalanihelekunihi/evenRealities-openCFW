/* Stock Terminal output phrase selector 0x5ea256/0x5ea270/0x5ea2a8. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_lv_anim_start_49942e(uint32_t object, const void *text);

static const char *const phrases[10] = {
    "Architecting...", "Cogitating...", "Computing...", "Exploring...",
    "Planning...", "Generating...", "Inferring...", "Pondering...",
    "Processing...", "Thinking..."
};

uint32_t audio_terminal_output_hash_5ea256(uint32_t value) {
    value = 0x7feb352du * (value ^ (value >> 16));
    value = 0x846ca68bu * (value ^ (value >> 15));
    return value ^ (value >> 16);
}

uint32_t audio_terminal_select_output_mode_core_5ea270(uint32_t payload) {
    uint32_t object = *(const uint32_t *)(const void *)
        (audio_terminal_ui_state_base + 0x1d4u);
    if (object == 0u)
        return 0u;
    uint32_t selected = audio_terminal_output_hash_5ea256(payload) % 10u;
    audio_lv_anim_start_49942e(object, phrases[selected]);
    return (uint8_t)selected;
}

uint32_t audio_terminal_select_output_mode_5ea2a8(uint32_t payload) {
    return audio_terminal_select_output_mode_core_5ea270(payload);
}

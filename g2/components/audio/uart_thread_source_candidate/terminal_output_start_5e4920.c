/* Stock Terminal output-start visual transition 0x5e4920. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_lv_obj_invalidate_43dfa4(uint32_t, uint32_t);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern void audio_terminal_processing_hide_5e4878(uint32_t);
extern void audio_lv_anim_start_49942e(uint32_t, const uint32_t *);
extern void audio_terminal_elapsed_refresh_5e4902(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[] = "terminal_ui_status_switch_to_processing_output";
static const char message[] =
    "apply output_start: hide thinking word and stop icon anim";
static const char short_message[] =
    "[terminal.ui]apply output_start: hide thinking word and stop icon anim";
static const uint32_t stopped_animation_value = 0u;

static uint32_t state_word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

void audio_terminal_output_start_5e4920(void) {
    if (state_word(0x1ccu) == 0u || state_word(0x1d0u) == 0u ||
        state_word(0x1d4u) == 0u || state_word(0x1dcu) == 0u)
        return;
    audio_lv_obj_invalidate_43dfa4(state_word(0x1ccu), 1u);
    audio_terminal_processing_prepare_5ea30c();
    audio_terminal_processing_hide_5e4878(state_word(0x1d0u));
    audio_lv_anim_start_49942e(state_word(0x1d4u),
                                &stopped_animation_value);
    audio_terminal_elapsed_refresh_5e4902();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0xaeu, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10000000u, short_message, short_message);
}

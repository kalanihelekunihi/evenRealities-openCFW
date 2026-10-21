/* Stock Terminal elapsed-time label formatter 0x5e48b8. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_lv_label_set_text_fmt_49954c(uint32_t label,
                                                const char *format, ...);
extern void audio_lv_obj_invalidate_43dfa4(uint32_t object, uint32_t redraw);

static const char seconds_format[] = "%lus";
static const char minutes_format[] = "%lum%02lus";

void audio_terminal_elapsed_text_5e48b8(uint32_t seconds) {
    uint32_t label = *(uint32_t *)(void *)(audio_terminal_ui_state_base + 0x1d8u);
    if (label == 0u)
        return;
    if (seconds < 60u)
        audio_lv_label_set_text_fmt_49954c(label, seconds_format, seconds);
    else
        audio_lv_label_set_text_fmt_49954c(label, minutes_format,
                                            seconds / 60u, seconds % 60u);
    audio_lv_obj_invalidate_43dfa4(label, 1u);
}

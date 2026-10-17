/* Apollo Main Conversate transcribe-label update 0x5b32b4..0x5b332d. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_lv_child_44dce2(uint32_t, uint32_t);
extern const char *audio_conversate_transcribe_get_5b4364(void);
extern void audio_uart_page_49942e(uint32_t, const char *);
extern int32_t audio_uart_lv_obj_height_43fdda(uint32_t);
extern void audio_terminal_display_status_44ea04(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_main_page.c";
static const char function[] = "conversate_ui_action_transcribe_update";
static const char missing[] = "transcribe_label is NULL";
static const char compact[] = "[conversate.ui]transcribe_label is NULL";

uint32_t audio_conversate_ui_route_5b32b4(void) {
    const volatile uint8_t *const ui = (const volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint32_t parent = *(const volatile uint32_t *)(const void *)(ui + 0x20u);
    const uint32_t label = audio_lv_child_44dce2(parent, 0u);
    if (label == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x208u, missing);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, compact, compact);
        return 0u;
    }
    audio_uart_page_49942e(label, audio_conversate_transcribe_get_5b4364());
    const int32_t parent_height = audio_uart_lv_obj_height_43fdda(parent);
    const int32_t label_height = audio_uart_lv_obj_height_43fdda(label);
    audio_terminal_display_status_44ea04(parent,
                                          (uint32_t)(label_height - parent_height), 0u);
    return 0u;
}

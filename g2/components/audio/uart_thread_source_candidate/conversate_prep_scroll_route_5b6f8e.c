/* Apollo Main prep-note page scroll route, 0x5b6f8e..0x5b705f. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern int32_t audio_conversate_prep_scroll_clamp_5b6a3a(int32_t);
extern int32_t audio_uart_lv_obj_y_44e498(uint32_t);
extern void audio_terminal_display_status_44ea04(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.prep";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_prep_note_page.c";
static const char function[] = "conversate_ui_action_prep_note_page_scroll";
static const char same[] =
    "prep scroll target y=%d is same as current y, skip";
static const char same_compact[] =
    "[conversate.prep]prep scroll target y=%d is same as current y, skip";
static const char begin[] = "prep scroll begin y=%d target=%d";
static const char begin_compact[] =
    "[conversate.prep]prep scroll begin y=%d target=%d";

static uint32_t word(const volatile uint8_t *bytes, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(bytes + offset);
}

uint32_t audio_conversate_ui_route_5b6f8e(uint32_t ignored, int32_t requested) {
    (void)ignored;
    const volatile uint8_t *const ui = (const volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    if (word(ui, 0x28u) == 0u) return 0u;
    const int32_t target = audio_conversate_prep_scroll_clamp_5b6a3a(requested);
    const uint32_t note = word(ui, 0x24u);
    const int32_t current = audio_conversate_prep_scroll_clamp_5b6a3a(
        audio_uart_lv_obj_y_44e498(note));
    if (current == target) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0x11eu,
                               same, target);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08400000u, same_compact,
                                        same_compact, target);
        return 0u;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x122u,
                           begin, current, target);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c800000u, begin_compact,
                                    begin_compact, current, target);
    audio_terminal_display_status_44ea04(note, (uint32_t)target, 1u);
    return 0u;
}

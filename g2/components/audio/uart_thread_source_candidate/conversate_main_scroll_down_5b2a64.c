/* Apollo Main Conversate main-page next-button route 0x5b2a64..0x5b2b73. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_conversate_ui_list_count_5b0c18(void);
extern uint32_t audio_lv_child_44dce2(uint32_t, uint32_t);
extern void audio_conversate_ui_list_view_mode_set_5b0edc(uint32_t, uint32_t, const char *);
extern uint32_t audio_terminal_session_animate_5896fc(uint32_t, uint32_t, uint32_t);
extern void audio_conversate_main_list_scroll_58a680(uint32_t, uint32_t, uint32_t,
                                                     uint32_t, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_main_page.c";
static const char function[] = "conversate_ui_action_main_page_scroll_down";
static const char bottom[] = "Reached bottom button during scroll, stopping at index %d";
static const char bottom_compact[] =
    "[conversate.ui]Reached bottom button during scroll, stopping at index %d";
static const char missing[] = "No next button found";
static const char missing_compact[] = "[conversate.ui]No next button found";
static const char reason[] = "main page scroll down";

static uint32_t word(const volatile uint8_t *state, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(state + offset);
}
static void put_word(volatile uint8_t *state, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(state + offset) = value;
}

uint32_t audio_conversate_ui_route_5b2a64(uint32_t ignored, uint32_t trigger,
                                            uint32_t extra) {
    (void)ignored;
    const uint32_t count = audio_conversate_ui_list_count_5b0c18();
    if (trigger == 0u) return 0u;
    volatile uint8_t *const ui = (volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint32_t list = word(ui, 0x64u);
    const int32_t index = (int32_t)word(ui, 0x84u);
    if (trigger == 0xaau) {
        audio_conversate_main_list_scroll_58a680(
            list, word(ui, 0x7cu) != 0u ? 40u : 0u, 0u, 0u, trigger, extra);
        return 0u;
    }
    if (index >= (int32_t)(count - 1u)) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, path, function, 0xedu, bottom, (uint32_t)index);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x10400000u,
                                        bottom_compact, bottom_compact, (uint32_t)index);
        return 0u;
    }
    const uint32_t next = audio_lv_child_44dce2(list, (uint32_t)(index + 1));
    if (next == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0xf3u, missing);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, missing_compact, missing_compact);
        return 0u;
    }
    audio_conversate_ui_list_view_mode_set_5b0edc(2u, 0u, reason);
    (void)audio_terminal_session_animate_5896fc(word(ui, 0x80u), next, 200u);
    put_word(ui, 0x80u, next);
    put_word(ui, 0x84u, (uint32_t)(index + 1));
    return 0u;
}

/* Apollo Main Conversate main-page previous-button route 0x5b29bc..0x5b2a63. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_lv_child_44dce2(uint32_t, uint32_t);
extern void audio_conversate_ui_list_view_mode_set_5b0edc(uint32_t, uint32_t, const char *);
extern uint32_t audio_terminal_session_animate_5896fc(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_main_page.c";
static const char function[] = "conversate_ui_action_main_page_scroll_up";
static const char missing[] = "No prev button found";
static const char compact[] = "[conversate.ui]No prev button found";
static const char reason[] = "main page scroll up";

static uint32_t word(const volatile uint8_t *state, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(state + offset);
}
static void put_word(volatile uint8_t *state, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(state + offset) = value;
}

uint32_t audio_conversate_ui_route_5b29bc(uint32_t ignored, uint32_t trigger) {
    (void)ignored;
    if (trigger == 0u) return 0u;
    volatile uint8_t *const ui = (volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint32_t selected = word(ui, 0x7cu);
    const int32_t index = (int32_t)word(ui, 0x84u);
    uint32_t previous = 0u;
    if (selected != 0u && index == 0) {
        previous = selected;
    } else if (index > 0) {
        previous = audio_lv_child_44dce2(word(ui, 0x64u), (uint32_t)(index - 1));
    }
    if (previous == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0xcbu, missing);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, compact, compact);
        return 0u;
    }
    audio_conversate_ui_list_view_mode_set_5b0edc(2u, 0u, reason);
    (void)audio_terminal_session_animate_5896fc(word(ui, 0x80u), previous, 200u);
    put_word(ui, 0x80u, previous);
    put_word(ui, 0x84u, (uint32_t)(index - 1));
    return 0u;
}
